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

shards = collections.defaultdict(dict)
for k, j, r, added in records():
    out = shards[k]
    u = r[6]
    if not u:
        continue
    u = u if re.match(r'^https?://', u) else 'https://' + u
    x = res.get(u)
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
    if code == 3 or new or staff or mass or conf:
        e = [code, new, staff, x.get('src', ''), mass, conf, x.get('msrc', '')]
        while e and not e[-1] and len(e) > 2:
            e.pop()
        out[j] = e
for k, out in shards.items():
    with open(f'data/web/{k}.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

meta = {'checked': datetime.date.today().isoformat(), 'stats': dict(stats)}
json.dump(meta, open('data/web/meta.json', 'w'), indent=1)
print(meta)
