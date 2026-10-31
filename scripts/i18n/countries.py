#!/usr/bin/env python3
"""Country names for languages whose browsers have none (Intl.DisplayNames falls back to English).

Each name is the title of the country's article on that language's Wikipedia, from the Wikidata
sitelinks dump (wikidatawiki-latest-wb_items_per_site.sql.gz).
Usage: countries.py cc_q.json sitelinks.json   (ISO2 -> Q-id, and Q-number -> {wiki: title})
Writes i18n/countries/<lang>.json.
"""
import json, os, re, sys

WIKI = {'fil': 'tlwiki', 'ig': 'igwiki', 'ilo': 'ilowiki', 'ht': 'htwiki', 'bcl': 'bclwiki', 'gn': 'gnwiki',
        'ny': 'nywiki', 'war': 'warwiki', 'sn': 'snwiki', 'tet': 'tetwiki', 'la': 'lawiki', 'mt': 'mtwiki',
        'zu': 'zuwiki', 'ak': 'twwiki'}
# Natural Earth gives some ISO codes to an outlying piece first; these are the countries themselves
FIX = {'AU': 'Q408', 'BR': 'Q155', 'FR': 'Q142', 'KZ': 'Q232'}

ccq, sl = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
ccq.update(FIX)
out = os.path.join(os.path.dirname(__file__), '..', '..', 'i18n', 'countries')
os.makedirs(out, exist_ok=True)
for lang, wiki in WIKI.items():
    names = {}
    for cc, q in ccq.items():
        t = sl.get(q[1:], {}).get(wiki)
        if t:
            names[cc.replace('CN-', '')] = re.sub(r'\s*\([^)]*\)$', '', t.replace('_', ' '))
    json.dump(dict(sorted(names.items())), open(os.path.join(out, lang + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(lang, len(names))
