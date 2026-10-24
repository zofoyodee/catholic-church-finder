"""Turn schedule lines ("Sunday: 8:00 AM, 10:30 AM (Spanish)") into structured slots.

slot = [kind (0 Mass, 1 Confession), day mask (bit 0 = Sunday ... bit 6 = Saturday),
        minutes after midnight, language code or '']
Only lines that name both a day and a time become slots.
"""
import regex as re

D = {  # word -> weekday (0 = Sunday)
    0: r'sun|sunday|sundays|domingos?|domenica|dimanches?|sonntags?|niedziel\w*|zondag|linggo',
    1: r'mon|monday|lunes|segunda(?:-feira)?|luned[ìi]|lundi|montags?|poniedzia\w*|maandag',
    2: r'tue|tues|tuesday|martes|ter[çc]a(?:-feira)?|marted[ìi]|mardi|dienstags?|wtor\w*|dinsdag',
    3: r'wed|wednesday|mi[ée]rcoles|quarta(?:-feira)?|mercoled[ìi]|mercredi|mittwochs?|[śs]rod\w*|woensdag',
    4: r'thu|thur|thurs|thursday|jueves|quinta(?:-feira)?|gioved[ìi]|jeudi|donnerstags?|czwart\w*|donderdag',
    5: r'fri|friday|viernes|sexta(?:-feira)?|venerd[ìi]|vendredi|freitags?|pi[ąa]t\w*|vrijdag',
    6: r'sat|saturday|s[áa]bados?|sabato|samedis?|samstags?|sobot\w*|zaterdag|sabado',
}
DAYWORD = re.compile(r'\b(' + '|'.join(f'(?P<d{k}>{v})' for k, v in D.items()) + r')\b\.?', re.I)
GROUPS = [
    (re.compile(r'\b(weekdays?|daily mass|weekday mass|entre semana|d[íi]as? (?:de semana|laborables|h[áa]biles)|dias? [úu]teis|feriali|en semaine|werktags?|dni powszednie)\b', re.I), 0b0111110),
    (re.compile(r'\b(daily|every day|todos los d[íi]as|diariamente|tous les jours|t[äa]glich|codziennie|ogni giorno)\b', re.I), 0b1111111),
    (re.compile(r'\b(weekends?|fin de semana)\b', re.I), 0b1000001),
    (re.compile(r'\b(festivi|festivos?|dimanches et f[êe]tes)\b', re.I), 0b0000001),
    (re.compile(r'\b(prefestiv\w*|vigil|vorabend)\b', re.I), 0b1000000),
]
RANGE = re.compile(r'\s*(?:-|–|—|to|a|al|à|bis|do|até|thru|through)\s*$', re.I)
TIME = re.compile(r'(?<![\d/.:])(?P<h>[01]?\d|2[0-3])(?:(?::|\.|h|H)(?P<m>[0-5]\d))?\s*(?P<ap>[ap])?\.?\s?(?:m\b\.?)?(?![\d/])', re.I)
NOON = re.compile(r'\b(noon|mediod[íi]a|midi|mezzogiorno)\b', re.I)
LANGS = [
    ('es', r'spanish|espa[ñn]ol|en espa[ñn]ol|castellano|misa en espa'),
    ('la', r'latin|latina|lat[íi]n|tridentin\w*|extraordinary form|traditional latin|\bTLM\b|vetus ordo|usus antiquior|forma extraordinaria'),
    ('vi', r'vietnamese|ti[ếe]ng vi[ệe]t|vi[ệe]t ng[ữu]'),
    ('pl', r'polish|po polsku|polska|polski'),
    ('pt', r'portuguese|portugu[êe]s|portugais'),
    ('it', r'italian|italiano|in italiano'),
    ('fr', r'\bfrench\b|fran[çc]ais|en fran[çc]ais'),
    ('ko', r'korean|한국어|한인'),
    ('tl', r'tagalog|filipino'),
    ('zh', r'chinese|mandarin|cantonese|中文|華語|國語|粵語'),
    ('ht', r'haitian|creole|kr[ée]y[òo]l|cr[ée]ole'),
    ('de', r'\bgerman\b|deutsch|auf deutsch'),
    ('en', r'\benglish\b|ingl[ée]s|in inglese|en anglais|auf englisch'),
    ('ga', r'\birish\b|gaeilge'),
    ('ar', r'arabic|[àa]rabe|syro|maronite|chaldean'),
    ('uk', r'ukrainian|ucraniano|byzantine'),
    ('hu', r'hungarian|magyar'),
    ('hr', r'croatian|hrvatski'),
    ('sw', r'swahili|kiswahili'),
    ('ig', r'\bigbo\b'),
    ('ml', r'malayalam|syro-malabar|syro malabar'),
    ('ta', r'\btamil\b'),
    ('asl', r'\bASL\b|sign language|deaf'),
]
LANG = [(c, re.compile(r, re.I)) for c, r in LANGS]


def days_of(text):
    """Day mask from day words, ranges ("Mon-Fri") and groups ("weekdays")."""
    mask = 0
    ms = list(DAYWORD.finditer(text))
    for i, m in enumerate(ms):
        d = next(int(k[1]) for k, v in m.groupdict().items() if v)
        mask |= 1 << d
        if i + 1 < len(ms) and RANGE.match(text[m.end():ms[i + 1].start()]):
            e = next(int(k[1]) for k, v in ms[i + 1].groupdict().items() if v)
            j = d
            while j != e:
                j = (j + 1) % 7
                mask |= 1 << j
    for rx, bits in GROUPS:
        if rx.search(text):
            mask |= bits
    return mask


def times_of(text):
    """[(minutes, end position)] for each start time in the line; a range ("3:30 - 4:30 pm") counts once."""
    # blank out things that look like times but aren't (phone numbers, dates), keeping positions
    t = re.sub(r'\+?\d[\d\s().-]{7,}\d', lambda m: ' ' * len(m.group(0)), text)
    t = re.sub(r'\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', lambda m: ' ' * len(m.group(0)), t)
    ms = list(TIME.finditer(t))
    linked = [i + 1 < len(ms) and bool(RANGE.match(t[m.end():ms[i + 1].start()])) for i, m in enumerate(ms)]
    has_ampm = bool(re.search(r'\d\s*[ap]\.?\s?m\b', t, re.I))
    out, skip = [], False
    for i, m in enumerate(ms):
        if skip:  # the end of a range
            skip = linked[i]
            continue
        h, mi, ap = int(m.group('h')), int(m.group('m') or 0), (m.group('ap') or '').lower()
        if not ap:
            # "3:30 - 4:30 pm" and "3 - 4 pm": the start takes the end's am/pm
            j = i
            while j < len(ms) - 1 and linked[j]:
                j += 1
                if ms[j].group('ap'):
                    ap = ms[j].group('ap').lower()
                    break
        if not ap and not m.group('m') and not re.search(r'[hH]', m.group(0)):
            continue  # a bare number
        if ap == 'p' and h < 12:
            h += 12
        elif ap == 'a' and h == 12:
            h = 0
        elif not ap and has_ampm:
            continue
        out.append((h * 60 + mi, m.end()))
        skip = linked[i]
    for m in NOON.finditer(text):
        out.append((12 * 60, m.end()))
    return [(x, e) for x, e in out if 300 <= x <= 23 * 60]  # 5:00 to 23:00


def slots(lines, kind):
    out = []
    for ln in lines:
        mask = days_of(ln)
        if not mask:
            continue
        ts = times_of(ln)
        if not ts:
            continue
        langs = [''] * len(ts)
        for c, rx in LANG:
            for m in rx.finditer(ln):
                # "(Spanish)" right after a time belongs to that time; at the start of the line, to all of them
                near = [k for k, (_, e) in enumerate(ts) if 0 <= m.start() - e <= 12]
                if near:
                    langs[near[-1]] = langs[near[-1]] or c
                elif m.start() < min(e for _, e in ts) or len(ts) == 1:
                    langs = [x or c for x in langs]
        for (t, _), lang in zip(ts, langs):
            out.append([kind, mask, t, lang])
    return out


if __name__ == '__main__':
    for s in ['Saturday Vigil: 5:00 PM', 'Sunday: 8:00 AM, 10:30 AM, 12:30 PM (Spanish)', 'Weekdays: Mon–Fri 7:00 am',
              'Lunes a Viernes: 19:00', 'Domingos: 9:00, 11:00 y 20:00', 'Domingo – 08h00 e 19h00', 'Saturday 3:30 – 4:30 pm',
              'Sat 3 - 4 pm', 'Sunday Latin Mass 12 noon', 'Tues-Thurs 8:15am', 'Call 555-123-4567 Sunday 9am']:
        print(s, '->', slots([s], 0))
