"""Check every i18n/<lang>.json against the English table in index.html: missing or unknown keys, placeholders, and plural keys that lack an _other form.

usage: python3 scripts/i18n/check.py
"""
import json, os, re, subprocess, sys

root = os.path.join(os.path.dirname(__file__), '..', '..')
html = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
src = html[html.index('const EN = {'):]
src = src[:src.index('\n};') + 3]
en = json.loads(subprocess.run(['node', '-e', src + '\nprocess.stdout.write(JSON.stringify(EN))'], capture_output=True, text=True, check=True).stdout)
base = lambda k: re.sub(r'_(zero|one|two|few|many|other)$', '', k)
ph = lambda s: sorted(set(re.findall(r'\{(\w+)\}', s)))
groups = {}
for k in en: groups.setdefault(base(k), []).append(k)
bad = 0
for f in sorted(os.listdir(os.path.join(root, 'i18n'))):
    if not f.endswith('.json'): continue
    d = json.load(open(os.path.join(root, 'i18n', f), encoding='utf-8'))
    have = {base(k) for k in d}
    missing = [g for g in groups if g not in have]
    unknown = [k for k in d if base(k) not in groups]
    wrong = [k for k in d if base(k) in groups and ph(d[k]) and not set(ph(d[k])) <= set(ph(en[groups[base(k)][-1]]) + ['n', 'roman', 'ord', 'y'])]
    plural = [g for g in groups if g in have and any(k != g for k in groups[g]) and g + '_other' not in d]
    lost = [k for k in d if base(k) in groups and set(ph(en[groups[base(k)][-1]])) - set(ph(d[k])) - {'n', 'ord', 'roman'}]
    if missing or unknown or wrong or lost or plural:
        bad += 1
        print(f, 'missing', missing, 'unknown', unknown, 'bad placeholders', wrong, 'dropped placeholders', lost, 'plural without _other', plural)
# every curated saint bio, translated: i18n/saints/<lang>.json holds [name, feast, bio] for each English title
bsrc = html[html.index('const BIOS = {'):]
bsrc = bsrc[:bsrc.index('\n};') + 3]
bios = json.loads(subprocess.run(['node', '-e', bsrc + '\nprocess.stdout.write(JSON.stringify(BIOS))'], capture_output=True, text=True, check=True).stdout)
sdir = os.path.join(root, 'i18n', 'saints')
for f in sorted(os.listdir(sdir)):
    d = json.load(open(os.path.join(sdir, f), encoding='utf-8'))
    missing = [k for k in bios if k not in d]
    unknown = [k for k in d if k not in bios]
    shape = [k for k, v in d.items() if not (isinstance(v, list) and len(v) == 3 and all(v))]
    if missing or unknown or shape:
        bad += 1
        print('saints/' + f, 'missing', missing, 'unknown', unknown, 'not [name, feast, bio]', shape)
print('checked', len(bios), 'saint bios')
print('checked', len(groups), 'keys;', 'problems in', bad, 'files' if bad != 1 else 'file')
sys.exit(1 if bad else 0)
