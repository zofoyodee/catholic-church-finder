"""City labels for page languages that Natural Earth has no column for, from Wikipedia article titles.

Each Natural Earth place carries its Wikidata id; the Wikidata sitelinks dump says what that place's
article is called on each language's Wikipedia (Vienna is "Vídeň" on cs.wikipedia, "Vindobona" on
la.wikipedia). Titles lose any "(disambiguation)" or ", Region" tail. Places without an article in a
language keep the default label, as in city_names.py.

usage:
  curl -s https://dumps.wikimedia.org/wikidatawiki/latest/wikidatawiki-latest-wb_items_per_site.sql.gz | gunzip \
    | grep -aE "'(cswiki|lawiki|...)'" | (keep rows whose item is a Natural Earth place)   # collect {Q-id: {site: title}} into sitelinks.json
  python3 scripts/i18n/city_names_wiki.py ne_10m_populated_places.geojson sitelinks.json
"""
import json, sys, os, re, unicodedata

# page language -> its Wikipedia. Tamil, Malayalam, Telugu and Konkani names are laid over the globe by the page (MapLibre cannot shape them).
WIKI = {'bcl': 'bclwiki', 'ceb': 'cebwiki', 'cs': 'cswiki', 'fil': 'tlwiki', 'gn': 'gnwiki', 'hr': 'hrwiki', 'ht': 'htwiki',
        'ig': 'igwiki', 'ilo': 'ilowiki', 'la': 'lawiki', 'lg': 'lgwiki', 'ln': 'lnwiki', 'lt': 'ltwiki', 'mg': 'mgwiki',
        'ny': 'nywiki', 'qu': 'quwiki', 'rn': 'rnwiki', 'rw': 'rwwiki', 'sk': 'skwiki', 'sl': 'slwiki', 'sn': 'snwiki',
        'sq': 'sqwiki', 'sw': 'swwiki', 'tet': 'tetwiki', 'war': 'warwiki', 'yo': 'yowiki', 'ki': 'kiwiki',
        'ca': 'cawiki', 'ro': 'rowiki', 'mt': 'mtwiki', 'zu': 'zuwiki', 'ak': 'twwiki',
        'ta': 'tawiki', 'ml': 'mlwiki', 'te': 'tewiki', 'gom': 'gomwiki'}
# where a language's Wikipedia has no article, a Natural Earth column in the same script comes next
FALLBACK = {'gom': 'NAME_HI'}
# Telugu, Malayalam and Tamil follow the Devanagari layout letter for letter, so the Hindi name carries over into
# their script. Tamil has no aspirated or voiced stops of its own: those fold into the plain letter.
BRAHMI = {'te': 0x0C00, 'ml': 0x0D00, 'ta': 0x0B80}
TA_FOLD = {0x16: 0x15, 0x17: 0x15, 0x18: 0x15, 0x1B: 0x1A, 0x1D: 0x1C, 0x20: 0x1F, 0x21: 0x1F, 0x22: 0x1F, 0x25: 0x24, 0x26: 0x24,
           0x27: 0x24, 0x2B: 0x2A, 0x2C: 0x2A, 0x2D: 0x2A, 0x5B: 0x1C, 0x5C: 0x1F, 0x5D: 0x1F, 0x5E: 0x2A, 0x58: 0x15, 0x59: 0x15, 0x5A: 0x15}
def from_hindi(s, lang):
    base, out = BRAHMI[lang], []
    for ch in s:
        c = ord(ch)
        if 0x0900 <= c < 0x0980:
            o = c - 0x0900
            if lang == 'ta': o = TA_FOLD.get(o, o)
            if o == 0x3C: continue  # the nukta dot
            n = base + o
            if not unicodedata.name(chr(n), ''): return ''  # a letter this script lacks
            out.append(chr(n))
        else: out.append(ch)
    s = ''.join(out)
    if lang == 'ta': s = s.replace(chr(base + 0x02), 'ம்')  # Tamil writes the nasal out in full
    # Hindi drops the vowel after a word's last consonant; these scripts would sound it, so it gets a virama
    cons = lambda c: base + 0x15 <= ord(c) <= base + 0x39
    return re.sub(r'(.)(?=$|[\s\-])', lambda m: m.group(1) + chr(base + 0x4D) if cons(m.group(1)) else m.group(1), s)

# "City of" words that small Wikipedias put in front of a city's name, and Japanese "-shi"
PREFIX = re.compile(r'^(Dakbayan sa|Lungsod sa|Lungsod ng|Siyudad ng|Syudad han|Siyudad han|Bungto han|Jiji la|Mji wa) ')

def clean(t, default):
    t = re.sub(r'\s*\(.*\)$', '', t.replace('_', ' ')).split(',')[0].strip()
    t = re.sub(r'-shi$', '', PREFIX.sub('', t))
    if len(t.split()) > len(default.split()) + 2: return ''  # a long official name, not what a map says
    return t if 0 < len(t) <= 40 and ':' not in t else ''

root = os.path.join(os.path.dirname(__file__), '..', '..')
ne = json.load(open(sys.argv[1]))['features']
links = json.load(open(sys.argv[2]))
places = json.load(open(os.path.join(root, 'base', 'places.json')))
key = lambda p, c: (p.get('nameascii') or p.get('NAMEASCII'), round(c[0], 2), round(c[1], 2))
by = {key(f['properties'], f['geometry']['coordinates']): f['properties'] for f in ne}
by_name = {}
for f in ne: by_name.setdefault(f['properties']['NAMEASCII'], []).append(f)

rows = []
for f in places['features']:
    p, c = f['properties'], f['geometry']['coordinates']
    hit = by.get(key(p, c))
    if not hit:
        cands = sorted(by_name.get(p['nameascii'], []), key=lambda g: abs(g['geometry']['coordinates'][0] - c[0]) + abs(g['geometry']['coordinates'][1] - c[1]))
        hit = cands[0]['properties'] if cands else {}
    rows.append(hit)

for lang, wiki in WIKI.items():
    out = []
    for f, h in zip(places['features'], rows):
        default = f['properties']['name']
        q = (h.get('WIKIDATAID') or '')[1:]
        name = clean(links.get(q, {}).get(wiki, ''), default) or h.get(FALLBACK.get(lang, ''), '') or (from_hindi(h.get('NAME_HI') or '', lang) if lang in BRAHMI else '') or h.get('NAME_EN') or default
        out.append('' if name == default else name)
    json.dump(out, open(os.path.join(root, 'base', 'names', lang + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(lang, sum(1 for x in out if x))
