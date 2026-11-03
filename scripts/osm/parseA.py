import osmium, json, sys, glob
S=sys.argv[1]
KEEP=None
out=[]
class H(osmium.SimpleHandler):
    def node(self,n):
        out.append({'t':'n','id':n.id,'tags':dict(n.tags),'lat':n.location.lat,'lon':n.location.lon})
    def way(self,w):
        out.append({'t':'w','id':w.id,'tags':dict(w.tags),'nds':[r.ref for r in w.nodes]})
    def relation(self,r):
        out.append({'t':'r','id':r.id,'tags':dict(r.tags),'mem':[[m.type,m.ref,m.role] for m in r.members]})
for f in sorted(glob.glob(S+'/A[0-9].osm.pbf')):
    H().apply_file(f)
seen=set(); res=[]
for o in out:
    k=(o['t'],o['id'])
    if k in seen: continue
    seen.add(k); res.append(o)
json.dump(res, open(S+'/A.json','w'))
from collections import Counter
print(len(res), Counter(o['t'] for o in res))
# ids for pass B: all way node refs; member ways of relations
nodes=set(); ways=set()
for o in res:
    if o['t']=='w': nodes.update(o['nds'])
    elif o['t']=='r':
        for t,ref,role in o['mem']:
            if t=='w': ways.add(ref)
            elif t=='n': nodes.add(ref)
with open(S+'/idsB.txt','w') as f:
    for n in sorted(nodes): f.write(f'n{n}\n')
    for w in sorted(ways): f.write(f'w{w}\n')
print('nodes',len(nodes),'ways',len(ways))
