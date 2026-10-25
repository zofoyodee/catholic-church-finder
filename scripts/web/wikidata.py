"""Fill missing church websites and social accounts from Wikidata.

Finds Catholic places on Wikidata that have coordinates and an official website
(P856) or social accounts (Facebook P2013, Instagram P2003, YouTube P2397,
X P2002), and gives them to the nearest church in our data (within 80 m).
Writes data/web/wikidata_sites.json ({church index: url}, only for churches
without a website) and data/web/wikidata_social.json ({church index: [url, ...]}).
"""
import json, math, struct, base64, urllib.request, urllib.parse, collections, os, re

Q = """SELECT ?item ?coord ?site WHERE {
  VALUES ?rel { wd:Q9592 wd:Q1841 }
  ?item wdt:P140 ?rel; wdt:P625 ?coord; wdt:P856 ?site.
}"""
SOCIAL = {'P2013': 'https://www.facebook.com/{}', 'P2003': 'https://www.instagram.com/{}',
          'P2397': 'https://www.youtube.com/channel/{}', 'P2002': 'https://x.com/{}'}


def sparql(q):
    req = urllib.request.Request('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(q),
                                 headers={'User-Agent': 'CatholicChurchFinderBot/1.0 (+https://github.com/zofoyodee/catholic-church-finder)', 'Accept': 'application/sparql-results+json'})
    return json.load(urllib.request.urlopen(req, timeout=300))['results']['bindings']


def points(rows, key):
    out = collections.defaultdict(list)
    for b in rows:
        m = re.match(r'Point\(([-\d.eE]+) ([-\d.eE]+)\)', b['coord']['value'])
        if m:
            out[b['item']['value']].append((float(m.group(1)), float(m.group(2)), key(b)))
    return out


items = {q: v[0] for q, v in points(sparql(Q), lambda b: b['site']['value']).items()}
print('wikidata items with website:', len(items))
social = collections.defaultdict(list)
for p, fmt in SOCIAL.items():
    try:
        rows = sparql(Q.replace('wdt:P856 ?site', f'wdt:{p} ?site'))
    except Exception as e:  # noqa: BLE001 - socials are a bonus; the websites still get written
        print('social query failed', p, e)
        continue
    for q, v in points(rows, lambda b: fmt.format(b['site']['value'])).items():
        if not any(u.split('/')[2] == v[0][2].split('/')[2] for *_, u in social[q]):
            social[q].append(v[0])
print('wikidata items with social accounts:', len(social))

raw = base64.b64decode(open('data/points.txt').read())
meta = json.load(open('data/meta.json'))
n = meta['count']
lon = struct.unpack_from(f'<{n}i', raw, 0)
lat = struct.unpack_from(f'<{n}i', raw, 4 * n)
grid = collections.defaultdict(list)
for i in range(n):
    grid[(round(lat[i] / 1e6 * 500), round(lon[i] / 1e6 * 500))].append(i)

def nearest(x, y):
    """The church within 80 m of a Wikidata point, when no other church is close behind."""
    gy, gx = round(y * 500), round(x * 500)
    cands = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            for i in grid.get((gy + dy, gx + dx), []):
                d = math.hypot((lat[i] / 1e6 - y) * 111320, (lon[i] / 1e6 - x) * 111320 * math.cos(math.radians(y)))
                cands.append((d, i))
    cands.sort()
    if cands and cands[0][0] <= 80 and (len(cands) == 1 or cands[1][0] > cands[0][0] + 15):
        return cands[0]
    return None


best = {}
for qid, (x, y, site) in items.items():
    hit = nearest(x, y)
    if hit and (hit[1] not in best or hit[0] < best[hit[1]][0]):
        best[hit[1]] = (hit[0], site)
soc = {}
for qid, v in social.items():
    hit = nearest(v[0][0], v[0][1])
    if hit and (hit[1] not in soc or hit[0] < soc[hit[1]][0]):
        soc[hit[1]] = (hit[0], [u for *_, u in v])

has_web = set()
for k in range(meta['shards']):
    for j, r in enumerate(json.load(open(f'data/d/{k}.json'))):
        if r[6]:
            has_web.add(k * meta['shardSize'] + j)
out = {str(i): s for i, (d, s) in sorted(best.items()) if i not in has_web}
os.makedirs('data/web', exist_ok=True)
json.dump(out, open('data/web/wikidata_sites.json', 'w'), separators=(',', ':'))
json.dump({str(i): u for i, (d, u) in sorted(soc.items())}, open('data/web/wikidata_social.json', 'w'), separators=(',', ':'))
print('matched', len(best), 'filled', len(out), 'social', len(soc))
