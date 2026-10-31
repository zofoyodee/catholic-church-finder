#!/usr/bin/env python3
"""Country and language names for languages whose browsers have none (Intl.DisplayNames falls back to English).

Each name is the title of the country's article on that language's Wikipedia, from the Wikidata
sitelinks dump (wikidatawiki-latest-wb_items_per_site.sql.gz).
Usage: countries.py cc_q.json lang_q.json sitelinks.json   (ISO2 -> Q-id, language code -> Q-id, Q-number -> {wiki: title})
Writes i18n/countries/<lang>.json: country names by ISO code, and language names by "_" + code (Mass languages
and the Wikipedias the page quotes).
"""
import json, os, re, sys

WIKI = {'fil': 'tlwiki', 'ig': 'igwiki', 'ilo': 'ilowiki', 'ht': 'htwiki', 'bcl': 'bclwiki', 'gn': 'gnwiki',
        'ny': 'nywiki', 'war': 'warwiki', 'sn': 'snwiki', 'tet': 'tetwiki', 'la': 'lawiki', 'mt': 'mtwiki',
        'zu': 'zuwiki', 'ak': 'twwiki', 'vi': 'viwiki', 'ceb': 'cebwiki', 'ln': 'lnwiki', 'mg': 'mgwiki', 'qu': 'quwiki',
        'rn': 'rnwiki', 'rw': 'rwwiki', 'lg': 'lgwiki', 'ki': 'kiwiki', 'yo': 'yowiki', 'gom': 'gomwiki', 'sq': 'sqwiki',
        # no Wikipedia of their own: the nearest one people there also read
        'hil': 'cebwiki', 'bem': 'nywiki'}
# Natural Earth gives some ISO codes to an outlying piece first; these are the countries themselves
FIX = {'AU': 'Q408', 'BR': 'Q155', 'FR': 'Q142', 'KZ': 'Q232'}
# where that Wikipedia keeps the English title or has no article
OVERRIDE = {'zu': {'IN': 'INdiya', 'PH': 'IPhilippines'}}

EXTRA = json.load(open(os.path.join(os.path.dirname(__file__), 'countries_extra.json')))
ccq, lq, sl = json.load(open(sys.argv[1])), json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
ccq.update(FIX)
out = os.path.join(os.path.dirname(__file__), '..', '..', 'i18n', 'countries')
os.makedirs(out, exist_ok=True)
for lang, wiki in WIKI.items():
    names = {}
    for cc, q in ccq.items():
        t = sl.get(q[1:], {}).get(wiki)
        if t:
            names[cc.replace('CN-', '')] = re.sub(r'\s*\([^)]*\)$', '', t.replace('_', ' '))
    for code, q in lq.items():
        t = sl.get(q[1:], {}).get(wiki)
        if t: names['_' + code] = re.sub(r'\s*\([^)]*\)$', '', t.replace('_', ' '))
    # names written by hand where that Wikipedia has no article (countries_extra.json)
    for k, v in EXTRA.get(lang, {}).items(): names.setdefault(k, v)
    names.update(OVERRIDE.get(lang, {}))
    json.dump(dict(sorted(names.items())), open(os.path.join(out, lang + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(lang, len(names))
