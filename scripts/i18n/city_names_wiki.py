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
import json, sys, os, re

# page language -> its Wikipedia. Hindi, Tamil, Malayalam and Konkani are left out: MapLibre cannot shape their scripts.
WIKI = {'bcl': 'bclwiki', 'ceb': 'cebwiki', 'cs': 'cswiki', 'fil': 'tlwiki', 'gn': 'gnwiki', 'hr': 'hrwiki', 'ht': 'htwiki',
        'ig': 'igwiki', 'ilo': 'ilowiki', 'la': 'lawiki', 'lg': 'lgwiki', 'ln': 'lnwiki', 'lt': 'ltwiki', 'mg': 'mgwiki',
        'ny': 'nywiki', 'qu': 'quwiki', 'rn': 'rnwiki', 'rw': 'rwwiki', 'sk': 'skwiki', 'sl': 'slwiki', 'sn': 'snwiki',
        'sq': 'sqwiki', 'sw': 'swwiki', 'tet': 'tetwiki', 'war': 'warwiki', 'yo': 'yowiki', 'ki': 'kiwiki',
        'ca': 'cawiki', 'ro': 'rowiki', 'mt': 'mtwiki', 'zu': 'zuwiki', 'ak': 'twwiki'}

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
        name = clean(links.get(q, {}).get(wiki, ''), default) or h.get('NAME_EN') or default
        out.append('' if name == default else name)
    json.dump(out, open(os.path.join(root, 'base', 'names', lang + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(lang, sum(1 for x in out if x))
