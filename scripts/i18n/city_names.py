"""City labels in each page language: base/names/<lang>.json, one name per feature of base/places.json.

Names come from Natural Earth 10m populated places (NAME_<LANG> columns). Languages without a
column, or places without a name in it, fall back to the English name. Entries equal to the
default label are left empty to keep the files small.

usage: python3 scripts/i18n/city_names.py ne_10m_populated_places.geojson
"""
import json, sys, os

# Every other page language uses en.json: it has no Natural Earth column, or (Hindi, Tamil, Malayalam)
# MapLibre cannot shape its script. The page lists these files in CITY_FILES.
LANGS = ['en', 'es', 'pt', 'fr', 'it', 'pl', 'de', 'zh', 'nl', 'id', 'vi', 'ko', 'hu', 'uk', 'ar', 'ru', 'ja']
NE_COL = {'en': 'NAME_EN', 'es': 'NAME_ES', 'pt': 'NAME_PT', 'fr': 'NAME_FR', 'it': 'NAME_IT', 'pl': 'NAME_PL', 'de': 'NAME_DE',
          'zh': 'NAME_ZH', 'nl': 'NAME_NL', 'id': 'NAME_ID', 'vi': 'NAME_VI', 'ko': 'NAME_KO', 'hu': 'NAME_HU', 'uk': 'NAME_UK', 'ar': 'NAME_AR',
          'ru': 'NAME_RU', 'ja': 'NAME_JA'}

root = os.path.join(os.path.dirname(__file__), '..', '..')
ne = json.load(open(sys.argv[1]))['features']
places = json.load(open(os.path.join(root, 'base', 'places.json')))
key = lambda p, c: (p.get('nameascii') or p.get('NAMEASCII'), round(c[0], 2), round(c[1], 2))
by = {key(f['properties'], f['geometry']['coordinates']): f['properties'] for f in ne}
by_name = {}
for f in ne: by_name.setdefault(f['properties']['NAMEASCII'], []).append(f)

rows = []
miss = 0
for f in places['features']:
    p, c = f['properties'], f['geometry']['coordinates']
    hit = by.get(key(p, c))
    if not hit:
        cands = by_name.get(p['nameascii'], [])
        cands.sort(key=lambda g: abs(g['geometry']['coordinates'][0] - c[0]) + abs(g['geometry']['coordinates'][1] - c[1]))
        hit = cands[0]['properties'] if cands else None
    if not hit: miss += 1
    rows.append(hit or {})
print('unmatched', miss, 'of', len(rows))

os.makedirs(os.path.join(root, 'base', 'names'), exist_ok=True)
for lang in LANGS:
    col = NE_COL.get(lang)
    out = []
    for f, h in zip(places['features'], rows):
        default = f['properties']['name']
        name = (h.get(col) if col else None) or h.get('NAME_EN') or default
        out.append('' if name == default else name)
    json.dump(out, open(os.path.join(root, 'base', 'names', lang + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(lang, sum(1 for x in out if x))
