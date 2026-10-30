"""Readable names for churches whose names are written only in a non-Latin script (Korean, Japanese, Chinese,
Cyrillic, Thai, Arabic, Greek...), so a visitor reading another language can still read them.

    python3 scripts/names/build.py            (run from the repo root after scripts/build_data.py)

Writes data/names-x.json: {church index: [script, kind, text]}
  script  the script the original name is written in (ko, cjk, cyr, ar, th, el, ...): the page shows the
          original name to visitors whose language uses that script, and this one to everyone else
  kind    c church, k cathedral, s shrine, or '' for a full name: c, k and s are wrapped in the page language
          ("{x} Catholic Church", "Catedral de {x}"), or stand alone when text is empty; '' shows text as it is
  text    the place or saint the church is named for (c, k), or the whole name ('')
  town    (when there is one) the town, romanized, for towns written in Korean, Japanese or Chinese

Sources, in order: translated.tsv (names translated by hand), the Latin part of a name that also carries one
("성 김대건 안드레아 성당 / Riverside"), then rules: Korean names are romanized (Revised Romanization), Japanese
names read with pykakasi, Chinese names in pinyin with pypinyin (pip install pykakasi pypinyin).
"""
import json, os, re, unicodedata
from collections import Counter
from pykakasi import kakasi
from pypinyin import lazy_pinyin

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
HERE = os.path.dirname(os.path.abspath(__file__))

SCRIPT = {'HANGUL': 'ko', 'CJK': 'cjk', 'HIRAGANA': 'cjk', 'KATAKANA': 'cjk', 'KATAKANA-HIRAGANA': 'cjk', 'HALFWIDTH': 'cjk',
          'CYRILLIC': 'cyr', 'ARABIC': 'ar', 'THAI': 'th', 'GREEK': 'el', 'TAMIL': 'ta', 'MALAYALAM': 'ml', 'DEVANAGARI': 'deva',
          'HEBREW': 'he', 'GEORGIAN': 'ka', 'ARMENIAN': 'hy', 'ETHIOPIC': 'et', 'LAO': 'lo', 'KHMER': 'km', 'SINHALA': 'si', 'BENGALI': 'bn'}

def script_of(name):
    c = Counter()
    for ch in name:
        if ch.isalpha():
            w = unicodedata.name(ch, '?').split()[0]
            if w not in ('LATIN', 'MATHEMATICAL', 'DOUBLE-STRUCK', 'MODIFIER', 'FULLWIDTH'): c[SCRIPT.get(w, 'x')] += 1
    return c.most_common(1)[0][0] if c else None

# ---------- Korean: Revised Romanization ----------
CHO = ['g', 'kk', 'n', 'd', 'tt', 'r', 'm', 'b', 'pp', 's', 'ss', '', 'j', 'jj', 'ch', 'k', 't', 'p', 'h']
JUNG = ['a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae', 'oe', 'yo', 'u', 'wo', 'we', 'wi', 'yu', 'eu', 'ui', 'i']
JONG = ['', 'k', 'k', 'k', 'n', 'n', 'n', 't', 'l', 'k', 'm', 'l', 'l', 'l', 'p', 'l', 'm', 'p', 'p', 't', 't', 'ng', 't', 't', 'k', 't', 'p', 't']
# a final consonant carried over to a following silent ㅇ
JONG_LINK = ['', 'g', 'kk', 'ks', 'n', 'nj', 'nh', 'd', 'r', 'lg', 'lm', 'lb', 'ls', 'lt', 'lp', 'lh', 'm', 'b', 'ps', 's', 'ss', 'ng', 'j', 'ch', 'k', 't', 'p', 'h']

def romanize_ko(word):
    syl = [ord(c) - 0xAC00 for c in word]
    out = []
    for k, s in enumerate(syl):
        if not 0 <= s < 11172: out.append(word[k]); continue
        cho, jung, jong = s // 588, (s % 588) // 28, s % 28
        nxt = syl[k + 1] // 588 if k + 1 < len(syl) and 0 <= syl[k + 1] < 11172 else None
        prev = syl[k - 1] if k and 0 <= syl[k - 1] < 11172 else None
        c = CHO[cho]
        if prev is not None and prev % 28 and cho == 11: c = ''  # handled by the carried-over final
        if prev is not None and prev % 28 == 8 and cho == 5: c = 'l'  # ㄹㄹ is ll
        if k == 0 and cho == 5: c = 'r'
        f = JONG[jong]
        if jong and nxt == 11: f = JONG_LINK[jong]
        elif jong == 8 and nxt == 5: f = 'l'
        out.append(c + JUNG[jung] + f)
    return ''.join(out)

# common Korean saints and titles, so "성요셉성당" reads "St. Joseph" and not "Seongyosep"
KO_WORDS = [
    ('성 김대건 안드레아', 'St. Andrew Kim Taegon'), ('김대건 안드레아', 'St. Andrew Kim Taegon'), ('김대건', 'St. Andrew Kim Taegon'),
    ('한국 순교자', 'Korean Martyrs'), ('한국순교자', 'Korean Martyrs'), ('순교자', 'Martyrs'), ('예수성심', 'Sacred Heart of Jesus'),
    ('성모성심', 'Immaculate Heart of Mary'), ('무염시태', 'Immaculate Conception'), ('원죄없으신', 'Immaculate'), ('성모승천', 'Assumption'),
    ('성모마리아', 'Holy Mary'), ('성모 마리아', 'Holy Mary'), ('삼위일체', 'Holy Trinity'), ('성가정', 'Holy Family'),
    ('성령', 'Holy Spirit'), ('성심', 'Sacred Heart'), ('성체', 'Blessed Sacrament'), ('성모', 'Our Lady'), ('그리스도왕', 'Christ the King'),
    ('평화의모후', 'Queen of Peace'), ('순교', 'Martyrs'), ('한인', 'Korean'), ('한국', 'Korea'), ('평화의 모후', 'Queen of Peace'),
]
KO_SAINTS = {'요한바오로2세': 'John Paul II', '요한 바오로 2세': 'John Paul II', '요한': 'John', '바오로': 'Paul', '베드로': 'Peter', '마태오': 'Matthew',
             '마르코': 'Mark', '루카': 'Luke', '요셉': 'Joseph', '안드레아': 'Andrew', '야고보': 'James', '토마스': 'Thomas', '필립보': 'Philip',
             '프란치스코': 'Francis', '미카엘': 'Michael', '가브리엘': 'Gabriel', '라파엘': 'Raphael', '이시돌': 'Isidore', '스테파노': 'Stephen',
             '안토니오': 'Anthony', '아우구스티노': 'Augustine', '베네딕토': 'Benedict', '도미니코': 'Dominic', '데레사': 'Teresa', '모니카': 'Monica',
             '바르나바': 'Barnabas', '시몬': 'Simon', '가롤로': 'Charles', '마리아': 'Mary', '안나': 'Anne', '루치아': 'Lucy', '세실리아': 'Cecilia',
             '클라라': 'Clare', '대건 안드레아': 'Andrew Kim Taegon', '정하상 바오로': 'Paul Chong Hasang', '정하상바오로': 'Paul Chong Hasang'}
ADMIN = ('동', '리', '읍', '면', '가', '로', '구', '군', '시')

def ko_word(w):
    for k, v in KO_WORDS:
        if w == k: return v
    m = re.fullmatch(r'(.*?)성\s?(.+)', w)  # 성요셉 = St. Joseph, 위례성데레사 = Wirye St. Teresa
    if m and m.group(2) in KO_SAINTS: return ((ko_word(m.group(1)) + ' ') if m.group(1) else '') + 'St. ' + KO_SAINTS[m.group(2)]
    if w in KO_SAINTS: return 'St. ' + KO_SAINTS[w]
    for k, v in KO_WORDS:
        if w.endswith(k) and len(w) > len(k): return ko_word(w[:-len(k)]) + ' ' + v
    m = re.fullmatch(r'(.+?)(\d*)(동|리|읍|면|가)', w)
    if m and re.fullmatch('[가-힣]+', m.group(1)):
        return romanize_ko(m.group(1)).capitalize() + m.group(2) + '-' + romanize_ko(m.group(3))
    return romanize_ko(w).capitalize()

def ko_place(s):
    s = s.strip()
    for k, v in KO_SAINTS.items():
        if ' ' in k and k in s: s = s.replace(k, k.replace(' ', ''))
    if s.replace(' ', '') in KO_SAINTS or any(s == k for k, _ in KO_WORDS): return ko_word(s.replace(' ', '') if s.replace(' ', '') in KO_SAINTS else s)
    return ' '.join(ko_word(w) for w in s.split())

def korean(name):
    s = re.sub(r'^\s*(천주교|가톨릭|카톨릭)\s*', '', name)
    s = re.sub(r'\S*(대교구|교구)\s+', '', s)  # "제주교구 중앙성당": the diocese goes
    m = re.fullmatch(r'(.+?)\s*(주교좌\s*(?:대)?성당|대성당)', s)
    if m: return 'k', ko_place(m.group(1))
    m = re.fullmatch(r'(.+?)\s*(?:순교\s?성지|성지)', s)
    if m: return 's', ko_place(m.group(1))
    m = re.fullmatch(r'(.*?)\s*(?:성당|천주교회|교회|본당)', s)
    if m: return 'c', ko_place(m.group(1))
    return '', ' '.join(romanize_ko(w).capitalize() for w in name.split())

# ---------- Japanese ----------
kks = kakasi()

def ja_read(s):
    r = ' '.join(w['hepburn'].capitalize() for w in kks.convert(s) if w['hepburn'].strip())
    return re.sub(r'(?<=[A-Za-z])ou|(?<=[A-Za-z])o(?=o)', 'o', r).replace('uu', 'u').replace('Oo', 'O')

def japanese(name):
    s = unicodedata.normalize('NFKC', name)
    s = re.sub(r'^(日本)?(カトリック|ｶﾄﾘｯｸ|天主公教)\s*', '', s).strip()
    s = re.sub(r'(カトリック|天主公教)', '', s).strip()
    m = re.fullmatch(r'(.+?)\s*(?:司教座聖堂|大聖堂|カテドラル)', s)
    if m: return 'k', ja_read(m.group(1))
    m = re.fullmatch(r'(.*?)\s*(?:教会|聖堂|天主堂)', s)
    if m: return 'c', ja_read(m.group(1))
    return '', ja_read(s)

# ---------- Chinese ----------
ZH_WORDS = [('聖母無原罪', 'Immaculate Conception'), ('無原罪聖母', 'Immaculate Conception'), ('耶穌聖心', 'Sacred Heart of Jesus'),
            ('聖母聖心', 'Immaculate Heart of Mary'), ('中華聖母', 'Our Lady of China'), ('玫瑰聖母', 'Our Lady of the Rosary'),
            ('露德聖母', 'Our Lady of Lourdes'), ('法蒂瑪聖母', 'Our Lady of Fatima'), ('花地瑪聖母', 'Our Lady of Fatima'),
            ('聖母升天', 'Assumption'), ('聖母聖衣', 'Our Lady of Mount Carmel'), ('聖家', 'Holy Family'), ('聖神', 'Holy Spirit'),
            ('聖心', 'Sacred Heart'), ('聖母', 'Our Lady'), ('若瑟', 'St. Joseph'), ('伯多祿', 'St. Peter'), ('保祿', 'St. Paul'),
            ('方濟各', 'St. Francis'), ('德蘭', 'St. Teresa'), ('彌額爾', 'St. Michael'), ('安多尼', 'St. Anthony'), ('聖若望', 'St. John'),
            ('基督君王', 'Christ the King'), ('耶穌君王', 'Christ the King'), ('聖體', 'Blessed Sacrament'), ('文生', 'St. Vincent'),
            ('聖安', 'St. Anne'), ('聖本篤', 'St. Benedict'), ('聖雅各伯', 'St. James'), ('聖瑪爾定', 'St. Martin'), ('耶穌', 'Jesus'), ('天主', ''), ('聖', '')]
ZH_TRAD = str.maketrans('圣会门稣罗马达贞亚纳尔约汉东华区堂', '聖會門穌羅馬達貞亞納爾約漢東華區堂')

def zh_read(s):
    out = []
    while s:
        for k, v in ZH_WORDS:
            if s.startswith(k):
                if v: out.append(v)
                s = s[len(k):]; break
        else:
            j = 1
            while j < len(s) and not any(s[j:].startswith(k) for k, _ in ZH_WORDS): j += 1
            # place names: counties and townships split off, the rest read two characters a word
            for seg in re.findall(r'[^縣鄉市區鎮村]+[縣鄉市區鎮村]?', s[:j]):
                core = seg.rstrip('縣鄉市區鎮村')
                for a in range(0, len(core), 2):
                    py = ''.join(lazy_pinyin(core[a:a + 2])).strip()
                    if py: out.append(py.capitalize())
            s = s[j:]
    return ' '.join(out).strip()

def chinese(name):
    s = unicodedata.normalize('NFKC', name).translate(ZH_TRAD).strip()
    s = re.sub(r'^天主教\S*?教區\s*', '', s)
    s = re.sub(r'^天主教\s*', '', s)
    m = re.fullmatch(r'(.*?)\s*(?:主教座堂|座堂|大教堂)', s)
    if m: return 'k', zh_read(m.group(1))
    m = re.fullmatch(r'(.*?)\s*(?:天主堂|天主教堂|天主教會|天主教|教堂|聖堂|堂|教會)', s)
    if m: return 'c', zh_read(m.group(1))
    return '', zh_read(s)

LATIN_WORD = re.compile(r"[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ'’.]+")

def latin_part(name):
    """The Latin-script part of a name written in two scripts, or None."""
    parts = [p.strip(' -–—|/,:;()·.') for p in re.split(r'[^\sA-Za-zÀ-ɏ0-9\'’.,&()-]+', name)]
    parts = [p for p in parts if len(LATIN_WORD.findall(p)) >= 2 or (len(LATIN_WORD.findall(p)) == 1 and len(p) >= 6)]
    if not parts: return None
    best = max(parts, key=len)
    return best if len(LATIN_WORD.findall(best)) >= 2 or len(name) < 30 else None

def town_reading(town, cc):
    """(original, romanized) for a town written in Korean, Japanese or Chinese, else None."""
    town = (town or '').strip(); sc = script_of(town)
    if sc == 'ko': return town, ' '.join(ko_word(w) for w in town.split())
    if sc == 'cjk' and (cc == 'JP' or re.search('[\u3040-\u30ff]', town)): return town, ja_read(re.sub(r'[市区町村郡]$', '', town))
    if sc == 'cjk': return town, zh_read(re.sub(r'[市縣县區区鎮镇鄉乡]$', '', unicodedata.normalize('NFKC', town).translate(ZH_TRAD)))
    return None

def main():
    hand = {}
    for line in open(os.path.join(HERE, 'translated.tsv'), encoding='utf-8'):
        if line.startswith('#') or not line.strip(): continue
        o, e = line.rstrip('\n').split('\t'); hand[o] = e
    meta = json.load(open(os.path.join(ROOT, 'data', 'meta.json')))
    out, how, towns = {}, Counter(), {}
    for sh in range(meta['shards']):
        for k, r in enumerate(json.load(open(os.path.join(ROOT, 'data', 'd', f'{sh}.json'), encoding='utf-8'))):
            name = (r[0] or '').strip()
            sc = script_of(name)
            i = sh * meta['shardSize'] + k
            town = town_reading(r[2], r[5])
            if town: towns[i] = town
            if not sc: continue
            if name in hand: out[i] = [sc, '', hand[name]]; how['hand'] += 1; continue
            lp = latin_part(name)
            if lp: out[i] = [sc, '', lp]; how['latin'] += 1; continue
            if sc == 'ko': kind, text = korean(name)
            elif sc == 'cjk' and (r[5] == 'JP' or re.search('[぀-ヿｦ-ﾟ]', name)): kind, text = japanese(name)
            elif sc == 'cjk': kind, text = chinese(name)
            else: how['missing ' + sc] += 1; print('no reading:', i, r[5], name); continue
            text = re.sub(r'\s+', ' ', text).strip()
            if not text and not kind: how['empty'] += 1; continue
            out[i] = [sc, kind, text]; how[sc + (':' + kind if kind else '')] += 1
    for i, t in towns.items():  # the town, read the same way, rides along as a fourth item
        out[i] = (out.get(i) or [script_of(t[0]), '', ''])[:3] + [t[1]]
    how['towns'] = len(towns)
    with open(os.path.join(ROOT, 'data', 'names-x.json'), 'w', encoding='utf-8') as f:
        f.write('{' + ',\n'.join(f'"{i}":{json.dumps(v, ensure_ascii=False)}' for i, v in sorted(out.items())) + '}\n')
    print(len(out), dict(how))

if __name__ == '__main__':
    main()
