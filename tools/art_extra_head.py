#!/usr/bin/env python3
"""Placeholders extras de crânios e caixas torácicas do Bone Tribe.

Mesmo estilo de tools/gen_art.py (marfim, contorno escuro, detalhes da família).
Uso: python3 tools/art_extra_head.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa
from PIL import ImageChops


def _intersect(a, b):
    m = a.copy()
    m.img = ImageChops.darker(a.img, b.img)
    m.d = ImageDraw.Draw(m.img)
    return m


def _skull_setup():
    s = slot_info("slot_skull")
    W, H = s["canvas"]
    return s, W, H, new_canvas(W, H), s["pivot"][0], s["pivot"][1] - 82, 70


def _ribs_setup():
    s = slot_info("slot_ribs")
    W, H = s["canvas"]
    return s, W, H, new_canvas(W, H), s["pivot"][0]


def _brighter(c, k=60):
    return tuple(min(255, v + k) for v in c)


def _darker(c, k=0.55):
    return tuple(int(v * k) for v in c)


BROWN = (120, 78, 44)
GOLD = (232, 186, 60)
PURPLE = (110, 60, 160)


# ================================================================ crânios

def draw_skull_bear(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 1.04
    sx, sy = cx - 6, cy + 2
    # orelhas redondas (atrás do crânio)
    ears = Layer(W, H)
    ears.circle(sx - rr * 0.62, sy - rr * 0.78, 22)
    ears.circle(sx + rr * 0.12, sy - rr * 0.95, 22)
    paint(cv, ears, outline_w=3)
    inner = Layer(W, H)
    inner.circle(sx - rr * 0.62, sy - rr * 0.78, 11)
    inner.circle(sx + rr * 0.12, sy - rr * 0.95, 11)
    fill(cv, inner, fc["detail"], alpha=220)
    # tufo de pelo na nuca
    fur(cv, W, H, sx - rr * 0.8, sy - rr * 0.2, 11, 30, BROWN, 11, angle=200, spread=45)
    draw_skull(cv, W, H, sx, sy, rr, snout=0.22, jaw=1.15, eye_color=fc["aura"])
    # sobrancelha grossa
    brow = Layer(W, H)
    brow.curve([(sx - rr * 0.32, sy - rr * 0.28), (sx + rr * 0.25, sy - rr * 0.48), (sx + rr * 0.82, sy - rr * 0.26)], 13)
    paint(cv, brow, base=IVORY, outline_w=2.5)
    # focinho escuro / nariz de urso
    nose = Layer(W, H)
    nose.ellipse(sx + rr * 1.08, sy + rr * 0.3, 11, 8)
    paint(cv, nose, base=(70, 46, 34), shadow=(36, 22, 18), light=(140, 100, 80), outline_w=2, grain=False)
    # presas curtas
    fang = Layer(W, H)
    fang.poly([(sx + rr * 0.78, sy + rr * 0.74), (sx + rr * 0.86, sy + rr * 1.02), (sx + rr * 0.94, sy + rr * 0.74)])
    paint(cv, fang, base=IVORY_LIGHT, outline_w=1.8, shade=False, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_skull_turtle(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.92
    sx, sy = cx - 10, cy + 6
    draw_skull(cv, W, H, sx, sy, rr, snout=0.2, jaw=0.9, eye_color=fc["aura"])
    # bico em gancho (córneo, cobre a frente do focinho)
    beak = Layer(W, H)
    top = bezier([(sx + rr * 0.84, sy + rr * 0.0), (sx + rr * 1.3, sy - rr * 0.1), (sx + rr * 1.55, sy + rr * 0.5), (sx + rr * 1.32, sy + rr * 0.92)], 16)
    low = bezier([(sx + rr * 1.32, sy + rr * 0.92), (sx + rr * 1.2, sy + rr * 0.66), (sx + rr * 1.0, sy + rr * 0.6), (sx + rr * 0.84, sy + rr * 0.62)], 12)
    beak.poly(top + low)
    beak.poly([(sx + rr * 0.55, sy + rr * 0.74), (sx + rr * 1.12, sy + rr * 0.74), (sx + rr * 0.9, sy + rr * 1.02), (sx + rr * 0.55, sy + rr * 1.0)])
    paint(cv, beak, base=(206, 180, 120), shadow=(130, 104, 60), light=(250, 230, 170), outline_w=2.8)
    nost = Layer(W, H)
    nost.circle(sx + rr * 1.12, sy + rr * 0.2, 3.5)
    fill(cv, nost, (60, 40, 20))
    # capacete de placas do casco
    cap = Layer(W, H)
    cap.ellipse(sx - rr * 0.05, sy - rr * 0.38, rr * 1.06, rr * 0.7)
    cut = Layer(W, H)
    cut.rrect(0, sy - rr * 0.22, W, H, 0)
    cut.ellipse(sx + rr * 0.52, sy + rr * 0.02, rr * 0.34, rr * 0.38)
    cap.cut(cut)
    paint(cv, cap, base=(80, 150, 140), shadow=(40, 90, 90), light=(150, 220, 200), outline_w=3)
    seams = Layer(W, H)
    for x0, x1 in ((-0.55, -0.48), (-0.08, -0.02), (0.4, 0.42)):
        seams.line([(sx + rr * x0, sy - rr * 0.98), (sx + rr * x1, sy - rr * 0.28)], 2.4)
    seams.curve([(sx - rr * 0.95, sy - rr * 0.55), (sx, sy - rr * 0.72), (sx + rr * 0.85, sy - rr * 0.6)], 2.4)
    fill(cv, seams, (30, 70, 70))
    accent_dots(cv, W, H, [(sx - rr * 0.3, sy - rr * 0.82), (sx + rr * 0.2, sy - rr * 0.86), (sx - rr * 0.75, sy - rr * 0.42)], (210, 240, 230), 4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_skull_bat(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.86
    sx, sy = cx - 4, cy + 14
    ears = Layer(W, H)
    ears.poly([(sx - rr * 0.85, sy - rr * 0.35), (sx - rr * 1.25, sy - rr * 2.2), (sx - rr * 0.05, sy - rr * 0.8)])
    ears.poly([(sx - rr * 0.1, sy - rr * 0.8), (sx + rr * 0.38, sy - rr * 2.3), (sx + rr * 0.86, sy - rr * 0.55)])
    paint(cv, ears, outline_w=3)
    inner = Layer(W, H)
    inner.poly([(sx - rr * 0.72, sy - rr * 0.6), (sx - rr * 1.1, sy - rr * 1.9), (sx - rr * 0.22, sy - rr * 0.86)])
    inner.poly([(sx + rr * 0.04, sy - rr * 0.86), (sx + rr * 0.38, sy - rr * 2.0), (sx + rr * 0.7, sy - rr * 0.68)])
    fill(cv, inner, fc["detail"], alpha=230)
    ridge = Layer(W, H)
    ridge.line([(sx - rr * 0.95, sy - rr * 1.3), (sx - rr * 0.55, sy - rr * 1.15)], 2.4)
    ridge.line([(sx + rr * 0.36, sy - rr * 1.5), (sx + rr * 0.56, sy - rr * 1.3)], 2.4)
    fill(cv, ridge, fc["aura"], alpha=160)
    draw_skull(cv, W, H, sx, sy, rr, snout=0.12, jaw=0.85, eye_color=fc["aura"])
    # folha nasal
    leaf = Layer(W, H)
    leaf.poly([(sx + rr * 0.9, sy + rr * 0.42), (sx + rr * 1.06, sy + rr * 0.05), (sx + rr * 1.16, sy + rr * 0.44)])
    paint(cv, leaf, base=IVORY, outline_w=2)
    fang = Layer(W, H)
    fang.poly([(sx + rr * 0.6, sy + rr * 0.68), (sx + rr * 0.68, sy + rr * 1.12), (sx + rr * 0.76, sy + rr * 0.68)])
    fang.poly([(sx + rr * 0.86, sy + rr * 0.66), (sx + rr * 0.93, sy + rr * 1.06), (sx + rr * 1.0, sy + rr * 0.66)])
    paint(cv, fang, base=IVORY_LIGHT, outline_w=1.8, shade=False, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_skull_mantis(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    hx, hy = cx + 2, cy - 4
    # antenas
    ant = Layer(W, H)
    ant.curve([(hx - 22, hy - 52), (hx - 40, hy - 100), (hx - 70, hy - 120), (hx - 92, hy - 112)], 4.5)
    ant.curve([(hx + 22, hy - 52), (hx + 34, hy - 104), (hx + 66, hy - 124), (hx + 92, hy - 116)], 4.5)
    paint(cv, ant, base=(150, 200, 90), shadow=(70, 120, 40), outline_w=2, shade=False, grain=False)
    # mandíbulas
    mand = Layer(W, H)
    mand.tapered([(hx - 22, hy + 62), (hx - 26, hy + 86), (hx - 4, hy + 92)], 13, 2)
    mand.tapered([(hx + 22, hy + 62), (hx + 26, hy + 86), (hx + 4, hy + 92)], 13, 2)
    paint(cv, mand, base=IVORY, outline_w=2.4)
    # cabeça triangular
    head = Layer(W, H)
    tri = [(hx - 92, hy - 34), (hx + 92, hy - 34), (hx + 12, hy + 74), (hx - 12, hy + 74)]
    head.poly(tri)
    head.line(tri + [tri[0]], 26)
    head.ellipse(hx, hy - 30, 70, 30)
    paint(cv, head, outline_w=3.2)
    # olhos compostos
    eyes = Layer(W, H)
    eyes.ellipse(hx - 70, hy - 30, 28, 32)
    eyes.ellipse(hx + 70, hy - 30, 28, 32)
    glow(cv, eyes, fc["aura"], radius=8, strength=1.6)
    paint(cv, eyes, base=(120, 210, 60), shadow=(50, 120, 30), light=(210, 255, 150), outline_w=2.6, grain=False)
    facets = Layer(W, H)
    for ex in (hx - 70, hx + 70):
        for dx, dy in ((-10, -12), (6, -14), (-12, 6), (6, 2), (-2, 18), (14, 14)):
            facets.circle(ex + dx, hy - 30 + dy, 3.2)
    fill(cv, facets, (40, 100, 30), alpha=170)
    shine = Layer(W, H)
    shine.ellipse(hx - 80, hy - 44, 7, 5)
    shine.ellipse(hx + 60, hy - 44, 7, 5)
    fill(cv, shine, (240, 255, 220))
    # ocelos e boca
    accent_dots(cv, W, H, [(hx - 12, hy - 50), (hx + 12, hy - 50), (hx, hy - 38)], fc["aura"], 3.5, glow_r=3)
    holes = Layer(W, H)
    holes.rrect(hx - 16, hy + 40, hx + 16, hy + 50, 4)
    holes.poly([(hx - 6, hy + 14), (hx + 6, hy + 14), (hx, hy + 2)])
    fill(cv, holes, (28, 16, 18))
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_skull_lizard(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.74
    sx, sy = cx - 34, cy + 24
    spikes = Layer(W, H)
    for i in range(6):
        bx = sx - rr * 0.8 + i * rr * 0.36
        by = sy - rr * 0.82 + abs(i - 2) * 3 + (i > 3) * 6
        spikes.poly([(bx - 9, by + 10), (bx - 2, by - 16 + i), (bx + 9, by + 10)])
    paint(cv, spikes, base=(190, 60, 40), shadow=(110, 24, 16), light=(250, 130, 80), outline_w=2.2, grain=False)
    draw_skull(cv, W, H, sx, sy, rr, snout=1.15, jaw=0.75, eye_color=fc["aura"])
    pupil = Layer(W, H)
    pupil.rrect(sx + rr * 0.53, sy - rr * 0.06, sx + rr * 0.58, sy + rr * 0.26, 2)
    pupil.rrect(sx - rr * 0.0, sy - rr * 0.08, sx + rr * 0.05, sy + rr * 0.24, 2)
    fill(cv, pupil, (40, 10, 6))
    scales = Layer(W, H)
    for i in range(5):
        x = sx + rr * (0.9 + i * 0.22)
        scales.circle(x, sy + rr * 0.22 - i * 1.5, 4.5)
    paint(cv, scales, base=(190, 60, 40), shadow=(110, 24, 16), light=(250, 130, 80), outline_w=1.6, grain=False)
    ember(cv, W, H, [(sx + 120, sy - 40, 3.5), (sx + 150, sy - 16, 2.5), (sx - 46, sy - 70, 3), (sx + 70, sy - 64, 2.5)], fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_skull_rat(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.72
    sx, sy = cx - 30, cy + 30
    ears = Layer(W, H)
    ears.circle(sx - rr * 0.55, sy - rr * 0.9, 24)
    ears.circle(sx + rr * 0.15, sy - rr * 1.05, 26)
    paint(cv, ears, outline_w=3)
    inner = Layer(W, H)
    inner.circle(sx - rr * 0.55, sy - rr * 0.9, 13)
    inner.circle(sx + rr * 0.15, sy - rr * 1.05, 15)
    fill(cv, inner, (200, 130, 170), alpha=210)
    draw_skull(cv, W, H, sx, sy, rr, snout=1.25, jaw=0.7, eye_color=fc["aura"])
    # incisivos longos
    tip = sx + rr * 2.0
    inc = Layer(W, H)
    inc.rrect(tip - 14, sy + rr * 0.55, tip - 4, sy + rr * 1.2, 3)
    inc.rrect(tip - 26, sy + rr * 0.55, tip - 16, sy + rr * 1.12, 3)
    paint(cv, inc, base=(246, 214, 120), shadow=(170, 130, 60), light=(255, 245, 190), outline_w=2, shade=False, grain=False)
    nose = Layer(W, H)
    nose.circle(tip + 4, sy + rr * 0.24, 7)
    paint(cv, nose, base=(200, 120, 160), shadow=(120, 60, 90), outline_w=2, grain=False)
    wh = Layer(W, H)
    for dy, ey in ((-6, -26), (2, 2), (8, 26)):
        wh.curve([(tip - 6, sy + rr * 0.3 + dy), (tip + 20, sy + rr * 0.3 + dy + ey * 0.3), (tip + 36, sy + rr * 0.3 + dy + ey)], 2)
    fill(cv, wh, (40, 26, 30))
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_skull_centaur(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.8
    sx, sy = cx - 24, cy + 18
    # orelhas de cavalo
    ears = Layer(W, H)
    ears.poly([(sx - rr * 0.35, sy - rr * 0.75), (sx - rr * 0.2, sy - rr * 1.6), (sx + rr * 0.15, sy - rr * 0.85)])
    paint(cv, ears, outline_w=3)
    # crina
    fur(cv, W, H, sx - rr * 0.7, sy - rr * 0.65, 9, 40, (150, 70, 36), 21, angle=210, spread=30)
    fur(cv, W, H, sx - rr * 0.9, sy - rr * 0.05, 9, 44, (150, 70, 36), 22, angle=170, spread=30)
    fur(cv, W, H, sx - rr * 0.2, sy - rr * 0.95, 6, 30, (170, 86, 44), 23, angle=-120, spread=30)
    draw_skull(cv, W, H, sx, sy, rr, snout=1.15, jaw=0.95, eye_color=fc["aura"])
    # pintura de guerra
    paint_l = Layer(W, H)
    for i in range(3):
        x = sx + rr * (0.8 + i * 0.25)
        paint_l.line([(x, sy - rr * 0.3), (x + 8, sy + rr * 0.05)], 5)
    fill(cv, paint_l, (200, 50, 40))
    # coroa de louros
    band = []
    for i in range(7):
        t = i / 6
        band.append((sx - rr * 0.75 + t * rr * 1.25, sy - rr * 0.62 - math.sin(t * math.pi) * rr * 0.32))
    leaves = Layer(W, H)
    for i, (x, y) in enumerate(band):
        leaves.ellipse(x, y - 6, 6, 10)
        leaves.ellipse(x + 4, y + 6, 6, 10)
    stem = Layer(W, H)
    stem.line(band, 3)
    fill(cv, stem, (60, 110, 40))
    paint(cv, leaves, base=(110, 170, 70), shadow=(50, 100, 30), light=(180, 230, 120), outline_w=1.8, grain=False)
    accent_dots(cv, W, H, [band[3]], GOLD, 5)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_skull_wasp(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    hx, hy = cx + 4, cy + 4
    ant = Layer(W, H)
    ant.line([(hx - 16, hy - 58), (hx - 34, hy - 100), (hx - 70, hy - 118)], 5)
    ant.line([(hx + 16, hy - 58), (hx + 30, hy - 104), (hx + 70, hy - 120)], 5)
    paint(cv, ant, base=(60, 46, 30), shadow=(30, 20, 14), outline_w=2, shade=False, grain=False)
    knob = Layer(W, H)
    knob.circle(hx - 70, hy - 118, 6)
    knob.circle(hx + 70, hy - 120, 6)
    paint(cv, knob, base=(230, 200, 60), outline_w=2, grain=False)
    mand = Layer(W, H)
    mand.tapered([(hx - 26, hy + 56), (hx - 30, hy + 78), (hx - 6, hy + 82)], 16, 3)
    mand.tapered([(hx + 26, hy + 56), (hx + 30, hy + 78), (hx + 6, hy + 82)], 16, 3)
    paint(cv, mand, base=(222, 190, 70), shadow=(140, 110, 30), light=(250, 240, 150), outline_w=2.6)
    head = Layer(W, H)
    head.circle(hx, hy - 4, 66)
    head.ellipse(hx, hy + 34, 46, 34)
    paint(cv, head, outline_w=3.2)
    # faixas amarelas e pretas no topo
    cap_y = hy - 22
    yel = Layer(W, H)
    yel.rrect(0, 0, W, cap_y, 0)
    yel = _intersect(yel, head)
    paint(cv, yel, base=(236, 200, 60), shadow=(160, 120, 30), light=(255, 240, 150), outline_w=0, grain=False)
    blk = Layer(W, H)
    for y in (hy - 62, hy - 40):
        blk.rrect(0, y, W, y + 9, 0)
    blk.rrect(0, cap_y - 3, W, cap_y + 3, 0)
    fill(cv, _intersect(blk, head), (40, 30, 20))
    # olhos grandes
    eyes = Layer(W, H)
    eyes.ellipse(hx - 46, hy + 4, 22, 34)
    eyes.ellipse(hx + 46, hy + 4, 22, 34)
    glow(cv, eyes, (210, 240, 60), radius=7, strength=1.5)
    paint(cv, eyes, base=(190, 225, 60), shadow=(100, 130, 20), light=(240, 255, 160), outline_w=2.6, grain=False)
    shine = Layer(W, H)
    shine.ellipse(hx - 52, hy - 10, 6, 9)
    shine.ellipse(hx + 40, hy - 10, 6, 9)
    fill(cv, shine, (250, 255, 220))
    holes = Layer(W, H)
    holes.poly([(hx - 7, hy + 24), (hx + 7, hy + 24), (hx, hy + 10)])
    holes.rrect(hx - 18, hy + 44, hx + 18, hy + 52, 4)
    fill(cv, holes, (28, 16, 18))
    finish(cv, W, H, out("bones", bone_id + ".png"))


# ================================================================ costelas

def draw_ribs_bear(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    paint(cv, rib_mask(W, H, cx, 18, 4, 72, 27, 16), outline_w=3.2)
    fur(cv, W, H, cx - 54, 34, 8, 24, BROWN, 31, angle=-150, spread=50)
    fur(cv, W, H, cx + 54, 34, 8, 24, BROWN, 32, angle=-30, spread=50)
    fur(cv, W, H, cx, 120, 7, 22, BROWN, 33, angle=90, spread=40)
    fur(cv, W, H, cx - 62, 96, 5, 20, BROWN, 34, angle=160, spread=40)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_wolf(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fur(cv, W, H, cx, 30, 9, 22, (120, 104, 96), 41, angle=-90, spread=70)
    paint(cv, rib_mask(W, H, cx, 18, 5, 50, 22, 7.5), outline_w=2.8)
    fur(cv, W, H, cx, 70, 5, 16, (120, 104, 96), 42, angle=180, spread=30)
    fur(cv, W, H, cx, 100, 5, 16, (120, 104, 96), 43, angle=0, spread=30)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_crab(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    paint(cv, rib_mask(W, H, cx, 18, 4, 56, 28, 9), outline_w=3)
    shell = Layer(W, H)
    shell.ellipse(cx, 70, 78, 46)
    for side in (-1, 1):
        for k, y in enumerate((52, 72, 92)):
            x = cx + side * (74 - k * 6)
            shell.poly([(x, y - 8), (x + side * 14, y + 2), (x, y + 10)])
    notch = Layer(W, H)
    for dx in (-18, 0, 18):
        notch.circle(cx + dx, 26, 8)
    shell.cut(notch)
    paint(cv, shell, base=(206, 84, 60), shadow=(130, 40, 30), light=(250, 150, 110), outline_w=3)
    rim = Layer(W, H)
    rim.curve([(cx - 70, 92), (cx, 126), (cx + 70, 92)], 7)
    paint(cv, rim, base=(70, 175, 170), shadow=(30, 100, 100), light=(150, 230, 220), outline_w=2, grain=False)
    groove = Layer(W, H)
    groove.curve([(cx - 30, 44), (cx, 64), (cx + 30, 44)], 3)
    groove.curve([(cx - 44, 84), (cx, 100), (cx + 44, 84)], 3)
    fill(cv, groove, (110, 34, 24))
    accent_dots(cv, W, H, [(cx - 44, 58), (cx + 44, 58), (cx - 16, 78), (cx + 18, 76), (cx, 46)], (240, 170, 130), 5)
    accent_dots(cv, W, H, [(cx - 58, 76), (cx + 58, 76)], fc["aura"], 4, glow_r=3)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_beetle(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    spine = Layer(W, H)
    spine.capsule((cx, 18), (cx, 140), 8)
    paint(cv, spine, outline_w=3)
    green = (60, 160, 80)
    for i, (y0, y1, hw) in enumerate(((26, 60, 70), (62, 94, 62), (96, 122, 50), (124, 144, 34))):
        seg = Layer(W, H)
        seg.rrect(cx - hw, y0, cx + hw, y1, 14)
        paint(cv, seg, base=green, shadow=(20, 80, 40), light=(140, 230, 140), outline_w=3, grain=False)
        sh = Layer(W, H)
        sh.ellipse(cx - hw * 0.45, y0 + 9, hw * 0.3, 3.5)
        fill(cv, sh, (230, 255, 230), alpha=210)
    mid = Layer(W, H)
    mid.line([(cx, 30), (cx, 140)], 3)
    fill(cv, mid, (20, 60, 30))
    accent_dots(cv, W, H, [(cx - 50, 44), (cx + 50, 44)], fc["aura"], 4, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_bat(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    mem = Layer(W, H)
    mem.poly([(cx, 22), (cx - 56, 36), (cx - 66, 70), (cx - 56, 136), (cx, 146), (cx + 56, 136), (cx + 66, 70), (cx + 56, 36)])
    sc = Layer(W, H)
    for x, y in ((cx - 66, 104), (cx + 66, 104), (cx - 30, 154), (cx + 30, 154)):
        sc.circle(x, y, 16)
    mem.cut(sc)
    paint(cv, mem, base=(110, 64, 156), shadow=(60, 30, 96), light=(170, 120, 220), outline_w=2.2, grain=False, alpha=225)
    veins = Layer(W, H)
    for side in (-1, 1):
        veins.curve([(cx, 50), (cx + side * 26, 70), (cx + side * 40, 118)], 1.6)
    fill(cv, veins, (60, 30, 96))
    paint(cv, rib_mask(W, H, cx, 18, 4, 58, 28, 6), outline_w=2.4)
    accent_dots(cv, W, H, [(cx, 32)], fc["aura"], 4, glow_r=5)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_lizard(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    core = Layer(W, H)
    core.ellipse(cx, 80, 40, 40)
    glow(cv, core, fc["aura"], radius=14, strength=1.8)
    c2 = Layer(W, H)
    c2.ellipse(cx, 82, 16, 18)
    glow(cv, c2, (255, 200, 90), radius=8, strength=2.0)
    paint(cv, rib_mask(W, H, cx, 18, 4, 64, 27, 10), outline_w=3)
    scales = Layer(W, H)
    for i in range(5):
        y = 30 + i * 22
        scales.poly([(cx - 8, y + 6), (cx, y - 8), (cx + 8, y + 6), (cx, y + 12)])
    for i in range(4):
        y = 46 + i * 27
        ww = 64 * (1 - 0.12 * i)
        for side in (-1, 1):
            x = cx + side * ww * 0.94
            scales.circle(x, y, 5)
            scales.circle(x - side * 9, y - 6, 4.5)
    paint(cv, scales, base=(190, 60, 40), shadow=(110, 24, 16), light=(250, 130, 80), outline_w=1.8, grain=False)
    ember(cv, W, H, [(cx - 20, 66, 3), (cx + 22, 92, 2.5), (cx + 6, 116, 2.5), (cx - 70, 30, 2.5), (cx + 72, 56, 2.5)], fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_mimic(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    wood = (150, 96, 52)
    wood_sh, wood_li = (90, 54, 26), (200, 146, 90)
    # tampa aberta (atrás)
    lid = Layer(W, H)
    lid.poly([(cx - 64, 58), (cx + 64, 58), (cx + 74, 14), (cx - 74, 14)])
    lid.ellipse(cx, 16, 74, 12)
    paint(cv, lid, base=_darker(wood, 0.8), shadow=wood_sh, light=wood, outline_w=3)
    inside = Layer(W, H)
    inside.poly([(cx - 58, 58), (cx + 58, 58), (cx + 66, 24), (cx - 66, 24)])
    fill(cv, inside, (60, 24, 30))
    tongue = Layer(W, H)
    tongue.ellipse(cx + 6, 60, 26, 10)
    paint(cv, tongue, base=(200, 80, 100), shadow=(130, 40, 60), outline_w=2, grain=False)
    up = Layer(W, H)
    for i in range(7):
        x = cx - 54 + i * 18
        up.poly([(x - 7, 26), (x, 42), (x + 7, 26)])
    paint(cv, up, base=IVORY_LIGHT, outline_w=1.8, shade=False, grain=False)
    # caixa
    box = Layer(W, H)
    box.rrect(cx - 72, 58, cx + 72, 146, 10)
    paint(cv, box, base=wood, shadow=wood_sh, light=wood_li, outline_w=3.2)
    slats = Layer(W, H)
    for y in (88, 116):
        slats.line([(cx - 68, y), (cx + 68, y)], 2.6)
    fill(cv, slats, wood_sh)
    teeth = Layer(W, H)
    for i in range(8):
        x = cx - 60 + i * 17
        teeth.poly([(x - 7, 62), (x, 46), (x + 7, 62)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=1.8, shade=False, grain=False)
    trim = Layer(W, H)
    trim.rrect(cx - 74, 58, cx + 74, 68, 4)
    trim.rrect(cx - 74, 136, cx + 74, 148, 5)
    for x in (cx - 54, cx + 54):
        trim.rrect(x - 6, 58, x + 6, 148, 3)
    paint(cv, trim, base=GOLD, shadow=(150, 110, 30), light=(255, 240, 160), outline_w=2.2, grain=False)
    lock = Layer(W, H)
    lock.rrect(cx - 14, 70, cx + 14, 100, 6)
    paint(cv, lock, base=GOLD, shadow=(150, 110, 30), light=(255, 240, 160), outline_w=2.2, grain=False)
    kh = Layer(W, H)
    kh.circle(cx, 80, 4)
    kh.poly([(cx - 3, 82), (cx + 3, 82), (cx + 4, 94), (cx - 4, 94)])
    fill(cv, kh, (40, 24, 20))
    accent_dots(cv, W, H, [(cx - 30, 100), (cx + 30, 100)], fc["aura"], 3.5, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_cyclops(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    stone = (156, 156, 150)
    paint(cv, rib_mask(W, H, cx, 18, 4, 72, 28, 17), base=stone, shadow=(86, 86, 84), light=(210, 210, 204), outline_w=3.2)
    bands = Layer(W, H)
    for side in (-1, 1):
        bands.rrect(cx + side * 56 - 8, 30, cx + side * 56 + 8, 120, 4)
    paint(cv, bands, base=(84, 90, 104), shadow=(46, 50, 60), light=(150, 160, 176), outline_w=2.4, grain=False)
    accent_dots(cv, W, H, [(cx + sd * 56, y) for sd in (-1, 1) for y in (42, 76, 110)], (180, 186, 200), 3.2)
    sock = Layer(W, H)
    sock.circle(cx, 78, 26)
    paint(cv, sock, base=(110, 110, 108), shadow=(60, 60, 60), light=(190, 190, 186), outline_w=3)
    hole = Layer(W, H)
    hole.circle(cx, 78, 18)
    fill(cv, hole, (24, 18, 26))
    iris = Layer(W, H)
    iris.circle(cx, 78, 11)
    glow(cv, iris, fc["aura"], radius=10, strength=2.4)
    fill(cv, iris, _brighter(fc["aura"], 50))
    runes(cv, W, H, cx, 78, 6, (30, 60, 140))
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_ribs_rat_king(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    cape = Layer(W, H)
    cape.poly([(cx - 30, 20), (cx + 30, 20), (cx + 74, 140), (cx + 50, 150), (cx + 24, 140), (cx, 152),
               (cx - 24, 140), (cx - 50, 150), (cx - 74, 140)])
    paint(cv, cape, base=PURPLE, shadow=(60, 30, 96), light=(170, 120, 220), outline_w=3, grain=False)
    paint(cv, rib_mask(W, H, cx, 18, 4, 56, 26, 9), outline_w=2.8)
    # gola de arminho
    collar = Layer(W, H)
    collar.capsule((cx - 40, 24), (cx + 40, 24), 9)
    paint(cv, collar, base=(246, 242, 236), shadow=(180, 170, 170), outline_w=2.4, grain=False)
    spots = Layer(W, H)
    for x in (cx - 30, cx - 10, cx + 12, cx + 32):
        spots.ellipse(x, 24, 2, 3.5)
    fill(cv, spots, (30, 24, 30))
    sash = Layer(W, H)
    sash.line([(cx - 52, 40), (cx + 50, 124)], 15)
    paint(cv, sash, base=(140, 70, 190), shadow=(70, 34, 110), light=(200, 150, 240), outline_w=2.6, grain=False)
    edge = Layer(W, H)
    edge.line([(cx - 52, 34), (cx + 54, 118)], 2.2)
    edge.line([(cx - 56, 46), (cx + 46, 130)], 2.2)
    fill(cv, edge, GOLD)
    chain = Layer(W, H)
    chain.curve([(cx - 30, 30), (cx, 62), (cx + 30, 30)], 3)
    fill(cv, chain, GOLD)
    med = Layer(W, H)
    med.circle(cx, 66, 14)
    glow(cv, med, GOLD, radius=6, strength=1.2)
    paint(cv, med, base=GOLD, shadow=(150, 110, 30), light=(255, 240, 160), outline_w=2.4, grain=False)
    crown = Layer(W, H)
    crown.poly([(cx - 8, 72), (cx - 8, 60), (cx - 4, 65), (cx, 58), (cx + 4, 65), (cx + 8, 60), (cx + 8, 72)])
    fill(cv, crown, (150, 100, 20))
    accent_dots(cv, W, H, [(cx - 66, 136), (cx + 66, 136)], fc["aura"], 3, glow_r=3)
    finish(cv, W, H, out("bones", bone_id + ".png"))


DRAW = {
    "bone_skull_bear": draw_skull_bear,
    "bone_skull_turtle": draw_skull_turtle,
    "bone_skull_bat": draw_skull_bat,
    "bone_skull_mantis": draw_skull_mantis,
    "bone_skull_lizard": draw_skull_lizard,
    "bone_skull_rat": draw_skull_rat,
    "bone_skull_centaur": draw_skull_centaur,
    "bone_skull_wasp": draw_skull_wasp,
    "bone_ribs_bear": draw_ribs_bear,
    "bone_ribs_wolf": draw_ribs_wolf,
    "bone_ribs_crab": draw_ribs_crab,
    "bone_ribs_beetle": draw_ribs_beetle,
    "bone_ribs_bat": draw_ribs_bat,
    "bone_ribs_lizard": draw_ribs_lizard,
    "bone_ribs_mimic": draw_ribs_mimic,
    "bone_ribs_cyclops": draw_ribs_cyclops,
    "bone_ribs_rat_king": draw_ribs_rat_king,
}

FAMILY_OF = {
    "bone_skull_bear": "family_beast",
    "bone_skull_turtle": "family_marine",
    "bone_skull_bat": "family_shadow",
    "bone_skull_mantis": "family_insect",
    "bone_skull_lizard": "family_dragon",
    "bone_skull_rat": "family_shadow",
    "bone_skull_centaur": "family_beast",
    "bone_skull_wasp": "family_insect",
    "bone_ribs_bear": "family_beast",
    "bone_ribs_wolf": "family_beast",
    "bone_ribs_crab": "family_marine",
    "bone_ribs_beetle": "family_insect",
    "bone_ribs_bat": "family_shadow",
    "bone_ribs_lizard": "family_dragon",
    "bone_ribs_mimic": "family_construct",
    "bone_ribs_cyclops": "family_construct",
    "bone_ribs_rat_king": "family_shadow",
}


if __name__ == "__main__":
    for bid, fn in DRAW.items():
        fn(bid, FAMILY_OF[bid])
        print("ok", bid)
