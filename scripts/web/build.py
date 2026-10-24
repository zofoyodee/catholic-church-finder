"""Merge crawl parts into data/web/N.json, one file per detail shard.

Each file maps a record's index within its shard to
  [status, url, staff, staffSource]
status: 2 = moved (url is the new address), 3 = dead, 1 = ok but at a new path (url).
staff:  [[kind "p"|"d", title, name, role, photoUrl], ...]
Records whose link works unchanged and have no staff are left out.

Usage: python build.py parts/*.json
"""
import json, re, sys, os, glob, collections, datetime

res = {}
for fn in sys.argv[1:]:
    res.update(json.load(open(fn)))

os.makedirs('data/web', exist_ok=True)
for old in glob.glob('data/web/[0-9]*.json'):
    os.remove(old)
CODE = {'ok': 1, 'moved': 2, 'dead': 3}
stats = collections.Counter()
sys.path.insert(0, os.path.dirname(__file__))
from crawl import records
from times import slots, LANGS
from tz import tz_of
import base64, struct

shards = collections.defaultdict(dict)
sched = {}
TZ = {}
_raw = base64.b64decode(open('data/points.txt').read())
_n = json.load(open('data/meta.json'))['count']
LON, LAT = struct.unpack_from(f'<{_n}i', _raw, 0), struct.unpack_from(f'<{_n}i', _raw, 4 * _n)
LANG_IDX = {c: i + 1 for i, (c, _) in enumerate(LANGS)}
OV = json.load(open('data/overrides.json'))
for k, j, r, added in records():
    out = shards[k]
    u = r[6]
    if not u:
        continue
    u = u if re.match(r'^https?://', u) else 'https://' + u
    x = res.get(u)
    o = OV.get(str(k * 2000 + j), {})
    if o.get('mass') or o.get('confession'):
        # hand-entered times for parishes whose sites turn crawlers away
        x = dict(x or {'s': 'unknown'}, mt=o.get('mass', []), ct=o.get('confession', []), msrc=o.get('times_source', u))
    if not x:
        stats['not_checked'] += 1
        if added:
            out[j] = [0, u]
        continue
    stats[x['s']] += 1
    code = CODE.get(x['s'], 0)
    new = x.get('u', '') or (u if added else '')
    staff = x.get('p') or []
    if staff:
        stats['with_staff'] += 1
        stats['people'] += len(staff)
        stats['with_photo'] += sum(1 for p in staff if p[4])
    mass, conf = x.get('mt') or [], x.get('ct') or []
    if mass or conf:
        stats['with_mass' if mass else 'with_confession_only'] += 1
        stats['with_confession'] += bool(conf)
    if any(p[3] in ('Pastor', 'Administrator', 'Rector') for p in staff):
        stats['with_pastor'] += 1
    sl = slots(mass, 0) + slots(conf, 1)
    if sl:
        # one int per slot: kind | day mask << 1 | minutes << 8 | language << 19 | week of month << 24
        i = k * 2000 + j
        tz = tz_of(r[5], LON[i] / 1e6, LAT[i] / 1e6)
        tzi = TZ.setdefault(tz, len(TZ))
        sched[i] = [tzi] + sorted({kd | m << 1 | t << 8 | (LANG_IDX[lg] if lg else 0) << 19 | wk << 24 for kd, m, t, lg, wk in sl})
        stats['with_times'] += 1
        stats['with_language'] += any(x[3] for x in sl)
    if code == 3 or new or staff or mass or conf:
        e = [code, new, staff, x.get('src', ''), mass, conf, x.get('msrc', '')]
        while e and not e[-1] and len(e) > 2:
            e.pop()
        out[j] = e
for k, out in shards.items():
    with open(f'data/web/{k}.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

json.dump({'langs': [''] + [c for c, _ in LANGS], 'tz': list(TZ), 'c': sched}, open('data/web/sched.json', 'w'), separators=(',', ':'))
meta = {'checked': datetime.date.today().isoformat(), 'stats': dict(stats)}
json.dump(meta, open('data/web/meta.json', 'w'), indent=1)
print(meta)
