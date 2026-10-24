import sys, json, pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
src, out = sys.argv[1], sys.argv[2]
f = pq.ParquetFile(src)
cols = ['id','geometry','confidence','websites','phones','socials','addresses','names','sources','operating_status','basic_category','taxonomy','bbox']
KEEP = {'roman_catholic_place_of_worship'}
CAND = {'christian_place_of_worship','place_of_worship','church_cathedral','religious_organization','religious_landmark','christian_church'}
n=0
with open(out,'w') as fo:
    for rg in range(f.num_row_groups):
        t = f.read_row_group(rg, columns=cols)
        prim = pc.struct_field(t.column('taxonomy'), 'primary')
        alts = pc.struct_field(t.column('taxonomy'), 'alternates')
        m = pc.or_(pc.is_in(prim, pa.array(list(KEEP|CAND))), pc.is_in(t.column('basic_category'), pa.array(list(CAND))))
        m = pc.fill_null(m, False)
        s = t.filter(m)
        for r in s.select([c for c in cols if c!='geometry']).to_pylist():
            tx = r['taxonomy'] or {}
            r['kind'] = 'rc' if tx.get('primary') in KEEP or 'roman_catholic_place_of_worship' in (tx.get('alternates') or []) else 'cand'
            b = r.pop('bbox'); r['lon']=(b['xmin']+b['xmax'])/2; r['lat']=(b['ymin']+b['ymax'])/2
            nm = r['names'] or {}; r['names'] = {'primary': nm.get('primary'), 'common': dict(nm.get('common') or [])}
            r['sources'] = [{k:x.get(k) for k in ('dataset','record_id','update_time')} for x in (r['sources'] or [])]
            fo.write(json.dumps(r, ensure_ascii=False)+'\n'); n+=1
print(src, n)
