# Turn pass-A objects + pass-B/C node coordinates into one record per OSM church-like object.
# usage: locate.py DIR  -> DIR/osm_churches.json  [ {k:'w123', lat, lon, tags, cls:'cath'|'unk'|'other'} ]
import osmium, json, sys, glob, re
D = sys.argv[1]
A = json.load(open(D + '/A.json'))
coords = {}; wayn = {}
class H(osmium.SimpleHandler):
    def node(self, n): coords[n.id] = (n.location.lat, n.location.lon)
    def way(self, w): wayn[w.id] = [r.ref for r in w.nodes]
for f in sorted(glob.glob(D + '/[BC][0-9].osm.pbf')): H().apply_file(f)
print('coords', len(coords), 'member ways', len(wayn))

CATH = {'roman_catholic','catholic','greek_catholic','ukrainian_greek_catholic','maronite','melkite','syro-malabar','syro_malabar','syro-malankara','syro_malankara','chaldean_catholic','chaldean','armenian_catholic','coptic_catholic','syriac_catholic','ruthenian_catholic','byzantine_catholic','romanian_greek_catholic','slovak_greek_catholic','eastern_catholic','latin_catholic','ethiopian_catholic','eritrean_catholic','hungarian_greek_catholic','ruthenian','italo-albanian','roman catholic'}
NOTCHURCH_POW = {'wayside_shrine','wayside_cross','cross','lourdes_grotto','grotto','shrine_small','statue','calvary','mass_rock','cemetery','columbarium'}

def center(refs):
    pts = [coords[r] for r in refs if r in coords]
    if not pts: return None
    la = [p[0] for p in pts]; lo = [p[1] for p in pts]
    if max(lo) - min(lo) > 180: return None
    return ((min(la) + max(la)) / 2, (min(lo) + max(lo)) / 2, len(pts))

out = []; stats = {}
def bump(k): stats[k] = stats.get(k, 0) + 1
for o in A:
    t = o['tags']
    am = t.get('amenity'); b = t.get('building'); rel = (t.get('religion') or '').lower()
    den = (t.get('denomination') or '').lower().strip()
    church_like = am == 'place_of_worship' or (b in ('church', 'chapel', 'cathedral') and (am is None))
    if not church_like: bump('not_church_like'); continue
    if (t.get('place_of_worship') or '').lower() in NOTCHURCH_POW or t.get('historic') in ('wayside_shrine', 'wayside_cross', 'ruins') or t.get('ruins') == 'yes' or t.get('abandoned') == 'yes' or t.get('disused') == 'yes':
        bump('shrine_or_ruin'); continue
    if rel and rel != 'christian': bump('other_religion'); continue
    if den in CATH: cls = 'cath'
    elif den and den not in ('christian', 'unknown', 'yes'): cls = 'other'
    else: cls = 'unk'
    if o['t'] == 'n': loc = (o['lat'], o['lon'], 1)
    elif o['t'] == 'w': loc = center(o['nds'])
    else:
        if t.get('type') not in ('multipolygon', 'building'): bump('rel_other_type'); continue
        refs = []
        for mt, ref, role in o['mem']:
            if mt == 'w' and role in ('outer', '') and ref in wayn: refs += wayn[ref]
            if mt == 'n': refs.append(ref)
        loc = center(refs)
    if not loc: bump('no_location_' + o['t']); continue
    keep = {k: v for k, v in t.items() if k in ('name', 'name:en', 'name:la', 'official_name', 'alt_name', 'denomination', 'religion', 'amenity', 'building', 'place_of_worship', 'website', 'contact:website', 'url', 'phone', 'contact:phone', 'facebook', 'contact:facebook', 'addr:street', 'addr:housenumber', 'addr:city', 'addr:place', 'addr:postcode', 'addr:state', 'addr:province', 'addr:country', 'wikidata', 'wikipedia', 'diocese', 'parish', 'church', 'church:type', 'historic', 'check_date', 'operator')}
    out.append({'k': o['t'] + str(o['id']), 'lat': round(loc[0], 6), 'lon': round(loc[1], 6), 'tags': keep, 'cls': cls})
    bump('kept_' + cls)
print(stats)
json.dump(out, open(D + '/osm_churches.json', 'w'), ensure_ascii=False)
# ids for pass C: nodes of relation member ways not yet located
need = set()
for o in A:
    if o['t'] == 'r':
        for mt, ref, role in o['mem']:
            if mt == 'w' and ref in wayn: need.update(r for r in wayn[ref] if r not in coords)
print('pass C nodes needed', len(need))
with open(D + '/idsC.txt', 'w') as f:
    for n in sorted(need): f.write(f'n{n}\n')
