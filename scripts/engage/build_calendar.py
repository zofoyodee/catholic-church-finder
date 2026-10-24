"""Find churches named for each celebration of the calendar and write data/calendar.json,
which the page uses to pick the church of the day."""
import base64, json, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from calendar_src import FIXED, MOVEABLE, FEATURED

ROOT = Path(__file__).resolve().parents[2]
meta = json.loads((ROOT / 'data/meta.json').read_text())
raw = base64.b64decode((ROOT / 'data/points.txt').read_text().strip())
n = len(raw) // 9
typ = raw[n * 8:]
lines = '\n'.join((ROOT / f'data/search-{k}.txt').read_text() for k in range(meta['searchChunks'])).split('\n')
fold = lambda s: ' ' + re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower())).strip() + ' '
names = [fold(l.split('\t')[0]) for l in lines[:n]]
ccs = [l.split('\t')[2] if l.count('\t') >= 2 else '' for l in lines[:n]]
tours = json.loads((ROOT / 'data/tours.json').read_text())
stop_idx = {s['name']: s['i'] for t in tours['tours'] for s in t['stops']}
RANK = {1: 0, 2: 0, 3: 1, 6: 2, 0: 3, 4: 3, 5: 4}  # cathedrals and basilicas first, then shrines, parishes
JUNK = re.compile(r'\b(school|escuela|colegio|escola|scuola|ecole|office|oficina|secretaria|ministry|ministerio|youth|grupo|group|pastoral|store|shop|tienda|loja|cemetery|cementerio|cemiterio|cimitero|hall|salon|center|centro|centre|foundation|fundacion|hospital|college|university|universidad|festival|fiesta|feria|event|eventos|choir|coro|museum|museo|museu|parking|rectory|2024|2025|2026)\b')

def candidates(pattern, k=40):
    rx = re.compile(pattern)
    hits = [i for i in range(n) if not (typ[i] >> 3) and rx.search(names[i]) and not JUNK.search(names[i])]
    hits.sort(key=lambda i: (RANK.get(typ[i] & 7, 3), i))
    # spread the picks across countries: take the best of each country in turn
    by_cc, order = {}, []
    for i in hits: by_cc.setdefault(ccs[i], []).append(i)
    queues = sorted(by_cc.values(), key=lambda q: (RANK.get(typ[q[0]] & 7, 3), -len(q)))
    while len(order) < k and any(queues):
        for q in queues:  # noqa
            if q and len(order) < k: order.append(q.pop(0))
    return order, len(hits)

out = {'fixed': [], 'moveable': {}, 'featured': {}}
for md, rank, title, wiki, pat in FIXED:
    c, total = candidates(pat) if pat else ([], 0)
    out['fixed'].append([md, rank, title, wiki, c])
    if total < 5: print(f'{md} {title}: only {total} churches', file=sys.stderr)
for key, (title, pat) in MOVEABLE.items():
    c, total = candidates(pat)
    out['moveable'][key] = [title, c]
for key, stop in FEATURED.items():
    if stop_idx.get(stop) is not None: out['featured'][key] = stop_idx[stop]
    else: print('featured stop has no church:', stop, file=sys.stderr)
# the rotation for ordinary days: every church the tours visit
out['rotation'] = [s['i'] for t in tours['tours'] for s in t['stops'] if s['i'] is not None]
(ROOT / 'data/calendar.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print('calendar.json', (ROOT / 'data/calendar.json').stat().st_size, 'bytes', file=sys.stderr)
for md, rank, title, wiki, c in out['fixed'][::12]:
    print(md, title, '->', [lines[i].split('\t')[0] + ' (' + ccs[i] + ')' for i in c[:4]], file=sys.stderr)
