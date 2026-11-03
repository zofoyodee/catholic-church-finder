# Match the site's pins to OSM churches and write the Dev data set.
# usage: match.py OSMDIR REPO OUTDIR
import json, sys, base64, struct, math, re, unicodedata, collections, csv, os
D, R, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, R + '/scripts')
from regions import search_line, write_chunks
os.makedirs(OUT + '/d', exist_ok=True)

meta = json.load(open(R + '/data/meta.json')); n = meta['count']; SH = meta['shardSize']
raw = base64.b64decode(open(R + '/data/points.txt').read())
lon = list(struct.unpack_from(f'<{n}i', raw, 0)); lat = list(struct.unpack_from(f'<{n}i', raw, 4 * n)); typ = bytearray(raw[8 * n:9 * n])
rows = []
for k in range(meta['shards']): rows += json.load(open(R + f'/data/d/{k}.json'))
assert len(rows) == n
ov = json.load(open(os.environ.get('OVR', R + '/dev/data/overrides.json')))
hidden = {int(k) for k, v in ov.items() if k[0] != '_' and v and (v.get('hide') or 'dup' in v)}
osm = json.load(open(D + '/osm_churches.json'))
print('pins', n, 'hidden by overrides', len(hidden), 'osm objects', len(osm), collections.Counter(o['cls'] for o in osm))

def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]+', ' ', s).strip()
STOP = set('the of and de del la las los el da do das dos di della delle dei du des le les st saint sankt san santa santo sao sainte parish church iglesia igreja eglise kirche chiesa parroquia paroquia paroisse parrocchia parafia pfarrkirche catholic catolica catolico catholique katholische kosciol chapel capilla capela chapelle kapelle cappella rc r c'.split())
def toks(s): return {w for w in norm(s).split() if len(w) > 1 and w not in STOP}
def sim(a, b):
    A, B = toks(a), toks(b)
    if not A or not B: return 0.0
    return len(A & B) / min(len(A), len(B))
def onames(o):
    t = o['tags']; return [t[k] for k in ('name', 'name:en', 'official_name', 'alt_name', 'name:la') if t.get(k)]

# grid index of OSM objects (cell ~ 0.01 deg)
G = collections.defaultdict(list)
for j, o in enumerate(osm): G[(int(math.floor(o['lat'] * 100)), int(math.floor(o['lon'] * 100)))].append(j)
def near(la, lo, m):
    out = []; cl = math.cos(math.radians(la))
    ci, cj = int(math.floor(la * 100)), int(math.floor(lo * 100))
    r = 1 + int(m / 1100)
    for di in range(-r, r + 1):
        for dj in range(-r, r + 1):
            for j in G.get((ci + di, cj + dj), ()):
                o = osm[j]; d = math.hypot((o['lat'] - la) * 111320, (o['lon'] - lo) * 111320 * cl)
                if d <= m: out.append((d, j))
    return sorted(out)

# 1) collapse OSM duplicates: the same church mapped as a node and as its building (within 80 m, same name or one unnamed)
rep = list(range(len(osm)))
def find(j):
    while rep[j] != j: rep[j] = rep[rep[j]]; j = rep[j]
    return j
for j, o in enumerate(osm):
    if o['cls'] == 'other': continue
    for d, k in near(o['lat'], o['lon'], 80):
        if k <= j or osm[k]['cls'] == 'other': continue
        a, b = o['tags'].get('name', ''), osm[k]['tags'].get('name', '')
        if (not a or not b or sim(a, b) >= 0.6 or norm(a) == norm(b)) and (o['k'][0] != osm[k]['k'][0] or norm(a) == norm(b)):
            rep[find(k)] = find(j)
groups = collections.defaultdict(list)
for j in range(len(osm)): groups[find(j)].append(j)
def best_of(js):  # building outline wins for position; Catholic tag wins for class; merge tags
    js = sorted(js, key=lambda j: ({'w': 0, 'r': 1, 'n': 2}[osm[j]['k'][0]]))
    o = dict(osm[js[0]]); tags = {}
    for j in reversed(js): tags.update(osm[j]['tags'])
    o['tags'] = tags; o['keys'] = [osm[j]['k'] for j in js]
    cl = {osm[j]['cls'] for j in js}
    o['cls'] = 'cath' if 'cath' in cl else ('other' if 'other' in cl else 'unk')
    return o
osm2 = [best_of(js) for js in groups.values()]
print('osm after merging node+building copies', len(osm2), collections.Counter(o['cls'] for o in osm2))
osm = osm2
G.clear()
for j, o in enumerate(osm): G[(int(math.floor(o['lat'] * 100)), int(math.floor(o['lon'] * 100)))].append(j)

# 2) match each visible pin
M = 150
match = {}; why = collections.Counter(); left = []
taken = collections.defaultdict(list)
for i in range(n):
    if (typ[i] & 7) == 7 or i in hidden: why['already_hidden'] += 1; continue
    la, lo = lat[i] / 1e6, lon[i] / 1e6; name = rows[i][0]
    c = near(la, lo, M)
    best = None; bs = -1
    for d, j in c:
        o = osm[j]
        if o['cls'] == 'other':
            continue
        s = max([sim(name, x) for x in onames(o)] + [0])
        if not (s >= 0.5 or d <= 60 or (not onames(o) and d <= 100) or not toks(name)): continue  # a different church's name, too far to be the same building
        score = (2 if o['cls'] == 'cath' else 1) + s * 2 - d / M
        if score > bs: bs, best = score, (j, d, s)
    if best:
        match[i] = best; taken[best[0]].append(i); why['matched_' + osm[best[0]]['cls']] += 1
    else:
        oth = [osm[j] for d, j in c if osm[j]['cls'] == 'other' and d < 60]
        r = 'other_denomination_church_here' if oth else 'no_osm_church_within_150m'
        why[r] += 1; left.append((i, r, oth[0]['tags'].get('denomination', '') if oth else ''))
print(why)

# several pins on one OSM church: keep the best name match, the rest repeat it
dups = {}
for j, iz in taken.items():
    if len(iz) < 2: continue
    iz = sorted(iz, key=lambda i: (-match[i][2], match[i][1], -(rows[i][9] or 0)))
    for i in iz[1:]:
        if not toks(rows[i][0]) or sim(rows[i][0], rows[iz[0]][0]) >= 0.5 or match[i][2] >= 0.5: dups[i] = iz[0]
        else:  # another church's name on this building: not confirmed
            del match[i]; left.append((i, 'osm_building_has_another_name', '')); why['matched_' + osm[j]['cls']] -= 1; why['another_name_same_building'] += 1
print(why)
print('extra pins on the same OSM church (marked as duplicates)', len(dups))

# 3) new OSM-only Catholic churches
used = set(taken)
new = [o for j, o in enumerate(osm) if j not in used and o['cls'] == 'cath']
noname = [o for o in new if not (o['tags'].get('name') or o['tags'].get('official_name'))]
new = [o for o in new if o['tags'].get('name') or o['tags'].get('official_name')]
print('OSM-only Catholic churches with a name', len(new), 'without a name (skipped)', len(noname))

if os.environ.get('STATS'):
    cc = lambda i: rows[i][5]
    vis = [i for i in range(n) if not ((typ[i] & 7) == 7 or i in hidden)]
    byc = collections.Counter(cc(i) for i in vis); um = collections.Counter(cc(i) for i, r, _ in left)
    print('unmatched by country (share of visible):')
    print([(c, um[c], round(um[c] / byc[c] * 100)) for c, _ in byc.most_common(30)])
    print('unmatched with website or phone', sum(1 for i, r, _ in left if rows[i][6] or rows[i][7]), 'facebook only/none', sum(1 for i, r, _ in left if not (rows[i][6] or rows[i][7])))
    print('unmatched how=name', sum(1 for i, r, _ in left if rows[i][12] == 'name'))
    mu = [i for i in match if osm[match[i][0]]['cls'] == 'unk']
    print('matched to unk: name sim>=0.5', sum(1 for i in mu if match[i][2] >= 0.5), 'd<50', sum(1 for i in mu if match[i][1] < 50))
    pw = collections.Counter((o['tags'].get('building') or '-') + '/' + (o['tags'].get('place_of_worship') or '-') for o in new)
    print('new by building/pow', pw.most_common(15))
    # rough country of new: nearest-pin grid
    PG = {}
    for i in range(n): PG.setdefault((lat[i] // 200000, lon[i] // 200000), cc(i))
    nc = collections.Counter(PG.get((int(o['lat'] * 1e6) // 200000, int(o['lon'] * 1e6) // 200000), '?') for o in new)
    print('new by rough country', nc.most_common(30))

# ---------- 4) write the Dev data set ----------
import numpy as np
from scipy.spatial import cKDTree
DROP_B = {'civic', 'house', 'ruins', 'shrine', 'wayside_shrine', 'residential', 'school', 'hospital', 'garage', 'shed', 'roof', 'construction', 'apartments', 'commercial', 'office', 'yes;ruins'}
DROP_P = {'holy_well', 'wayside_chapel', 'shrine'}
new = [o for o in new if (o['tags'].get('building') or '') not in DROP_B and (o['tags'].get('place_of_worship') or '') not in DROP_P]
print('new after dropping shrines, ruins, houses', len(new))
C = [l.rstrip('\n').split(',') for l in open('/tmp/claude-0/rg/reverse_geocoder-1.5.1/reverse_geocoder/rg_cities1000.csv', encoding='utf-8')][1:]
def xyz(la, lo):
    la, lo = np.radians(la), np.radians(lo); return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]
cla = np.array([float(c[0]) for c in C]); clo = np.array([float(c[1]) for c in C])
T = cKDTree(xyz(cla, clo))
# nearest confirmed site pin gives the country more reliably near borders
vis_m = sorted(match); PT = cKDTree(xyz(np.array([lat[i] / 1e6 for i in vis_m]), np.array([lon[i] / 1e6 for i in vis_m])))
nla = np.array([o['lat'] for o in new]); nlo = np.array([o['lon'] for o in new])
dc, jc = T.query(xyz(nla, nlo)); dp, jp = PT.query(xyz(nla, nlo))
NUMFIRST = {'US', 'CA', 'AU', 'GB', 'IE', 'NZ', 'FR', 'PH', 'IN', 'ZA', 'MY', 'SG', 'NG', 'KE', 'LU', 'BE_fr'}
CT = re.compile(r'\b(cathedral|catedral|cathedrale|cattedrale|kathedrale|katedra|katedrala|katedralis|duomo|co cathedral|concatedral|se catedral|dom)\b')
def ctype(nm, tags):
    if CT.search(nm) or tags.get('building') == 'cathedral' or tags.get('church:type') == 'cathedral': return 1
    if re.search(r'\b(basilica|basilique|basilika|bazylika|bazilika|bazilica)\b', nm): return 2
    if re.search(r'\b(santuario|sanctuaire|sanktuarium|shrine|wallfahrtskirche)\b', nm): return 3
    if re.search(r'\b(convento|convent|monastery|monasterio|mosteiro|abbey|abadia|abbaye|abtei|abbazia|kloster|klasztor)\b', nm) or tags.get('building') == 'monastery': return 4
    if re.search(r'\b(capilla|capela|cappella|chapelle|chapel|kaplica|kapelle|ermita|oratorio|oratory|kapel|kaple)\b', nm) or tags.get('building') == 'chapel' or tags.get('place_of_worship') == 'chapel': return 5
    if re.search(r'\b(parroquia|paroquia|paroisse|parrocchia|parafia|pfarr\w*|parish|parochie|farnost|plebania)\b', nm): return 6
    return 0
def web(t):
    w = t.get('website') or t.get('contact:website') or t.get('url') or ''
    return w if re.match(r'^https?://', w) else ('https://' + w if w and '.' in w and ' ' not in w else '')
def qid(t):
    q = t.get('wikidata') or ''; return q if re.fullmatch(r'Q\d+', q) else ''
newrows = []; newpts = []
for k, o in enumerate(new):
    t = o['tags']; c = C[jc[k]]
    cc = (t.get('addr:country') or '').upper()
    if not re.fullmatch(r'[A-Z]{2}', cc):
        cc = rows[vis_m[jp[k]]][5] if dp[k] * 6371 < 3 and rows[vis_m[jp[k]]][5] else c[5]
    town = t.get('addr:city') or t.get('addr:place') or (c[2] if dc[k] * 6371 < 15 else '')
    region = t.get('addr:state') or t.get('addr:province') or (c[3] if c[5] == cc else '')
    st, hn = t.get('addr:street', ''), t.get('addr:housenumber', '')
    addr = ((hn + ' ' + st) if cc in NUMFIRST else (st + ' ' + hn)).strip() if st else ''
    soc = [s for s in [t.get('facebook') or t.get('contact:facebook')] if s and s.startswith('http')]
    name = t.get('name') or t.get('official_name')
    newrows.append([name, addr, town, region, t.get('addr:postcode', ''), cc, web(t), t.get('phone') or t.get('contact:phone') or '', soc, 1.0, ['OpenStreetMap'], 'osm:' + o['k'], 'osm', (t.get('check_date') or '')[:10], qid(t)])
    newpts.append((o['lon'], o['lat'], ctype(norm(name), t)))

def morton(lo, la):
    x = int((lo + 180) / 360 * 65535); y = int((la + 90) / 180 * 65535); z = 0
    for b in range(16): z |= ((x >> b) & 1) << (2 * b) | ((y >> b) & 1) << (2 * b + 1)
    return z
order = sorted(range(len(new)), key=lambda k: morton(newpts[k][0], newpts[k][1]))

hide_left = os.environ.get('HIDE_LEFT', '1') == '1'
for i, (j, d, s) in match.items():
    o = osm[j]; t = o['tags']; r = rows[i]
    lat[i] = round(o['lat'] * 1e6); lon[i] = round(o['lon'] * 1e6)
    if not r[6]: r[6] = web(t)
    if not r[7]: r[7] = t.get('phone') or t.get('contact:phone') or ''
    r[9] = max(r[9] or 0, 0.9)
    if 'OpenStreetMap' not in r[10]: r[10] = r[10] + ['OpenStreetMap']
    if o['cls'] == 'cath' and r[12] == 'name': r[12] = 'category'; typ[i] &= ~8
    while len(r) < 14: r.append('')
    r.append(qid(t))
for i, rsn, _ in left:
    if hide_left: typ[i] = (typ[i] & ~7) | 7
rows_all = rows + [newrows[k] for k in order]
lon_all = lon + [round(newpts[k][0] * 1e6) for k in order]; lat_all = lat + [round(newpts[k][1] * 1e6) for k in order]
typ_all = bytes(typ) + bytes(newpts[k][2] for k in order)
N = len(rows_all)
with open(OUT + '/points.txt', 'w') as f:
    f.write(base64.b64encode(struct.pack(f'<{N}i', *lon_all) + struct.pack(f'<{N}i', *lat_all) + typ_all).decode())
for old in __import__('glob').glob(OUT + '/d/*.json'): os.remove(old)
for s0 in range(0, N, SH):
    with open(f'{OUT}/d/{s0 // SH}.json', 'w') as f: json.dump(rows_all[s0:s0 + SH], f, ensure_ascii=False, separators=(',', ':'))
lines = []
for c0 in range(meta['searchChunks']): lines += open(R + f'/data/search-{c0}.txt', encoding='utf-8').read().split('\n')
assert len(lines) == n, (len(lines), n)
lines += [search_line(r[0], r[2], r[5], r[3]) for r in rows_all[n:]]
chunks = write_chunks(OUT, lines)
vis = [i for i in range(N) if (typ_all[i] & 7) != 7]
m2 = dict(meta)
m2.update({'count': len(vis), 'shards': (N + SH - 1) // SH, 'searchChunks': len(chunks), 'searchSizes': [len(c) for c in chunks],
           'countries': collections.Counter(rows_all[i][5] for i in vis).most_common(),
           'types': {str(k): v for k, v in collections.Counter(typ_all[i] & 7 for i in vis).items()},
           'byMatch': dict(collections.Counter(rows_all[i][12] for i in vis)), 'osm': '2026-10-26', 'osmConfirmed': len(match), 'osmAdded': len(new)})
json.dump(m2, open(OUT + '/meta.json', 'w'))
ov2 = dict(ov)
for i, keep in dups.items():
    if str(i) not in ov2: ov2[str(i)] = {'dup': keep}
json.dump(ov2, open(OUT + '/overrides.json', 'w'), ensure_ascii=False, indent=0)
# review lists
with open(OUT + '/hidden-no-osm-church.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['index', 'name', 'town', 'region', 'country', 'website', 'phone', 'lat', 'lon', 'reason', 'other_denomination'])
    for i, rsn, od in left: r = rows[i]; w.writerow([i, r[0], r[2], r[3], r[5], r[6], r[7], lat[i] / 1e6, lon[i] / 1e6, rsn, od])
with open(OUT + '/added-from-osm-by-country.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['country', 'added'])
    for c0, v in collections.Counter(r[5] for r in rows_all[n:]).most_common(): w.writerow([c0, v])
print('WROTE', N, 'records;', len(vis), 'visible before overrides;', json.dumps({k: m2[k] for k in ('types', 'byMatch', 'osmConfirmed', 'osmAdded')}))
print('top countries', m2['countries'][:20])
