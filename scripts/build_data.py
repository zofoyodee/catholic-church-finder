import sys, json, glob, re, unicodedata, math, struct, os, collections
src_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir+'/d', exist_ok=True)

def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]+',' ', s).strip()

STRONG = re.compile(r'\b(catholic|catolica|catolico|catholique|katholisch\w*|kath\.|cattolic\w*|katolick\w*|katolik\w*|katholiek\w*|catolica|rk kerk|r\.k\.|roman catholic|parroquia|paroquia|paroisse|parrocchia|parafia|pfarrei|plebania|basilica|basilique|basilika|bazylika|bazilika|cathedral|catedral|cathedrale|cattedrale|kathedrale|katedra|duomo|santuario|sanctuaire|sanktuarium|nuestra senora|nossa senhora|notre dame|nostra signora|our lady|madonna|virgen|santisimo|sagrado corazon|sacred heart|sacre coeur|sagrado coracao|sacro cuore|herz jesu|immaculate|inmaculada|imaculada|immacolata|guadalupe|diocese|diocesis|diocesi|archdiocese|arquidiocesis|eveche|capilla|capela|cappella|chapelle|kaplica|kapelle|oratorio|ermita|templo expiatorio|san |santa |santo |sao |saint |sainte |sankt |st\. |st |sv\. |sw\. |swietego|sw )')
CATH_WORD = re.compile(r'\b(catholic|catolica|catolico|catholique|katholisch\w*|cattolic\w*|katolick\w*|katholiek\w*|roman catholic|parroquia|paroquia|paroisse|parrocchia|parafia|basilica|basilique|basilika|bazylika|bazilika|santuario|sanctuaire|sanktuarium|nuestra senora|nossa senhora|notre dame|nostra signora|sagrado corazon|sacre coeur|sacro cuore|immacolata|inmaculada|imaculada|guadalupe|diocesis|diocesi|arquidiocesis|capilla|capela|cappella|chapelle|kaplica|oratorio|ermita|templo expiatorio|catedral|cathedrale|cattedrale|duomo)\b')
OTHER = re.compile(r'\b(orthodox|ortodox\w*|pravoslav\w*|anglican|episcopal|lutheran|luther\w*|evangel\w*|baptist\w*|bautista|batista|methodist\w*|metodista|presbyterian|presbiterian\w*|pentecost\w*|adventist\w*|adventista|assembl\w* of god|asamblea de dios|assembleia de deus|mormon|latter day|jehovah|testigos|kingdom hall|salon del reino|nazarene|nazareno|apostolic|apostolica|church of christ|iglesia de cristo|iglesia de dios|church of god|igreja universal|universal|reformed|reformiert|reformada|protestant\w*|cristiana|cristiano|christian center|christian centre|ministr\w*|ministerio\w*|worship center|vineyard|calvary chapel|bethel|maranatha|hillsong|coptic|copta|armenian|maronite\b(?!.*catholic)|unitarian|quaker|salvation army|ejercito de salvacion|seventh|full gospel|evangelho|evangelica|evangelico|iglesia ni cristo|templo|tabernacle|tabernaculo|gospel|mission church|ccc|methodiste|reformee|evangelique|church of england|church of scotland|united church|uniting church|kirk|mosque|mezquita|masjid|temple|synagogue)\b')
JUNK = re.compile(r'\b(monaguillos|acolitos|grupo|group|coro|choir|ministerio|ministry|youth|jovenes|juventud|pastoral|catequesis|catechesis|escuela|school|colegio|college|university|universidad|academy|academia|tienda|shop|store|libreria|bookstore|oficina|office|radio|tv|television|club|asociacion|association|fundacion|foundation|movimiento|movement|renovacion|encuentro|retiro|retreat|hermandad|cofradia|scouts|caritas|charity|charities|hospital|clinica|cemetery|cementerio|cemiterio|cimetiere|friedhof|cimitero|cmentarz|funeral|funeraria|seminar\w*|convento|convent|monastery|monasterio|mosteiro|abbey|abadia|kloster|nunnery|sisters of|hermanas|irmas|knights of|caballeros de colon|legion of mary|legion de maria|opus dei|ccr|food pantry|banco de alimentos|museum|museo|restaurant|cafe|hotel|hostel|guest house|apartment|parking|estacionamiento)\b')
# Some JUNK (convents, monasteries, abbeys) are churches too, but they are religious houses; we keep abbeys/monasteries if category is RC.
HOUSE = re.compile(r'\b(convento|convent|monastery|monasterio|mosteiro|abbey|abadia|abbaye|abtei|abbazia|kloster)\b')

def ctype(n):
    if re.search(r'\b(cathedral|catedral|cathedrale|cattedrale|kathedrale|katedra|katedrala|katedralis|duomo|co cathedral|concatedral|se catedral)\b', n): return 1
    if re.search(r'\b(basilica|basilique|basilika|bazylika|bazilika)\b', n): return 2
    if re.search(r'\b(santuario|sanctuaire|sanktuarium|shrine|wallfahrtskirche)\b', n): return 3
    if HOUSE.search(n): return 4
    if re.search(r'\b(capilla|capela|cappella|chapelle|chapel|kaplica|kapelle|ermita|oratorio|oratory)\b', n): return 5
    if re.search(r'\b(parroquia|paroquia|paroisse|parrocchia|parafia|pfarr\w*|parish)\b', n): return 6
    return 0

EXCL = re.compile(r'\b(old catholic|altkatholisch\w*|alt katholisch\w*|anglo ?catholic\w*|anglocatolic\w*|polish national catholic|national catholic|liberal catholic|independent catholic|ecumenical catholic|catolica apostolica brasileira|igreja catolica brasileira|icab|catolica nacional|evangelical catholic|orthodox catholic|catolica ortodoxa|agape|companerismo|crisitano|charismatic episcopal|mariavite|old roman catholic|catholic apostolic church|apostolic catholic|ortodox\w*|orthodox)\b')
NONLATIN = re.compile(r'(성당|천주교|天主堂|天主教|カトリック|католи|كاثوليك|καθολικ)', re.I)
VN = re.compile(r'\b(giao xu|giao ho|nha tho chinh toa|tieu vuong cung thanh duong)\b')
rows = []
stats = collections.Counter()
for fn in sorted(glob.glob(src_dir+'/part-*.jsonl')):
    for line in open(fn):
        r = json.loads(line)
        name = (r['names'] or {}).get('primary') or ''
        if not name.strip(): stats['noname']+=1; continue
        n = norm(name)
        if not n: n = name.strip().lower(); stats['nonlatin']+=1
        if r.get('operating_status') == 'permanently_closed': stats['closed']+=1; continue
        conf = r.get('confidence') or 0
        if EXCL.search(n): stats['excluded_noncatholic']+=1; continue
        if r['kind'] == 'rc':
            if conf < 0.35: stats['rc_lowconf']+=1; continue
            if JUNK.search(n) and not HOUSE.search(n) and not re.search(r'\b(parroquia|parish|church|iglesia|igreja|eglise|kirche|chiesa|kosciol|templo|capilla|basilica|catedral|cathedral|santuario)\b', n): stats['rc_junk']+=1; continue
            if OTHER.search(n) and not CATH_WORD.search(n): stats['rc_otherdenom']+=1; continue
            how = 'category'
        else:
            if conf < 0.5: continue
            if not (CATH_WORD.search(n) or NONLATIN.search(name) or VN.search(n)) or OTHER.search(n) or JUNK.search(n) or re.search(r'(정교회|東正|正教会|православ|개신교|基督教会)', name): continue
            how = 'name'
        rows.append((r, name, n, how))
        stats['keep_'+how]+=1
print(stats)

# dedupe: same normalized name within ~200m
seen = {}
keep = []
for r, name, n, how in sorted(rows, key=lambda x: (x[3]!='category', -(x[0].get('confidence') or 0))):
    key = (n, round(r['lat']*500), round(r['lon']*500))
    dup = False
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if (n, key[1]+dy, key[2]+dx) in seen: dup = True
    if dup: stats['dup']+=1; continue
    seen[key] = 1
    keep.append((r, name, n, how))
print('kept', len(keep), 'dups', stats['dup'])

# spatial sort (Hilbert-ish via Morton on 16-bit grid)
def morton(lon, lat):
    x = int((lon+180)/360*65535); y = int((lat+90)/180*65535)
    z = 0
    for b in range(16): z |= ((x>>b)&1)<<(2*b) | ((y>>b)&1)<<(2*b+1)
    return z
keep.sort(key=lambda k: morton(k[0]['lon'], k[0]['lat']))

N = len(keep); SH = 2000
lons = []; lats = []; types = bytearray(); search = []
country_counts = collections.Counter(); type_counts = collections.Counter()
shard = []
def flush(si):
    with open(f'{out_dir}/d/{si}.json','w') as f: json.dump(shard, f, ensure_ascii=False, separators=(',',':'))
for i,(r,name,n,how) in enumerate(keep):
    t = ctype(n)
    lons.append(round(r['lon']*1e6)); lats.append(round(r['lat']*1e6))
    types.append(t | (8 if how=='name' else 0))
    a = (r.get('addresses') or [{}])[0] or {}
    cc = (a.get('country') or '').upper()
    country_counts[cc]+=1; type_counts[t]+=1
    socials = [s for s in (r.get('socials') or []) if s][:2]
    rec = [name, a.get('freeform') or '', a.get('locality') or '', a.get('region') or '', a.get('postcode') or '', cc,
           (r.get('websites') or [''])[0] or '', (r.get('phones') or [''])[0] or '', socials,
           round(r.get('confidence') or 0, 2), sorted({s['dataset'] for s in r['sources'] if s.get('dataset')}),
           r['id'], how, max((s.get('update_time') or '')[:10] for s in r['sources']) if r['sources'] else '']
    shard.append(rec)
    search.append(f"{name}\t{a.get('locality') or ''}\t{cc}".replace('\n',' '))
    if len(shard) == SH: flush(i//SH); shard = []
if shard: flush((N-1)//SH)
with open(f'{out_dir}/points.bin','wb') as f:
    f.write(struct.pack(f'<{N}i', *lons)); f.write(struct.pack(f'<{N}i', *lats)); f.write(bytes(types))
# search chunks <= 4.5MB
chunks=[]; cur=[]; size=0
for s in search:
    b=len(s.encode())+1
    if size+b>4_500_000: chunks.append(cur); cur=[]; size=0
    cur.append(s); size+=b
chunks.append(cur)
for ci,c in enumerate(chunks):
    with open(f'{out_dir}/search-{ci}.txt','w') as f: f.write('\n'.join(c))
meta = {'count': N, 'shardSize': SH, 'shards': (N+SH-1)//SH, 'searchChunks': len(chunks), 'searchSizes':[len(c) for c in chunks],
        'countries': country_counts.most_common(), 'types': {str(k):v for k,v in type_counts.items()},
        'byMatch': collections.Counter(k[3] for k in keep), 'release': '2026-10-21.0'}
json.dump(meta, open(f'{out_dir}/meta.json','w'))
print(json.dumps({k:meta[k] for k in ('count','shards','searchChunks','types','byMatch')}), meta['countries'][:25])
