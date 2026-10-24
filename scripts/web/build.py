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
k = 0
while os.path.exists(f'data/d/{k}.json'):
    out = {}
    for j, r in enumerate(json.load(open(f'data/d/{k}.json'))):
        u = r[6]
        if not u:
            continue
        u = u if re.match(r'^https?://', u) else 'https://' + u
        x = res.get(u)
        if not x:
            stats['not_checked'] += 1
            continue
        stats[x['s']] += 1
        code = CODE.get(x['s'], 0)
        new = x.get('u', '')
        staff = x.get('p') or []
        if staff:
            stats['with_staff'] += 1
            stats['people'] += len(staff)
            stats['with_photo'] += sum(1 for p in staff if p[4])
        if code == 3 or new or staff:
            out[j] = [code, new, staff, x.get('src', '')] if staff else [code, new]
    with open(f'data/web/{k}.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    k += 1

meta = {'checked': datetime.date.today().isoformat(), 'stats': dict(stats)}
json.dump(meta, open('data/web/meta.json', 'w'), indent=1)
print(meta)
