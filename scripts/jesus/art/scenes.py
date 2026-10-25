"""The 69 paintings, one function per moment, numbered as in data/jesus.json."""
from paint import *

S = {}


def scene(k):
    def deco(fn):
        S[k] = fn
        return fn
    return deco


@scene(0)
def annunciation(sc):
    room(sc, wall='#ead9b8', floor='#c9ae86', y=560, window=(300, 130, 120, 210, '#a9c4dc'))
    light(sc, 300, 200, 120, '#fff6d8', .6)
    rays(sc, 300, 120, n=5, length=520, spread=40, start=70, op=.25)
    dove(sc, 300, 175, .45)
    angel(sc, 170, 600, 330, pose='bless', face=1)
    sc.add(person(420, 600, 300, MARY, pose='pray', face=-1, kneel=True))
    sc.add(g('<path d="M 492 600 L 492 520 L 520 520 L 520 600 Z" fill="#8a6a44"/><rect x="484" y="512" width="44" height="10" fill="#6a4a2a"/>' + P('M 488 512 L 522 504 L 524 512 Z', '#efe4c8'), 'w', .85))


@scene(10)
def baptism(sc):
    sky(sc, '#8fb5d8', '#e9e2c8', y1=520)
    rays(sc, 300, -60, n=9, length=700, spread=50, start=65, op=.4)
    light(sc, 300, 40, 140, '#fff3c4', .8)
    dove(sc, 300, 120, .7)
    ridge(sc, 380, 30, '#b9a77a', .8)
    ridge(sc, 440, 20, '#8f9a62', .8)
    palm(sc, 70, 470, 230)
    water(sc, 470, '#6f9cc0', .8)
    sc.add(person(300, 640, 330, JESUS, pose='pray', face=1, robe_len=.75))
    water(sc, 548, '#6f9cc0', .8, waves=6)
    sc.add(person(470, 650, 330, JOHN_BAPTIST, pose='bless', face=-1, robe_len=.8))
    sc.add(g('<path d="M 420 535 Q 400 520 380 528" fill="none" stroke="#8a6a3e" stroke-width="4"/><ellipse cx="376" cy="528" rx="12" ry="6" fill="#d8c8a0"/>', 'w', .9))


@scene(26)
def storm(sc):
    sky(sc, '#3b4560', '#7b8aa0', mid='#56617a', y1=520)
    clouds(sc, 9, 40, 260, '#2b3248', .55, 1.4)
    light(sc, 470, 120, 90, '#f8f0d0', .45)
    water(sc, 420, '#3f6688', .85, waves=22, wave_color='#1f3a55')
    boat(sc, 300, 610, 460, mast=True, sail=False)
    for i, (x, p, f) in enumerate([(170, 'cover', 1), (230, 'open', 1), (380, 'pray', -1), (440, 'cover', -1)]):
        sc.add(person(x, 600, 210, apostle(i) if i != 1 else PETER, pose=p, face=f))
    sc.add(person(310, 600, 250, JESUS, pose='raise', face=1, glow=True))
    boat_front(sc, 300, 610, 460)
    sc.add(g(''.join(P(f'M {x} {y} q 30 -40 70 -10 q -30 -10 -70 10 Z', '#e8eef4') for x, y in ((60, 520), (430, 540), (220, 560))), 'w', .7, blend=False))
    water(sc, 600, '#3f6688', .6, waves=10, wave_color='#1f3a55')


@scene(61)
def crucifixion(sc):
    sky(sc, '#3a3348', '#c49a7a', mid='#7a5a6a', y1=560)
    clouds(sc, 6, 60, 260, '#2a2436', .45, 1.5)
    light(sc, 300, 170, 150, '#f6dca0', .5)
    ridge(sc, 560, 18, '#7a6a52', .9)
    cross(sc, 300, 600, h=470, w=300)
    sc.add(crucified(300, 470, 290))
    sc.add(person(170, 680, 250, MARY, pose='pray', face=1))
    sc.add(person(440, 680, 250, JOHN, pose='cover', face=-1))
    sc.add(person(110, 690, 210, MAGDALENE, pose='open', face=1, kneel=True))


def holding(sc, x, y, h, c, face=1, child_s=None, kneel=False, seated=False):
    """Someone holding the Child upright in their arms."""
    sc.add(person(x, y, h, c, pose='hold', face=face, kneel=kneel, seated=seated))
    dy = (30 if kneel else 24 if seated else 0) * h / 100
    sc.add(infant(x + 2 * face * h / 100, y - h * .5 + dy, child_s or h / 150, lying=False))


@scene(1)
def visitation(sc):
    sky(sc, '#a9c6de', '#f1e4c4', y1=480)
    clouds(sc, 5, 60, 200)
    ridge(sc, 360, 40, '#a9b07a', .8)
    ridge(sc, 430, 30, '#8a9a5a', .8)
    town(sc, 470, 330, 600, n=4, hmax=90)
    ground(sc, 600, '#c8b483')
    olive(sc, 90, 610, 1.2)
    sc.add(person(240, 680, 300, MARY, pose='reach', face=1))
    sc.add(person(370, 680, 290, ELIZABETH, pose='open', face=-1))


@scene(2)
def nativity(sc):
    sky(sc, '#1e2a4a', '#3a4a6e', y1=700)
    stars(sc, 60, 260)
    star_of_bethlehem(sc, 300, 90, 1.1)
    rays(sc, 300, 90, n=5, length=400, spread=30, start=75, op=.3)
    sc.add(g(P('M -40 760 L -40 330 C 80 230 520 230 640 330 L 640 760 Z', '#6a5038') + P('M 70 760 L 70 380 C 160 300 440 300 530 380 L 530 760 Z', '#2e2a2e'), 'w', .9))
    light(sc, 300, 560, 170, '#ffe2a0', .65)
    ground(sc, 640, '#9a7a4a', .9)
    sc.add(g(donkey(170, 540, .9, flip=False) , 'wf', .7, blend=False))
    sc.add(g(manger(300, 640, 1.1), 'wf', 1, blend=False))
    sc.add(infant(300, 572, 1.25))
    sc.add(person(170, 690, 260, MARY, pose='pray', face=1, kneel=True))
    sc.add(person(450, 690, 290, JOSEPH, pose='hold', face=-1))
    sc.add(g(staff(478, 690, 240), 'wf', 1, blend=False))


@scene(3)
def shepherds(sc):
    sky(sc, '#18244a', '#3c4c78', y1=700)
    stars(sc, 70, 380)
    light(sc, 330, 190, 220, '#fff2c0', .8)
    rays(sc, 330, 190, n=16, length=420, op=.25)
    angel(sc, 330, 330, 230, pose='orans', fly=True)
    ridge(sc, 470, 30, '#3a4a3a', .9)
    town(sc, 470, 430, 600, color='#6a6a72', roof='#55555e', n=4, hmax=40)
    ridge(sc, 560, 25, '#4f5f3e', .9)
    sc.add(g(''.join(sheep(x, y, .9, flip=f) for x, y, f in ((140, 640, False), (210, 660, True), (440, 650, False), (510, 630, True))), 'wf', .9, blend=False))
    sc.add(person(110, 690, 220, folk(0), pose='cover', face=1, kneel=True))
    sc.add(person(470, 700, 250, folk(4), pose='open', face=-1))
    sc.add(g(staff(500, 700, 210), 'wf', 1, blend=False))
    sc.add(person(290, 700, 200, folk(2), pose='pray', face=1, kneel=True))


@scene(4)
def magi(sc):
    sky(sc, '#24305a', '#7a6a8a', y1=640)
    stars(sc, 40, 200)
    star_of_bethlehem(sc, 200, 80, .9)
    rays(sc, 200, 80, n=3, length=300, spread=20, start=80, op=.3)
    sc.add(g('<rect x="40" y="240" width="300" height="420" fill="#c8a882"/><path d="M 20 250 L 190 170 L 360 250 Z" fill="#8a6a48"/>', 'w', .8))
    sc.add(g(camel(520, 520, .9, flip=True), 'wf', .65, blend=False))
    ground(sc, 640, '#b89a6a', .9)
    holding(sc, 190, 690, 250, MARY, face=1, seated=True)
    sc.add(person(90, 690, 270, JOSEPH, pose='stand', face=1))
    sc.add(person(320, 700, 220, KINGS[0], pose='hold', face=-1, kneel=True))
    sc.add(g(gift(292, 590, 1.6), 'wf', 1, blend=False))
    sc.add(person(420, 700, 260, KINGS[1], pose='hold', face=-1))
    sc.add(g(gift(412, 560, 1.4, '#c8c4bc'), 'wf', 1, blend=False))
    sc.add(person(520, 700, 260, KINGS[2], pose='hold', face=-1))
    sc.add(g(jar(512, 562, .7, '#8a5a3a'), 'wf', 1, blend=False))


@scene(5)
def presentation(sc):
    room(sc, wall='#e8dcc0', floor='#d0b88e', y=600, arch=False)
    colonnade(sc, 600, h=440, gap=150, col=34, op=.6)
    light(sc, 300, 240, 160, '#fff6d8', .5)
    sc.add(g(lamp(300, 360, .8), 'wf', .8, blend=False))
    holding(sc, 300, 690, 300, SIMEON, face=-1)
    sc.add(person(160, 690, 280, MARY, pose='open', face=1))
    sc.add(person(70, 690, 290, JOSEPH, pose='hold', face=1))
    sc.add(g('<ellipse cx="86" cy="532" rx="12" ry="8" fill="#f2efe8"/><ellipse cx="72" cy="528" rx="10" ry="7" fill="#e6e2da"/>', 'wf', 1, blend=False))
    sc.add(person(460, 690, 260, dict(ELIZABETH, tunic='#5a5a7a', halo='faint'), pose='orans', face=-1))


@scene(6)
def flight(sc):
    sky(sc, '#1c2848', '#5a5a7a', y1=640)
    stars(sc, 50, 300)
    moon(sc, 470, 110, 24)
    ridge(sc, 470, 14, '#6a5a5a', .7)
    sc.add(g('<path d="M 60 480 L 120 400 L 180 480 Z M 150 480 L 190 430 L 230 480 Z" fill="#8a7a6a"/>', 'w', .6))
    ground(sc, 560, '#a8906a', .85)
    palm(sc, 540, 600, 240, '#3e5a3a', '#5a4a3a')
    sc.add(g(donkey(330, 690, 1.5, flip=True), 'wf', 1, blend=False))
    sc.add(person(360, 600, 230, MARY, pose='hold', face=-1, seated=True))
    sc.add(infant(358, 548, 1.5, lying=False))
    sc.add(person(130, 700, 280, JOSEPH, pose='point', face=-1))
    sc.add(g(staff(110, 700, 250), 'wf', 1, blend=False))


@scene(7)
def return_nazareth(sc):
    sky(sc, '#9fc1de', '#f2e6c6', y1=500)
    clouds(sc, 6, 50, 200)
    sun(sc, 480, 110, 30)
    hill(sc, 300, 300, 420, '#a4ae74', .75)
    town(sc, 380, 160, 450, n=6, hmax=50)
    ridge(sc, 520, 22, '#90a060', .85)
    sc.add(g(P('M 240 760 C 270 640 330 580 340 520 L 360 520 C 360 590 330 650 380 760 Z', '#d8c69c'), 'w', .8))
    olive(sc, 520, 620, 1.1)
    sc.add(person(200, 700, 290, JOSEPH, pose='side', face=1))
    sc.add(person(300, 700, 170, BOY, pose='open', face=1))
    sc.add(person(400, 700, 280, MARY, pose='side', face=-1))


@scene(8)
def finding(sc):
    room(sc, wall='#e8dcc0', floor='#cbb48c', y=600, arch=False)
    colonnade(sc, 600, h=430, gap=160, col=34, op=.55)
    light(sc, 300, 430, 150, '#fff6d8', .55)
    sc.add(person(300, 610, 180, BOY, pose='bless', face=1, seated=True))
    sc.add(g(scroll(300, 610, 1.2), 'wf', 1, blend=False))
    sc.add(person(200, 680, 220, PHARISEE, pose='hold', face=1, seated=True))
    sc.add(person(440, 680, 230, SIMEON, pose='open', face=-1, seated=True))
    sc.add(person(500, 700, 250, PRIEST, pose='stand', face=-1, seated=True))
    sc.add(person(70, 710, 280, MARY, pose='open', face=1))
    sc.add(person(130, 715, 300, JOSEPH, pose='stand', face=1))


@scene(9)
def hidden_life(sc):
    room(sc, wall='#dcc8a4', floor='#b89a6e', y=580, arch=False, window=(470, 160, 110, 170, '#b8d0e0'))
    light(sc, 470, 220, 140, '#fff3d0', .5)
    sc.add(g(line('M 60 300 L 200 300 M 70 340 L 210 340', '#6a4a2a', 6, .8) + '<rect x="80" y="276" width="10" height="26" fill="#8a8a8a"/><rect x="130" y="270" width="40" height="8" fill="#8a6a44"/>', 'wf', .9, blend=False))
    sc.add(g('<rect x="150" y="560" width="300" height="24" fill="#a07a4a"/><rect x="170" y="584" width="14" height="80" fill="#7a5a36"/><rect x="420" y="584" width="14" height="80" fill="#7a5a36"/><rect x="230" y="548" width="140" height="14" fill="#d8b88a"/>', 'wf', 1, blend=False))
    sc.add(person(200, 690, 300, JOSEPH, pose='reachdown', face=1))
    sc.add(person(400, 690, 310, dict(JESUS, mantle='#a52a2a'), pose='hold', face=-1))
    sc.add(g(''.join(f'<path d="M {x} 700 q 6 -8 12 0" stroke="#d8b88a" stroke-width="3" fill="none"/>' for x in (240, 300, 330, 360)), 'wf', 1, blend=False))


@scene(11)
def desert(sc):
    sky(sc, '#e8c890', '#f4e4c0', mid='#efd6a6', y1=500)
    sun(sc, 470, 100, 36, '#fbe6a0')
    ridge(sc, 380, 50, '#c8a070', .8, rough=1.4)
    ridge(sc, 470, 30, '#b88a5a', .85)
    rocks(sc, 640, 6, '#a07a52')
    sc.add(g(P('M 160 640 C 170 560 420 550 440 640 Z', '#9a7650'), 'wf', .95, blend=False))
    sc.add(person(300, 590, 290, JESUS, pose='pray', face=-1, kneel=True))
    sc.add(g(''.join(f'<ellipse cx="{x}" cy="{y}" rx="16" ry="10" fill="#a88a68"/>' for x, y in ((120, 690), (150, 700), (480, 700))), 'wf', .9, blend=False))
    light(sc, 300, 360, 120, '#fff3d0', .35)


@scene(12)
def first_disciples(sc):
    sky(sc, '#a9c6de', '#efe2c0', y1=480)
    clouds(sc, 4, 60, 180)
    ridge(sc, 400, 25, '#b9a77a', .8)
    water(sc, 450, '#6f9cc0', .75, waves=8, y1=530)
    ground(sc, 520, '#a8b07a', .9)
    palm(sc, 540, 560, 250)
    sc.add(person(130, 700, 300, JOHN_BAPTIST, pose='point', face=1))
    sc.add(person(470, 680, 300, JESUS, pose='bless', face=-1))
    sc.add(person(300, 700, 260, apostle(0), pose='hold', face=1))
    sc.add(person(220, 710, 270, PETER, pose='stand', face=1))


@scene(13)
def cana(sc):
    room(sc, wall='#e4d2ae', floor='#c4a67a', y=560, arch=True)
    sc.add(g(''.join(f'<path d="M {x} 120 q 40 30 80 0" stroke="#8a9a5a" stroke-width="5" fill="none"/>' for x in (80, 220, 360)), 'wf', .8, blend=False))
    table(sc, 300, 470, 520)
    sc.add(g(''.join(f'<rect x="{x}" y="452" width="12" height="20" fill="#a8302a"/>' for x in (120, 200, 400, 480)), 'wf', .9, blend=False))
    stone_jars(sc, 380, 700, 4, 1.4, gap=55)
    sc.add(person(140, 700, 290, MARY, pose='point', face=1))
    sc.add(person(290, 700, 300, JESUS, pose='bless', face=1))
    sc.add(person(560, 700, 240, folk(5), pose='reachdown', face=-1))


@scene(14)
def cleansing(sc):
    sky(sc, '#b8cce0', '#efe2c4', y1=400)
    colonnade(sc, 600, h=420, gap=170, col=36, op=.6)
    sc.add(g(P('M 360 620 L 520 600 L 540 640 L 380 662 Z', '#8a6040') + ''.join(f'<circle cx="{x}" cy="{y}" r="6" fill="#d4a63a"/>' for x, y in ((400, 690), (430, 700), (470, 684), (510, 700), (350, 706))), 'wf', 1, blend=False))
    sc.add(g(''.join(P(f'M {x} {y} q -14 -14 -26 -2 q 12 -2 16 8 q 10 -12 24 -6 q -10 -4 -14 0 Z', '#f2f0ea') for x, y in ((420, 200), (470, 160), (520, 230), (380, 140))), 'wf', .95, blend=False))
    sc.add(person(200, 700, 320, JESUS, pose='raise', face=1))
    sc.add(g(line('M 263 400 q 30 -40 10 -80 q -10 30 20 -20', '#6a4a2a', 3, .9), 'wf', 1, blend=False))
    sc.add(person(470, 700, 250, folk(6), pose='cover', face=1))
    sc.add(person(560, 700, 230, folk(1), pose='open', face=1))


@scene(15)
def samaritan(sc):
    sky(sc, '#9fc4e2', '#f2e4c2', y1=480)
    sun(sc, 300, 70, 30)
    hill(sc, 470, 270, 260, '#a4a06a', .8)
    ridge(sc, 470, 20, '#b8a87a', .8)
    ground(sc, 560, '#cbb486', .9)
    sc.add(g('<rect x="230" y="560" width="160" height="80" fill="#b8a080"/><ellipse cx="310" cy="560" rx="80" ry="16" fill="#9a8466"/><ellipse cx="310" cy="560" rx="58" ry="10" fill="#3e3a3a"/>', 'wf', 1, blend=False))
    sc.add(person(180, 690, 300, JESUS, pose='reach', face=1, seated=True))
    sc.add(person(450, 690, 290, folk(1, woman=True), pose='hold', face=-1))
    sc.add(g(jar(442, 560, .8, '#b8784e'), 'wf', 1, blend=False))


@scene(16)
def official(sc):
    sky(sc, '#a9c6de', '#f1e4c4', y1=470)
    ridge(sc, 380, 30, '#a9b07a', .8)
    town(sc, 440, 0, 260, n=5, hmax=50)
    ground(sc, 540, '#c8b483', .9)
    sc.add(g(P('M 0 760 C 200 640 300 600 600 560 L 600 620 C 330 650 250 690 160 760 Z', '#dccb9c'), 'w', .8))
    sc.add(person(200, 690, 310, JESUS, pose='bless', face=1))
    sc.add(person(400, 700, 270, dict(KINGS[0], hairlen='turban', veil='#d4a63a', halo=None, mantle='#5a3a6a'), pose='pray', face=-1, kneel=True))
    sc.add(person(520, 700, 240, folk(3), pose='stand', face=-1))


@scene(17)
def nazareth_synagogue(sc):
    room(sc, wall='#d8c6a0', floor='#b89a6e', y=580, arch=False)
    colonnade(sc, 580, h=440, gap=200, col=40, op=.5)
    sc.add(g('<rect x="230" y="500" width="140" height="90" fill="#8a6440"/>', 'wf', 1, blend=False))
    sc.add(person(300, 640, 300, JESUS, pose='hold', face=1))
    sc.add(g(scroll(300, 470, 1.6), 'wf', 1, blend=False))
    sc.add(g(''.join(person(x, 720, 230, folk(i), pose=p, face=f, raw=True) for i, (x, p, f) in enumerate(((60, 'point', 1), (140, 'raise', 1), (470, 'point', -1), (550, 'raise', -1)))), 'wf', 1, blend=False))


@scene(18)
def kingdom(sc):
    sky(sc, '#9fc4e2', '#f3e8cc', y1=440)
    clouds(sc, 5, 50, 200)
    ridge(sc, 330, 18, '#9aa8b0', .6)
    water(sc, 360, '#6f9cc0', .8, waves=10, y1=470)
    ground(sc, 470, '#cbb486', .9)
    town(sc, 480, 380, 640, n=4, hmax=50, color='#c8c0b0', roof='#8a8478')
    sc.add(person(300, 610, 300, JESUS, pose='open', face=1))
    crowd(sc, 720, 20, 580, n=8, s=1.5, kneel=True, op=.95)


@scene(19)
def fishers(sc):
    sky(sc, '#f2c89a', '#f6e6c8', mid='#f4d8b0', y1=480)
    sun(sc, 120, 160, 34, '#fbd27a')
    ridge(sc, 330, 16, '#a8a0a8', .55)
    water(sc, 360, '#7aa0be', .8, waves=10, y1=560)
    boat(sc, 440, 520, 300, mast=True)
    net(sc, 360, 470, 160, 70)
    sc.add(g(''.join(fish(370 + (i % 5) * 30, 490 + (i // 5) * 18, .8, '#9aa8b0') for i in range(12)), 'wf', 1, blend=False))
    ground(sc, 560, '#d8c49a', .9)
    sc.add(person(170, 700, 310, JESUS, pose='reach', face=1))
    sc.add(person(330, 700, 270, PETER, pose='pray', face=-1, kneel=True))
    sc.add(person(440, 700, 260, apostle(0), pose='hold', face=-1))
    sc.add(person(520, 700, 250, JOHN, pose='stand', face=-1))


@scene(20)
def capernaum_sunset(sc):
    sky(sc, '#e09a6a', '#f6dcb0', mid='#eebc86', y1=500)
    sun(sc, 480, 330, 40, '#f8c070')
    sc.add(g('<rect x="-20" y="230" width="260" height="440" fill="#c8b08a"/><rect x="-30" y="220" width="280" height="14" fill="#9a8466"/><rect x="80" y="420" width="90" height="180" fill="#4a3a30"/>', 'w', .85))
    light(sc, 125, 520, 70, '#ffd890', .6)
    ground(sc, 600, '#c8a27a', .9)
    sc.add(person(220, 700, 300, JESUS, pose='reachdown', face=1))
    sc.add(g(lying(360, 640, 1.4, folk(3), cover='#d8c8a8', bed='#8a6a44', head_left=True), 'wf', 1, blend=False))
    crowd(sc, 600, 330, 590, n=6, s=1.3, op=.85, face=-1)


@scene(21)
def paralytic(sc):
    room(sc, wall='#d8c4a0', floor='#b8986c', y=600, arch=False)
    sc.add(g('<rect x="210" y="-20" width="180" height="110" fill="#9fc4e2"/>', 'w', .9))
    sc.add(g(line('M 230 90 L 250 330 M 370 90 L 350 330', '#6a4a2a', 3, .9), 'wf', 1, blend=False))
    sc.add(g(lying(300, 340, 1.3, folk(5), cover='#e6d8b8', bed='#8a6a44'), 'wf', 1, blend=False))
    sc.add(g('<ellipse cx="236" cy="70" rx="14" ry="16" fill="#c08a62"/><ellipse cx="364" cy="70" rx="14" ry="16" fill="#b0805a"/>', 'wf', .9, blend=False))
    sc.add(person(150, 700, 310, JESUS, pose='reach', face=1))
    crowd(sc, 700, 330, 590, n=5, s=1.6, op=.95, face=-1)


@scene(22)
def sermon(sc):
    sky(sc, '#a9c9e4', '#f2e6c6', y1=440)
    clouds(sc, 6, 50, 200)
    water(sc, 330, '#7ea6c6', .7, waves=6, y1=420)
    ridge(sc, 330, 10, '#9aa8b0', .5, bottom=340)
    ridge(sc, 420, 40, '#9aac6a', .9)
    sc.add(g(''.join(f'<circle cx="{x}" cy="{y}" r="4" fill="{c}"/>' for x, y, c in ((60, 600, '#e8d060'), (90, 640, '#d86a8a'), (520, 610, '#e8d060'), (560, 650, '#f2f0ea'), (130, 700, '#d86a8a'))), 'w', .9))
    sc.add(g(P('M 200 500 C 220 440 380 440 400 500 Z', '#8a8068'), 'wf', 1, blend=False))
    sc.add(person(300, 500, 260, JESUS, pose='bless', face=1, seated=True))
    crowd(sc, 650, 20, 580, n=9, s=1.5, kneel=True, op=.95)


@scene(23)
def centurion(sc):
    sky(sc, '#a9c6de', '#f1e4c4', y1=470)
    town(sc, 520, -20, 640, n=9, hmax=110, dome=0)
    ground(sc, 560, '#cbb486', .9)
    sc.add(person(190, 700, 310, JESUS, pose='bless', face=1))
    sc.add(person(140, 700, 260, PETER, pose='stand', face=1))
    sc.add(person(420, 700, 300, dict(SOLDIER, mantle='#b8302a', tunic='#c8b48a'), pose='pray', face=-1))


@scene(24)
def nain(sc):
    sky(sc, '#b8c8d8', '#efe2c4', y1=460)
    hill(sc, 200, 300, 300, '#a8a87a', .7)
    town(sc, 420, 80, 320, n=5, hmax=40)
    ground(sc, 520, '#c8b483', .9)
    sc.add(g('<rect x="280" y="560" width="240" height="14" fill="#7a5a36"/>' + line('M 300 574 L 290 640 M 500 574 L 510 640', '#6a4a2a', 6, .9), 'wf', 1, blend=False))
    sc.add(person(420, 560, 200, folk(4, woman=False), pose='open', face=-1, seated=True))
    sc.add(g('<ellipse cx="420" cy="556" rx="90" ry="10" fill="#efe6d2"/>', 'wf', 1, blend=False))
    sc.add(person(160, 700, 310, JESUS, pose='reachdown', face=1))
    sc.add(person(560, 710, 270, dict(folk(1, woman=True), veil='#3a3a46', mantle='#3a3a46', tunic='#4a4a56'), pose='cover', face=-1))


@scene(25)
def bethesda(sc):
    sky(sc, '#a9c6de', '#f1e4c4', y1=400)
    colonnade(sc, 480, h=330, gap=130, col=30, op=.7)
    water(sc, 500, '#6aa0b0', .8, waves=6, y1=590)
    ground(sc, 590, '#d8c8a6', .95)
    sc.add(person(170, 710, 310, JESUS, pose='raise', face=1))
    sc.add(person(400, 710, 290, folk(7), pose='orans', face=-1))
    sc.add(g('<rect x="450" y="600" width="90" height="26" rx="13" fill="#c8a87a"/>', 'wf', 1, blend=False))
