# Download 960px thumbs + wikitext credit for selected matches; write 640x320 JPEGs and credits.json.
import sys, json, hashlib, urllib.parse, urllib.request, time, io, re, os, threading, concurrent.futures as cf
from PIL import Image, ImageOps
W = '/tmp/claude-0/work/'; OUT = W + 'img/'; os.makedirs(OUT, exist_ok=True)
sel = json.load(open(sys.argv[1]))  # {church_idx: filename}
UA = 'CatholicChurchGlobe/1.0 (https://claude.ai; zofoyodee@gmail.com)'
cred_path = W + 'credits.json'
credits = json.load(open(cred_path)) if os.path.exists(cred_path) else {}
lock = threading.Lock(); pause = [0.0]
def get(url, tries=10):
    for k in range(tries):
        while time.time() < pause[0]: time.sleep(0.5)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                ra = float(e.headers.get('Retry-After') or 10)
                pause[0] = max(pause[0], time.time() + ra); continue
            if e.code in (400, 404, 500): return None
        except Exception: time.sleep(2 * (k + 1))
    return None
def clean(s):
    s = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', s); s = re.sub(r'\[https?://\S+ ([^\]]*)\]', r'\1', s)
    s = re.sub(r'\{\{(?:[a-z\-]{2,5}\|1=|[a-z\-]{2,5}\|)?([^{}|]*)\}\}', r'\1', s); s = re.sub(r"<[^>]+>|'''?|\{\{|\}\}", '', s)
    return re.sub(r'\s+', ' ', s).strip()[:80]
LIC = [(r'cc-zero|cc0', 'CC0'), (r'cc-by-sa-4\.0', 'CC BY-SA 4.0'), (r'cc-by-sa-3\.0', 'CC BY-SA 3.0'), (r'cc-by-sa-2\.5', 'CC BY-SA 2.5'), (r'cc-by-sa-2\.0', 'CC BY-SA 2.0'),
       (r'cc-by-4\.0', 'CC BY 4.0'), (r'cc-by-3\.0', 'CC BY 3.0'), (r'cc-by-2\.0', 'CC BY 2.0'), (r'cc-by-sa', 'CC BY-SA'), (r'cc-by', 'CC BY'), (r'gfdl', 'GFDL'), (r'pd-|public domain|pd\}', 'Public domain'), (r'flickr-no known', 'No known restrictions')]
def credit(fn):
    t = get('https://commons.wikimedia.org/w/index.php?' + urllib.parse.urlencode({'title': 'File:' + fn, 'action': 'raw'}))
    if t is None: return None
    t = t.decode('utf-8', 'replace'); low = t.lower()
    m = re.search(r'\|\s*(?:author|photographer|artist)\s*=\s*(.+)', t, re.I)
    au = clean(m.group(1)) if m else ''
    if not au:
        m = re.search(r'\{\{\s*self\s*\|', low)
    lic = next((n for p, n in LIC if re.search(p, low)), 'See file page')
    return [au or 'Wikimedia Commons contributor', lic]
def job(ci, fn):
    if os.path.exists(OUT + ci + '.jpg'):
        if ci in credits: return 'skip'
        c = credit(fn)
        with lock: credits[ci] = [fn] + (c or ['Wikimedia Commons contributor', 'See file page'])
        return 'ok'
    f = fn.replace(' ', '_'); h = hashlib.md5(f.encode()).hexdigest(); q = urllib.parse.quote(f)
    base = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/'
    ext = '.jpg' if f.lower().endswith(('.tif', '.tiff', '.pdf', '.webp')) else ''
    b = get(base + f'500px-{q}{ext}', 30) or (None if ext else get(f'https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}'))
    if not b: return 'noimg'
    try:
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(b))).convert('RGB')
        if im.width < 300: return 'small'
        im = ImageOps.fit(im, (500, 250), Image.LANCZOS, centering=(0.5, 0.42))
        im.save(OUT + ci + '.jpg', 'JPEG', quality=70, optimize=True, progressive=True)
    except Exception as e: return 'bad'
    c = credit(fn)
    with lock: credits[ci] = [fn] + (c or ['Wikimedia Commons contributor', 'See file page'])
    return 'ok'
import collections; st = collections.Counter(); n = 0
with cf.ThreadPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 3) as ex:
    for r in ex.map(lambda kv: job(*kv), sel.items()):
        st[r] += 1; n += 1
        if st["ok"] and n % 5 == 0:
            print(n, dict(st), flush=True)
            with lock: json.dump(credits, open(cred_path, 'w'), ensure_ascii=False)
json.dump(credits, open(cred_path, 'w'), ensure_ascii=False); print('done', dict(st))
