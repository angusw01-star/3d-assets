# 形音義-字靈大師：量產全部 3D 模型
#   字靈 12 種 × 3 段進化（音／形／義／辨 四屬性 × 三個世界）、世界守護者 3 位、
#   寶劍 6 把、鎧甲 4 套、戰馬 4 匹、世界寶石 3 顆
# 用法：blender -b --factory-startup --python scripts/blender/make_zilin_all.py -- <輸出資料夾> [只做某類，例如 sp,boss]
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_zilin import (OUT, blush, cone, export, eyes, hexc, ico, lathe, mat, reset, sphere, torus)

ONLY = set(sys.argv[sys.argv.index('--') + 2].split(',')) if len(sys.argv) > sys.argv.index('--') + 2 else None
GLOW = {'yin': '#b9fff4', 'xing': '#ffe27a', 'yi': '#ffc46b', 'bian': '#e3b8ff'}
TAU = math.pi * 2


def white():
    return mat('EyeWhite', (1, 1, 1), rough=0.3)


def glow(el):
    return mat('Glow' + el, hexc(GLOW[el]), emit=hexc(GLOW[el]), strength=2.5)


def gold():
    return mat('Gold', hexc('#ffcf4a'), metal=0.75, rough=0.3)


def box(name, loc, size, m, rot=(0, 0, 0)):
    """方塊：用四邊錐台做，size 為 (寬, 深, 高)。"""
    o = cone(name, loc, 0.7071, 0.7071, 1, m, rot=(0, 0, 0), seg=4, smooth=False)
    o.rotation_euler = (rot[0], rot[1], rot[2] + math.pi / 4)
    o.scale = (size[0], size[1], size[2])
    return o


# ======================= 字靈身體：每種回傳臉的位置與頭頂高度 =======================
def body_yin1(s):          # 鈴鈴：鐘
    b = mat('YinBell', hexc('#5fd3c6'), rough=0.45)
    lathe('Body', [(0, 0), (.42 * s, 0), (.44 * s, .06 * s), (.36 * s, .25 * s), (.3 * s, .5 * s), (.26 * s, .68 * s), (.15 * s, .8 * s), (0, .83 * s)], b)
    sphere('Belly', (0, -.2 * s, .25 * s), .22 * s, mat('Belly', hexc('#e9fffb')), scale=(1, .5, .9))
    torus('Rim', (0, 0, .04 * s), .43 * s, .035 * s, gold())
    for k in (-1, 1):
        cone(f'Ant{k}', (k * .1 * s, 0, .9 * s), .015 * s, .012 * s, .18 * s, gold(), rot=(0, k * .4, 0))
        sphere(f'AntB{k}', (k * .15 * s, 0, 1.0 * s), .05 * s, glow('yin'))
    return dict(fz=.55 * s, fy=-.25 * s, ex=.11 * s, er=.06 * s, top=.85 * s, w=.44 * s, color=b)


def body_yin2(s):          # 咚咚：小鼓
    b = mat('Drum', hexc('#f2784b'), rough=0.5)
    lathe('Body', [(0, .05 * s), (.34 * s, .05 * s), (.37 * s, .1 * s), (.36 * s, .33 * s), (.37 * s, .55 * s), (.34 * s, .6 * s), (0, .6 * s)], b)
    sphere('Head', (0, 0, .6 * s), .34 * s, mat('DrumSkin', hexc('#fff1d6'), rough=.7), scale=(1, 1, .08))
    for z in (.1, .55):
        torus(f'Rim{z}', (0, 0, z * s), .37 * s, .03 * s, gold())
    for i in range(8):                                  # 鼓釘
        a = TAU * i / 8
        sphere(f'Stud{i}', (math.cos(a) * .37 * s, math.sin(a) * .37 * s, .52 * s), .02 * s, gold())
    for k in (-1, 1):                                   # 鼓棒觸角
        cone(f'Stick{k}', (k * .14 * s, .05 * s, .78 * s), .015 * s, .015 * s, .34 * s, mat('Wood', hexc('#b98250')), rot=(0, k * .5, 0))
        sphere(f'StickB{k}', (k * .22 * s, .05 * s, .93 * s), .045 * s, glow('yin'))
    return dict(fz=.36 * s, fy=-.36 * s, ex=.12 * s, er=.06 * s, top=.62 * s, w=.38 * s, color=b)


def body_yin3(s):          # 鏘鏘：銅鑼
    b = mat('Gong', hexc('#e8b130'), metal=.6, rough=.3)
    cone('Disc', (0, 0, .55 * s), .42 * s, .4 * s, .1 * s, b, rot=(math.pi / 2, 0, 0), seg=32)
    torus('Boss', (0, -.06 * s, .55 * s), .16 * s, .025 * s, mat('GongDark', hexc('#a8781a'), metal=.6, rough=.35), rot=(math.pi / 2, 0, 0))
    torus('Ring', (0, 0, .55 * s), .42 * s, .03 * s, mat('GongDark', hexc('#a8781a')), rot=(math.pi / 2, 0, 0))
    for k in (-1, 1):                                   # 掛架雙腿
        cone(f'Leg{k}', (k * .33 * s, 0, .2 * s), .03 * s, .03 * s, .42 * s, mat('Frame', hexc('#8a3b2b')), rot=(0, k * .25, 0))
        sphere(f'Tassel{k}', (k * .46 * s, 0, .95 * s), .05 * s, glow('yin'))
        cone(f'Cord{k}', (k * .4 * s, 0, .88 * s), .01 * s, .01 * s, .2 * s, mat('Cord', hexc('#d8322d')), rot=(0, k * .9, 0))
    return dict(fz=.6 * s, fy=-.1 * s, ex=.13 * s, er=.065 * s, top=.97 * s, w=.44 * s, color=b)


def body_xing1(s):         # 墨墨：墨滴＋毛筆尾
    b = mat('Ink', hexc('#3a3f86'), rough=.35)
    lathe('Body', [(0, 0), (.25 * s, .03 * s), (.38 * s, .2 * s), (.36 * s, .42 * s), (.25 * s, .62 * s), (.12 * s, .8 * s), (0, .98 * s)], b)
    sphere('Face', (0, -.29 * s, .36 * s), .24 * s, mat('InkFace', hexc('#f5efe0')), scale=(1.05, .4, .85))
    cone('BrushH', (0, .36 * s, .22 * s), .025 * s, .025 * s, .32 * s, mat('Bamboo', hexc('#c9a26b')), rot=(-1.0, 0, 0))
    cone('BrushT', (0, .52 * s, .33 * s), .05 * s, 0, .16 * s, mat('BrushTip', hexc('#1b1b24')), rot=(-1.0, 0, 0))
    return dict(fz=.4 * s, fy=-.375 * s, ex=.1 * s, er=.055 * s, top=.95 * s, w=.38 * s, color=b, nowhite=True)


def body_xing2(s):         # 硯硯：硯台
    b = mat('Stone', hexc('#4f6b6a'), rough=.6)
    sphere('Body', (0, 0, .28 * s), .4 * s, b, scale=(1.15, .9, .7))
    sphere('Pool', (0, .05 * s, .55 * s), .26 * s, mat('InkPool', hexc('#0f1424'), rough=.05), scale=(1, .8, .12))
    sphere('Bar', (.18 * s, .12 * s, .62 * s), .07 * s, mat('InkStick', hexc('#22222c')), scale=(1, .5, 1.6))
    return dict(fz=.32 * s, fy=-.34 * s, ex=.13 * s, er=.065 * s, top=.6 * s, w=.46 * s, color=b)


def body_xing3(s):         # 印印：印章
    b = mat('Seal', hexc('#c8322d'), rough=.4)
    box('Body', (0, 0, .3 * s), (.62 * s, .62 * s, .58 * s), b)
    box('Face', (0, 0, .02 * s), (.64 * s, .64 * s, .04 * s), mat('SealBase', hexc('#7a1a17')))
    sphere('Knob', (0, 0, .7 * s), .17 * s, b)
    for k in (-1, 1):
        sphere(f'Ear{k}', (k * .13 * s, 0, .83 * s), .06 * s, b)
    return dict(fz=.38 * s, fy=-.32 * s, ex=.12 * s, er=.065 * s, top=.85 * s, w=.36 * s, color=b)


def body_yi1(s):           # 卷卷：卷軸
    paper = mat('Paper', hexc('#fff3d0'), rough=.8)
    cone('Roll', (0, 0, .78 * s), .11 * s, .11 * s, .8 * s, paper, rot=(0, math.pi / 2, 0))
    for k in (-1, 1):
        sphere(f'Knob{k}', (k * .44 * s, 0, .78 * s), .07 * s, mat('Rod', hexc('#8a4b22')))
    box('Sheet', (0, -.04 * s, .42 * s), (.66 * s, .04 * s, .7 * s), paper)
    box('Edge', (0, -.04 * s, .08 * s), (.7 * s, .08 * s, .06 * s), mat('Rod', hexc('#8a4b22')))
    return dict(fz=.45 * s, fy=-.08 * s, ex=.12 * s, er=.065 * s, top=.9 * s, w=.45 * s, color=paper)


def body_yi2(s):           # 書書：書本
    b = mat('Cover', hexc('#2f8f5b'), rough=.5)
    box('Body', (0, 0, .4 * s), (.6 * s, .26 * s, .78 * s), b)
    box('Pages', (.02 * s, .0, .4 * s), (.58 * s, .22 * s, .72 * s), mat('Pages', hexc('#fff6dc')))
    for zx in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        sphere(f'Corner{zx}', (zx[0] * .29 * s, -.13 * s, (.4 + zx[1] * .37) * s), .04 * s, gold())
    return dict(fz=.48 * s, fy=-.14 * s, ex=.12 * s, er=.065 * s, top=.8 * s, w=.32 * s, color=b)


def body_yi3(s):           # 簡簡：竹簡
    b = mat('Bamboo', hexc('#d9b45a'), rough=.6)
    for i in range(5):
        x = (i - 2) * .13 * s
        o = cone(f'Slip{i}', (x, 0, .42 * s), .06 * s, .06 * s, .8 * s, b)
        o.scale = (1, .4, 1)
    for z in (.2, .64):
        t = torus(f'Cord{z}', (0, 0, z * s), .33 * s, .015 * s, mat('Cord', hexc('#8a3b2b')))
        t.scale = (1, .18, 1)
    return dict(fz=.45 * s, fy=-.04 * s, ex=.12 * s, er=.06 * s, top=.83 * s, w=.36 * s, color=b)


def body_bian1(s):         # 鏡鏡：圓鏡
    frame = mat('Silver', hexc('#d6dce6'), metal=.8, rough=.25)
    cone('Glass', (0, 0, .58 * s), .34 * s, .34 * s, .06 * s, mat('Mirror', hexc('#a9d8ff'), metal=.4, rough=.05), rot=(math.pi / 2, 0, 0), seg=32)
    torus('Frame', (0, 0, .58 * s), .35 * s, .04 * s, frame, rot=(math.pi / 2, 0, 0))
    cone('Stem', (0, 0, .15 * s), .05 * s, .07 * s, .28 * s, frame)
    sphere('Base', (0, 0, .02 * s), .2 * s, frame, scale=(1, 1, .25))
    return dict(fz=.6 * s, fy=-.06 * s, ex=.12 * s, er=.065 * s, top=.95 * s, w=.38 * s, color=frame)


def body_bian2(s):         # 燈燈：紅燈籠
    b = mat('Lantern', hexc('#e23b3b'), rough=.5, emit=hexc('#ff6a3d'), strength=.4)
    sphere('Body', (0, 0, .45 * s), .36 * s, b, scale=(1, 1, 1.05))
    for z in (.1, .83):
        cone(f'Cap{z}', (0, 0, z * s), .14 * s, .14 * s, .07 * s, gold())
    for i in range(6):
        t = torus(f'Rib{i}', (0, 0, .45 * s), .36 * s, .008 * s, mat('Rib', hexc('#a52222')), rot=(math.pi / 2, 0, TAU * i / 12))
        t.scale = (1, 1, 1.05)
    cone('Tassel', (0, 0, -.02 * s), .05 * s, .01 * s, .14 * s, mat('TasselRed', hexc('#ffcf4a')))
    return dict(fz=.47 * s, fy=-.33 * s, ex=.12 * s, er=.065 * s, top=.88 * s, w=.38 * s, color=b, lift=.1 * s)


def body_bian3(s):         # 晶晶：水晶
    b = mat('Crystal', hexc('#a67bf0'), rough=.1, emit=hexc('#7a4ad6'), strength=.5)
    ico('Body', (0, 0, .45 * s), .4 * s, b, scale=(.85, .75, 1.15))
    for i, a in enumerate((-.6, .6)):
        ico(f'Shard{i}', (math.sin(a) * .38 * s, .05 * s, .2 * s), .12 * s, b, scale=(.6, .6, 1.4))
    return dict(fz=.48 * s, fy=-.3 * s, ex=.12 * s, er=.065 * s, top=.92 * s, w=.4 * s, color=b)


BODIES = {('yin', 1): body_yin1, ('yin', 2): body_yin2, ('yin', 3): body_yin3,
          ('xing', 1): body_xing1, ('xing', 2): body_xing2, ('xing', 3): body_xing3,
          ('yi', 1): body_yi1, ('yi', 2): body_yi2, ('yi', 3): body_yi3,
          ('bian', 1): body_bian1, ('bian', 2): body_bian2, ('bian', 3): body_bian3}


def spirit(el, world, stage):
    reset()
    s = [.8, 1.0, 1.15][stage - 1]
    f = BODIES[(el, world)](s)
    eyes(f['fz'], f['ex'], f['fy'], f['er'], white=None if f.get('nowhite') else white())
    blush(f['fz'] - f['er'] * 1.8, f['ex'] * 1.8, f['fy'] + .01 * s, f['er'] * .8)
    for k in (-1, 1):                                   # 小腳
        sphere(f'Foot{k}', (k * .15 * s, -.1 * s, .03 * s), .075 * s, f['color'], scale=(1, 1.3, .6))
    g, top, w = glow(el), f['top'], f['w']
    if stage >= 2:                                      # 成長：屬性配件
        for k in (-1, 1):
            if el == 'yin':
                for j, rr in enumerate((.12, .18, .24)):
                    t = torus(f'Wave{k}{j}', (k * (w + .05 + j * .05 * s), 0, top * .55), rr * s, .016 * s, g, rot=(0, math.pi / 2, 0))
                    t.scale = (1, 1, .5)
            elif el == 'xing':
                cone(f'Horn{k}', (k * .12 * s, 0, top + .08 * s), .025 * s, .025 * s, .22 * s, mat('Bamboo', hexc('#c9a26b')), rot=(0, k * .5, 0))
                cone(f'HornT{k}', (k * .19 * s, 0, top + .22 * s), .04 * s, 0, .12 * s, mat('BrushTip', hexc('#1b1b24')), rot=(0, k * .5, 0))
            elif el == 'yi':
                o = box(f'PageWing{k}', (k * (w + .14 * s), .05 * s, top * .6), (.26 * s, .02 * s, .2 * s), mat('Paper', hexc('#fff3d0')), rot=(0, k * -.5, k * .3))
            else:
                ico(f'Spike{k}', (k * .12 * s, 0, top + .06 * s), .07 * s, g, scale=(.6, .6, 1.5))
        if el == 'bian':
            ico('SpikeC', (0, 0, top + .1 * s), .08 * s, g, scale=(.6, .6, 1.7))
    if stage >= 3:                                      # 完全體：金冠＋光環＋光球
        for i in range(5):
            a = TAU * i / 5
            cone(f'Crown{i}', (math.cos(a) * .11 * s, math.sin(a) * .11 * s, top + .03 * s), .035 * s, 0, .13 * s, gold(), seg=4)
        torus('CrownBand', (0, 0, top), .12 * s, .02 * s, gold())
        torus('Halo', (0, 0, top * .5), w + .2 * s, .018 * s, g, rot=(.25, 0, 0))
        for i in range(6):
            a = TAU * i / 6
            ico(f'Orb{i}', (math.cos(a) * (w + .2 * s), math.sin(a) * (w + .2 * s) * .97, top * .5 + math.sin(a) * .12 * s), .035 * s, g)
    if f.get('lift'):
        pass
    export(f'sp-{el}{world}-{stage}')


# ======================= 世界守護者 =======================
def angry_brows(z, x, y, r, m):
    for k in (-1, 1):
        b = sphere(f'Brow{k}', (k * x, y, z + r * 1.6), r, m, scale=(1.4, .35, .3))
        b.rotation_euler = (0, k * .45, 0)


def boss1():               # 鐘王：音之守護者
    reset()
    bronze = mat('Bronze', hexc('#c98a2b'), metal=.7, rough=.3)
    lathe('Bell', [(0, 0), (.95, 0), (1.0, .12), (.8, .5), (.66, 1.1), (.58, 1.5), (.35, 1.75), (0, 1.8)], bronze)
    torus('Rim', (0, 0, .1), .98, .07, gold())
    for z in (.6, 1.2):
        torus(f'Band{z}', (0, 0, z), .76 if z < 1 else .62, .03, gold())
    for i in range(10):                                 # 鐘乳釘
        a = TAU * i / 10
        sphere(f'Nub{i}', (math.cos(a) * .73, math.sin(a) * .73, .85), .05, gold())
    eyes(1.15, .22, -.6, .11, white=white())
    angry_brows(1.15, .22, -.66, .11, mat('Dark', hexc('#3a2410')))
    sphere('Mouth', (0, -.66, .9), .14, mat('MouthDark', hexc('#3a1a10')), scale=(1.4, .4, .5))
    for i in range(5):                                  # 王冠
        a = TAU * i / 5
        cone(f'Crown{i}', (math.cos(a) * .25, math.sin(a) * .25, 1.85), .09, 0, .3, gold(), seg=4)
    torus('CrownBand', (0, 0, 1.8), .27, .05, gold())
    ico('CrownGem', (0, -.28, 1.86), .07, glow('yin'))
    for k in (-1, 1):                                   # 手臂與鐘槌
        cone(f'Arm{k}', (k * .95, 0, .9), .09, .12, .6, bronze, rot=(0, k * .9, 0))
        sphere(f'Fist{k}', (k * 1.2, -.05, .7), .15, bronze)
    cone('Mallet', (1.25, -.1, 1.0), .035, .035, .9, mat('Wood', hexc('#8a4b22')), rot=(.2, 0, 0))
    sphere('MalletHead', (1.25, -.18, 1.45), .16, gold(), scale=(1, 1, .8))
    for k in (-1, 1):
        sphere(f'Foot{k}', (k * .45, -.2, .06), .2, bronze, scale=(1, 1.3, .5))
    torus('Aura', (0, 0, .9), 1.35, .03, glow('yin'), rot=(.3, 0, 0))
    export('boss-1')


def boss2():               # 墨龍：形之守護者
    reset()
    ink, belly = mat('DragonInk', hexc('#2b2f7a'), rough=.35), mat('DragonBelly', hexc('#ffd56b'), rough=.5)
    n = 14
    for i in range(n):                                  # 蛇身：一節一節往上盤
        t = i / (n - 1)
        x, y, z = math.sin(t * 5) * .55 * (1 - t * .5), math.cos(t * 5) * .4 * (1 - t * .5), .2 + t * 1.35
        r = .26 - t * .1
        sphere(f'Seg{i}', (x, y, z), r, ink)
        sphere(f'Belly{i}', (x, y - r * .55, z), r * .65, belly, scale=(1, .45, 1))
        if i % 2 == 0:
            cone(f'Fin{i}', (x, y + r * .8, z + r * .5), .07, 0, .2, mat('Fin', hexc('#c43b3b')), rot=(-.6, 0, 0), seg=4)
    hz = 1.75
    sphere('Head', (0, -.15, hz), .32, ink, scale=(1, 1.25, .85))
    sphere('Snout', (0, -.48, hz - .06), .18, ink, scale=(1.1, 1, .7))
    for k in (-1, 1):
        sphere(f'Nostril{k}', (k * .07, -.63, hz - .02), .03, mat('Dark', hexc('#111122')))
        cone(f'Horn{k}', (k * .16, .0, hz + .3), .035, .035, .4, mat('Bamboo', hexc('#c9a26b')), rot=(-.5, k * .45, 0))
        cone(f'HornTip{k}', (k * .25, .1, hz + .52), .06, 0, .18, mat('BrushTip', hexc('#1b1b24')), rot=(-.5, k * .45, 0))
        cone(f'Whisker{k}', (k * .2, -.58, hz - .12), .012, .004, .55, glow('xing'), rot=(.3, k * 1.2, 0))
    eyes(hz + .1, .16, -.36, .07, white=white())
    angry_brows(hz + .1, .16, -.4, .07, mat('Dark', hexc('#111122')))
    ico('Pearl', (.55, -.45, 1.0), .14, glow('xing'))
    export('boss-2')


def boss3():               # 文獅：義之守護者
    reset()
    stone, mane = mat('LionStone', hexc('#d9a441'), rough=.55), mat('Mane', hexc('#b5651d'), rough=.6)
    sphere('Body', (0, .2, .55), .5, stone, scale=(.9, 1.2, .8))
    for kx in (-1, 1):
        for ky in (-1, 1):
            cone(f'Leg{kx}{ky}', (kx * .28, .2 + ky * .4, .2), .1, .12, .42, stone)
            sphere(f'Paw{kx}{ky}', (kx * .28, .2 + ky * .4 - .05, .03), .13, stone, scale=(1, 1.3, .5))
    hz = 1.1
    for i in range(14):                                 # 鬃毛
        a = TAU * i / 14
        cone(f'Mane{i}', (math.cos(a) * .36, -.25 + .05, hz + math.sin(a) * .36), .14, 0, .3, mane, rot=(math.pi / 2, 0, 0), seg=6).rotation_euler = (math.pi / 2 - .2, -a + math.pi / 2, 0)
    sphere('ManeBall', (0, -.15, hz), .48, mane, scale=(1, .6, 1))
    sphere('Head', (0, -.35, hz), .34, stone)
    sphere('Muzzle', (0, -.62, hz - .12), .16, mat('Muzzle', hexc('#f2d08a')), scale=(1.3, .8, .8))
    sphere('Nose', (0, -.75, hz - .06), .05, mat('Dark', hexc('#3a2410')))
    for k in (-1, 1):
        sphere(f'Ear{k}', (k * .25, -.3, hz + .3), .09, stone)
    eyes(hz + .1, .13, -.64, .065, white=white())
    angry_brows(hz + .1, .13, -.68, .065, mat('Dark', hexc('#3a2410')))
    cone('Tail', (0, .75, .7), .04, .02, .5, stone, rot=(-.8, 0, 0))
    sphere('TailTip', (0, .95, .92), .1, mane)
    ico('Ball', (.3, -.55, .18), .17, glow('yi'))             # 腳下的繡球
    torus('Collar', (0, -.3, hz - .3), .25, .04, gold(), rot=(1.2, 0, 0))
    ico('Bell', (0, -.52, hz - .42), .07, gold())
    export('boss-3')


# ======================= 寶劍 =======================
SWORDS = [  # 名稱, 劍身長, 寬, 顏色, 金屬度, 發光色, 護手色, 寶石色
    ('木劍', .55, .05, '#b9834b', 0, None, '#6b4a2a', None),
    ('精鐵劍', .65, .05, '#cfd6df', .7, None, '#6b4a2a', None),
    ('千錘百鍊劍', .72, .055, '#8fdcff', .7, '#57c7ff', '#7b869c', None),
    ('鋒芒畢露劍', .72, .05, '#e1ecf8', .6, '#4fd8ff', '#ffcf4a', '#e8213a'),
    ('太阿神劍', .8, .06, '#ffd65a', .8, '#ffb000', '#ffcf4a', '#b46bff'),
    ('出神入化劍', .88, .065, '#f3c4ff', .5, '#c56bff', '#ffcf4a', '#ff6fd8'),
]


def sword(i):
    reset()
    name, L, W, col, metal, gl, gcol, gem = SWORDS[i]
    bl = mat('Blade', hexc(col), metal=metal, rough=.2 if metal else .7)
    # 劍身：菱形斷面，最後收成劍尖
    o = cone('Blade', (0, 0, .02 + L * .45), W, W * .75, L * .9, bl, seg=4, smooth=False)
    o.scale = (1, .25, 1)
    t = cone('Tip', (0, 0, .02 + L * .9 + L * .05), W * .75, 0, L * .1, bl, seg=4, smooth=False)
    t.scale = (1, .25, 1)
    if gl:
        g = cone('Fuller', (0, 0, .06 + L * .4), W * .25, W * .2, L * .7, mat('BladeGlow', hexc(gl), emit=hexc(gl), strength=2.5), seg=4, smooth=False)
        g.scale = (1, .32, 1)
    gm = mat('Guard', hexc(gcol), metal=.7 if i else 0, rough=.35)
    if i >= 3:                                           # 上翹的護手
        for k in (-1, 1):
            cone(f'Wing{k}', (k * .1, 0, .03), .03, .012, .2, gm, rot=(0, k * -1.2, 0))
            sphere(f'WingEnd{k}', (k * .18, 0, .08), .025, gm)
    else:
        box('Guard', (0, 0, 0), (.24, .05, .04), gm)
    cone('Grip', (0, 0, -.11), .022, .022, .2, mat('Grip', hexc('#4a2c12'), rough=.8))
    for j in range(4):
        torus(f'Wrap{j}', (0, 0, -.04 - j * .045), .024, .006, gm)
    sphere('Pommel', (0, 0, -.23), .035, gm)
    if gem:
        ico('Gem', (0, -.03, .01), .035, mat('Gem', hexc(gem), rough=.05, emit=hexc(gem), strength=.8), scale=(1, .5, 1.1))
    export(f'sword-{i}')


# ======================= 鎧甲（展示在木架上） =======================
ARMORS = [  # 名稱, 主色, 邊色, 金屬度, 肩甲, 寶石
    ('布衣', '#e9dcc0', '#b9a47a', 0, False, None),
    ('皮甲', '#a8703c', '#6e4520', 0, True, None),
    ('玄鐵甲', '#5b6478', '#2e3445', .7, True, '#57c7ff'),
    ('金縷鎧', '#f2c94c', '#a87a00', .8, True, '#e2483d'),
]


def armor(i):
    reset()
    name, c1, c2, metal, pad, gem = ARMORS[i]
    a, b = mat('Arm1', hexc(c1), metal=metal, rough=.35 if metal else .8), mat('Arm2', hexc(c2), metal=metal, rough=.4)
    wood = mat('Stand', hexc('#8a5a2b'), rough=.8)
    sphere('Base', (0, 0, .03), .3, wood, scale=(1, 1, .15))
    cone('Pole', (0, 0, .4), .03, .03, .8, wood)
    lathe('Torso', [(0, .35), (.3, .35), (.27, .45), (.24, .62), (.27, .8), (.2, .9), (0, .92)], a)
    torus('Belt', (0, 0, .5), .25, .025, b)
    if i == 0:
        torus('Sash', (0, 0, .7), .26, .02, mat('Sash', hexc('#7ba0d6')), rot=(0, .6, 0))
    if pad:
        for k in (-1, 1):
            sphere(f'Pad{k}', (k * .3, 0, .85), .13, a, scale=(1.1, 1, .7))
            torus(f'PadRim{k}', (k * .3, 0, .81), .12, .015, b)
    if i >= 2:
        sphere('Plate', (0, -.12, .74), .2, a, scale=(1, .5, .7))
    if i == 1:
        for k in (-1, 1):
            t = torus(f'Strap{k}', (0, 0, .7), .27, .015, b, rot=(0, k * .5, 0))
    if gem:
        ico('Gem', (0, -.24, .76), .04, mat('Gem', hexc(gem), emit=hexc(gem), strength=1.2))
    cone('Neck', (0, 0, .96), .08, .07, .08, a)
    export(f'armor-{i}')


# ======================= 戰馬 =======================
HORSES = [  # 名稱, 身體色, 鬃毛色, 翅膀, 火焰鬃
    ('小棕馬', '#a8703c', '#4a2c12', False, False),
    ('白雪駒', '#f4f4f8', '#c9d3e6', False, False),
    ('赤焰駒', '#c0392b', '#ffb000', False, True),
    ('雲翼天馬', '#fbf7ff', '#b9a4f0', True, False),
]


def horse(i):
    reset()
    name, c1, c2, wings, fire = HORSES[i]
    b = mat('HorseBody', hexc(c1), rough=.5)
    m = mat('Mane', hexc(c2), rough=.5, emit=hexc(c2) if fire else None, strength=1.5 if fire else 0)
    hoof = mat('Hoof', hexc('#3a2a20'))
    sphere('Body', (0, 0, .75), .32, b, scale=(.8, 1.5, .8))
    for kx in (-1, 1):
        for ky in (-1, 1):
            cone(f'Leg{kx}{ky}', (kx * .14, ky * .32, .33), .055, .065, .6, b)
            cone(f'Hoof{kx}{ky}', (kx * .14, ky * .32, .04), .065, .065, .08, hoof)
    cone('Neck', (0, -.48, 1.05), .12, .16, .5, b, rot=(-.6, 0, 0))
    sphere('Head', (0, -.66, 1.3), .15, b, scale=(.85, 1.6, .9))
    sphere('Nose', (0, -.88, 1.24), .1, b, scale=(.9, .9, .8))
    for k in (-1, 1):
        cone(f'Ear{k}', (k * .07, -.58, 1.46), .04, 0, .12, b, seg=6)
    eyes(1.36, .1, -.72, .035, white=white())
    for j in range(5):                                  # 鬃毛
        cone(f'Mane{j}', (0, -.36 - j * .07, 1.0 + j * .1), .07, 0, .2, m, rot=(.8, 0, 0), seg=6)
    cone('Tail', (0, .55, .8), .08, .02, .5, m, rot=(-2.4, 0, 0))
    saddle = mat('Saddle', hexc('#b3261e'), rough=.6)
    sphere('Saddle', (0, .02, 1.0), .24, saddle, scale=(1, 1.1, .3))
    torus('SaddleRim', (0, .02, .98), .24, .02, gold())
    if wings:
        w = mat('Wing', hexc('#ffffff'), rough=.6, emit=hexc('#e3d0ff'), strength=.3)
        for k in (-1, 1):
            for j, (L, z) in enumerate(((.55, 1.05), (.42, 1.0), (.3, .95))):
                o = box(f'Feather{k}{j}', (k * (.25 + L / 2), -.05 + j * .08, z + .1), (L, .12, .02), w, rot=(0, k * -.5, 0))
    if fire:
        ico('FlameTail', (0, .78, .45), .1, m)
    export(f'horse-{i}')


# ======================= 世界寶石 =======================
GEMS = [('音之寶石', '#3fe0c8'), ('形之寶石', '#5b6bff'), ('義之寶石', '#ffb52e')]


def gem(i):
    reset()
    name, col = GEMS[i]
    g = mat('GemBody', hexc(col), rough=.05, metal=.1, emit=hexc(col), strength=.35)
    o = lathe('Gem', [(0, 0), (.24, .3), (.28, .36), (.2, .46), (0, .48)], g, seg=8)
    for p in o.data.polygons:
        p.use_smooth = False
    o.location.z = .25
    torus('Setting', (0, 0, .61), .29, .03, gold())
    for j in range(8):
        a = TAU * j / 8
        cone(f'Prong{j}', (math.cos(a) * .28, math.sin(a) * .28, .62), .015, 0, .12, gold())
    ico('Core', (0, 0, .6), .08, mat('Core', (1, 1, 1), emit=(1, 1, 1), strength=3))
    torus('Orbit', (0, 0, .58), .45, .012, g, rot=(1.2, .3, 0))
    export(f'gem-{i}')


def want(k):
    return ONLY is None or k in ONLY


if want('sp'):
    for el in ('yin', 'xing', 'yi', 'bian'):
        for w in (1, 2, 3):
            for st in (1, 2, 3):
                spirit(el, w, st)
if want('boss'):
    boss1(); boss2(); boss3()
if want('sword'):
    for i in range(len(SWORDS)):
        sword(i)
if want('armor'):
    for i in range(len(ARMORS)):
        armor(i)
if want('horse'):
    for i in range(len(HORSES)):
        horse(i)
if want('gem'):
    for i in range(len(GEMS)):
        gem(i)
