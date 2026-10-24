"""Check every church's website and look for its priests and deacons.

Runs in GitHub Actions (the sandbox that built the data can't reach parish
sites). For each unique website URL in data/d/*.json it:
  1. fetches the home page, following redirects, and classifies the link as
     ok / moved / dead / unknown (blocked by the site, timed out, etc.);
  2. on parish-specific sites, finds likely staff pages (Staff, Clergy, Our
     Priests, Equipe, Clero, Seelsorge...) and reads names that carry a clergy
     title (Fr., Rev., Msgr., Deacon, Padre, Pbro., Abbe, Pfarrer, Ks., ...),
     their role, and a nearby photo URL.

Usage: python crawl.py PART PARTS OUT.json [LIMIT]
"""
import asyncio, json, re, sys, time, collections
from urllib.parse import urljoin, urlsplit
from urllib import robotparser

import aiohttp
from bs4 import BeautifulSoup, NavigableString

UA = 'CatholicChurchFinderBot/1.0 (+https://github.com/zofoyodee/catholic-church-finder)'
HEADERS = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.5', 'Accept-Language': 'en,es;q=0.8,pt;q=0.7,it;q=0.6,fr;q=0.5,de;q=0.4,pl;q=0.3'}
MAX_BYTES = 1_500_000

# Links that are profiles on big platforms, not a parish's own site. The page
# labels these by platform; checking them is pointless (they block crawlers).
PLATFORM = re.compile(r'(^|\.)(facebook|fb|instagram|youtube|youtu|tiktok|twitter|x|linktr|whatsapp|wa|t|threads|wikipedia|google|goo|bit|tinyurl|maps\.app\.goo|cafe\.daum|blog\.naver|band|line|vk|ok|pinterest|flickr|spotify|soundcloud|linkedin)\.(com|me|ee|ly|gl|net|org|be|co|ru|us)$')

PARKED = re.compile(r'(domain (name )?(is |may be )?for sale|buy this domain|this domain (has expired|is parked|is available)|parked (free|domain)|domain parking|sedoparking|hugedomains|dan\.com|afternic|godaddy\.com/domains|this site can.t be reached|account (has been )?suspended|website (is )?(expired|suspended)|hosting (account )?(has )?expired|future home of|coming soon|under construction|default web site page|welcome to nginx|apache2 (ubuntu|debian) default page|it works!)', re.I)

STAFF_STRONG = re.compile(r'(staff|clergy|priest|pastor|deacon|our-team|parish-team|pastoral-team|leadership|equipe|équipe|clero|sacerdot|padres|presbit|curas|personale|sacerdoti|seelsorge|pfarrteam|seelsorgeteam|ansprechpartner|duszpaster|kaplan|ksieza|księża|duchowni|kapłani|zesp[oó]ł|parocco|parroco|párroco|pároco|vigario|vicari|cure-|curé|pretre|prêtre|pfarrer|team|who-we-are|quienes-somos|quem-somos|chi-siamo|qui-sommes|o-nas|wir-ueber-uns|uber-uns|über-uns|meet-)', re.I)
STAFF_WEAK = re.compile(r'(about|contact|parish-office|office|nosotros|parroquia|parish|kontakt|contatti|contacto|contato)', re.I)

T_DEACON = r"(?:Deacon|Dcn\.?|Deac\.|Rev(?:erend|\.)?\s+Mr\.|Di[aá]cono|Diac\.|Diacre|Diakon|Dk\.|Diac\b)"
T_PRIEST = (r"(?:(?:The\s+)?(?:Very|Most|Right|Rt\.?|V\.)\s+Rev(?:erend|\.)?(?:\s+(?:Msgr\.?|Monsignor|Fr\.?|Father|Dr\.))?|Rev(?:erend|\.)?(?:\s+(?:Msgr\.?|Monsignor|Fr\.?|Father|Dr\.|Canon))?|"
            r"Fr\.|Father|Msgr\.?|Monsignor|Mons\.|Mgr\.?|Padre|Pe\.|Pbro\.?|Presb\.|Sac\.|Sacerdote|Don|Abb[eé]|P[eè]re|Pfarrer|Kaplan|Pater|P\.|Ks\.|Ksi[aą]dz|O\.|Cônego|C[oó]n\.|Canon|Frei|Fray|Fra|Dom)")
NAMEW = r"[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿA-ZÀ-ÖØ-Þ'’\-]+\.?"
INIT = r"[A-Z]\."
NAME = rf"((?:{NAMEW}|{INIT})(?:\s+(?:de|da|do|dos|das|del|de la|di|van|von|der|le|la|y|e|mac|st\.)?\s*(?:{NAMEW}|{INIT})){{1,4}})"
RE_PERSON = re.compile(rf"(?<![\w])({T_DEACON}|{T_PRIEST})\s+{NAME}")
SUFFIX = re.compile(r",?\s*(?:O\.?F\.?M\.?(?:\s*Cap\.?)?|S\.?J\.?|O\.?P\.?|C\.?S\.?C\.?|O\.?S\.?B\.?|C\.?S\.?s\.?R\.?|S\.?D\.?B\.?|O\.?Carm\.?|C\.?M\.?|M\.?S\.?F\.?|S\.?V\.?D\.?|O\.?S\.?A\.?|C\.?P\.?|O\.?M\.?I\.?|J\.?C\.?L\.?|S\.?T\.?L\.?|S\.?T\.?D\.?|Ph\.?D\.?|D\.?Min\.?|V\.?F\.?)\b")

DEACON_ROLE = re.compile(r'\b(deacon|di[aá]cono|diacre|diakon|diakoni|diacon)', re.I)
ROLES = [
    (re.compile(r'\b(pastor emeritus|párroco emérito|pároco emérito|retired|emeritus|jubilado)\b', re.I), 'Pastor emeritus'),
    (re.compile(r'\b(parochial vicar|associate pastor|assistant pastor|assistant priest|curate|vicario parroquial|vigário paroquial|vicario parrocchiale|vicaire|kaplan|wikariusz|wikary|coadjutor|vicar)\b', re.I), 'Parochial vicar'),
    (re.compile(r'\b(administrator|administrador|amministratore)\b', re.I), 'Administrator'),
    (re.compile(r'\b(rector|rettore|reitor|recteur)\b', re.I), 'Rector'),
    (re.compile(r'\b(chaplain|capellán|capelão|cappellano|aumônier)\b', re.I), 'Chaplain'),
    (re.compile(r'\b(in residence|residente|resident priest|priest in residence)\b', re.I), 'In residence'),
    (re.compile(r'\b(pastor|parish priest|párroco|pároco|parroco|curé|pfarrer|proboszcz|moderator)\b', re.I), 'Pastor'),
]
# Words that mean the match is a saint, a feast, a church name or prose rather than a person
STOP = re.compile(r"\b(Pio|Bosco|Damien|Kolbe|Champagnat|Christmas|Day|Time|Son|God|Lord|Jesus|Christ|Mary|Church|Parish|Iglesia|Igreja|Chiesa|Paroisse|Kirche|Mass|Masses|Misa|Missa|Messe|Office|Prayer|Program|Contact|Click|Read|More|Our|The|Of|And|Saint|San|Santo|Santa|Sao|São|Sankt|St|Blessed|Holy|Sacred|Hospital|School|Center|Centre|Ministry|Pope|Bishop|Archbishop|Cardinal|Obispo|Arzobispo|Bispo|Vescovo|Papa|Francis\s*$|Leo\s*$|Benedict\s*$|Francisco\s*$|Prisco|Gnocchi|Milani|Orione|Rua|Puglisi|Calabria|Guanella|Bibbia|Fátima|Fatima|Week|Weekend|Sunday|Monday|Message|Corner|Notes|Desk|Says|Writes|Speaks|Blog|Reflection|Reflections|Homily|Homilies|Podcast|Video|Walk|Talk|Club)\b")
SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'template', 'iframe', 'select', 'option', 'button', 'form', 'head'}
BLOCKS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'dt', 'dd', 'figcaption', 'div', 'section', 'article', 'header', 'footer', 'aside', 'blockquote', 'tr', 'ul', 'ol', 'figure', 'main', 'nav', 'body', 'address', 'table'}
BAD_IMG = re.compile(r'(logo|icon|sprite|banner|header|footer|background|bg[-_]|placeholder|blank|spacer|pixel|loader|facebook|instagram|twitter|youtube|social|flag|arrow|button|btn|donate|seal|crest|coat[-_]?of[-_]?arms|wappen|escudo|map|\.svg|\.gif|data:)', re.I)


def norm_host(h):
    return (h or '').lower().removeprefix('www.')


def text_of(el):
    """Text of el excluding nested block elements (so a name and its line stay together)."""
    out = []
    for c in el.children:
        if isinstance(c, NavigableString):
            out.append(str(c))
        elif c.name in SKIP_TAGS or c.name in BLOCKS:
            continue
        elif c.name == 'br':
            out.append('\n')
        else:
            out.append(text_of(c))
    return ''.join(out)


def img_src(img, base):
    for a in ('data-src', 'data-lazy-src', 'data-original', 'data-srcset', 'srcset', 'src'):
        v = (img.get(a) or '').strip()
        if not v or v.startswith('data:'):
            continue
        if 'srcset' in a:
            # pick the widest candidate up to ~400px when possible
            cands = [p.strip().split() for p in v.split(',') if p.strip()]
            v = cands[0][0] if cands else ''
            for c in cands:
                if len(c) > 1 and c[1].endswith('w') and c[1][:-1].isdigit() and int(c[1][:-1]) <= 500:
                    v = c[0]
        if v:
            u = urljoin(base, v)
            if u.startswith('http') and not BAD_IMG.search(urlsplit(u).path + ' ' + ' '.join(img.get('class') or [])):
                w = img.get('width') or ''
                if w.isdigit() and int(w) < 40:
                    return ''
                return u
    return ''


def clean_name(title, name):
    name = SUFFIX.sub('', name).strip(' ,.;:-–')
    words = name.split()
    # drop trailing words that look like the next sentence
    while words and words[-1].lower() in ('is', 'the', 'and', 'our', 'will', 'has', 'was'):
        words.pop()
    if len(words) < 2 or len(words) > 5:
        return None
    if sum(1 for w in words if len(w.rstrip('.')) > 1) < 2 and not re.match(r'^[A-Z]\.$', words[0]):
        return None
    name = ' '.join(words)
    if STOP.search(name) or STOP.search(words[0]):
        return None
    if name.isupper() and len(name) > 4:
        name = name.title()
    return name


def kind_of(title, ctx):
    if re.match(T_DEACON + '$', title.strip(), re.I) or re.match(T_DEACON, title, re.I):
        return 'deacon'
    return 'priest'


def role_of(kind, ctx):
    if kind == 'deacon':
        return 'Deacon'
    for rx, label in ROLES:
        if rx.search(ctx):
            return label
    return ''


def extract_people(html, base, church_name=''):
    soup = BeautifulSoup(html, 'lxml')
    for t in soup.find_all(SKIP_TAGS):
        t.decompose()
    body = soup.body or soup
    people = collections.OrderedDict()
    church_words = set(re.findall(r'\w+', (church_name or '').lower()))
    for el in body.find_all(list(BLOCKS)):
        txt = re.sub(r'[ \t\xa0]+', ' ', text_of(el)).strip()
        if not txt or len(txt) > 4000:
            continue
        for m in RE_PERSON.finditer(txt):
            title, raw = m.group(1), m.group(2)
            # "Don" and "P." and "O." and "Dom" are ambiguous; only accept them in short lines (lists, captions)
            if title in ('Don', 'P.', 'O.', 'Dom', 'Fra', 'Pater', 'Sac.') and len(txt) > 160:
                continue
            name = clean_name(title, raw)
            if not name:
                continue
            nw = set(re.findall(r'\w+', name.lower()))
            if nw and nw <= church_words:
                continue  # the church's own patron (e.g. "Padre Pio" in "Parroquia Padre Pio")
            start = max(0, m.start() - 120)
            ctx = txt[start:m.end() + 140]
            if len(txt) < 120:
                ctx += ' ' + near_text(el)
            kind = kind_of(title, ctx)
            if kind == 'priest' and DEACON_ROLE.search(txt[max(0, m.start() - 25):m.start()]):
                kind = 'deacon'
            key = name.lower().replace('.', '')
            if key in people:
                p = people[key]
                if not p['role']:
                    p['role'] = role_of(p['kind'], ctx)
                if not p['img']:
                    p['img'] = find_img(el, base, name)
                continue
            people[key] = {'kind': kind, 'title': title.strip(), 'name': name, 'role': role_of(kind, ctx), 'img': find_img(el, base, name)}
    # images whose alt text names a person
    if people:
        for img in body.find_all('img'):
            alt = ' '.join(filter(None, [img.get('alt'), img.get('title')]))
            if not alt:
                continue
            for p in people.values():
                if not p['img'] and p['name'].split()[-1].lower() in alt.lower():
                    p['img'] = img_src(img, base)
    return list(people.values())


def near_text(el):
    """Text around a short line (a card's caption), as long as it belongs to just this person."""
    par = el.parent
    if par is not None and par.name not in ('body', 'html'):
        t = par.get_text(' ', strip=True)
        if len(t) < 400 and len(RE_PERSON.findall(t)) <= 1:
            return t
    sib = el.find_next_sibling()
    if sib is not None:
        t = sib.get_text(' ', strip=True)
        if len(t) < 120 and not RE_PERSON.search(t):
            return t
    return ''


def find_img(el, base, name):
    """A photo near this person's line, but only from a container that holds just this one person."""
    node = el
    for _ in range(4):
        if node is None or node.name in ('body', 'html', 'main'):
            break
        imgs = node.find_all('img') if hasattr(node, 'find_all') else []
        if imgs:
            t = node.get_text(' ', strip=True)
            if len(RE_PERSON.findall(t)) > 1:
                return ''
            for img in imgs:
                u = img_src(img, base)
                if u:
                    return u
        # the image is often the previous sibling (card layout: <img> then <h3>name</h3>)
        sib = node.find_previous_sibling()
        if sib is not None and getattr(sib, 'name', None) in ('img', 'figure', 'picture', 'div', 'a', 'span', 'p'):
            simgs = [sib] if sib.name == 'img' else sib.find_all('img')
            if simgs and len(simgs) == 1 and not RE_PERSON.search(sib.get_text(' ', strip=True) or ''):
                u = img_src(simgs[0], base)
                if u:
                    return u
        node = node.parent
    return ''


def staff_links(html, base):
    soup = BeautifulSoup(html, 'lxml')
    host = norm_host(urlsplit(base).hostname)
    scored = {}
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            continue
        u = urljoin(base, href).split('#')[0]
        sp = urlsplit(u)
        if sp.scheme not in ('http', 'https') or norm_host(sp.hostname) != host:
            continue
        if re.search(r'\.(pdf|jpe?g|png|gif|docx?|mp3|mp4|zip)$', sp.path, re.I):
            continue
        label = (a.get_text(' ', strip=True) or '')[:60] + ' ' + sp.path
        s = 0
        if STAFF_STRONG.search(label):
            s = 3
            if re.search(r'(staff|clergy|priest|clero|sacerdot|seelsorge|duszpaster|equipe|équipe)', label, re.I):
                s = 5
        elif STAFF_WEAK.search(label):
            s = 1
        if s and u.rstrip('/') != base.rstrip('/'):
            scored[u] = max(scored.get(u, 0), s)
    return [u for u, s in sorted(scored.items(), key=lambda kv: -kv[1])[:3]]


class Crawler:
    def __init__(self, session):
        self.s = session
        self.robots = {}

    async def get(self, url, timeout=20):
        try:
            async with self.s.get(url, timeout=aiohttp.ClientTimeout(total=timeout, sock_connect=10), allow_redirects=True, max_redirects=8) as r:
                ctype = r.headers.get('content-type', '')
                body = b''
                if 'html' in ctype or 'xml' in ctype or not ctype:
                    body = await r.content.read(MAX_BYTES)
                charset = r.charset or 'utf-8'
                try:
                    text = body.decode(charset, errors='replace')
                except LookupError:
                    text = body.decode('utf-8', errors='replace')
                return r.status, str(r.url), text, None
        except asyncio.TimeoutError:
            return 0, url, '', 'timeout'
        except aiohttp.ClientConnectorCertificateError:
            return 0, url, '', 'cert'
        except aiohttp.ClientSSLError:
            return 0, url, '', 'ssl'
        except aiohttp.ClientConnectorDNSError:
            return 0, url, '', 'dns'
        except aiohttp.ClientConnectorError:
            return 0, url, '', 'refused'
        except aiohttp.TooManyRedirects:
            return 0, url, '', 'redirects'
        except Exception as e:  # noqa: BLE001 - every odd failure becomes "unknown"
            return 0, url, '', type(e).__name__

    async def allowed(self, url):
        sp = urlsplit(url)
        key = sp.scheme + '://' + sp.netloc
        if key not in self.robots:
            rp = robotparser.RobotFileParser()
            st, _, txt, _ = await self.get(key + '/robots.txt', timeout=10)
            rp.parse(txt.splitlines() if st == 200 else [])
            self.robots[key] = rp
        return self.robots[key].can_fetch(UA, url)

    async def check(self, url, name, shared):
        res = {'s': 'unknown'}
        st, final, html, err = await self.get(url)
        if err in ('ssl', 'cert') and url.startswith('https://'):
            st2, final2, html2, err2 = await self.get('http://' + url[8:])
            if not err2 and st2 < 400:
                st, final, html, err = st2, final2, html2, None
        if err == 'timeout':
            st, final, html, err = await self.get(url, timeout=40)
        if err:
            res['s'] = 'dead' if err in ('dns', 'refused', 'redirects', 'cert', 'ssl') else 'unknown'
            res['e'] = err
            return res
        res['c'] = st
        if st in (404, 410) or (st >= 500 and st not in (503,)) or (st < 400 and PARKED.search(html[:20000]) and len(html) < 60000):
            # a 5xx gets one more try before we call it dead
            if st >= 500:
                st, final, html, err = await self.get(url, timeout=30)
                if not err and st < 400:
                    return await self._ok(url, final, html, name, shared, res)
            res['s'] = 'dead'
            res['e'] = 'parked' if st < 400 else str(st)
            return res
        if st >= 400:
            return res  # 401/403/429/503: the site is up but turned us away
        return await self._ok(url, final, html, name, shared, res)

    async def _ok(self, url, final, html, name, shared, res):
        a, b = urlsplit(url), urlsplit(final)
        if norm_host(a.hostname) != norm_host(b.hostname):
            res['s'] = 'moved'
            res['u'] = final
        else:
            res['s'] = 'ok'
            if b.scheme != a.scheme or b.path.rstrip('/') != a.path.rstrip('/'):
                res['u'] = final
        if shared:
            return res  # a diocese or directory site shared by many churches: its clergy aren't this parish's
        try:
            people = extract_people(html, final, name)
            src = final if people else ''
            if len(people) < 2:
                for link in staff_links(html, final):
                    if not await self.allowed(link):
                        continue
                    st, f2, h2, err = await self.get(link)
                    if err or st >= 400 or not h2:
                        continue
                    more = extract_people(h2, f2, name)
                    if len(more) > len(people):
                        people, src = more, f2
                    if len(people) >= 2:
                        break
        except Exception as e:  # noqa: BLE001
            res['x'] = type(e).__name__
            return res
        if 0 < len(people) <= 25:
            res['p'] = [[p['kind'][0], p['title'], p['name'], p['role'], p['img']] for p in people[:12]]
            res['src'] = src
        return res


def load_urls():
    count = collections.Counter()
    names = {}
    for k in range(10_000):
        try:
            recs = json.load(open(f'data/d/{k}.json'))
        except FileNotFoundError:
            break
        for r in recs:
            u = r[6]
            if not u:
                continue
            u = u if re.match(r'^https?://', u) else 'https://' + u
            count[u] += 1
            names.setdefault(u, r[0])
    return count, names


async def main():
    part, parts, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    count, names = load_urls()
    host_count = collections.Counter(norm_host(urlsplit(u).hostname) for u in count)
    todo = []
    for i, u in enumerate(sorted(count)):
        if i % parts != part:
            continue
        h = norm_host(urlsplit(u).hostname)
        if PLATFORM.search(h or ''):
            continue
        todo.append(u)
    if limit:
        todo = todo[:limit]
    print(f'part {part}/{parts}: {len(todo)} urls', flush=True)
    results = {}
    conn = aiohttp.TCPConnector(limit=120, limit_per_host=4, ttl_dns_cache=600, ssl=True)
    t0 = time.time()
    async with aiohttp.ClientSession(connector=conn, headers=HEADERS, cookie_jar=aiohttp.DummyCookieJar()) as s:
        c = Crawler(s)
        sem = asyncio.Semaphore(100)
        done = 0

        async def one(u):
            nonlocal done
            async with sem:
                h = norm_host(urlsplit(u).hostname)
                path = urlsplit(u).path.strip('/')
                shared = count[u] > 2 or (host_count[h] > 3 and not path)
                try:
                    results[u] = await asyncio.wait_for(c.check(u, names[u], shared), timeout=180)
                except asyncio.TimeoutError:
                    results[u] = {'s': 'unknown', 'e': 'slow'}
                done += 1
                if done % 250 == 0:
                    print(f'{done}/{len(todo)} {time.time() - t0:.0f}s', flush=True)
        await asyncio.gather(*(one(u) for u in todo))
    json.dump(results, open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
    st = collections.Counter(r['s'] for r in results.values())
    print('status', dict(st), 'with staff', sum(1 for r in results.values() if r.get('p')), f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    asyncio.run(main())
