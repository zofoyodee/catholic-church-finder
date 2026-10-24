"""Print a review sample of the crawl: status counts, errors, and some staff finds."""
import json, sys, collections, random
res = {}
for fn in sys.argv[1:]:
    res.update(json.load(open(fn)))
random.seed(1)
staff = [(u, r) for u, r in res.items() if r.get('p')]
dead = [(u, r.get('e')) for u, r in res.items() if r['s'] == 'dead']
moved = [(u, r.get('u')) for u, r in res.items() if r['s'] == 'moved']
print(json.dumps({
    'status': collections.Counter(r['s'] for r in res.values()),
    'errors': collections.Counter(r.get('e') for r in res.values() if r.get('e')),
    'staff_sites': len(staff),
    'people': collections.Counter(p[0] for _, r in staff for p in r['p']),
    'with_photo': sum(1 for _, r in staff for p in r['p'] if p[4]),
    'schedule_sites': sum(1 for r in res.values() if r.get('mt') or r.get('ct')),
    'schedule_sample': random.sample([(u, r.get('mt'), r.get('ct'), r.get('msrc')) for u, r in res.items() if r.get('mt') or r.get('ct')], min(150, sum(1 for r in res.values() if r.get('mt') or r.get('ct')))),
    'staff_sample': random.sample(staff, min(200, len(staff))),
    'dead_sample': random.sample(dead, min(60, len(dead))),
    'moved_sample': random.sample(moved, min(60, len(moved))),
}, ensure_ascii=False, indent=0))
