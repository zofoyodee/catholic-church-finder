"""Watercolor painting kit for the Life of Jesus moments.

Every picture is built from the same figures, so Our Lord looks the same in each one: shoulder-length brown hair and beard,
a cream tunic, a crimson mantle over His left shoulder and a gold halo marked with the cross. Our Lady always wears a blue
mantle over her head and a rose dress, Saint Joseph an olive tunic and ochre mantle, Saint Peter grey hair and a blue tunic.

A scene is SVG drawn on a 600 x 750 sheet. The watercolor look comes from SVG filters (wobbled edges, pigment granulation,
darker rims where the wash dries) and multiply blending, so layers deepen where they overlap like real washes.
"""
import math, random

W, H = 600, 750
PAPER = '#f4ecda'
INK = '#4a3b2e'

# the people who appear more than once; every scene draws them from here
JESUS = dict(tunic='#f1e6cf', mantle='#a52a2a', skin='#d9a77f', hair='#5b3a22', beard=True, halo='cross', hairlen='long', face='jesus')
CHILD = dict(tunic='#f1e6cf', mantle='#a52a2a', skin='#e2b48c', hair='#5b3a22', beard=False, halo='cross', hairlen='short', face='jesus')
MARY = dict(tunic='#c97b7b', mantle='#2f5b9a', skin='#e0b08a', hair='#4a2f1d', beard=False, halo='gold', hairlen='veil')
JOSEPH = dict(tunic='#6f7a45', mantle='#c08a3e', skin='#c9966d', hair='#6b6158', beard=True, halo='gold', hairlen='short')
PETER = dict(tunic='#4f6f8f', mantle='#c79a4a', skin='#c9926a', hair='#9a958c', beard=True, halo='faint', hairlen='short')
JOHN = dict(tunic='#c4553f', mantle='#5f8a4e', skin='#dcae86', hair='#7a4b2a', beard=False, halo='faint', hairlen='short')
MAGDALENE = dict(tunic='#8c3b5a', mantle='#b8434a', skin='#deae88', hair='#8a4a24', beard=False, halo='faint', hairlen='veil', veil='#c95b5b')
JOHN_BAPTIST = dict(tunic='#8a6a3e', mantle='#6b4f2a', skin='#b9845a', hair='#3e2a1a', beard=True, halo='gold', hairlen='long')
ANGEL = dict(tunic='#f6f1e4', mantle='#e9d9a6', skin='#e4b994', hair='#c99a4e', beard=False, halo='gold', hairlen='short')


def apostle(i):
    """The other apostles and disciples: a fixed palette each, so a crowd of followers stays recognisable."""
    tun = ['#6d8a5a', '#9a6b4a', '#7d6a9a', '#b2804a', '#5e7f86', '#8f5a4a', '#a39a6a', '#6a6f8f']
    man = ['#c8a25e', '#5d6f8f', '#b58a5a', '#6b8a6b', '#c27a4a', '#8d9a6a', '#7a5a7a', '#b8a07a']
    hair = ['#4a3220', '#6b5440', '#2e2219', '#8a8278', '#5a3a26', '#3a2a1e', '#7a6a5a', '#4e3a2a']
    skin = ['#c9966d', '#d4a27a', '#b98a62', '#cf9e74']
    return dict(tunic=tun[i % 8], mantle=man[(i * 3) % 8], skin=skin[i % 4], hair=hair[(i * 5) % 8], beard=i % 3 != 2, halo='faint', hairlen='short')


def folk(i, woman=None):
    """Ordinary people in the crowds."""
    woman = (i % 3 == 1) if woman is None else woman
    tun = ['#a8876a', '#8a9a7a', '#b89a7a', '#7a8a9a', '#a87a6a', '#9a8a5a', '#c2a27a', '#6f7f6a']
    man = ['#d1b68a', '#7a6a5a', '#9aa08a', '#c9a07a', '#8a7a9a', '#b8a58a', '#6a7a8a', '#a8906a']
    skin = ['#c9966d', '#d8a982', '#b0805a', '#d0a07a', '#a87650']
    hair = ['#3a2a1e', '#5a4030', '#2a1e16', '#7a7068', '#4a3424']
    d = dict(tunic=tun[i % 8], mantle=man[(i * 3 + 1) % 8], skin=skin[i % 5], hair=hair[(i * 2) % 5], beard=not woman and i % 2 == 0, halo=None, hairlen='veil' if woman else 'short')
    if woman: d['veil'] = man[(i * 5 + 2) % 8]
    return d


SOLDIER = dict(tunic='#9a3a2a', mantle='#7a5a3a', skin='#c08a62', hair='#3a2a1e', beard=False, halo=None, hairlen='helmet')
PRIEST = dict(tunic='#e6dcc4', mantle='#5a5a8a', skin='#c9966d', hair='#8a8278', beard=True, halo=None, hairlen='turban', veil='#e8e0cc')
PHARISEE = dict(tunic='#5a4a6a', mantle='#2f3f5a', skin='#c08a62', hair='#4a4038', beard=True, halo=None, hairlen='turban', veil='#7a6a8a')


class Scene:
    def __init__(self, seed):
        self.seed = seed
        self.r = random.Random(seed)
        self.parts = []

    def add(self, s):
        self.parts.append(s)
        return self

    def svg(self):
        s = self.seed
        defs = f'''<defs>
<filter id="w" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="3" seed="{s}" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
 <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="{s + 7}" result="g"/>
 <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="2" seed="{s + 3}" result="lo"/>
 <feComposite in="g" in2="lo" operator="arithmetic" k2="0.5" k3="0.6" result="gl"/>
 <feColorMatrix in="gl" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.9 0 0 0 0.22" result="ga"/>
 <feComposite in="d" in2="ga" operator="in" result="body"/>
 <feMorphology in="d" operator="erode" radius="1.6" result="er"/>
 <feComposite in="d" in2="er" operator="out" result="rim"/>
 <feGaussianBlur in="rim" stdDeviation="0.7" result="rimb"/>
 <feComponentTransfer in="rimb" result="rimd"><feFuncR type="linear" slope="0.72"/><feFuncG type="linear" slope="0.68"/><feFuncB type="linear" slope="0.66"/><feFuncA type="linear" slope="0.75"/></feComponentTransfer>
 <feMerge><feMergeNode in="body"/><feMergeNode in="rimd"/></feMerge>
</filter>
<filter id="wf" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="{s}" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G" result="d"/>
 <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="{s + 7}" result="g"/>
 <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.35 0 0 0 0.78" result="ga"/>
 <feComposite in="d" in2="ga" operator="in" result="body"/>
 <feMorphology in="d" operator="erode" radius="1.1" result="er"/>
 <feComposite in="d" in2="er" operator="out" result="rim"/>
 <feComponentTransfer in="rim" result="rimd"><feFuncR type="linear" slope="0.6"/><feFuncG type="linear" slope="0.56"/><feFuncB type="linear" slope="0.54"/><feFuncA type="linear" slope="0.8"/></feComponentTransfer>
 <feMerge><feMergeNode in="body"/><feMergeNode in="rimd"/></feMerge>
</filter>
<filter id="wash" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="{s + 11}" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="40" xChannelSelector="R" yChannelSelector="G" result="d"/>
 <feGaussianBlur in="d" stdDeviation="5" result="b"/>
 <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="{s + 5}" result="lo"/>
 <feColorMatrix in="lo" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0 0 0 0.62" result="la"/>
 <feComposite in="b" in2="la" operator="in"/>
</filter>
<filter id="line" x="-5%" y="-5%" width="110%" height="110%">
 <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="{s + 2}" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="2.5" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="paper" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="4" result="t"/>
 <feColorMatrix in="t" type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.28  0 0 0 -1.4 0.95"/>
 <feComposite in2="SourceGraphic" operator="in"/>
</filter>
<filter id="edge" x="-5%" y="-5%" width="110%" height="110%">
 <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="4" seed="{s + 9}" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="34" xChannelSelector="R" yChannelSelector="G" result="d"/>
 <feGaussianBlur in="d" stdDeviation="1.2"/>
</filter>
<mask id="sheet"><rect x="26" y="26" width="{W - 52}" height="{H - 52}" rx="10" fill="#fff" filter="url(#edge)"/></mask>
</defs>'''
        body = '\n'.join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}'
                f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
                f'<g mask="url(#sheet)">{body}</g>'
                f'<rect width="{W}" height="{H}" fill="{PAPER}" filter="url(#paper)" opacity=".55" style="mix-blend-mode:multiply"/></svg>')


def g(inner, f='w', op=0.92, blend=True, extra=''):
    st = ' style="mix-blend-mode:multiply"' if blend else ''
    flt = f' filter="url(#{f})"' if f else ''
    return f'<g{flt} opacity="{op}"{st}{extra}>{inner}</g>'


def P(d, fill, op=None, stroke=None, sw=None, extra=''):
    o = f' opacity="{op}"' if op is not None else ''
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else ''
    return f'<path d="{d}" fill="{fill}"{o}{s}{extra}/>'


def line(d, color=INK, sw=1.2, op=0.55):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'


# ---------- skies and land ----------

def sky(sc, top, bottom, mid=None, y1=H):
    stops = f'<stop offset="0" stop-color="{top}"/>' + (f'<stop offset=".55" stop-color="{mid}"/>' if mid else '') + f'<stop offset="1" stop-color="{bottom}"/>'
    gid = f'sk{len(sc.parts)}'
    sc.add(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient></defs>')
    sc.add(g(f'<rect x="-40" y="-40" width="{W + 80}" height="{y1 + 40}" fill="url(#{gid})"/>', 'wash', 0.9))


def clouds(sc, n, y0, y1, color='#ffffff', op=0.5, size=1.0):
    r = sc.r
    out = []
    for _ in range(n):
        x, y, s = r.uniform(-40, W + 40), r.uniform(y0, y1), r.uniform(40, 110) * size
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{s:.0f}" ry="{s * 0.32:.0f}" fill="{color}"/>')
    sc.add(g(''.join(out), 'wash', op, blend=False))


def ridge(sc, y, amp, color, op=0.85, n=7, bottom=H + 40, rough=1.0, f='w'):
    r = sc.r
    pts = [(-40, y + r.uniform(-amp, amp))]
    for i in range(1, n + 1):
        pts.append((-40 + (W + 80) * i / n, y + r.uniform(-amp, amp) * rough))
    d = f'M -40 {bottom} L {pts[0][0]:.0f} {pts[0][1]:.0f}'
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx = (x0 + x1) / 2
        d += f' C {mx:.0f} {y0:.0f} {mx:.0f} {y1:.0f} {x1:.0f} {y1:.0f}'
    d += f' L {W + 40} {bottom} Z'
    sc.add(g(P(d, color), f, op))


def hill(sc, cx, top, w, color, op=0.85, base=H + 40):
    d = f'M {cx - w} {base} C {cx - w * .5} {base - (base - top) * .4} {cx - w * .35} {top} {cx} {top} C {cx + w * .35} {top} {cx + w * .5} {base - (base - top) * .4} {cx + w} {base} Z'
    sc.add(g(P(d, color), 'w', op))


def ground(sc, y, color, op=0.8):
    ridge(sc, y, 6, color, op, n=4)


def water(sc, y, color='#5b8db8', op=0.75, waves=12, wave_color='#2f5f8a', y1=H + 40):
    sc.add(g(f'<rect x="-40" y="{y}" width="{W + 80}" height="{y1 - y}" fill="{color}"/>', 'wash', op))
    r = sc.r
    ls = []
    for _ in range(waves):
        x, yy, w = r.uniform(0, W), r.uniform(y + 10, min(y1, H) - 10), r.uniform(30, 80)
        ls.append(line(f'M {x - w:.0f} {yy:.0f} q {w / 2:.0f} -6 {w:.0f} 0 t {w:.0f} 0', wave_color, 2, 0.45))
    sc.add(g(''.join(ls), 'line', 1, blend=True))


def sun(sc, x, y, r, color='#f7d77a', glow='#fbe9a8'):
    sc.add(g(f'<circle cx="{x}" cy="{y}" r="{r * 2.6}" fill="{glow}"/>', 'glow', 0.7, blend=False))
    sc.add(g(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>', 'w', 0.9))


def moon(sc, x, y, r=18):
    sc.add(g(f'<circle cx="{x}" cy="{y}" r="{r * 2.2}" fill="#f2ecd2"/>', 'glow', 0.35, blend=False))
    sc.add(g(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f6efd6"/><circle cx="{x + r * .3}" cy="{y + r * .1}" r="{r * .2}" fill="#d8d0b4" opacity=".7"/>', 'w', 0.95, blend=False))


def stars(sc, n, y1=300, color='#fbf3d2'):
    r = sc.r
    sc.add(''.join(f'<circle cx="{r.uniform(30, W - 30):.0f}" cy="{r.uniform(30, y1):.0f}" r="{r.uniform(.8, 2.2):.1f}" fill="{color}" opacity="{r.uniform(.5, .95):.2f}"/>' for _ in range(n)))


def star_of_bethlehem(sc, x, y, s=1.0):
    sc.add(g(f'<circle cx="{x}" cy="{y}" r="{40 * s}" fill="#fff3c4"/>', 'glow', 0.8, blend=False))
    a = 34 * s
    d = f'M {x} {y - a} L {x + 5 * s} {y - 5 * s} L {x + a * .8} {y} L {x + 5 * s} {y + 5 * s} L {x} {y + a * 1.6} L {x - 5 * s} {y + 5 * s} L {x - a * .8} {y} L {x - 5 * s} {y - 5 * s} Z'
    sc.add(g(P(d, '#fff6d0'), 'w', 1, blend=False))


def rays(sc, x, y, n=14, length=700, color='#fff3c4', op=0.35, spread=360, start=0, width=7):
    out = []
    for i in range(n):
        a = math.radians(start + spread * (i + .5) / n)
        x1, y1 = x + math.cos(a) * length, y + math.sin(a) * length
        px, py = -math.sin(a) * width * 3, math.cos(a) * width * 3
        out.append(f'<path d="M {x} {y} L {x1 + px:.0f} {y1 + py:.0f} L {x1 - px:.0f} {y1 - py:.0f} Z" fill="{color}"/>')
    sc.add(g(''.join(out), 'wash', op, blend=False))


def light(sc, x, y, r, color='#fff6d8', op=0.75):
    sc.add(g(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>', 'glow', op, blend=False))


# ---------- buildings and things ----------

def town(sc, y, x0=0, x1=W, color='#d8c3a0', roof='#b89a72', op=0.7, n=9, hmax=70, dome=0):
    r = sc.r
    out = []
    x = x0
    while x < x1:
        w, h = r.uniform(34, 70), r.uniform(28, hmax)
        out.append(f'<rect x="{x:.0f}" y="{y - h:.0f}" width="{w:.0f}" height="{h + 30:.0f}" fill="{color}"/>')
        out.append(f'<rect x="{x - 2:.0f}" y="{y - h - 5:.0f}" width="{w + 4:.0f}" height="7" fill="{roof}"/>')
        if r.random() < .6:
            out.append(f'<rect x="{x + w * .35:.0f}" y="{y - h * .6:.0f}" width="{w * .18:.0f}" height="{h * .25:.0f}" fill="#7a6248" opacity=".6"/>')
        x += w + r.uniform(-6, 8)
    for _ in range(dome):
        cx, w = r.uniform(x0 + 40, x1 - 40), r.uniform(26, 40)
        out.append(f'<rect x="{cx - w * .7:.0f}" y="{y - hmax - 10:.0f}" width="{w * 1.4:.0f}" height="{hmax + 40}" fill="{color}"/><path d="M {cx - w * .7:.0f} {y - hmax - 10:.0f} A {w * .7:.0f} {w * .75:.0f} 0 0 1 {cx + w * .7:.0f} {y - hmax - 10:.0f} Z" fill="{roof}"/>')
    sc.add(g(''.join(out), 'w', op))


def walls(sc, y, h=60, color='#d6c09a', op=0.75, x0=-20, x1=W + 20, tower_every=140):
    out = [f'<rect x="{x0}" y="{y - h}" width="{x1 - x0}" height="{h + 60}" fill="{color}"/>']
    x = x0
    while x < x1:
        out.append(f'<rect x="{x}" y="{y - h - 10}" width="14" height="12" fill="{color}"/>')
        x += 26
    x = x0 + 40
    while x < x1:
        out.append(f'<rect x="{x}" y="{y - h - 40}" width="44" height="{h + 40}" fill="{color}"/><rect x="{x}" y="{y - h - 40}" width="44" height="{h + 40}" fill="#8a6a48" opacity=".12"/>')
        x += tower_every
    sc.add(g(''.join(out), 'w', op))


def temple(sc, x, y, w=340, h=200, color='#e6d6b2', op=0.8, gold=True):
    """Herod's Temple: a tall white and gold facade on its platform."""
    out = [f'<rect x="{x - w / 2}" y="{y - h}" width="{w}" height="{h}" fill="{color}"/>',
           f'<rect x="{x - w * .22}" y="{y - h * 1.35}" width="{w * .44}" height="{h * .4}" fill="{color}"/>',
           f'<rect x="{x - w * .1}" y="{y - h * .75}" width="{w * .2}" height="{h * .75}" fill="#8a6a3a" opacity=".55"/>']
    if gold:
        out.append(f'<rect x="{x - w * .22}" y="{y - h * 1.36}" width="{w * .44}" height="8" fill="#d4a63a"/><rect x="{x - w / 2}" y="{y - h - 4}" width="{w}" height="7" fill="#d4a63a"/>')
    for i in range(7):
        cx = x - w / 2 + 18 + i * (w - 36) / 6
        if abs(cx - x) < w * .12: continue
        out.append(f'<rect x="{cx - 5:.0f}" y="{y - h * .9:.0f}" width="10" height="{h * .9:.0f}" fill="#fff" opacity=".55"/>')
    out.append(f'<rect x="{x - w / 2 - 30}" y="{y}" width="{w + 60}" height="16" fill="#cdb894"/>')
    sc.add(g(''.join(out), 'w', op))


def colonnade(sc, y, x0=-20, x1=W + 20, h=280, color='#e8dcc0', shade='#b8a07a', op=0.75, gap=95, col=26):
    out = [f'<rect x="{x0}" y="{y - h - 34}" width="{x1 - x0}" height="40" fill="{color}"/>', f'<rect x="{x0}" y="{y - h - 8}" width="{x1 - x0}" height="10" fill="{shade}" opacity=".6"/>']
    x = x0 + 20
    while x < x1:
        out.append(f'<rect x="{x}" y="{y - h}" width="{col}" height="{h}" fill="{color}"/><rect x="{x + col * .6}" y="{y - h}" width="{col * .4}" height="{h}" fill="{shade}" opacity=".5"/><rect x="{x - 4}" y="{y - h - 4}" width="{col + 8}" height="10" fill="{shade}" opacity=".7"/>')
        x += gap
    out.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="200" fill="#d8c8a6"/>')
    sc.add(g(''.join(out), 'w', op))


def room(sc, wall='#e2d2b2', floor='#c8ad86', y=520, arch=True, window=None):
    sc.add(g(f'<rect x="-20" y="-20" width="{W + 40}" height="{y + 20}" fill="{wall}"/>', 'wash', 0.85))
    sc.add(g(f'<rect x="-20" y="{y}" width="{W + 40}" height="{H - y + 20}" fill="{floor}"/>', 'w', 0.8))
    if arch:
        sc.add(g(P(f'M 60 {y} L 60 220 A 240 240 0 0 1 540 220 L 540 {y} L 600 {y} L 600 -20 L 0 -20 L 0 {y} Z', '#b89c76', 0.55), 'w', 0.8))
    if window:
        x, wy, ww, wh, col = window
        sc.add(g(f'<path d="M {x - ww / 2} {wy + wh} L {x - ww / 2} {wy + ww / 2} A {ww / 2} {ww / 2} 0 0 1 {x + ww / 2} {wy + ww / 2} L {x + ww / 2} {wy + wh} Z" fill="{col}"/>', 'w', 0.9))


def palm(sc, x, y, h=200, color='#5d7a3e', trunk='#8a6a48', op=0.85):
    out = [P(f'M {x - 5} {y} C {x - 3} {y - h * .5} {x + 8} {y - h * .8} {x + 6} {y - h} L {x + 12} {y - h} C {x + 14} {y - h * .8} {x + 4} {y - h * .5} {x + 6} {y} Z', trunk)]
    tx, ty = x + 9, y - h
    for a in (-160, -125, -90, -55, -20, 15, 200):
        ra = math.radians(a)
        ex, ey = tx + math.cos(ra) * h * .45, ty + math.sin(ra) * h * .32 + h * .12
        mx, my = tx + math.cos(ra) * h * .25, ty + math.sin(ra) * h * .3 - 12
        out.append(P(f'M {tx} {ty} Q {mx:.0f} {my:.0f} {ex:.0f} {ey:.0f} Q {mx:.0f} {my + 14:.0f} {tx} {ty + 4} Z', color))
    sc.add(g(''.join(out), 'w', op))


def olive(sc, x, y, s=1.0, color='#7c8f5a', trunk='#6a5440', op=0.85):
    r = sc.r
    out = [P(f'M {x - 10 * s} {y} C {x - 14 * s} {y - 40 * s} {x + 6 * s} {y - 50 * s} {x - 4 * s} {y - 90 * s} L {x + 8 * s} {y - 90 * s} C {x + 16 * s} {y - 50 * s} {x + 2 * s} {y - 40 * s} {x + 14 * s} {y} Z', trunk)]
    for _ in range(9):
        out.append(f'<ellipse cx="{x + r.uniform(-60, 60) * s:.0f}" cy="{y + r.uniform(-150, -90) * s:.0f}" rx="{r.uniform(30, 50) * s:.0f}" ry="{r.uniform(18, 28) * s:.0f}" fill="{color}"/>')
    sc.add(g(''.join(out), 'w', op))


def tree(sc, x, y, s=1.0, color='#6f8a4a', trunk='#6a5038', op=0.85):
    """A broad sycamore-fig."""
    r = sc.r
    out = [P(f'M {x - 12 * s} {y} C {x - 10 * s} {y - 60 * s} {x - 30 * s} {y - 110 * s} {x - 40 * s} {y - 150 * s} L {x - 28 * s} {y - 152 * s} C {x - 10 * s} {y - 120 * s} {x} {y - 100 * s} {x + 4 * s} {y - 90 * s} C {x + 14 * s} {y - 120 * s} {x + 30 * s} {y - 140 * s} {x + 44 * s} {y - 160 * s} L {x + 54 * s} {y - 154 * s} C {x + 30 * s} {y - 120 * s} {x + 14 * s} {y - 70 * s} {x + 12 * s} {y} Z', trunk)]
    for _ in range(14):
        out.append(f'<ellipse cx="{x + r.uniform(-110, 120) * s:.0f}" cy="{y + r.uniform(-250, -150) * s:.0f}" rx="{r.uniform(36, 60) * s:.0f}" ry="{r.uniform(22, 34) * s:.0f}" fill="{color}"/>')
    sc.add(g(''.join(out), 'w', op))


def rocks(sc, y, n=5, color='#a8957a', op=0.8, x0=0, x1=W):
    r = sc.r
    out = []
    for _ in range(n):
        x, w, h = r.uniform(x0, x1), r.uniform(30, 90), r.uniform(18, 50)
        out.append(P(f'M {x - w / 2:.0f} {y} C {x - w / 2:.0f} {y - h:.0f} {x + w / 3:.0f} {y - h * 1.1:.0f} {x + w / 2:.0f} {y} Z', color))
    sc.add(g(''.join(out), 'w', op))


def boat(sc, x, y, w=300, color='#8a5a34', op=0.9, sail=False, mast=True):
    out = [P(f'M {x - w / 2} {y - 40} C {x - w * .42} {y + 10} {x + w * .42} {y + 10} {x + w / 2} {y - 46} L {x + w * .38} {y - 30} L {x - w * .38} {y - 26} Z', color),
           P(f'M {x - w / 2} {y - 40} L {x + w / 2} {y - 46} L {x + w / 2 - 6} {y - 36} L {x - w / 2 + 6} {y - 31} Z', '#5a3a22', .8)]
    if mast:
        out.append(f'<rect x="{x - 3}" y="{y - 250}" width="6" height="220" fill="#6a4a2a"/>')
    if sail:
        out.append(P(f'M {x + 6} {y - 240} C {x + 90} {y - 200} {x + 100} {y - 120} {x + 8} {y - 70} Z', '#e8dcc0'))
    sc.add(g(''.join(out), 'w', op))


def boat_front(sc, x, y, w=300, color='#8a5a34', op=0.92):
    """The near gunwale, drawn over the people standing in the boat."""
    sc.add(g(P(f'M {x - w / 2 - 10} {y - 66} C {x - w * .42} {y + 14} {x + w * .42} {y + 14} {x + w / 2 + 10} {y - 72} C {x + w * .3} {y - 52} {x - w * .3} {y - 50} {x - w / 2 - 10} {y - 66} Z', color)
             + line(f'M {x - w / 2 + 10} {y - 40} C {x - w * .3} {y - 24} {x + w * .3} {y - 26} {x + w / 2 - 10} {y - 46} M {x - w / 2 + 30} {y - 18} C {x - w * .3} {y - 4} {x + w * .3} {y - 6} {x + w / 2 - 30} {y - 22}', '#4a2a14', 2, .5), 'wf', op, blend=False))


def net(sc, x, y, w, h, color='#6a5a40'):
    ls = []
    for i in range(9):
        ls.append(line(f'M {x + w * i / 8:.0f} {y} Q {x + w * i / 8 + 10:.0f} {y + h / 2} {x + w * i / 8 - 6:.0f} {y + h}', color, 1.2, .6))
    for j in range(6):
        ls.append(line(f'M {x} {y + h * j / 5:.0f} Q {x + w / 2} {y + h * j / 5 + 12:.0f} {x + w} {y + h * j / 5:.0f}', color, 1.2, .6))
    sc.add(g(''.join(ls), 'line', 1))


def fish(x, y, s=1.0, color='#8a9aa8', flip=False):
    k = -1 if flip else 1
    return P(f'M {x - 14 * s * k} {y} C {x - 6 * s * k} {y - 7 * s} {x + 8 * s * k} {y - 7 * s} {x + 14 * s * k} {y} C {x + 8 * s * k} {y + 7 * s} {x - 6 * s * k} {y + 7 * s} {x - 14 * s * k} {y} Z M {x + 13 * s * k} {y} L {x + 22 * s * k} {y - 7 * s} L {x + 22 * s * k} {y + 7 * s} Z', color)


def loaf(x, y, s=1.0, color='#c8964e'):
    return f'<ellipse cx="{x}" cy="{y}" rx="{14 * s}" ry="{8 * s}" fill="{color}"/>' + line(f'M {x - 6 * s} {y - 3 * s} q 6 {-3 * s} 12 0', '#8a5a2a', 1.2 * s, .6)


def basket(x, y, s=1.0, color='#a87a42'):
    return P(f'M {x - 22 * s} {y - 18 * s} L {x + 22 * s} {y - 18 * s} L {x + 16 * s} {y + 6 * s} L {x - 16 * s} {y + 6 * s} Z', color) + line(f'M {x - 20 * s} {y - 10 * s} L {x + 20 * s} {y - 10 * s} M {x - 18 * s} {y - 2 * s} L {x + 18 * s} {y - 2 * s}', '#6a4a22', 1.2, .6)


def jar(x, y, s=1.0, color='#b88a5e'):
    return P(f'M {x - 9 * s} {y - 52 * s} L {x + 9 * s} {y - 52 * s} L {x + 7 * s} {y - 44 * s} C {x + 22 * s} {y - 36 * s} {x + 22 * s} {y - 6 * s} {x + 12 * s} {y} L {x - 12 * s} {y} C {x - 22 * s} {y - 6 * s} {x - 22 * s} {y - 36 * s} {x - 7 * s} {y - 44 * s} Z', color)


def cross(sc, x, y, h=380, w=200, color='#7a5636', op=0.92, tilt=0, beam=20, sign=True):
    out = [f'<rect x="{x - beam / 2}" y="{y - h}" width="{beam}" height="{h + 30}" fill="{color}"/>', f'<rect x="{x - w / 2}" y="{y - h * .78}" width="{w}" height="{beam * .9}" fill="{color}"/>']
    if sign:
        out.append(f'<rect x="{x - 22}" y="{y - h - 4}" width="44" height="22" fill="#efe4c8"/>')
    t = f' transform="rotate({tilt} {x} {y})"' if tilt else ''
    sc.add(g(f'<g{t}>' + ''.join(out) + '</g>', 'w', op))


def dove(sc, x, y, s=1.0, op=0.95):
    d = (f'M {x} {y} C {x - 14 * s} {y - 4 * s} {x - 44 * s} {y - 30 * s} {x - 60 * s} {y - 22 * s} C {x - 40 * s} {y - 8 * s} {x - 26 * s} {y + 2 * s} {x - 14 * s} {y + 6 * s} '
         f'C {x - 10 * s} {y + 18 * s} {x - 4 * s} {y + 30 * s} {x} {y + 34 * s} C {x + 4 * s} {y + 30 * s} {x + 10 * s} {y + 18 * s} {x + 14 * s} {y + 6 * s} '
         f'C {x + 26 * s} {y + 2 * s} {x + 40 * s} {y - 8 * s} {x + 60 * s} {y - 22 * s} C {x + 44 * s} {y - 30 * s} {x + 14 * s} {y - 4 * s} {x} {y} Z')
    sc.add(g(f'<circle cx="{x}" cy="{y + 10 * s}" r="{70 * s}" fill="#fff6d0"/>', 'glow', 0.75, blend=False))
    sc.add(g(P(d, '#ffffff') + f'<circle cx="{x}" cy="{y - 2 * s}" r="{6 * s}" fill="#ffffff"/>', 'w', op, blend=False))


def sheep(x, y, s=1.0, flip=False, color='#efe8d8'):
    k = -1 if flip else 1
    return (f'<ellipse cx="{x}" cy="{y}" rx="{24 * s}" ry="{15 * s}" fill="{color}"/>'
            f'<ellipse cx="{x + 24 * s * k}" cy="{y - 6 * s}" rx="{8 * s}" ry="{6 * s}" fill="#5a4a3a"/>'
            + ''.join(f'<rect x="{x + dx * s - 2 * s}" y="{y + 10 * s}" width="{4 * s}" height="{12 * s}" fill="#5a4a3a"/>' for dx in (-14, -6, 8, 15)))


def donkey(x, y, s=1.0, flip=False, color='#8a8078'):
    k = -1 if flip else 1
    body = (f'<ellipse cx="{x}" cy="{y - 62 * s}" rx="{46 * s}" ry="{24 * s}" fill="{color}"/>'
            + P(f'M {x + 34 * s * k} {y - 74 * s} C {x + 44 * s * k} {y - 100 * s} {x + 52 * s * k} {y - 110 * s} {x + 62 * s * k} {y - 104 * s} L {x + 74 * s * k} {y - 82 * s} C {x + 70 * s * k} {y - 76 * s} {x + 62 * s * k} {y - 78 * s} {x + 56 * s * k} {y - 84 * s} C {x + 52 * s * k} {y - 74 * s} {x + 48 * s * k} {y - 64 * s} {x + 40 * s * k} {y - 56 * s} Z', color)
            + P(f'M {x + 56 * s * k} {y - 106 * s} L {x + 52 * s * k} {y - 128 * s} L {x + 62 * s * k} {y - 108 * s} Z', color)
            + ''.join(f'<rect x="{x + dx * s * k - 3.5 * s}" y="{y - 46 * s}" width="{7 * s}" height="{46 * s}" fill="{color}"/>' for dx in (-34, -22, 22, 34)))
    return body


def camel(x, y, s=1.0, flip=False, color='#c49a62'):
    k = -1 if flip else 1
    return (P(f'M {x - 50 * s * k} {y - 80 * s} C {x - 40 * s * k} {y - 130 * s} {x - 10 * s * k} {y - 130 * s} {x} {y - 100 * s} C {x + 10 * s * k} {y - 128 * s} {x + 34 * s * k} {y - 126 * s} {x + 44 * s * k} {y - 92 * s} '
              f'C {x + 54 * s * k} {y - 110 * s} {x + 60 * s * k} {y - 140 * s} {x + 72 * s * k} {y - 146 * s} L {x + 88 * s * k} {y - 140 * s} L {x + 86 * s * k} {y - 132 * s} L {x + 76 * s * k} {y - 132 * s} C {x + 70 * s * k} {y - 110 * s} {x + 64 * s * k} {y - 80 * s} {x + 46 * s * k} {y - 66 * s} '
              f'L {x - 46 * s * k} {y - 64 * s} Z', color)
            + ''.join(f'<rect x="{x + dx * s * k - 4 * s}" y="{y - 70 * s}" width="{8 * s}" height="{70 * s}" fill="{color}"/>' for dx in (-40, -28, 30, 40)))


def manger(x, y, s=1.0):
    return (P(f'M {x - 60 * s} {y - 50 * s} L {x + 60 * s} {y - 50 * s} L {x + 46 * s} {y - 14 * s} L {x - 46 * s} {y - 14 * s} Z', '#9a6e44')
            + line(f'M {x - 50 * s} {y - 14 * s} L {x - 62 * s} {y} M {x + 50 * s} {y - 14 * s} L {x + 62 * s} {y} M {x - 40 * s} {y - 14 * s} L {x - 30 * s} {y} M {x + 40 * s} {y - 14 * s} L {x + 30 * s} {y}', '#6a4a2a', 6 * s, .9)
            + P(f'M {x - 58 * s} {y - 50 * s} C {x - 40 * s} {y - 62 * s} {x + 40 * s} {y - 64 * s} {x + 58 * s} {y - 50 * s} Z', '#d8b85a'))


def tomb(sc, x, y, w=220, h=200, open_=True, stone_x=None, color='#b8a88a', dark='#4a3e34', op=0.9):
    out = [P(f'M {x - w} {y} C {x - w} {y - h * 1.2} {x + w} {y - h * 1.3} {x + w} {y} Z', color),
           P(f'M {x - w * .28} {y} L {x - w * .28} {y - h * .5} A {w * .28} {w * .28} 0 0 1 {x + w * .28} {y - h * .5} L {x + w * .28} {y} Z', dark if open_ else '#8a7a60')]
    sx = x + w * .62 if stone_x is None else stone_x
    if open_:
        out.append(f'<circle cx="{sx}" cy="{y - w * .3}" r="{w * .32}" fill="#9a8a70"/><circle cx="{sx}" cy="{y - w * .3}" r="{w * .32}" fill="none" stroke="#6a5a48" stroke-width="3" opacity=".5"/>')
    sc.add(g(''.join(out), 'w', op))


def table(sc, x, y, w=420, color='#9a6e44', cloth='#efe6d2', op=0.9):
    sc.add(g(f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="20" fill="{cloth}"/><rect x="{x - w / 2}" y="{y + 16}" width="{w}" height="60" fill="{cloth}" opacity=".85"/>'
             f'<rect x="{x - w / 2 + 14}" y="{y + 70}" width="10" height="60" fill="{color}"/><rect x="{x + w / 2 - 24}" y="{y + 70}" width="10" height="60" fill="{color}"/>', 'w', op))


def chalice(x, y, s=1.0, color='#d4a63a'):
    return P(f'M {x - 14 * s} {y - 40 * s} L {x + 14 * s} {y - 40 * s} C {x + 14 * s} {y - 22 * s} {x + 6 * s} {y - 16 * s} {x + 3 * s} {y - 14 * s} L {x + 3 * s} {y - 5 * s} L {x + 12 * s} {y} L {x - 12 * s} {y} L {x - 3 * s} {y - 5 * s} L {x - 3 * s} {y - 14 * s} C {x - 6 * s} {y - 16 * s} {x - 14 * s} {y - 22 * s} {x - 14 * s} {y - 40 * s} Z', color)


def crowd(sc, y, x0, x1, n=10, s=1.0, seed_off=0, op=0.7, kneel=False, face=0):
    """A row of townspeople, smaller and paler, set behind the main figures."""
    r = sc.r
    out = []
    xs = sorted(r.uniform(x0, x1) for _ in range(n))
    for i, x in enumerate(xs):
        f = folk(i + seed_off)
        out.append(person(x, y + r.uniform(-6, 6), (110 + r.uniform(-10, 14)) * s, f, pose=r.choice(['stand', 'stand', 'hold', 'pray']), face=face or r.choice([-1, 1]), kneel=kneel, raw=True))
    sc.add(g(''.join(out), 'wf', op, blend=False))


# ---------- people ----------

ARMS = {
    # each arm: (path from the shoulder, hand position); figures face the viewer, 'L' is the viewer's left
    'stand': (('M -11 -73 Q -15 -56 -6 -49', (-5, -48)), ('M 11 -73 Q 14 -56 5 -50', (4, -49))),
    'side': (('M -11 -73 Q -16 -60 -15 -44', (-15, -42)), ('M 11 -73 Q 16 -60 15 -44', (15, -42))),
    'bless': (('M -11 -73 Q -14 -56 -6 -50', (-5, -49)), ('M 11 -73 Q 22 -66 19 -80', (19, -82))),
    'reach': (('M -11 -73 Q -15 -56 -6 -50', (-5, -49)), ('M 11 -73 Q 22 -66 31 -62', (33, -61))),
    'reachdown': (('M -11 -73 Q -15 -56 -6 -50', (-5, -49)), ('M 11 -73 Q 22 -62 30 -48', (31, -46))),
    'orans': (('M -11 -73 Q -22 -70 -23 -86', (-23, -88)), ('M 11 -73 Q 22 -70 23 -86', (23, -88))),
    'open': (('M -11 -73 Q -20 -62 -26 -54', (-27, -53)), ('M 11 -73 Q 20 -62 26 -54', (27, -53))),
    'pray': (('M -11 -73 Q -12 -60 -1.5 -63', (0, -64)), ('M 11 -73 Q 12 -60 1.5 -63', (0, -64))),
    'hold': (('M -11 -73 Q -13 -58 -6 -55', (-5, -55)), ('M 11 -73 Q 13 -58 6 -55', (5, -55))),
    'raise': (('M -11 -73 Q -15 -56 -6 -50', (-5, -49)), ('M 11 -73 Q 20 -82 19 -98', (19, -100))),
    'carry': (('M -11 -73 Q -8 -84 -4 -88', (-3, -89)), ('M 11 -73 Q 14 -80 12 -86', (12, -88))),
    'point': (('M -11 -73 Q -15 -56 -6 -50', (-5, -49)), ('M 11 -73 Q 20 -76 30 -80', (32, -81))),
    'cover': (('M -11 -73 Q -14 -66 -4 -84', (-3, -86)), ('M 11 -73 Q 14 -66 4 -84', (3, -86))),
    'cross': (('M -11 -73 L -48 -76', (-50, -76)), ('M 11 -73 L 48 -76', (50, -76))),
    'bound': (('M -11 -73 Q -13 -58 -3 -52', (-1, -51)), ('M 11 -73 Q 13 -58 3 -52', (1, -51))),
    'none': (),
}


def person(x, y, h, c, pose='stand', face=1, kneel=False, seated=False, raw=False, tilt=0, robe_len=1.0, glow=False, wounds=False, thorns=False, eyes=None):
    """One figure, feet at (x, y), h pixels tall when standing. face is 1 or -1 (the way the head turns and the free arm reaches)."""
    sx = h / 100
    tun, man, skin, hair = c['tunic'], c['mantle'], c['skin'], c['hair']
    kind = c.get('hairlen', 'short')
    dy = 30 if kneel else (24 if seated else 0)
    out = []
    # halo behind everything
    hy = -91 + dy
    if c.get('halo') == 'cross':
        out.append(f'<circle cx="0" cy="{hy}" r="12.5" fill="#e9c35a" opacity=".95"/><circle cx="0" cy="{hy}" r="12.5" fill="none" stroke="#b8862a" stroke-width=".8"/>'
                   f'<path d="M -1.3 {hy - 12.4} L 1.3 {hy - 12.4} L 1 {hy - 7} L -1 {hy - 7} Z M -12.4 {hy - 1.4} L -7 {hy - 1} L -7 {hy + 1} L -12.4 {hy + 1.4} Z M 12.4 {hy - 1.4} L 7 {hy - 1} L 7 {hy + 1} L 12.4 {hy + 1.4} Z" fill="#a8402a" opacity=".85"/>')
    elif c.get('halo') == 'gold':
        out.append(f'<circle cx="0" cy="{hy}" r="11.5" fill="#e9c35a" opacity=".85"/><circle cx="0" cy="{hy}" r="11.5" fill="none" stroke="#b8862a" stroke-width=".7"/>')
    elif c.get('halo') == 'faint':
        out.append(f'<circle cx="0" cy="{hy}" r="10.5" fill="#efd48a" opacity=".55"/>')
    # long hair falls behind the shoulders
    if kind == 'long':
        out.append(P(f'M -7 {-89 + dy} C -8 {-100 + dy} 8 {-100 + dy} 7 {-89 + dy} C 7.6 {-83 + dy} 8.6 {-77 + dy} 10 {-72 + dy} L -10 {-72 + dy} C -8.6 {-77 + dy} -7.6 {-83 + dy} -7 {-89 + dy} Z', hair))
    if kind == 'veil':
        vc = c.get('veil', man)
        out.append(P(f'M -8.5 {-86 + dy} C -10 {-101 + dy} 10 {-101 + dy} 8.5 {-86 + dy} C 9.5 {-80 + dy} 12 {-76 + dy} 15 {-72 + dy} L -15 {-72 + dy} C -12 {-76 + dy} -9.5 {-80 + dy} -8.5 {-86 + dy} Z', vc))
    # the robe
    L = robe_len
    if kneel:
        tunic_d = f'M -10 -47 C -13 -46 -14.5 -42 -15 -36 C -15 -26 -17 -10 -18 0 L {20 * face} 0 C {22 * face} -4 {18 * face} -9 {12 * face} -12 C 14 -24 14.5 -36 14.5 -38 C 14 -43 13 -46 10 -47 C 6 -49 -6 -49 -10 -47 Z'
        tunic_d = f'M -10 -47 C -14 -45 -15 -38 -15 -30 L -17 0 L 17 0 L 15 -30 C 15 -38 14 -45 10 -47 C 6 -49 -6 -49 -10 -47 Z'
        out.append(P(tunic_d, tun))
        out.append(P(f'M {-6 * face} -14 C {-4 * face} -3 {24 * face} -6 {30 * face} -1 L {30 * face} 0 L {-8 * face} 0 Z', tun))
        mantle_d = f'M 3 -48 C 9 -49 13 -47 15 -40 C 17 -26 18 -10 19 -2 L -16 -2 C -16 -10 -14 -16 -11 -20 C -4 -24 4 -30 8 -36 C 7 -40 5 -45 3 -48 Z'
    elif seated:
        out.append(P(f'M -10 -53 C -14 -51 -15 -44 -15 -36 L -15 -22 C -15 -14 -12 -10 -8 -8 L {30 * face} -6 L {32 * face} 0 L {14 * face} 0 L {12 * face} -14 L 14 -36 C 14 -44 13 -51 10 -53 C 6 -55 -6 -55 -10 -53 Z', tun))
        mantle_d = f'M 3 -54 C 9 -55 13 -53 15 -46 C 17 -34 17 -24 {28 * face if face > 0 else 16} -10 L {30 * face} -4 L -14 -8 C -15 -14 -14 -18 -11 -22 C -4 -26 4 -34 8 -42 C 7 -46 5 -51 3 -54 Z'
    else:
        tunic_d = f'M -10 -77 C -13 -76 -14 -72 -14.5 -66 C -15 -45 -16 {-20 * L} -17.5 {-100 + 100 * L} L 17.5 {-100 + 100 * L} C 16 {-20 * L} 15 -45 14.5 -66 C 14 -72 13 -76 10 -77 C 6 -79 -6 -79 -10 -77 Z'
        out.append(P(tunic_d, tun))
        if L >= 1:
            out.append(f'<ellipse cx="-6" cy="-0.5" rx="3.6" ry="1.6" fill="{skin}"/><ellipse cx="6" cy="-0.5" rx="3.6" ry="1.6" fill="{skin}"/>')
        mantle_d = f'M 3 -78 C 9 -79 13 -77 15 -70 C 17 -50 18 -25 18.5 {-104 + 100 * L} L -15 {-104 + 100 * L} C -16 -20 -14 -34 -12 -40 C -5 -44 4 -52 8 -64 C 7 -70 5 -75 3 -78 Z'
    # arms (sleeves) under the mantle
    arms = ARMS.get(pose, ARMS['stand'])
    for path, (hx, hy2) in arms:
        if face < 0 and pose not in ('orans', 'open', 'pray', 'hold', 'stand', 'cover', 'cross', 'bound', 'side', 'carry'):
            path = flipx(path)
            hx = -hx
        out.append(f'<path d="{shift(path, dy)}" fill="none" stroke="{tun}" stroke-width="6.5" stroke-linecap="round"/>')
        out.append(f'<ellipse cx="{hx}" cy="{hy2 + dy}" rx="2.4" ry="2.8" fill="{skin}"/>')
        if wounds:
            out.append(f'<circle cx="{hx}" cy="{hy2 + dy}" r=".9" fill="#a8322a"/>')
    if man and kind != 'none' and c.get('mantle_on', True):
        md = mantle_d if face > 0 else flipx(mantle_d)
        out.append(P(md, man))
        out.append(line(md, INK, .5, .35))
    # neck, head, face
    out.append(f'<rect x="-2.4" y="{-82 + dy}" width="4.8" height="7" fill="{skin}"/>')
    out.append(f'<ellipse cx="{0.8 * face}" cy="{-89 + dy}" rx="6.2" ry="7.4" fill="{skin}"/>')
    out.append(f'<ellipse cx="{0.8 * face - 2.2 * face}" cy="{-87 + dy}" rx="2.4" ry="3.6" fill="#b06a4a" opacity=".18"/>')
    if c.get('face') == 'jesus':
        pass
    elif eyes == 'closed':
        out.append(line(f'M {-3 + face} {-89.5 + dy} q 1.2 .8 2.4 0 M {1.8 + face} {-89.5 + dy} q 1.2 .8 2.4 0', '#4a3022', .55, .7))
    elif eyes != 'none':
        out.append(f'<ellipse cx="{-2.3 + 1.6 * face}" cy="{-89.6 + dy}" rx=".75" ry=".55" fill="#3a2418" opacity=".75"/><ellipse cx="{2.3 + 1.6 * face}" cy="{-89.6 + dy}" rx=".75" ry=".55" fill="#3a2418" opacity=".75"/>')
    # hair on top
    if kind in ('long', 'short'):
        out.append(P(f'M -6.6 {-89 + dy} C -7 {-98.5 + dy} 7 {-98.5 + dy} 6.6 {-89 + dy} C 5.6 {-93.5 + dy} 2 {-95 + dy} 0 {-94.5 + dy} C -2 {-95 + dy} -5.6 {-93.5 + dy} -6.6 {-89 + dy} Z', hair))
        if kind == 'long':
            out.append(P(f'M -6.6 {-90 + dy} C -7.6 {-84 + dy} -7.2 {-79 + dy} -8 {-74 + dy} L -5.5 {-75 + dy} C -5.6 {-80 + dy} -5.2 {-85 + dy} -5.6 {-89 + dy} Z', hair))
            out.append(P(f'M 6.6 {-90 + dy} C 7.6 {-84 + dy} 7.2 {-79 + dy} 8 {-74 + dy} L 5.5 {-75 + dy} C 5.6 {-80 + dy} 5.2 {-85 + dy} 5.6 {-89 + dy} Z', hair))
    if kind == 'veil':
        vc = c.get('veil', man)
        out.append(P(f'M -7.4 {-87 + dy} C -7.8 {-99 + dy} 7.8 {-99 + dy} 7.4 {-87 + dy} C 6.4 {-93 + dy} -6.4 {-93 + dy} -7.4 {-87 + dy} Z', vc))
        out.append(P(f'M -7.4 {-87 + dy} C -8.5 {-82 + dy} -9 {-78 + dy} -11 {-74 + dy} L -8 {-75 + dy} C -7 {-79 + dy} -6.4 {-83 + dy} -6.6 {-87 + dy} Z M 7.4 {-87 + dy} C 8.5 {-82 + dy} 9 {-78 + dy} 11 {-74 + dy} L 8 {-75 + dy} C 7 {-79 + dy} 6.4 {-83 + dy} 6.6 {-87 + dy} Z', vc))
    if kind == 'crown':
        out.append(P(f'M -6.6 {-89 + dy} C -7 {-98.5 + dy} 7 {-98.5 + dy} 6.6 {-89 + dy} C 4 {-92 + dy} -4 {-92 + dy} -6.6 {-89 + dy} Z', hair))
        out.append(P(f'M -7 {-94 + dy} L -7 {-102 + dy} L -3.5 {-98 + dy} L 0 {-104 + dy} L 3.5 {-98 + dy} L 7 {-102 + dy} L 7 {-94 + dy} Z', '#d4a63a'))
    if kind == 'helmet':
        out.append(P(f'M -7.2 {-87 + dy} C -8 {-100 + dy} 8 {-100 + dy} 7.2 {-87 + dy} L 8.6 {-86 + dy} L 8.6 {-84 + dy} L -8.6 {-84 + dy} L -8.6 {-86 + dy} Z', '#8a8a8a'))
        out.append(P(f'M -1.5 {-98 + dy} C -1 {-106 + dy} 6 {-108 + dy} 9 {-104 + dy} L 1.5 {-97 + dy} Z', '#a8322a'))
    if kind == 'turban':
        vc = c.get('veil', '#e8e0cc')
        out.append(P(f'M -7.6 {-89 + dy} C -9 {-101 + dy} 9 {-101 + dy} 7.6 {-89 + dy} C 4 {-92 + dy} -4 {-92 + dy} -7.6 {-89 + dy} Z', vc))
        out.append(P(f'M -7.4 {-89 + dy} C -8.5 {-82 + dy} -9 {-78 + dy} -11 {-74 + dy} L -8 {-75 + dy} C -7 {-79 + dy} -6.4 {-83 + dy} -6.6 {-87 + dy} Z M 7.4 {-89 + dy} C 8.5 {-82 + dy} 9 {-78 + dy} 11 {-74 + dy} L 8 {-75 + dy} C 7 {-79 + dy} 6.4 {-83 + dy} 6.6 {-87 + dy} Z', vc))
    if c.get('beard'):
        out.append(P(f'M -5.6 {-88 + dy} C -5.6 {-81 + dy} -2.4 {-79 + dy} 0 {-79 + dy} C 2.4 {-79 + dy} 5.6 {-81 + dy} 5.6 {-88 + dy} C 4.4 {-84 + dy} -4.4 {-84 + dy} -5.6 {-88 + dy} Z', hair if kind != 'helmet' else '#3a2a1e'))
    if c.get('face') == 'jesus':
        out.append(jface(1.2 * face, -89 + dy, closed=eyes == 'closed', beard=c.get('beard'), hair=hair))
    if thorns:
        out.append(f'<ellipse cx="0" cy="{-93 + dy}" rx="7.2" ry="2" fill="none" stroke="#5a4a2a" stroke-width="1.4"/>' + ''.join(line(f'M {a} {-94 + dy} l {b} -2', '#4a3a1a', .6, .9) for a, b in ((-6, -1.5), (-3, 1), (0, -1.5), (3, 1.5), (6, 1.2))))
    inner = ''.join(out)
    t = f'translate({x:.1f} {y:.1f}) scale({sx:.3f})' + (f' rotate({tilt})' if tilt else '')
    s = f'<g transform="{t}">{inner}</g>'
    if raw: return s
    halo_glow = g(f'<ellipse cx="{x}" cy="{y - h * (.5 - dy / 200)}" rx="{h * .3}" ry="{h * .55}" fill="#fff3c8"/>', 'glow', .5, blend=False) if glow else ''
    return halo_glow + g(s, 'wf', 1, blend=False)


def flipx(path):
    """Mirror an SVG path made of absolute M/L/C/Q commands across x = 0."""
    toks = path.replace(',', ' ').split()
    out, i, cmd = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            out.append(t)
            i += 1
            continue
        out.append(str(-float(t)))
        out.append(toks[i + 1])
        i += 2
    return ' '.join(out)


def shift(path, dy):
    if not dy: return path
    toks = path.split()
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            out.append(t); i += 1; continue
        out.append(t); out.append(str(float(toks[i + 1]) + dy)); i += 2
    return ' '.join(out)


def infant(x, y, s=1.0, c=CHILD, lying=True, halo=True):
    """The Child in swaddling bands, lying (in the manger) or held upright."""
    out = []
    if lying:
        if halo: out.append(f'<circle cx="{x - 24 * s}" cy="{y - 6 * s}" r="{13 * s}" fill="#e9c35a" opacity=".95"/><path d="M {x - 24 * s} {y - 19 * s} L {x - 24 * s} {y - 13 * s} M {x - 37 * s} {y - 6 * s} L {x - 31 * s} {y - 6 * s}" stroke="#a8402a" stroke-width="{2 * s}" opacity=".8"/>')
        out.append(f'<ellipse cx="{x + 6 * s}" cy="{y}" rx="{26 * s}" ry="{10 * s}" fill="#f4ecdc"/>')
        out.append(line(f'M {x - 6 * s} {y - 9 * s} l {4 * s} {18 * s} M {x + 6 * s} {y - 10 * s} l {4 * s} {20 * s} M {x + 18 * s} {y - 9 * s} l {4 * s} {17 * s}', '#c8b896', 1.4 * s, .8))
        out.append(f'<circle cx="{x - 24 * s}" cy="{y - 3 * s}" r="{8 * s}" fill="{c["skin"]}"/><path d="M {x - 31 * s} {y - 6 * s} C {x - 30 * s} {y - 13 * s} {x - 18 * s} {y - 13 * s} {x - 17 * s} {y - 6 * s} Z" fill="{c["hair"]}" opacity=".8"/>')
    else:
        if halo: out.append(f'<circle cx="{x}" cy="{y - 30 * s}" r="{12 * s}" fill="#e9c35a" opacity=".95"/><path d="M {x} {y - 42 * s} L {x} {y - 37 * s} M {x - 12 * s} {y - 30 * s} L {x - 7 * s} {y - 30 * s} M {x + 12 * s} {y - 30 * s} L {x + 7 * s} {y - 30 * s}" stroke="#a8402a" stroke-width="{2 * s}" opacity=".8"/>')
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{11 * s}" ry="{24 * s}" fill="#f4ecdc"/>')
        out.append(f'<circle cx="{x}" cy="{y - 28 * s}" r="{7.5 * s}" fill="{c["skin"]}"/><path d="M {x - 7 * s} {y - 30 * s} C {x - 6 * s} {y - 37 * s} {x + 6 * s} {y - 37 * s} {x + 7 * s} {y - 30 * s} Z" fill="{c["hair"]}" opacity=".85"/>')
    return g(''.join(out), 'w', 1)


def wings(x, y, s=1.0, color='#eadcb4', edge='#b8945a', up=False):
    """A pair of angel wings centred at the shoulders (x, y)."""
    k = -1 if up else 1
    d = f'M {x} {y} C {x - 30 * s} {y - 60 * s * k} {x - 70 * s} {y - 70 * s * k} {x - 84 * s} {y - 40 * s * k} C {x - 80 * s} {y + 10 * s} {x - 60 * s} {y + 50 * s} {x - 16 * s} {y + 60 * s} Z'
    fe = ''.join(f'M {x - 14 * s * i / 4 - 10 * s} {y + 4 * s * i} C {x - 40 * s} {y - 20 * s + 8 * s * i} {x - 60 * s} {y - 10 * s + 10 * s * i} {x - 76 * s + 6 * s * i} {y - 4 * s + 12 * s * i} ' for i in range(5))
    return P(d, color) + P(flipx_abs(d, x), color) + line(d + fe, edge, 1.2, .55) + line(flipx_abs(d + fe, x), edge, 1.2, .55)


def flipx_abs(path, cx):
    toks = path.replace(',', ' ').split()
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            out.append(t); i += 1; continue
        out.append(f'{2 * cx - float(t):.1f}'); out.append(toks[i + 1]); i += 2
    return ' '.join(out)


def angel(sc, x, y, h, pose='bless', face=1, fly=False, op=0.95):
    sc.add(g(f'<circle cx="{x}" cy="{y - h * .6}" r="{h * .6}" fill="#fff6d8"/>', 'glow', .7, blend=False))
    sc.add(g(wings(x, y - h * .72, h / 150), 'wf', .95, blend=False))
    sc.add(person(x, y, h, ANGEL, pose=pose, face=face, robe_len=.86 if fly else 1))


def lying(x, y, s, c, shroud=False, cover='#efe6d2', bed=None, head_left=True):
    """A sick or dead person on a mat or bier: (x, y) is the middle of the body."""
    k = -1 if head_left else 1
    out = []
    if bed:
        out.append(f'<rect x="{x - 70 * s}" y="{y + 6 * s}" width="{140 * s}" height="{12 * s}" fill="{bed}"/>')
    out.append(f'<ellipse cx="{x}" cy="{y}" rx="{58 * s}" ry="{11 * s}" fill="{cover}"/>')
    if not shroud:
        out.append(f'<circle cx="{x + 62 * s * k}" cy="{y - 4 * s}" r="{8 * s}" fill="{c["skin"]}"/><path d="M {x + 62 * s * k - 8 * s} {y - 6 * s} C {x + 62 * s * k - 8 * s} {y - 14 * s} {x + 62 * s * k + 8 * s} {y - 14 * s} {x + 62 * s * k + 8 * s} {y - 6 * s} Z" fill="{c["hair"]}"/>')
    else:
        out.append(f'<ellipse cx="{x + 60 * s * k}" cy="{y - 3 * s}" rx="{10 * s}" ry="{9 * s}" fill="{cover}"/>')
        out.append(''.join(line(f'M {x + dx * s} {y - 10 * s} l {3 * s} {20 * s}', '#b8a88a', 1.2 * s, .7) for dx in (-40, -24, -8, 8, 24, 40)))
    return g(''.join(out), 'w', .95)


def crucified(x, y, h, c=JESUS):
    """Our Lord on the cross: (x, y) is where His feet rest, h His height. Arms along the beam, head bowed to His right."""
    s = h / 100
    sk, hair = c['skin'], c['hair']
    o = []
    o.append(f'<circle cx="-3" cy="-89" r="12.5" fill="#e9c35a" opacity=".95"/><path d="M -4.3 -101.4 L -1.7 -101.4 L -2 -96 L -4 -96 Z M -15.4 -90.4 L -10 -90 L -10 -88 L -15.4 -87.6 Z M 9.4 -90.4 L 4 -90 L 4 -88 L 9.4 -87.6 Z" fill="#a8402a" opacity=".85"/>')
    o.append(P('M -8 -80 C -16 -79 -32 -81 -46 -83 L -46 -78 C -32 -76 -18 -74 -10 -70 Z', sk))
    o.append(P('M 8 -80 C 16 -79 32 -81 46 -83 L 46 -78 C 32 -76 18 -74 10 -70 Z', sk))
    o.append('<circle cx="-46" cy="-80.5" r="1" fill="#8a2a22"/><circle cx="46" cy="-80.5" r="1" fill="#8a2a22"/>')
    o.append(P('M -10 -80 C -11 -64 -9 -52 -7 -44 L 7 -44 C 9 -52 11 -64 10 -80 C 4 -82 -4 -82 -10 -80 Z', sk))
    o.append(line('M -6 -66 q 6 3 12 0 M -5 -58 q 5 2 10 0', '#9a6a4a', .6, .5))
    o.append('<path d="M 6 -62 l 2 3" stroke="#9a2a22" stroke-width="1.2"/>')
    o.append(P('M -5.5 -42 C -6 -28 -4 -12 -2.5 -2 L 2.5 -2 C 4 -12 6 -28 5.5 -42 Z', sk))
    o.append(P('M -9 -47 C -4 -49 4 -49 9 -47 L 10 -36 C 6 -30 -6 -30 -11 -34 Z', c['tunic']))
    o.append(line('M -7 -42 q 7 4 15 1', '#b8a78a', .7, .6))
    o.append('<circle cx="0" cy="-4" r="1" fill="#8a2a22"/>')
    o.append(P('M -6.5 -90 C -7.5 -84 -7.2 -78 -6 -74 L -3 -75 C -4 -80 -4.6 -85 -4 -89 Z', hair))
    o.append(P('M 5 -90 C 6 -84 6 -78 7.5 -73 L 4 -75 C 3.8 -80 3.4 -85 3.4 -89 Z', hair))
    o.append('<rect x="-2.4" y="-82" width="4.8" height="5" fill="' + sk + '"/>')
    o.append(f'<g transform="rotate(14 0 -82)"><ellipse cx="-1" cy="-89" rx="6" ry="7.2" fill="{sk}"/>'
             + P('M -6.4 -89 C -7 -98.5 6 -98.5 5.6 -89 C 4.6 -93.5 1 -95 -1 -94.5 C -3 -95 -5.6 -93.5 -6.4 -89 Z', hair)
             + P('M -6.4 -88 C -6.4 -81 -3.2 -79 -1 -79 C 1.4 -79 4.6 -81 4.6 -88 C 3.4 -84 -5.2 -84 -6.4 -88 Z', hair)
             + jface(-1, -89, closed=True, beard=True, hair=hair)
             + '<ellipse cx="-1" cy="-92.6" rx="7.2" ry="2" fill="none" stroke="#4a3a1a" stroke-width="1.6"/></g>')
    return g(f'<g transform="translate({x} {y}) scale({s:.3f})">' + ''.join(o) + '</g>', 'wf', 1, blend=False)


ELIZABETH = dict(tunic='#8a7a5a', mantle='#a8784a', skin='#cf9e78', hair='#8a8278', beard=False, halo='gold', hairlen='veil', veil='#d8c8a0')
BOY = dict(CHILD, mantle='#a52a2a')
SIMEON = dict(tunic='#e8e0cc', mantle='#7a6a9a', skin='#cf9e78', hair='#e0dcd2', beard=True, halo='faint', hairlen='turban', veil='#efe8d6')
KINGS = [dict(tunic='#7a3a6a', mantle='#d4a63a', skin='#d8a982', hair='#e0dcd2', beard=True, halo=None, hairlen='crown'),
         dict(tunic='#2f5a5a', mantle='#a8402a', skin='#b8845a', hair='#3a2a1e', beard=True, halo=None, hairlen='crown'),
         dict(tunic='#c48a2a', mantle='#3a5a8a', skin='#7a4a2e', hair='#1e1612', beard=False, halo=None, hairlen='crown')]
PILATE = dict(tunic='#efe6d2', mantle='#7a2a4a', skin='#d0a07a', hair='#4a3a2a', beard=False, halo=None, hairlen='short')
MOSES = dict(tunic='#a8402a', mantle='#e0c88a', skin='#cf9e78', hair='#e8e4da', beard=True, halo='gold', hairlen='long')
ELIJAH = dict(tunic='#6a5a3a', mantle='#c4553f', skin='#c08a62', hair='#d8d2c6', beard=True, halo='gold', hairlen='long')


def fire(sc, x, y, s=1.0):
    light(sc, x, y - 30 * s, 90 * s, '#ffd27a', .7)
    sc.add(g(P(f'M {x - 26 * s} {y} C {x - 30 * s} {y - 30 * s} {x - 10 * s} {y - 40 * s} {x - 6 * s} {y - 70 * s} C {x + 6 * s} {y - 46 * s} {x + 14 * s} {y - 50 * s} {x + 12 * s} {y - 80 * s} C {x + 34 * s} {y - 50 * s} {x + 30 * s} {y - 20 * s} {x + 26 * s} {y} Z', '#f0a03a')
             + P(f'M {x - 12 * s} {y} C {x - 14 * s} {y - 20 * s} {x} {y - 26 * s} {x + 2 * s} {y - 44 * s} C {x + 12 * s} {y - 26 * s} {x + 16 * s} {y - 14 * s} {x + 12 * s} {y} Z', '#fbe08a')
             + line(f'M {x - 34 * s} {y + 4 * s} L {x + 34 * s} {y - 4 * s} M {x - 30 * s} {y - 4 * s} L {x + 30 * s} {y + 6 * s}', '#4a2a14', 6 * s, .9), 'w', .95, blend=False))


def scroll(x, y, s=1.0):
    return (f'<rect x="{x - 22 * s}" y="{y - 12 * s}" width="{44 * s}" height="{24 * s}" fill="#efe2c2"/>'
            f'<rect x="{x - 26 * s}" y="{y - 14 * s}" width="{6 * s}" height="{28 * s}" rx="{3 * s}" fill="#9a6e44"/><rect x="{x + 20 * s}" y="{y - 14 * s}" width="{6 * s}" height="{28 * s}" rx="{3 * s}" fill="#9a6e44"/>'
            + line(f'M {x - 16 * s} {y - 5 * s} h {32 * s} M {x - 16 * s} {y} h {28 * s} M {x - 16 * s} {y + 5 * s} h {30 * s}', '#6a5a40', .8 * s, .6))


def staff(x, y, h, color='#7a5a36'):
    return line(f'M {x} {y} L {x + 4} {y - h} q 4 -14 -8 -16', color, 4, .95)


def stone_jars(sc, x, y, n=6, s=1.0, gap=44):
    sc.add(g(''.join(jar(x + i * gap * s, y + (i % 2) * 8, s * (1 if i % 2 else .9), '#b8a88a' if i % 2 else '#c4b494') for i in range(n)), 'wf', .95, blend=False))


def rooster(x, y, s=1.0):
    return (P(f'M {x} {y} C {x - 20 * s} {y - 4 * s} {x - 24 * s} {y - 24 * s} {x - 8 * s} {y - 26 * s} L {x - 4 * s} {y - 40 * s} C {x + 6 * s} {y - 44 * s} {x + 10 * s} {y - 36 * s} {x + 6 * s} {y - 26 * s} C {x + 12 * s} {y - 20 * s} {x + 10 * s} {y - 6 * s} {x} {y} Z', '#8a5a34')
            + P(f'M {x - 8 * s} {y - 22 * s} C {x - 30 * s} {y - 40 * s} {x - 36 * s} {y - 20 * s} {x - 22 * s} {y - 6 * s} Z', '#3a4a3a')
            + P(f'M {x - 2 * s} {y - 42 * s} l {3 * s} {-6 * s} l {3 * s} {5 * s} l {3 * s} {-5 * s} l {1 * s} {7 * s} Z', '#c4322a')
            + P(f'M {x + 8 * s} {y - 36 * s} l {6 * s} {2 * s} l {-6 * s} {2 * s} Z', '#d4a63a'))


def crown(x, y, s=1.0, color='#d4a63a'):
    return P(f'M {x - 8 * s} {y} L {x - 8 * s} {y - 8 * s} L {x - 4 * s} {y - 4 * s} L {x} {y - 10 * s} L {x + 4 * s} {y - 4 * s} L {x + 8 * s} {y - 8 * s} L {x + 8 * s} {y} Z', color)


def gift(x, y, s=1.0, color='#d4a63a'):
    return f'<rect x="{x - 9 * s}" y="{y - 12 * s}" width="{18 * s}" height="{12 * s}" rx="{2 * s}" fill="{color}"/><rect x="{x - 10 * s}" y="{y - 15 * s}" width="{20 * s}" height="{4 * s}" fill="#8a6a2a"/>'


def keys(x, y, s=1.0):
    k = ''
    for dx, a, c in ((-4, -20, '#d4a63a'), (4, 20, '#c8c4bc')):
        k += f'<g transform="rotate({a} {x + dx * s} {y})"><circle cx="{x + dx * s}" cy="{y - 18 * s}" r="{5 * s}" fill="none" stroke="{c}" stroke-width="{2.4 * s}"/><rect x="{x + dx * s - 1.4 * s}" y="{y - 13 * s}" width="{2.8 * s}" height="{24 * s}" fill="{c}"/><rect x="{x + dx * s}" y="{y + 5 * s}" width="{6 * s}" height="{3 * s}" fill="{c}"/></g>'
    return k


def pillar(sc, x, y, h=200, w=34, color='#d8ccb4'):
    sc.add(g(f'<rect x="{x - w / 2}" y="{y - h}" width="{w}" height="{h}" fill="{color}"/><rect x="{x + w * .15}" y="{y - h}" width="{w * .35}" height="{h}" fill="#a8987a" opacity=".5"/><rect x="{x - w / 2 - 6}" y="{y - h - 10}" width="{w + 12}" height="12" fill="{color}"/><rect x="{x - w / 2 - 6}" y="{y - 8}" width="{w + 12}" height="10" fill="#b8a88a"/>', 'wf', .95, blend=False))


def lamp(x, y, s=1.0):
    return (f'<rect x="{x - 3 * s}" y="{y - 160 * s}" width="{6 * s}" height="{160 * s}" fill="#b8902a"/><rect x="{x - 40 * s}" y="{y - 160 * s}" width="{80 * s}" height="{8 * s}" fill="#b8902a"/>'
            + ''.join(f'<ellipse cx="{x + dx * s}" cy="{y - 172 * s}" rx="{8 * s}" ry="{14 * s}" fill="#f6b84a"/>' for dx in (-36, 0, 36)))


def jface(cx, cy, closed=False, beard=True, hair='#5b3a22'):
    """Our Lord's face, the same in every picture: level brows, long almond eyes, a straight nose, a gentle mouth under a parted beard."""
    o = []
    o.append(line(f'M {cx - 4.3} {cy - 3} q 1.6 -1 3.2 -.2 M {cx + 1.1} {cy - 3.2} q 1.6 -.8 3.2 .2', hair, .7, .9))
    if closed:
        o.append(line(f'M {cx - 4} {cy - .9} q 1.5 1.1 3 0 M {cx + 1} {cy - .9} q 1.5 1.1 3 0', '#3a2418', .6, .85))
    else:
        for ex in (cx - 2.5, cx + 2.5):
            o.append(f'<path d="M {ex - 1.7} {cy - 1.2} Q {ex} {cy - 2.4} {ex + 1.7} {cy - 1.2} Q {ex} {cy - .3} {ex - 1.7} {cy - 1.2} Z" fill="#fbf5ea"/><circle cx="{ex}" cy="{cy - 1.25}" r=".72" fill="#3a2418"/>')
        o.append(line(f'M {cx - 4.2} {cy - 1.3} q 1.7 -1.3 3.4 0 M {cx + .8} {cy - 1.3} q 1.7 -1.3 3.4 0', '#3a2418', .4, .8))
    o.append(line(f'M {cx - .1} {cy - 1.4} L {cx - .5} {cy + 2.4} q .5 .5 1.2 .1', '#9a5a3a', .45, .75))
    if beard:
        o.append(P(f'M {cx - 3.2} {cy + 4.4} q 3.2 -1.8 6.4 0 q -3.2 -.4 -6.4 0 Z', hair))
        o.append(P(f'M {cx - 1.4} {cy + 5.6} q 1.4 .6 2.8 0 q -1.4 1 -2.8 0 Z', '#b0604a'))
        o.append(P(f'M {cx - 1} {cy + 8.6} L {cx} {cy + 10.4} L {cx + 1} {cy + 8.6} Z', hair))
    else:
        o.append(P(f'M {cx - 1.4} {cy + 4.2} q 1.4 .7 2.8 0 q -1.4 1 -2.8 0 Z', '#c0705a'))
    o.append(f'<ellipse cx="{cx - 3.6}" cy="{cy + 1.6}" rx="1.4" ry=".9" fill="#c86a5a" opacity=".22"/><ellipse cx="{cx + 3.6}" cy="{cy + 1.6}" rx="1.4" ry=".9" fill="#c86a5a" opacity=".22"/>')
    return ''.join(o)
