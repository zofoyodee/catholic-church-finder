# Stream page_props dump; for candidate page ids keep wikibase_item and page_image(_free).
import sys, gzip, re, json
dump, cand, out = sys.argv[1:4]
ids = {int(l.split('\t',1)[0]) for l in open(cand)}
rx = re.compile(rb"\((\d+),'(wikibase_item|page_image_free|page_image)','((?:[^'\\]|\\.)*)',")
res = {}
with gzip.open(dump, 'rb') as f:
    for line in f:
        for m in rx.finditer(line):
            p = int(m.group(1))
            if p in ids:
                res.setdefault(p, {})[m.group(2).decode()] = m.group(3).decode('utf-8', 'replace').replace("\\'", "'")
json.dump(res, open(out, 'w'), ensure_ascii=False)
print(len(ids), len(res), sum('wikibase_item' in v for v in res.values()), sum(('page_image_free' in v or 'page_image' in v) for v in res.values()))
