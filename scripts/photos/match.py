# Match each church to a nearby Commons category (or gallery) whose title names it and that has a lead image.
import json, re, unicodedata, collections, numpy as np
W = '/tmp/claude-0/work/'
names = json.load(open(W+'names.json')); c = np.load(W+'churches.npz'); typ = c['typ']
props = {int(k): v for k, v in json.load(open(W+'props.json')).items()}
titles = {}
for l in open(W+'titles.tsv'):
    pid, ns, t = l.rstrip('\n').split('\t'); 
    if ns in ('14', '0'): titles[int(pid)] = (int(ns), t.replace('_', ' ').replace("\\'", "'"))
def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
CHURCHY = re.compile(r'\b(church|churches|iglesia|igreja|chiesa|eglise|kirche|kerk|kosciol|kostel|kostol|templom|crkva|cerkiew|biserica|basilica|basilique|basilika|bazylika|bazilika|cathedral|catedral|cathedrale|cattedrale|kathedrale|katedra|katedrala|duomo|dom|munster|chapel|chapelle|capilla|capela|cappella|kapelle|kaplica|kaple|parroquia|paroquia|parrocchia|parafia|pfarrkirche|parish|santuario|sanctuaire|sanktuarium|shrine|oratory|oratorio|ermita|pieve|collegiata|collegiale|abbey|abbaye|abtei|abbazia|monastery|convent|convento|kloster|klasztor|mission|misiones|wallfahrtskirche|stiftskirche|sanctuary|tempio|templo|nha tho|seongdang|kyokai)\b')
STOP = set('church iglesia igreja chiesa eglise kirche kerk kosciol kostel parroquia paroquia parrocchia parafia parish catholic catolica catolico cattolica roman of the de del la las los di da do dos das du des der die das st saint sainte san santa santo sao sankt sv sw and y e et und in en a al au le church chapel capilla capela cappella chapelle basilica cathedral catedral santuario shrine nuestra senora nossa senhora notre dame our lady parish rc r c rk pfarrkirche kath katholische filialkirche pfarrei mission misión mision templo cathedrale cattedrale duomo maria mary virgen virgin madonna'.split())
def toks(s): return [t for t in norm(s).split() if t not in STOP and len(t) > 1]
BADIMG = re.compile(r'\.(svg|gif)$|coat_of_arms|wappen|escudo|stemma|herb_|blason|logo|map|karte|mapa|locator|flag|signature|plan|grundriss|interior_plan', re.I)
near = collections.defaultdict(list)
for l in open(W+'near.tsv'):
    pid, la, lo, ci, d = l.split('\t'); pid = int(pid)
    if pid in titles and pid in props: near[int(ci)].append((pid, int(d)))
out = {}; stat = collections.Counter()
for ci, cands in near.items():
    nm = names[ci]; ct = set(toks(nm)); best = None
    for pid, d in cands:
        ns, t = titles[pid]; pr = props[pid]
        img = pr.get('page_image_free') or pr.get('page_image')
        if not img or BADIMG.search(img): continue
        tn = norm(t); tt = set(toks(t))
        churchy = bool(CHURCHY.search(tn))
        ov = len(ct & tt); jacc = ov / max(1, len(ct | tt))
        if not churchy: continue
        if ov == 0 and d > 30: continue
        if re.search(r'marker|plaque|sign|schild|tafel|placa|lapide', img, re.I): continue
        if re.search(r'\b(interior|organ|organs|altar|window|windows|bells?|graves?|cemetery|cemeteries|people|events|paintings|sculptures|details|tombs?|views? from|in art|photographs|maps|plans|by year|history of|clergy|priests|bishops)\b', tn): continue
        score = (2.0 if churchy else 0) + 3.0 * jacc + (1.0 if ov >= 1 else 0) - d / 150.0 + (0.3 if ns == 14 else 0)
        if not ct: score += 0.5 if churchy else 0
        if score < 2.2: continue
        if best is None or score > best[0]: best = (score, pid, t, img, d, pr.get('wikibase_item'))
    if best: out[ci] = best; stat[typ[ci] & 7] += 1
print(len(out), dict(stat))
json.dump({str(k): v for k, v in out.items()}, open(W+'matches.json', 'w'), ensure_ascii=False)
imgs = collections.Counter(v[3] for v in out.values()); print('distinct images', len(imgs), imgs.most_common(5))
import random; random.seed(1)
for k in random.sample(list(out), 40): v = out[k]; print(f"{v[0]:.2f} {v[4]:>4}m | {names[k][:45]:45} | {v[2][:60]:60} | {v[3][:50]}")
