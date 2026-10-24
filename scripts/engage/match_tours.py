"""Snap each tour stop to the church it names in data/, so a stop can open that church's card.
Prints the candidates for review and writes data/tours.json."""
import base64, json, math, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
meta = json.loads((ROOT / 'data/meta.json').read_text())
raw = base64.b64decode((ROOT / 'data/points.txt').read_text().strip())
n = len(raw) // 9
import array
lon = array.array('i'); lon.frombytes(raw[:n * 4])
lat = array.array('i'); lat.frombytes(raw[n * 4:n * 8])
typ = raw[n * 8:]
shards = {}
def rec(i):
    s = i // meta['shardSize']
    if s not in shards: shards[s] = json.loads((ROOT / f'data/d/{s}.json').read_text())
    return shards[s][i - s * meta['shardSize']]
fold = lambda s: re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower())
def metres(a, b, c, d):
    r = math.pi / 180; x = (d - b) * r * math.cos((a + c) / 2 * r); y = (c - a) * r
    return math.hypot(x, y) * 6371000

src = json.loads((Path(__file__).parent / 'tours_src.json').read_text())
for tour in src['tours']:
    for st in tour['stops']:
        cands = []
        for i in range(n):
            la, lo = lat[i] / 1e6, lon[i] / 1e6
            if abs(la - st['lat']) > 0.02 or abs(lo - st['lon']) > 0.03: continue
            d = metres(st['lat'], st['lon'], la, lo)
            if d > 400: continue
            nm = fold(rec(i)[0])
            hits = sum(1 for k in st['match'] if fold(k).strip() in nm)
            t = typ[i] & 7
            score = hits * 2 + (1 if t in (1, 2, 3) else 0) - d / 500 + (10 if st.get('pick') and st['pick'] in rec(i)[0] else 0)
            cands.append((score, d, i, rec(i)[0], t))
        cands.sort(reverse=True)
        best = cands[0] if cands and cands[0][0] > 0.5 else None
        st['i'] = best[2] if best else None
        if best and best[1] < 150:  # the stop's own position wins when the listing sits further off
            st['lat'], st['lon'] = round(lat[best[2]] / 1e6, 5), round(lon[best[2]] / 1e6, 5)
        print(f"{tour['id']:10} {st['name'][:40]:40} -> " + (f"{best[3]} ({best[1]:.0f} m, t{best[4]}, score {best[0]:.1f})" if best else 'NO MATCH'), file=sys.stderr)
        for c in cands[1:4]: print(f"{'':54}   alt: {c[3]} ({c[1]:.0f} m, score {c[0]:.1f})", file=sys.stderr)
        st.pop('match', None); st.pop('pick', None)
(ROOT / 'data/tours.json').write_text(json.dumps(src, ensure_ascii=False, separators=(',', ':')))
