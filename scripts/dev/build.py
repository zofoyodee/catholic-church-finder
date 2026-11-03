"""Build the test copy of the site at churchglobe.com/dev/ from a working tree.

    python3 scripts/dev/build.py [SOURCE_DIR] [OUT_DIR]

SOURCE_DIR is a checkout of the branch being tested (default: this checkout) and OUT_DIR is
the dev/ folder of the live branch (default: ./dev). The test page, its app/ scripts and its
i18n/ dictionaries, the search index (data/meta.json, data/search-*.txt) and readable church names (data/names-x.json) and hand corrections (data/overrides.json) come from SOURCE_DIR; the other big data files (data/, base/, photos/, fonts/)
are the live site's own, shared through <base href="../">. The copy is kept out of search
engines and never installs the offline service worker, so it can't disturb the live site.
"""
import pathlib, re, shutil, sys, datetime

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else 'dev').resolve()

html = (src / 'index.html').read_text(encoding='utf-8')

def sub(pattern, repl, text, count=0):
    new, n = re.subn(pattern, repl, text, count=count)
    if not n:
        sys.exit(f'build.py: nothing matched {pattern!r}; update the script')
    return new

# everything relative resolves against the live site's root, except this copy's own scripts and words
html = sub(r'<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="../">', html, 1)
html = sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', html, 1)
html = sub(r'(href|src)="app/', r'\1="dev/app/', html)
html = sub(r"'i18n/' \+ code", "'dev/i18n/' + code", html)
html = sub(r"'i18n/content/' \+ code", "'dev/i18n/content/' + code", html)
html = sub(r"getJSON\('data/meta\.json'\)", "getJSON('dev/data/meta.json')", html, 1)
html = sub(r"BASE \+ 'data/search-'", "BASE + 'dev/data/search-'", html, 1)
html = sub(r"getJSON\('data/names-x\.json'\)", "getJSON('dev/data/names-x.json')", html, 1)
html = sub(r"BASE \+ 'data/overrides\.json'", "BASE + 'dev/data/overrides.json'", html, 1)
html = sub(r"getJSON\('data/overrides\.json\?t='", "getJSON('dev/data/overrides.json?t='", html, 1)
html = sub(r"if \('serviceWorker' in navigator", "if (false && 'serviceWorker' in navigator", html, 1)
html = sub(r"new URL\('i18n/countries/'", "new URL('dev/i18n/countries/'", html, 1)
html = sub(r"history\.replaceState\(null, '', '\?", "history.replaceState(null, '', location.pathname + '?", html)  # keep /dev/ in the address
# the church pins themselves (data/points.txt, data/d/) are Dev's own when SOURCE_DIR has them in dev-data/
own_pins = (src / 'dev-data' / 'points.txt').exists()
if own_pins:
    html = sub(r"BASE \+ 'data/points\.txt'", "BASE + 'dev/data/points.txt'", html, 1)
    html = sub(r"getJSON\('data/d/' \+ s", "getJSON('dev/data/d/' + s", html, 1)
html = html.replace('href="./" id="homeLink"', 'href="dev/" id="homeLink"')
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
ribbon = ('<div style="position:fixed;z-index:30;top:0;left:50%;transform:translateX(-50%);background:#e8b84a;color:#1a1406;'
          'font:700 10px/1 system-ui,sans-serif;letter-spacing:.1em;padding:3px 10px;border-radius:0 0 8px 8px;white-space:nowrap;pointer-events:none">'
          f'TEST SITE</div><!-- built {stamp} -->')
html = sub(r'<body>', '<body>\n' + ribbon, html, 1)

if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
(out / 'index.html').write_text(html, encoding='utf-8')
shutil.copytree(src / 'app', out / 'app')
shutil.copytree(src / 'i18n', out / 'i18n')
(out / 'data').mkdir()
for f in [src / 'data' / 'meta.json', src / 'data' / 'names-x.json', src / 'data' / 'overrides.json', *sorted((src / 'data').glob('search-*.txt'))]:
    shutil.copy(f, out / 'data' / f.name)
if own_pins:  # a rebuilt pin set under test (e.g. the OpenStreetMap switch): its points, details, search index, counts and corrections
    for f in (src / 'dev-data').glob('*'):
        if f.is_dir(): shutil.copytree(f, out / 'data' / f.name)
        elif f.suffix in ('.txt', '.json'): shutil.copy(f, out / 'data' / f.name)
print(f'built {out} from {src} ({stamp})')
