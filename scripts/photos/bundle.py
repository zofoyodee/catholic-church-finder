# Pack fetched photos into concatenated JPEG bundles (stable, in priority order) + data/photos.json index.
import json, os, re, sys
W = '/tmp/claude-0/work/'; SITE = sys.argv[1]; PER = 20
sel = json.load(open(W + 'selected.json')); credits = json.load(open(W + 'credits.json'))
os.makedirs(SITE + '/photos', exist_ok=True); os.makedirs(SITE + '/data', exist_ok=True)
def author(a):
    a = re.sub(r'^(?:original uploader|creator:|user:)\s*\|?', '', a, flags=re.I)
    a = a.split('|')[0].strip(' :?')
    if not a or re.fullmatch(r'unknown|author|unknown author|\?', a, re.I): return 'Unknown author'
    return a[:60]
done = [k for k in sel if k in credits and os.path.exists(W + 'img/' + k + '.jpg')]
rows = []; total = 0
for b in range(0, len(done) - len(done) % PER if len(sys.argv) < 3 else len(done), PER):
    chunk = done[b:b + PER]; off = 0; blob = bytearray()
    for k in chunk:
        d = open(W + 'img/' + k + '.jpg', 'rb').read()
        fn, au, lic = credits[k]
        rows.append([int(k), b // PER, off, len(d), fn.replace('_', ' '), author(au), lic]); blob += d; off += len(d)
    open(f'{SITE}/photos/{b // PER}.jpg', 'wb').write(blob); total += len(blob)
rows.sort()
json.dump({'p': rows, 'source': 'Wikimedia Commons'}, open(SITE + '/data/photos.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(rows), 'photos in', (len(rows) + PER - 1) // PER, 'bundles', round(total / 1e6, 1), 'MB; index', os.path.getsize(SITE + '/data/photos.json'))
