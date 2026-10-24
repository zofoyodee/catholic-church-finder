"""Fill missing church websites from Wikidata (official website, P856).

Finds Catholic places on Wikidata that have coordinates and a website, and
gives the website to the nearest church in our data (within 80 m) when that
church has none. Writes data/web/wikidata_sites.json: {church index: url}.
"""
import json, math, struct, base64, urllib.request, urllib.parse, collections, os, re

Q = """SELECT ?item ?coord ?site WHERE {
  VALUES ?rel { wd:Q9592 wd:Q1841 }
  ?item wdt:P140 ?rel; wdt:P625 ?coord; wdt:P856 ?site.
}"""
req = urllib.request.Request('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(Q),
                             headers={'User-Agent': 'CatholicChurchFinderBot/1.0 (+https://github.com/zofoyodee/catholic-church-finder)', 'Accept': 'application/sparql-results+json'})
rows = json.load(urllib.request.urlopen(req, timeout=300))['results']['bindings']
items = {}
for b in rows:
    m = re.match(r'Point\(([-\d.eE]+) ([-\d.eE]+)\)', b['coord']['value'])
    if m:
        items.setdefault(b['item']['value'], (float(m.group(1)), float(m.group(2)), b['site']['value']))
print('wikidata items with website:', len(items))

raw = base64.b64decode(open('data/points.txt').read())
meta = json.load(open('data/meta.json'))
n = meta['count']
lon = struct.unpack_from(f'<{n}i', raw, 0)
lat = struct.unpack_from(f'<{n}i', raw, 4 * n)
grid = collections.defaultdict(list)
for i in range(n):
    grid[(round(lat[i] / 1e6 * 500), round(lon[i] / 1e6 * 500))].append(i)

best = {}
for qid, (x, y, site) in items.items():
    gy, gx = round(y * 500), round(x * 500)
    cands = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            for i in grid.get((gy + dy, gx + dx), []):
                d = math.hypot((lat[i] / 1e6 - y) * 111320, (lon[i] / 1e6 - x) * 111320 * math.cos(math.radians(y)))
                cands.append((d, i))
    cands.sort()
    if cands and cands[0][0] <= 80 and (len(cands) == 1 or cands[1][0] > cands[0][0] + 15):
        d, i = cands[0]
        if i not in best or d < best[i][0]:
            best[i] = (d, site)

has_web = set()
for k in range(meta['shards']):
    for j, r in enumerate(json.load(open(f'data/d/{k}.json'))):
        if r[6]:
            has_web.add(k * meta['shardSize'] + j)
out = {str(i): s for i, (d, s) in sorted(best.items()) if i not in has_web}
os.makedirs('data/web', exist_ok=True)
json.dump(out, open('data/web/wikidata_sites.json', 'w'), separators=(',', ':'))
print('matched', len(best), 'filled', len(out))
