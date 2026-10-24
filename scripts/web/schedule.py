"""Read Mass and Confession times from a parish web page.

Keeps short lines that pair a day ("Sunday", "Sábado", "Niedziela"...) with a
time ("8:00 am", "18h30", "10.30"), and sorts them into Mass or Confession by
the keywords on the line or in the heading above it. Lines under other
headings (office hours, adoration, events) are skipped.
"""
from urllib.parse import urljoin, urlsplit

import regex as re
from bs4 import BeautifulSoup, NavigableString

TIME = re.compile(r'(?<![\d/.:])(?:(?:[01]?\d|2[0-3])(?::|\.|h|H)[0-5]\d(?:\s*[ap]\.?\s?m\.?)?|(?:1[0-2]|0?[1-9])\s*[ap]\.?\s?m\b\.?|(?:[01]?\d|2[0-3])\s?[hH](?![a-z]))(?![\d/])', re.I)
DAY = re.compile(r'\b(sun|sunday|sat|saturday|mon|monday|tue|tues|tuesday|wed|wednesday|thu|thur|thurs|thursday|fri|friday|weekdays?|weekends?|daily|holy days?|holydays?|vigil'
                 r'|domingos?|s[áa]bados?|lunes|martes|mi[ée]rcoles|jueves|viernes|entre semana|d[íi]as? de semana|festivos?'
                 r'|segunda|ter[çc]a|quarta|quinta|sexta|dias? [úu]teis'
                 r'|domenica|sabato|luned[ìi]|marted[ìi]|mercoled[ìi]|gioved[ìi]|venerd[ìi]|feriali|festivi|prefestiv\w*'
                 r'|dimanches?|samedis?|lundi|mardi|mercredi|jeudi|vendredi|en semaine'
                 r'|sonntags?|samstags?|montags?|dienstags?|mittwochs?|donnerstags?|freitags?|werktags?|vorabend'
                 r'|niedziel\w*|sobot\w*|poniedzia\w*|wtor\w*|[śs]rod\w*|czwart\w*|pi[ąa]t\w*|dni powszednie|[śs]wi[ęe]t\w*'
                 r'|zondag|zaterdag|maandag|dinsdag|woensdag|donderdag|vrijdag'
                 r'|linggo|sabado|lunes)\b', re.I)
MASS = re.compile(r'\b(mass|masses|eucharist\w*|liturg\w*|misas?|missas?|messes?|messa|sante messe|s\. ?messe|celebra\w*|gottesdienst\w*|eucharistiefeier|hl\.? messe|msz[ae]|msze [śs]w|nabo[żz]e\w*|mis[ae] dominical|vigil)\b', re.I)
CONF = re.compile(r'\b(confessions?|reconciliation|penance|confesi[oó]n\w*|confiss\w*|confessioni|confessione|beicht\w*|spowied\w*|sacramento de la reconciliaci[oó]n|riconciliazione|biecht)\b', re.I)
OTHER = re.compile(r'\b(office|oficina|secretar[íi]a|secretaria|ufficio|bureau|sekretariat|pfarrb[üu]ro|kancelari\w*|biuro|adoration|adoraci[oó]n|adora[çc][ãa]o|adorazione|anbetung|adoracj\w*|rosary|rosario|ros[áa]rio|chapelet|r[óo][żz]aniec|bingo|religious education|catequesis|catechesi|catequese|youth|j[óo]venes|choir|coro|meeting|reuni[oó]n|food pantry|thrift|gift shop|tienda|museum|museo|tours?|visit|horario de visita|opening hours|[öo]ffnungszeiten|apertura|ouverture|parking|bulletin deadline|novena|stations of the cross|via crucis|vespers|v[íi]speras|lauds|holy hour|hora santa|roraty|droga krzy\w*|gorzkie|nabo[żz]e[ńn]stw\w* (?:ku|majowe|czerwcowe|fatimsk)|rosarios?|ros[áa]rio|via crucis|aanbidding|anbetung|kreuzweg|chrzest|catechism\w*|catechismo|cresima|sakrament chrztu|incontro|reunión|zoom|livestream\w*|live ?stream\w*|communion service|liturgy of the word|baptism|bautismo|batismo|wedding|boda|casamento|funeral|quincea[ñn]era)\b', re.I)
AFTER = re.compile(r'\b(followed by|before|after|then|antes de|despu[ée]s de|seguid[oa] de)\s+(the\s+|la\s+|el\s+)?(\w+\s+)?(mass|misa|messe|eucharist\w*)\b', re.I)
INTENTION = re.compile(r'(^|\s)[+†]\s*\p{Lu}|\bintenc\w*|\bintenzion\w*|\bza \+|\bdo bo[żz]ej opatrzno', re.I)
CHURCHY = re.compile(r'(church|parish|catholic|cat[óo]lic|catholique|cattolic|katholi|katolick|parroquia|par[óo]quia|parrocchia|paroisse|pfarr|parafi|iglesia|igreja|chiesa|[ée]glise|kirche|ko[śs]ci[óo][łl]|santuario|sanctuaire|catedral|cathedral|cattedrale|basilic|capela|capilla|cappella|chapel|chapelle|kaplica|\bmass\b|\bmisas?\b|\bmissas?\b|\bmesses?\b|\bmsz[ae]|eucharist)', re.I)
DMONTH = re.compile(r'\b\d{1,2}\.?\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre|januar|februar|m[äa]rz|april|juni|juli|august|september|oktober|dezember|stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|wrze[śs]nia|pa[źz]dziernika|listopada|grudnia|de \w+|janeiro|fevereiro|abril|maio|junho|julho|setembro|outubro|novembro|dezembro|januari|februari|maart|mei|augustus|oktober)\b|\b\d{1,2}\.\d{1,2}\.(\d{2,4})?(?!\d)', re.I)
DATEY = re.compile(r'\b(20\d\d|19\d\d)\b|\b(january|february|march|april|june|july|august|september|october|november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|gennaio|febbraio|aprile|maggio|giugno|luglio|settembre|ottobre|dicembre|janvier|f[ée]vrier|avril|juin|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre|januar|februar|m[äa]rz|juni|juli|oktober|dezember|stycz\w+|lut\w+|kwie\w+|maj[a]?|czerw\w+|lip\w+|sierp\w+|wrze[śs]\w+|pa[źz]dziern\w+|listopad\w*|grud\w+|janeiro|fevereiro|mar[çc]o|maio|junho|julho|setembro|outubro|dezembro)\b\.?\s*\d{1,2}\b|\b\d{1,2}(st|nd|rd|th)?\s+(of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b|\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', re.I)
LINKS = re.compile(r'(mass|masses|schedule|liturg|horario|hor[aá]rio|misas|missas|orari|messe|horaires|gottesdienst|msz|porz[aą]dek|nabo[żz]|confess|reconcil|sacrament|worship|celebrac|celebraz|beicht|spowied|times)', re.I)
LINKS_STRONG = re.compile(r'(mass[-_ ]?(times|schedule)|masses|horarios?|hor[aá]rios|misas|missas|orari|horaires|gottesdienst|msze|porz[aą]dek|confession|reconcil)', re.I)
SKIP = {'script', 'style', 'noscript', 'svg', 'template', 'iframe', 'select', 'option', 'button', 'form', 'head', 'nav'}
BLOCKS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'dt', 'dd', 'div', 'section', 'article', 'header', 'footer', 'aside', 'blockquote', 'tr', 'ul', 'ol', 'table', 'tbody', 'thead', 'figure', 'main', 'body', 'address'}
HEAD = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dt', 'th', 'strong', 'b'}


def _text(el):
    out = []
    for c in el.children:
        if isinstance(c, NavigableString):
            out.append(str(c))
        elif c.name in SKIP:
            continue
        elif c.name in BLOCKS:
            out.append('\n')
        elif c.name == 'br':
            out.append('\n')
        else:
            # inline pieces laid out side by side ("<span>10:00 AM</span><span>English</span>") need a gap
            out.append(' ' + _text(c) + ' ')
    return ''.join(out)


def _lines(soup):
    """Visible text as lines in document order; table rows become one line."""
    body = soup.body or soup
    out = []
    for el in body.find_all(True):
        if el.name in SKIP or any(p.name in SKIP for p in el.parents):
            continue
        if el.name == 'tr':
            cells = [c.get_text(' ', strip=True) for c in el.find_all(['td', 'th'], recursive=False)]
            out.append((' – '.join(c for c in cells if c), 'tr'))
            continue
        if el.name in ('td', 'th') and el.find_parent('tr') is not None:
            continue
        if el.name not in BLOCKS and el.name not in HEAD:
            continue
        for ln in _text(el).split('\n'):
            ln = re.sub(r'\s+', ' ', ln).strip(' \t|•·-–—:')
            if ln:
                out.append((ln, el.name))
    return out


def extract_schedule(html, section=None):
    """section='m' on a page that is itself the Mass schedule."""
    soup = BeautifulSoup(html, 'lxml')
    for t in soup.find_all(SKIP):
        t.decompose()
    text = soup.get_text(' ', strip=True)[:300000]
    if not CHURCHY.search(text):
        return [], []  # a town hall, school or shop page
    mass, conf = [], []
    seen = set()
    day = ''  # a day heading ("Saturday") that applies to the time lines under it
    for ln, tag in _lines(soup):
        if len(ln) > 140:
            section = None if not (MASS.search(ln) or CONF.search(ln)) else section
            day = ''
            continue
        has_time = bool(TIME.search(ln))
        if not has_time:
            # a heading-like line sets the section for the lines below it
            if len(ln) <= 60:
                if CONF.search(ln):
                    section = 'c'
                elif MASS.search(ln):
                    section = 'm'
                elif OTHER.search(ln):
                    section = 'x'
                day = ln.rstrip(' :') if DAY.search(ln) and len(ln) <= 30 else ''
            continue
        if DATEY.search(ln) or DMONTH.search(ln) or INTENTION.search(ln):
            continue  # an event on a date or a Mass intention, not the weekly schedule
        if OTHER.search(ln) and not (MASS.search(ln) or CONF.search(ln)):
            continue
        if AFTER.search(ln):
            continue  # "Sodality at 4:45, followed by Mass at 6:30": the times belong to something else
        kind = 'c' if CONF.search(ln) else 'm' if MASS.search(ln) else section
        if kind not in ('m', 'c'):
            continue
        if not DAY.search(ln):
            if day:
                ln = f'{day}: {ln}'
            elif not re.search(r'\b(vigil|anticip\w*|prefestiv\w*|vorabend)\b', ln, re.I):
                continue  # a time with no day reads as noise on its own
        key = re.sub(r'\W+', '', ln.lower())
        if key in seen or any(key in s for s in seen):
            continue
        seen.add(key)
        (conf if kind == 'c' else mass).append(ln)
    # a page with dozens of matches is a calendar or bulletin archive, not a schedule
    if len(mass) > 14:
        mass = []
    if len(conf) > 8:
        conf = []
    if mass and not any(DAY.search(m) for m in mass):
        mass = []
    return mass[:10], conf[:5]


def schedule_links(html, base):
    soup = BeautifulSoup(html, 'lxml')
    host = (urlsplit(base).hostname or '').lower().removeprefix('www.')
    scored = {}
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            continue
        u = urljoin(base, href).split('#')[0]
        sp = urlsplit(u)
        if sp.scheme not in ('http', 'https') or (sp.hostname or '').lower().removeprefix('www.') != host:
            continue
        if re.search(r'\.(pdf|jpe?g|png|gif|docx?|mp3|mp4|zip)$', sp.path, re.I):
            continue
        label = (a.get_text(' ', strip=True) or '')[:60] + ' ' + sp.path
        s = 3 if LINKS_STRONG.search(label) else 1 if LINKS.search(label) else 0
        if s and u.rstrip('/') != base.rstrip('/'):
            scored[u] = max(scored.get(u, 0), s)
    return [u for u, s in sorted(scored.items(), key=lambda kv: -kv[1])[:2]]
