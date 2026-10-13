#!/usr/bin/env python3
"""Ossos da segunda leva (35 ossos novos) do Bone Tribe.

Mesmo estilo de tools/gen_art.py e dos módulos art_extra_*: marfim com contorno escuro,
detalhes na cor da família e mais enfeite conforme a raridade (comum simples, raro com
mais detalhe, lendário ornamentado e com brilho). Tamanho e pivot vêm de data/skeleton.json.

Uso: python3 tools/art_wave2_bones.py   (ou BT_ONLY=... python3 tools/gen_art.py bones)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa
from art_extra_back import (pc, inter, leaf_pts, leaf_axis, rot_rect, rot_ellipse, hexagon,  # noqa
                            path_normals, insect_wing, root_knob, back_canvas, tail_canvas, _dir)
from art_extra_limbs import Y, _arm_base, _arm_canvas, _legs_canvas, _pelvis, _jointed  # noqa
from art_extra_head import _skull_setup, _ribs_setup  # noqa


# ------------------------------------------------------------- cores

def _dk(c, k=0.55):
    return tuple(max(0, int(v * k)) for v in c)


def _lt(c, add=60):
    return tuple(min(255, v + add) for v in c)


BRASS = (214, 164, 70)
BRASS_KW = dict(base=BRASS, shadow=(130, 90, 30), light=(255, 228, 150))
GOLD = (236, 190, 64)
GOLD_KW = dict(base=GOLD, shadow=(150, 106, 24), light=(255, 240, 160))
IRON = (100, 108, 126)
IRON_KW = dict(base=IRON, shadow=(56, 60, 74), light=(170, 180, 200))
STONE = (148, 150, 158)
STONE_KW = dict(base=STONE, shadow=(84, 86, 96), light=(206, 208, 216))
OBS = (52, 48, 66)
OBS_KW = dict(base=OBS, shadow=(22, 20, 30), light=(130, 124, 160))
HORN = (226, 204, 160)
HORN_KW = dict(base=HORN, shadow=(150, 120, 80), light=(255, 240, 210))
BROWN = (120, 78, 44)
DARK_BROWN = (86, 60, 40)
PALE = (214, 212, 192)
PALE_KW = dict(base=PALE, shadow=(140, 142, 124), light=(240, 240, 226))
SINEW = (138, 134, 140)
OLIVE = (150, 140, 70)
OLIVE_KW = dict(base=OLIVE, shadow=(86, 78, 30), light=(210, 200, 120))
CROC = (98, 126, 86)
CROC_KW = dict(base=CROC, shadow=(50, 70, 44), light=(160, 186, 130))
HOLE = (28, 16, 18)
LAVA = (255, 120, 30)


def _out(bone_id):
    return out("bones", bone_id + ".png")


def gear_mask(W, H, cx, cy, r, n=8, hole=0.32):
    m = Layer(W, H)
    m.circle(cx, cy, r * 0.8)
    for i in range(n):
        a = 360.0 * i / n
        ux, uy = _dir(a)
        m.poly(rot_rect(cx + ux * r * 0.86, cy + uy * r * 0.86, r * 0.36, r * 0.34, a))
    if hole:
        h = Layer(W, H)
        h.circle(cx, cy, r * hole)
        m.cut(h)
    return m


def gear(cv, W, H, cx, cy, r, kw=BRASS_KW, n=8, ow=2.4, spokes=True):
    m = gear_mask(W, H, cx, cy, r, n)
    paint(cv, m, outline_w=ow, grain=False, **kw)
    if spokes and r > 12:
        sp = Layer(W, H)
        for a in (0, 120, 240):
            ux, uy = _dir(a + 30)
            sp.line([(cx + ux * r * 0.36, cy + uy * r * 0.36), (cx + ux * r * 0.62, cy + uy * r * 0.62)], max(2, r * 0.12))
        fill(cv, sp, _dk(kw["base"], 0.6), alpha=200)
    return m


def flame(m, x, y, h, w, lean=0.0):
    """Labareda (gota virada para cima) com base em (x, y)."""
    m.tapered([(x, y), (x + lean * h * 0.4, y - h * 0.5), (x + lean * h, y - h)], w, 1)
    m.ellipse(x, y - w * 0.15, w * 0.5, w * 0.45)


def membrane_wings(cv, W, H, px, py, mem_col, bone_kw, elbow, tips, k=1.0, back_scale=0.72, back_dim=0.6,
                   mem_ow=2.6, decorate=None, bone_w=8, claw=True, scallop=0.22):
    """Par de asas de membrana (a de trás menor e mais escura), no estilo de bone_wings_bat."""
    res = []
    for side, sc, dim in ((1, back_scale, back_dim), (-1, 1.0, 1.0)):
        f = sc * k

        def P(v):
            return (px + v[0] * f, py + v[1] * f)
        el = P(elbow)
        tps = [P(v) for v in tips]
        poly = [(px, py), el]
        for i, tp in enumerate(tps):
            poly.append(tp)
            if i < len(tps) - 1:
                n = tps[i + 1]
                mx, my = (tp[0] + n[0]) / 2, (tp[1] + n[1]) / 2
                poly.append((mx + (el[0] - mx) * scallop, my + (el[1] - my) * scallop))
        poly.append((px + side * 4, py + 30))
        mem = Layer(W, H)
        mem.poly(poly)
        col = tuple(int(c * dim) for c in mem_col)
        paint(cv, mem, base=col, shadow=_dk(col, 0.5), light=tuple(min(255, int(c * 1.7) + 10) for c in col), outline_w=mem_ow)
        if decorate:
            decorate(mem, el, tps, f, dim)
        bones = Layer(W, H)
        bones.capsule((px, py), el, bone_w * f)
        for tp in tps:
            bones.tapered([el, tp], bone_w * 0.88 * f, 2.5)
        if claw:
            bones.tapered([el, (el[0] + 4 * side, el[1] - 24 * f)], bone_w * 0.88 * f, 1)
        bkw = dict(bone_kw)
        bkw["base"] = tuple(int(c * (0.78 + 0.22 * dim)) for c in bkw["base"])
        paint(cv, bones, outline_w=2.4, **bkw)
        res.append((mem, el, tps, f, dim))
    return res


# ================================================================ crânios

def draw_skull_hyena(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.94
    sx, sy = cx - 8, cy + 4
    ears = Layer(W, H)
    ears.ellipse(sx - rr * 0.58, sy - rr * 0.92, 19, 27)
    ears.ellipse(sx + rr * 0.08, sy - rr * 1.06, 20, 29)
    paint(cv, ears, outline_w=3)
    inner = Layer(W, H)
    inner.ellipse(sx - rr * 0.58, sy - rr * 0.9, 10, 17)
    inner.ellipse(sx + rr * 0.08, sy - rr * 1.04, 11, 18)
    fill(cv, inner, (90, 60, 40), alpha=220)
    # crina eriçada
    fur(cv, W, H, sx - rr * 0.55, sy - rr * 0.62, 9, 30, DARK_BROWN, 101, angle=-150, spread=35)
    fur(cv, W, H, sx - rr * 0.9, sy - rr * 0.05, 8, 28, DARK_BROWN, 102, angle=185, spread=35)
    m = draw_skull(cv, W, H, sx, sy, rr, snout=0.38, jaw=1.1, eye_color=fc["aura"], base=(234, 220, 186))
    spots = Layer(W, H)
    for x, y, rad in ((-0.55, -0.42, 8), (-0.22, -0.66, 7), (0.2, -0.6, 6), (-0.8, 0.12, 7), (-0.5, 0.52, 6),
                      (0.55, -0.42, 5), (-0.75, -0.3, 5)):
        spots.circle(sx + rr * x, sy + rr * y, rad)
    fill(cv, inter(spots, m), (130, 88, 50), alpha=210)
    # sorriso: canto da boca puxado para cima
    grin = Layer(W, H)
    grin.curve([(sx - rr * 0.42, sy + rr * 0.4), (sx - rr * 0.3, sy + rr * 0.66), (sx - rr * 0.08, sy + rr * 0.66)], 3.4)
    fill(cv, grin, HOLE)
    fang = Layer(W, H)
    fang.poly([(sx + rr * 1.02, sy + rr * 0.7), (sx + rr * 1.1, sy + rr * 1.05), (sx + rr * 1.18, sy + rr * 0.7)])
    fang.poly([(sx + rr * 0.62, sy + rr * 0.72), (sx + rr * 0.68, sy + rr * 0.98), (sx + rr * 0.74, sy + rr * 0.72)])
    paint(cv, fang, base=IVORY_LIGHT, outline_w=1.8, shade=False, grain=False)
    nose = Layer(W, H)
    nose.ellipse(sx + rr * 1.3, sy + rr * 0.3, 9, 7)
    paint(cv, nose, base=(60, 40, 34), shadow=(30, 18, 16), light=(130, 100, 80), outline_w=2, grain=False)
    finish(cv, W, H, _out(bone_id))


def draw_skull_salamander(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    sx, sy = cx - 2, cy + 34
    # guelras de brasa atrás da cabeça
    gills = Layer(W, H)
    for k, (ex, ey) in enumerate(((-30, -50), (-42, -20), (-38, 12))):
        gills.tapered([(sx - 50, sy - 8 + k * 8), (sx - 50 + ex * 0.6, sy - 8 + ey * 0.6 + 4), (sx - 50 + ex, sy - 8 + ey)], 13, 3)
    glow(cv, gills, fc["aura"], radius=6, strength=1.2)
    paint(cv, gills, base=(232, 96, 60), shadow=(150, 40, 24), light=(255, 170, 120), outline_w=2.4, grain=False)
    head = Layer(W, H)
    head.ellipse(sx, sy, 76, 40)
    head.ellipse(sx + 58, sy + 6, 52, 32)
    head.rrect(sx - 40, sy + 14, sx + 104, sy + 44, 14)
    head.circle(sx + 18, sy - 30, 17)
    head.circle(sx + 54, sy - 26, 14)
    paint(cv, head, base=(232, 214, 186), outline_w=3)
    # rachaduras de lava
    cracks = Layer(W, H)
    cracks.line([(sx - 60, sy - 4), (sx - 40, sy - 14), (sx - 28, sy - 2), (sx - 8, sy - 12)], 3)
    cracks.line([(sx - 40, sy - 14), (sx - 34, sy - 30)], 2.6)
    cracks.line([(sx + 70, sy - 10), (sx + 84, sy - 2), (sx + 100, sy - 6)], 2.6)
    cracks.line([(sx - 50, sy + 20), (sx - 30, sy + 26), (sx - 20, sy + 18)], 2.4)
    cracks = inter(cracks, head)
    glow(cv, cracks, LAVA, radius=4, strength=1.8)
    fill(cv, cracks, (255, 200, 90))
    holes = Layer(W, H)
    holes.circle(sx + 18, sy - 28, 10)
    holes.circle(sx + 54, sy - 24, 8.5)
    holes.circle(sx + 100, sy + 0, 3)
    holes.circle(sx + 90, sy - 2, 3)
    fill(cv, holes, HOLE)
    eyes = Layer(W, H)
    eyes.circle(sx + 20, sy - 27, 4.5)
    eyes.circle(sx + 55, sy - 23, 4)
    glow(cv, eyes, fc["aura"], radius=7, strength=2.2)
    fill(cv, eyes, _lt(fc["aura"], 80))
    mouth = Layer(W, H)
    mouth.curve([(sx - 30, sy + 20), (sx + 40, sy + 30), (sx + 106, sy + 16)], 3.2)
    fill(cv, mouth, HOLE)
    ember(cv, W, H, [(sx - 84, sy - 72, 3), (sx - 92, sy - 40, 2.5), (sx + 30, sy - 64, 2.5)], fc["aura"])
    finish(cv, W, H, _out(bone_id))


def draw_skull_mammoth(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.84
    sx, sy = cx - 24, cy + 8
    wool = (124, 80, 46)

    def tusk(dx, dy, dim, w0):
        t = Layer(W, H)
        pts = [(sx + rr * 0.6 + dx, sy + rr * 0.7 + dy), (sx + rr * 1.5 + dx, sy + rr * 1.35 + dy),
               (sx + rr * 2.35 + dx, sy + rr * 0.95 + dy), (sx + rr * 2.2 + dx, sy - rr * 0.15 + dy)]
        t.tapered(pts, w0, 4)
        paint(cv, t, base=tuple(int(c * dim) for c in IVORY_LIGHT), outline_w=3)
        path = bezier(pts, 24)
        band = Layer(W, H)
        bx, by = path[7]
        band.circle(bx, by, w0 * 0.6)
        paint(cv, inter(band, t), outline_w=1.8, grain=False, **GOLD_KW)
        return path[-1]
    tusk(-16, -10, 0.8, 24)
    # lã atrás e domo alto
    fur(cv, W, H, sx - rr * 0.8, sy + rr * 0.05, 12, 30, wool, 111, angle=190, spread=35)
    dome = Layer(W, H)
    dome.ellipse(sx - rr * 0.1, sy - rr * 0.45, rr * 0.82, rr * 0.75)
    paint(cv, dome, outline_w=3)
    draw_skull(cv, W, H, sx, sy, rr, snout=0.3, jaw=0.95, eye_color=fc["aura"])
    # capa de lã sobre o domo, caindo para trás
    for i, (ax, ay) in enumerate(((-0.75, -0.75), (-0.45, -1.05), (-0.1, -1.18), (0.25, -1.08), (0.5, -0.85))):
        fur(cv, W, H, sx + rr * ax, sy + rr * ay, 7, 30, wool if i % 2 else (146, 98, 58), 112 + i, angle=200 - i * 10, spread=25)
    accent_dots(cv, W, H, [(sx - rr * 0.98, sy + rr * 0.3), (sx - rr * 1.02, sy + rr * 0.52)], GOLD, 3.6)
    tip = tusk(0, 0, 1.0, 28)
    accent_dots(cv, W, H, [tip], fc["aura"], 3, glow_r=5)
    finish(cv, W, H, _out(bone_id))


def draw_skull_angler(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.8
    sx, sy = cx - 18, cy + 6
    # isca: haste saindo do alto da cabeça
    stalk = Layer(W, H)
    pts = [(sx + 2, sy - rr * 0.8), (sx + 4, sy - rr * 1.9), (sx + rr * 1.4, sy - rr * 2.05), (sx + rr * 1.72, sy - rr * 1.35)]
    stalk.tapered(pts, 9, 4)
    paint(cv, stalk, outline_w=2.4)
    bx, by = pts[-1][0], pts[-1][1] + 10
    bulb = Layer(W, H)
    bulb.circle(bx, by, 11)
    glow(cv, bulb, fc["aura"], radius=14, strength=2.4)
    paint(cv, bulb, base=_lt(fc["aura"], 40), shadow=fc["detail"], light=(240, 255, 255), outline_w=2.2, grain=False)
    core = Layer(W, H)
    core.circle(bx - 3, by - 3, 4)
    fill(cv, core, (255, 255, 255))
    # nadadeira atrás da cabeça
    fin = Layer(W, H)
    fin.poly([(sx - rr * 0.7, sy - rr * 0.5), (sx - rr * 1.5, sy - rr * 0.7), (sx - rr * 1.3, sy - rr * 0.2),
              (sx - rr * 1.55, sy + rr * 0.15), (sx - rr * 0.8, sy + rr * 0.3)])
    paint(cv, fin, base=(70, 160, 160), shadow=(30, 90, 96), light=(150, 220, 220), outline_w=2.4, grain=False)
    sp = Layer(W, H)
    for e in ((-1.5, -0.7), (-1.3, -0.2), (-1.55, 0.15)):
        sp.line([(sx - rr * 0.8, sy - rr * 0.1), (sx + rr * e[0], sy + rr * e[1])], 2.4)
    fill(cv, inter(sp, fin), IVORY)
    draw_skull(cv, W, H, sx, sy, rr, snout=0.25, jaw=0.6, eye_color=fc["aura"])
    # queixo enorme projetado com dentes de agulha
    jaw = Layer(W, H)
    jaw.poly([(sx - rr * 0.35, sy + rr * 0.62), (sx + rr * 1.6, sy + rr * 0.32), (sx + rr * 1.62, sy + rr * 0.6),
              (sx + rr * 1.2, sy + rr * 1.0), (sx - rr * 0.25, sy + rr * 1.1)])
    jaw.circle(sx - rr * 0.1, sy + rr * 0.86, rr * 0.26)
    teeth = Layer(W, H)
    for i in range(7):
        t = i / 6
        x = sx + rr * (0.1 + 1.42 * t)
        y = sy + rr * (0.62 - 0.24 * t)
        h = rr * (0.2 + 0.14 * math.sin(t * math.pi))
        teeth.poly([(x - 4, y + 4), (x + 1, y - h), (x + 4, y + 4)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=1.8, shade=False, grain=False)
    paint(cv, jaw, outline_w=3)
    ridge = Layer(W, H)
    ridge.line([(sx - rr * 0.1, sy + rr * 0.92), (sx + rr * 1.2, sy + rr * 0.7)], 2.4)
    fill(cv, ridge, (170, 150, 120))
    accent_dots(cv, W, H, [(sx + rr * 0.4, sy + rr * 0.86), (sx + rr * 0.9, sy + rr * 0.76)], (210, 240, 230), 3)
    finish(cv, W, H, _out(bone_id))


def draw_skull_croc(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.76
    sx, sy = cx - 52, cy + 24
    snout = 1.45
    # escudos nas costas da cabeça
    sc = Layer(W, H)
    for i in range(4):
        x = sx - rr * 0.85 + i * 15
        y = sy - rr * 0.72 - (i % 2) * 4
        sc.poly([(x - 8, y + 10), (x, y - 10), (x + 8, y + 10)])
    paint(cv, sc, outline_w=2, grain=False, **CROC_KW)
    m = draw_skull(cv, W, H, sx, sy, rr, snout=snout, jaw=0.8, eye_color=fc["aura"])
    # dentes tortos saindo por cima e por baixo da boca
    teeth = Layer(W, H)
    y = sy + rr * 0.64
    for i in range(9):
        x = sx + rr * (0.25 + i * 0.27)
        if i % 2:
            teeth.poly([(x - 4, y), (x, y + 13), (x + 4, y)])
        else:
            teeth.poly([(x - 4, y + 2), (x, y - 12), (x + 4, y + 2)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=1.6, shade=False, grain=False)
    # sobrancelha saliente e narina na ponta
    bumps = Layer(W, H)
    bumps.ellipse(sx + rr * (0.82 + snout), sy + rr * 0.08, 11, 9)
    paint(cv, bumps, outline_w=2.4)
    nose = Layer(W, H)
    nose.circle(sx + rr * (0.86 + snout), sy + rr * 0.06, 3)
    fill(cv, nose, HOLE)
    pits = Layer(W, H)
    for i in range(6):
        pits.circle(sx + rr * (1.0 + i * 0.22), sy + rr * (0.3 + (i % 2) * 0.08), 2)
    fill(cv, inter(pits, m), (170, 150, 120))
    accent_dots(cv, W, H, [(sx - rr * 0.6, sy - rr * 0.1)], fc["aura"], 3.5, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_skull_wraith(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    hx, hy = cx + 6, cy - 4
    cloth = (66, 40, 100)
    hood = Layer(W, H)
    hood.ellipse(hx - 4, hy - 6, 92, 98)
    hood.poly([(hx - 60, hy - 70), (hx - 92, hy - 116), (hx - 30, hy - 96)])
    hood.poly([(hx - 92, hy + 20), (hx - 96, hy + 90), (hx + 86, hy + 90), (hx + 88, hy + 20)])
    rag = Layer(W, H)
    for i in range(8):
        x = hx - 98 + i * 26
        rag.poly([(x, hy + 96), (x + 13, hy + 70 - (i % 2) * 10), (x + 26, hy + 96)])
    hood.cut(rag)
    glow(cv, hood, fc["aura"], radius=10, strength=0.9)
    paint(cv, hood, base=cloth, shadow=_dk(cloth, 0.5), light=(130, 96, 180), outline_w=3, grain=False, alpha=240)
    opening = Layer(W, H)
    opening.ellipse(hx + 14, hy + 10, 74, 80)
    fill(cv, inter(opening, hood), (22, 12, 34), alpha=240)
    draw_skull(cv, W, H, hx + 10, hy + 6, r * 0.78, snout=0.1, jaw=0.85, eye_color=fc["aura"], base=(222, 220, 238))
    rim = Layer(W, H)
    rim.curve([(hx - 66, hy + 70), (hx - 70, hy - 76), (hx + 40, hy - 92), (hx + 92, hy + 10)], 14)
    paint(cv, rim, base=(84, 52, 126), shadow=(44, 24, 70), light=(150, 110, 200), outline_w=2.6, grain=False)
    fold = Layer(W, H)
    fold.curve([(hx - 40, hy - 60), (hx - 74, hy - 20), (hx - 80, hy + 60)], 3)
    fill(cv, inter(fold, hood), (40, 22, 64), alpha=200)
    wisps = Layer(W, H)
    wisps.tapered([(hx - 66, hy + 86), (hx - 84, hy + 96), (hx - 100, hy + 90)], 8, 1)
    wisps.tapered([(hx + 56, hy + 86), (hx + 76, hy + 96), (hx + 94, hy + 88)], 8, 1)
    glow(cv, wisps, fc["aura"], radius=5, strength=1.4)
    fill(cv, wisps, (170, 140, 220), alpha=200)
    finish(cv, W, H, _out(bone_id))


def draw_skull_minotaur(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.86
    sx, sy = cx - 10, cy + 14

    def horn(pts, dim):
        h = Layer(W, H)
        h.tapered(pts, 26, 3)
        paint(cv, h, outline_w=3, **dict(HORN_KW, base=tuple(int(c * dim) for c in HORN)))
        path = bezier(pts, 20)
        rings = Layer(W, H)
        for i in (3, 6, 9):
            (x0, y0), (x1, y1) = path[i - 1], path[i + 1]
            dx, dy = x1 - x0, y1 - y0
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln * 16, dx / ln * 16
            rings.line([(path[i][0] - nx, path[i][1] - ny), (path[i][0] + nx, path[i][1] + ny)], 2.2)
        fill(cv, inter(rings, h), (150, 116, 76), alpha=200)
        tp = Layer(W, H)
        tp.circle(path[-1][0], path[-1][1], 9)
        paint(cv, inter(tp, h), outline_w=1.6, grain=False, **GOLD_KW)
    horn([(sx - rr * 0.35, sy - rr * 0.6), (sx - rr * 1.3, sy - rr * 0.7), (sx - rr * 1.45, sy - rr * 1.3), (sx - rr * 1.15, sy - rr * 1.85)], 0.8)
    ear = Layer(W, H)
    ear.poly([(sx - rr * 0.6, sy - rr * 0.2), (sx - rr * 1.25, sy - rr * 0.15), (sx - rr * 0.7, sy + rr * 0.15)])
    paint(cv, ear, outline_w=2.6)
    fur(cv, W, H, sx - rr * 0.75, sy + rr * 0.15, 8, 26, DARK_BROWN, 121, angle=170, spread=40)
    draw_skull(cv, W, H, sx, sy, rr, snout=0.6, jaw=1.0, eye_color=fc["aura"])
    brow = Layer(W, H)
    brow.curve([(sx - rr * 0.35, sy - rr * 0.32), (sx + rr * 0.25, sy - rr * 0.5), (sx + rr * 0.8, sy - rr * 0.32)], 11)
    paint(cv, brow, outline_w=2.4)
    horn([(sx + rr * 0.25, sy - rr * 0.72), (sx + rr * 1.15, sy - rr * 0.95), (sx + rr * 1.4, sy - rr * 1.45), (sx + rr * 1.05, sy - rr * 1.95)], 1.0)
    # argola de ouro no focinho
    ring = Layer(W, H)
    rx, ry = sx + rr * 1.42, sy + rr * 0.62
    ring.circle(rx, ry, 11)
    hole = Layer(W, H)
    hole.circle(rx, ry, 6.5)
    ring.cut(hole)
    glow(cv, ring, GOLD, radius=4, strength=0.8)
    paint(cv, ring, outline_w=1.8, grain=False, **GOLD_KW)
    finish(cv, W, H, _out(bone_id))


def draw_crown_matriarch(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.9
    sx, sy = cx - 4, cy + 16
    # pontas da coroa (osso) atrás de tudo, com halo
    band_pts = []
    for i in range(7):
        t = i / 6
        band_pts.append((sx - rr * 0.82 + t * rr * 1.6, sy - rr * 0.5 - math.sin(t * math.pi) * rr * 0.36))
    spikes = Layer(W, H)
    heights = [34, 50, 62, 78, 62, 50, 34]
    tips = []
    for (x, y), hgt in zip(band_pts, heights):
        tip = (x + (x - sx) * 0.12, y - hgt)
        spikes.tapered([(x, y + 6), ((x + tip[0]) / 2, (y + tip[1]) / 2), tip], 15, 3)
        tips.append(tip)
    halo = Layer(W, H)
    halo.ellipse(sx, sy - rr * 1.1, rr * 1.1, rr * 0.6)
    glow(cv, halo, fc["aura"], radius=22, strength=0.7)
    glow(cv, spikes, fc["aura"], radius=8, strength=1.2)
    paint(cv, spikes, base=IVORY_LIGHT, outline_w=2.6)
    # correntes com pérolas pendendo dos lados
    chain = Layer(W, H)
    chain.curve([(sx - rr * 0.82, sy - rr * 0.5), (sx - rr * 1.1, sy + rr * 0.1), (sx - rr * 0.8, sy + rr * 0.55)], 2.4)
    fill(cv, chain, GOLD)
    draw_skull(cv, W, H, sx, sy, rr, snout=0.12, jaw=0.9, eye_color=fc["aura"])
    band = Layer(W, H)
    band.line(band_pts, 14)
    paint(cv, band, outline_w=2.6, grain=False, **GOLD_KW)
    edge = Layer(W, H)
    edge.line([(x, y + 4) for x, y in band_pts], 2)
    fill(cv, edge, (150, 106, 24))
    gems = Layer(W, H)
    for i in (1, 3, 5):
        x, y = band_pts[i]
        rad = 7 if i == 3 else 5
        gems.poly([(x, y - rad), (x + rad * 0.8, y), (x, y + rad), (x - rad * 0.8, y)])
    glow(cv, gems, fc["aura"], radius=6, strength=2.2)
    paint(cv, gems, base=(170, 90, 250), shadow=(80, 30, 140), light=(230, 190, 255), outline_w=1.8, grain=False)
    pearls = [(sx - rr * 1.08, sy - rr * 0.05), (sx - rr * 1.02, sy + rr * 0.25), (sx - rr * 0.84, sy + rr * 0.52)] + \
             [(x, y) for (x, y) in tips[::2]]
    accent_dots(cv, W, H, pearls, (246, 236, 250), 3.6)
    ember(cv, W, H, [(sx - rr * 1.3, sy - rr * 1.4, 2.5), (sx + rr * 1.2, sy - rr * 1.2, 3), (sx + rr * 0.3, sy - rr * 2.0, 2.5)], fc["aura"])
    finish(cv, W, H, _out(bone_id))


def draw_skull_lich(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    rr = r * 0.88
    sx, sy = cx - 4, cy + 18
    purple = (150, 70, 240)
    # chamas roxas subindo do topo do crânio
    fl = Layer(W, H)
    for x, h, w, lean in ((-0.75, 54, 26, -0.25), (-0.4, 84, 30, -0.1), (0.0, 104, 34, 0.05), (0.38, 82, 30, 0.15),
                          (0.7, 52, 24, 0.3)):
        flame(fl, sx + rr * x, sy - rr * 0.55 - abs(x) * 6, h, w, lean)
    glow(cv, fl, purple, radius=16, strength=1.4)
    paint(cv, fl, base=(140, 70, 220), shadow=(70, 26, 130), light=(210, 160, 255), outline_w=2.4, grain=False)
    fl2 = Layer(W, H)
    for x, h, w, lean in ((-0.4, 52, 14, -0.1), (0.0, 66, 16, 0.05), (0.38, 50, 14, 0.15)):
        flame(fl2, sx + rr * x, sy - rr * 0.6, h, w, lean)
    fill(cv, fl2, (230, 200, 255), alpha=230)
    draw_skull(cv, W, H, sx, sy, rr, snout=0.1, jaw=0.95, eye_color=purple, base=(228, 222, 230))
    cracks = Layer(W, H)
    cracks.line([(sx - rr * 0.6, sy - rr * 0.6), (sx - rr * 0.48, sy - rr * 0.36), (sx - rr * 0.6, sy - rr * 0.18)], 2.2)
    fill(cv, cracks, (110, 90, 110))
    # tiara de ouro com gema
    band = []
    for i in range(7):
        t = i / 6
        band.append((sx - rr * 0.92 + t * rr * 1.75, sy - rr * 0.36 - math.sin(t * math.pi) * rr * 0.22))
    bl = Layer(W, H)
    bl.line(band, 9)
    paint(cv, bl, outline_w=2.4, grain=False, **GOLD_KW)
    gx, gy = band[4]
    gem = Layer(W, H)
    gem.poly([(gx, gy - 12), (gx + 8, gy), (gx, gy + 10), (gx - 8, gy)])
    glow(cv, gem, purple, radius=8, strength=2.4)
    paint(cv, gem, base=(180, 110, 255), shadow=(90, 40, 160), light=(240, 210, 255), outline_w=2, grain=False)
    accent_dots(cv, W, H, [band[1], band[6]], (180, 110, 255), 3, glow_r=4)
    ember(cv, W, H, [(sx - rr * 1.3, sy - rr * 1.5, 3), (sx + rr * 1.25, sy - rr * 1.7, 2.5), (sx + rr * 0.1, sy - rr * 2.4, 3),
                     (sx - rr * 0.6, sy - rr * 2.1, 2)], purple)
    finish(cv, W, H, _out(bone_id))


# ================================================================ costelas

def _rib_pts(cx, top, n, width, gap, i, side):
    y = top + 14 + i * gap
    ww = width * (1 - 0.12 * i)
    return bezier([(cx, y), (cx + side * ww * 0.65, y - 10), (cx + side * ww, y + 14), (cx + side * ww * 0.75, y + gap * 0.9)], 12)


def draw_ribs_clockwork(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    ribs = rib_mask(W, H, cx, 18, 4, 64, 27, 9)
    paint(cv, ribs, outline_w=3, **IRON_KW)
    bands = Layer(W, H)
    riv = Layer(W, H)
    for i in range(4):
        for side in (-1, 1):
            p = _rib_pts(cx, 18, 4, 64, 27, i, side)
            x, y = p[7]
            bands.circle(x, y, 7)
            riv.circle(p[4][0], p[4][1], 2.4)
            riv.circle(p[11][0], p[11][1], 2.4)
    paint(cv, bands, outline_w=2, grain=False, **BRASS_KW)
    fill(cv, riv, (220, 226, 236))
    gear(cv, W, H, cx + 20, 104, 15, kw=IRON_KW, n=7)
    gear(cv, W, H, cx, 70, 24, kw=BRASS_KW, n=10)
    gear(cv, W, H, cx - 22, 104, 11, kw=BRASS_KW, n=6, spokes=False)
    hub = Layer(W, H)
    hub.circle(cx, 70, 6)
    paint(cv, hub, outline_w=1.8, grain=False, **IRON_KW)
    accent_dots(cv, W, H, [(cx, 70)], fc["aura"], 3.6, glow_r=5)
    finish(cv, W, H, _out(bone_id))


def draw_ribs_ghoul(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    ribs = rib_mask(W, H, cx, 18, 4, 60, 27, 8.5)
    br = Layer(W, H)
    # costelas quebradas
    br.poly([(cx + 52, 100), (cx + 70, 96), (cx + 76, 140), (cx + 50, 140)])
    br.poly([(cx - 58, 70), (cx - 76, 64), (cx - 80, 92), (cx - 56, 86)])
    br.rrect(cx - 42, 132, cx - 30, 160, 2)
    ribs.cut(br)
    # tendões cinzentos ligando as costelas
    sin = Layer(W, H)
    for i in range(3):
        for side in (-1, 1):
            a = _rib_pts(cx, 18, 4, 60, 27, i, side)
            b = _rib_pts(cx, 18, 4, 60, 27, i + 1, side)
            p, q = a[8], b[6]
            sin.curve([p, ((p[0] + q[0]) / 2 + side * 5, (p[1] + q[1]) / 2), q], 3.4)
            p, q = a[4], b[3]
            sin.curve([p, ((p[0] + q[0]) / 2 - side * 3, (p[1] + q[1]) / 2 + 3), q], 2.6)
    e = _rib_pts(cx, 18, 4, 60, 27, 3, 1)[-1]
    sin.tapered([e, (e[0] + 4, e[1] + 6), (e[0] - 2, e[1] + 12)], 3, 1.2)
    paint(cv, sin, base=SINEW, shadow=_dk(SINEW, 0.6), light=(190, 186, 192), outline_w=1.6, grain=False)
    paint(cv, ribs, outline_w=2.8, **PALE_KW)
    wrap = Layer(W, H)
    for y in (34, 70, 102):
        wrap.rrect(cx - 9, y, cx + 9, y + 6, 2)
    paint(cv, wrap, base=SINEW, shadow=_dk(SINEW, 0.6), outline_w=1.6, grain=False)
    accent_dots(cv, W, H, [(cx, 22)], fc["aura"], 3.5, glow_r=5)
    finish(cv, W, H, _out(bone_id))


def draw_ribs_gargoyle(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    ribs = rib_mask(W, H, cx, 18, 4, 70, 27, 15)
    paint(cv, ribs, outline_w=3.2, **STONE_KW)
    grooves = Layer(W, H)
    for i in range(4):
        y = 18 + 14 + i * 27
        ww = 70 * (1 - 0.12 * i)
        for side in (-1, 1):
            grooves.curve([(cx + side * 14, y + 2), (cx + side * ww * 0.6, y - 6), (cx + side * ww * 0.95, y + 14)], 1.8)
    fill(cv, inter(grooves, ribs), (90, 92, 102), alpha=220)
    cracks = Layer(W, H)
    cracks.line([(cx - 60, 52), (cx - 52, 62), (cx - 58, 72)], 2)
    cracks.line([(cx + 48, 108), (cx + 56, 116)], 2)
    fill(cv, inter(cracks, ribs), (70, 72, 82))
    plate = Layer(W, H)
    plate.poly([(cx, 46), (cx + 20, 72), (cx, 100), (cx - 20, 72)])
    paint(cv, plate, outline_w=2.6, base=(126, 128, 138), shadow=(70, 72, 84), light=(190, 192, 204))
    runes(cv, W, H, cx, 72, 8, fc["aura"])
    moss = Layer(W, H)
    moss.ellipse(cx - 52, 40, 12, 5)
    moss.ellipse(cx + 60, 92, 9, 4)
    fill(cv, inter(moss, ribs), (110, 150, 80), alpha=220)
    finish(cv, W, H, _out(bone_id))


def draw_ribs_titan(bone_id, family):
    s, W, H, cv, cx = _ribs_setup()
    fc = fam(family)
    ice = (170, 220, 250)
    core = Layer(W, H)
    core.ellipse(cx, 80, 36, 40)
    glow(cv, core, fc["aura"], radius=16, strength=1.6)
    ribs = rib_mask(W, H, cx, 16, 4, 74, 30, 14)
    glow(cv, ribs, (150, 210, 255), radius=6, strength=0.8)
    paint(cv, ribs, base=(222, 232, 240), shadow=(120, 150, 180), light=(255, 255, 255), outline_w=3.2)
    heart = Layer(W, H)
    heart.poly([(cx, 56), (cx + 14, 76), (cx + 8, 102), (cx - 8, 102), (cx - 14, 76)])
    glow(cv, heart, fc["aura"], radius=10, strength=2.2)
    paint(cv, heart, base=(130, 200, 255), shadow=(50, 110, 200), light=(235, 250, 255), outline_w=2.4, grain=False)
    facet = Layer(W, H)
    facet.line([(cx, 58), (cx - 2, 100)], 1.6)
    fill(cv, facet, (235, 250, 255), alpha=200)

    def shard(m, x, y, ang, ln, w):
        ux, uy = _dir(ang)
        nx, ny = -uy, ux
        m.poly([(x + nx * w, y + ny * w), (x + ux * ln * 0.8 + nx * w, y + uy * ln * 0.8 + ny * w), (x + ux * ln, y + uy * ln),
                (x + ux * ln * 0.8 - nx * w, y + uy * ln * 0.8 - ny * w), (x - nx * w, y - ny * w)])
    cr = Layer(W, H)
    for side in (-1, 1):
        for i, (k, ang, ln, w) in enumerate(((5, -70, 24, 5.5), (8, -35, 20, 5), (8, -5, 16, 4.5), (9, 25, 16, 4.5))):
            x, y = _rib_pts(cx, 16, 4, 74, 30, i, side)[k]
            a = ang if side > 0 else 180 - ang
            shard(cr, x, y, a, ln, w)
            if i == 0:
                shard(cr, x - side * 10, y + 2, a - side * 30, ln * 0.7, w * 0.8)
    glow(cv, cr, (160, 220, 255), radius=6, strength=1.4)
    paint(cv, cr, base=ice, shadow=(80, 140, 200), light=(245, 252, 255), outline_w=2.2, grain=False, alpha=235)
    frost = Layer(W, H)
    for x, y in ((-40, 50), (38, 46), (-30, 110), (34, 118), (-56, 88), (58, 86)):
        frost.circle(cx + x, y, 3)
    fill(cv, inter(frost, ribs), (255, 255, 255))
    accent_dots(cv, W, H, [(cx - 70, 12), (cx + 74, 140), (cx - 70, 146), (cx + 60, 8)], (220, 245, 255), 2.2, glow_r=5)
    finish(cv, W, H, _out(bone_id))


# ================================================================ braços

def draw_claw_ghoul(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    arm = Layer(W, H)
    arm.bone((cx, Y(6)), (cx + 2, Y(86)), 6.5)
    arm.bone((cx + 2, Y(92)), (cx - 2, Y(150)), 5.5)
    paint(cv, arm, outline_w=2.8, **PALE_KW)
    wrap = Layer(W, H)
    for y in (40, 52, 112, 124):
        wrap.poly(rot_rect(cx + 1, Y(y), 6, 18, 80))
    paint(cv, wrap, base=SINEW, shadow=_dk(SINEW, 0.6), outline_w=1.6, grain=False)
    hand = Layer(W, H)
    hand.ellipse(cx - 2, Y(160), 13, 11)
    tips = []
    for dx, ex in ((-10, -26), (-3, -8), (4, 10), (10, 26)):
        e = (cx + ex, Y(224))
        mid = (cx + dx + ex * 0.4, Y(192))
        hand.tapered([(cx + dx * 0.6, Y(164)), mid], 6, 4.5)
        hand.circle(mid[0], mid[1], 3.6)
        hand.tapered([mid, e], 4.5, 1.2)
        tips.append(e)
    thumb = (cx - 18, Y(172))
    hand.tapered([(cx - 8, Y(160)), thumb, (cx - 22, Y(188))], 5, 1.2)
    paint(cv, hand, outline_w=2.4, **PALE_KW)
    accent_dots(cv, W, H, [(cx + 2, Y(89))], fc["aura"], 3.4, glow_r=5)
    accent_dots(cv, W, H, tips[1:3], fc["aura"], 2, glow_r=3)
    finish(cv, W, H, _out(bone_id))


def draw_tusk_mammoth(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.62), outline_w=3)
    pts = [(cx, Y(140)), (cx + 40, Y(176)), (cx + 26, Y(222)), (cx - 30, Y(224))]
    tusk = Layer(W, H)
    tusk.tapered(pts, 30, 4)
    paint(cv, tusk, base=IVORY_LIGHT, outline_w=3)
    path = bezier(pts, 20)
    grain_l = Layer(W, H)
    grain_l.line([(x - 4, y - 4) for x, y in path[3:15]], 1.8)
    fill(cv, inter(grain_l, tusk), (200, 186, 156), alpha=200)
    band = Layer(W, H)
    bx, by = path[6]
    band.circle(bx, by, 16)
    paint(cv, inter(band, tusk), outline_w=2, grain=False, **GOLD_KW)
    fur(cv, W, H, cx, Y(140), 12, 26, BROWN, 141, angle=90, spread=80)
    cuff = Layer(W, H)
    cuff.rrect(cx - 16, Y(126), cx + 16, Y(140), 5)
    paint(cv, cuff, outline_w=2.2, grain=False, **GOLD_KW)
    accent_dots(cv, W, H, [(cx, Y(133))], fc["aura"], 3.4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_mandible_locust(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.5), outline_w=3)
    base = Layer(W, H)
    base.ellipse(cx, Y(140), 18, 15)
    paint(cv, base, outline_w=2.8, **OLIVE_KW)
    outer = bezier([(cx - 10, Y(134)), (cx + 44, Y(160)), (cx + 38, Y(214)), (cx - 6, Y(228))], 20)
    inner = bezier([(cx - 6, Y(228)), (cx + 16, Y(200)), (cx + 14, Y(168)), (cx - 8, Y(150))], 20)
    blade = Layer(W, H)
    blade.poly(outer + inner)
    teeth = Layer(W, H)
    for i in (4, 8, 12, 16):
        x, y = inner[i]
        teeth.poly([(x + 2, y - 6), (x - 11, y), (x + 2, y + 6)])
    blade.add(teeth)
    paint(cv, blade, outline_w=3, **OLIVE_KW)
    edge = Layer(W, H)
    edge.line(outer[4:17], 3)
    fill(cv, inter(edge, blade), (230, 220, 150))
    stripes = Layer(W, H)
    for i in (6, 11):
        x, y = outer[i]
        stripes.line([(x - 4, y), (x - 24, y + 4)], 3)
    fill(cv, inter(stripes, blade), (86, 78, 30), alpha=200)
    accent_dots(cv, W, H, [(cx, Y(140))], fc["aura"], 3.6, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_claw_wyvern(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    green = (92, 140, 64)
    gkw = dict(base=green, shadow=(44, 80, 30), light=(160, 210, 110))
    spikes = Layer(W, H)
    for i, y in enumerate((70, 84, 98)):
        spikes.poly([(cx - 6, Y(y) - 6), (cx - 26 + i * 3, Y(y + 4)), (cx - 6, Y(y) + 8)])
    paint(cv, spikes, base=(200, 56, 40), shadow=(110, 20, 14), light=(255, 130, 90), outline_w=2, grain=False)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.8), outline_w=3)
    sc = Layer(W, H)
    for i in range(4):
        y = Y(106) + i * 12
        sc.poly([(cx - 10, y), (cx, y + 11), (cx + 10, y)])
    paint(cv, sc, outline_w=1.6, grain=False, **gkw)
    hand = Layer(W, H)
    hand.ellipse(cx, Y(176), 22, 17)
    tips = []
    for dx, ex in ((-14, -32), (0, 2), (14, 32)):
        k = (cx + ex * 0.75, Y(196))
        hand.tapered([(cx + dx, Y(180)), k], 12, 9)
        tips.append(k)
    paint(cv, hand, outline_w=3, **gkw)
    claws = Layer(W, H)
    for (x, y), ex in zip(tips, (-1, 0, 1)):
        claws.tapered([(x, y), (x + ex * 6 + 8, y + 12), (x + ex * 4 - 2, y + 24)], 11, 1)
    glow(cv, claws, fc["aura"], radius=5, strength=1.2)
    paint(cv, claws, base=(70, 56, 50), shadow=(30, 22, 20), light=(160, 140, 130), outline_w=2.2, grain=False)
    band = Layer(W, H)
    band.rrect(cx - 12, Y(148), cx + 12, Y(160), 4)
    paint(cv, band, outline_w=2, grain=False, **GOLD_KW)
    accent_dots(cv, W, H, [(cx, Y(154))], fc["aura"], 3, glow_r=4)
    ember(cv, W, H, [(cx + 30, Y(150), 2.4), (cx - 30, Y(120), 2.2)], fc["aura"])
    finish(cv, W, H, _out(bone_id))


def draw_fist_sentinel(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.6), outline_w=3)
    brace = Layer(W, H)
    brace.poly([(cx - 14, Y(104)), (cx + 16, Y(100)), (cx + 20, Y(146)), (cx - 18, Y(150))])
    paint(cv, brace, outline_w=3, **OBS_KW)
    fist = Layer(W, H)
    fist.poly([(cx - 34, Y(156)), (cx - 10, Y(146)), (cx + 26, Y(150)), (cx + 40, Y(176)), (cx + 34, Y(216)),
               (cx - 28, Y(220)), (cx - 40, Y(190))])
    paint(cv, fist, outline_w=3.2, **OBS_KW)
    knuck = Layer(W, H)
    for i in range(4):
        x = cx - 28 + i * 18
        knuck.poly([(x, Y(204)), (x + 8, Y(196)), (x + 16, Y(204)), (x + 8, Y(220))])
    paint(cv, knuck, outline_w=1.8, grain=False, base=(70, 66, 86), shadow=(30, 28, 40), light=(150, 146, 180))
    shine = Layer(W, H)
    shine.line([(cx - 24, Y(162)), (cx - 8, Y(154))], 2.4)
    shine.line([(cx - 8, Y(110)), (cx + 6, Y(108))], 2)
    fill(cv, shine, (200, 200, 230), alpha=200)
    seam = Layer(W, H)
    seam.line([(cx - 20, Y(180)), (cx, Y(170)), (cx + 28, Y(178))], 2.6)
    glow(cv, seam, fc["aura"], radius=4, strength=1.6)
    fill(cv, seam, _lt(fc["aura"], 60))
    runes(cv, W, H, cx + 1, Y(126), 7, fc["aura"])
    finish(cv, W, H, _out(bone_id))


def draw_stinger_hornet(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.45), outline_w=3)
    st = Layer(W, H)
    st.tapered([(cx, Y(188)), (cx + 6, Y(204)), (cx + 2, Y(220))], 14, 1.5)
    paint(cv, st, base=(50, 40, 34), shadow=(20, 16, 14), light=(130, 116, 104), outline_w=2.6)
    ab = Layer(W, H)
    ab.ellipse(cx, Y(164), 26, 34)
    paint(cv, ab, base=(222, 130, 40), shadow=(140, 70, 16), light=(255, 200, 120), outline_w=3)
    bands = Layer(W, H)
    for y in (148, 166, 184):
        bands.rrect(cx - 30, Y(y), cx + 30, Y(y) + 8, 3)
    fill(cv, inter(bands, ab), (70, 40, 20))
    top_c = Layer(W, H)
    top_c.ellipse(cx, Y(132), 14, 9)
    paint(cv, top_c, base=(70, 40, 20), shadow=(36, 20, 10), outline_w=2.2, grain=False)
    gloss = Layer(W, H)
    gloss.ellipse(cx - 12, Y(150), 4, 9)
    fill(cv, gloss, (255, 240, 210), alpha=170)
    accent_dots(cv, W, H, [(cx + 2, Y(219))], fc["aura"], 3.4, glow_r=5)
    finish(cv, W, H, _out(bone_id))


# ================================================================ pernas

def draw_legs_clockwork(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    hip = Layer(W, H)
    hip.rrect(cx - 56, top - 8, cx + 56, top + 16, 8)
    paint(cv, hip, outline_w=3, **IRON_KW)
    knees = []
    rods = Layer(W, H)
    pist = Layer(W, H)
    for side in (-1, 1):
        h = (cx + side * 40, top + 8)
        k = (cx + side * 46, top + 104)
        a = (cx + side * 38, H - 40)
        rods.capsule(h, k, 7)
        rods.capsule(k, a, 6)
        pist.capsule((h[0] + side * 14, h[1] + 20), (k[0] + side * 12, k[1] - 26), 6)
        knees.append(k)
    paint(cv, pist, outline_w=2.4, **BRASS_KW)
    paint(cv, rods, outline_w=3, **IRON_KW)
    for side in (-1, 1):
        gear(cv, W, H, cx + side * 40, top + 8, 17, n=8)
    for k in knees:
        gear(cv, W, H, k[0], k[1], 15, n=7)
    feet = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 40
        feet.rrect(x - 26, H - 42, x + 26, H - 10, 7)
        feet.poly([(x + side * 20, H - 40), (x + side * 38, H - 18), (x + side * 22, H - 10)])
    paint(cv, feet, outline_w=3, **IRON_KW)
    riv = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 40
        for dx in (-16, 0, 16):
            riv.circle(x + dx, H - 26, 2.4)
    fill(cv, riv, (210, 216, 230))
    accent_dots(cv, W, H, [(cx - 40, top + 8), (cx + 40, top + 8)] + knees, fc["aura"], 3.4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_legs_locust(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    legs = Layer(W, H)
    spines = Layer(W, H)
    feet = Layer(W, H)
    joints = []
    femurs = []
    for side in (-1, 1):
        hp = (cx + side * 24, top + 12)
        kn = (cx + side * 96, top - 4)
        md = (cx + side * 86, top + 104)
        ft = (cx + side * 58, H - 24)
        fm = [hp, ((hp[0] + kn[0]) / 2 + side * 4, (hp[1] + kn[1]) / 2 + 22), kn]
        ang = math.degrees(math.atan2(kn[1] - hp[1], kn[0] - hp[0]))
        ln = math.hypot(kn[0] - hp[0], kn[1] - hp[1])
        c = ((hp[0] + kn[0]) / 2 - side * 4, (hp[1] + kn[1]) / 2 + 4)
        legs.poly(rot_ellipse(c[0], c[1], ln * 0.55, 17, ang))
        legs.circle(kn[0], kn[1], 8)
        femurs.append([hp, c, kn])
        legs.tapered([kn, md], 8.5, 7)
        legs.tapered([md, ft], 7, 5)
        for t in (0.2, 0.4, 0.6, 0.8):
            for a, b in ((kn, md), (md, ft)):
                x = a[0] + (b[0] - a[0]) * t
                y = a[1] + (b[1] - a[1]) * t
                spines.poly([(x - side * 2, y - 4), (x - side * 12, y + 3), (x - side * 2, y + 4)])
        f1 = (ft[0] + side * 22, H - 12)
        feet.tapered([ft, f1], 6, 4)
        feet.tapered([f1, (f1[0] + side * 10, f1[1] + 2), (f1[0] + side * 12, f1[1] - 6)], 4, 1.5)
        joints += [kn, md]
    paint(cv, spines, outline_w=1.6, grain=False, **OLIVE_KW)
    paint(cv, legs, outline_w=3, **OLIVE_KW)
    paint(cv, feet, outline_w=2.2, grain=False, **OLIVE_KW)
    chev = Layer(W, H)
    for fm in femurs:
        path = bezier(fm, 20)
        for i in (5, 9, 13):
            (x0, y0), (x1, y1) = path[i - 1], path[i + 1]
            dx, dy = x1 - x0, y1 - y0
            ln = math.hypot(dx, dy) or 1
            ux, uy = dx / ln, dy / ln
            nx, ny = -uy, ux
            x, y = path[i]
            w = 12 - i * 0.5
            chev.line([(x + nx * w - ux * 6, y + ny * w - uy * 6), (x + ux * 4, y + uy * 4), (x - nx * w - ux * 6, y - ny * w - uy * 6)], 2.4)
    fill(cv, inter(chev, legs), (86, 78, 30), alpha=220)
    paint(cv, _pelvis(W, H, cx, top + 4, 34, 13), outline_w=2.8)
    accent_dots(cv, W, H, joints, fc["aura"], 3.4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_legs_minotaur(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    for side in (-1, 1):
        fur(cv, W, H, cx + side * 46, top + 40, 12, 34, BROWN, 151 + side, angle=90 - side * 60, spread=40)
        fur(cv, W, H, cx + side * 50, top + 84, 9, 30, BROWN, 153 + side, angle=90 - side * 45, spread=30)
    paint(cv, _pelvis(W, H, cx, top, 54, 18), outline_w=3)
    thighs = Layer(W, H)
    for side in (-1, 1):
        thighs.tapered([(cx + side * 38, top + 8), (cx + side * 52, top + 56), (cx + side * 46, top + 104)], 50, 26)
    paint(cv, thighs, base=(130, 86, 50), shadow=(76, 46, 24), light=(184, 136, 90), outline_w=3)
    legs = Layer(W, H)
    for side in (-1, 1):
        kn = (cx + side * 46, top + 104)
        hk = (cx + side * 36, top + 160)
        an = (cx + side * 44, H - 44)
        legs.bone(kn, hk, 10)
        legs.bone(hk, an, 8.5)
    paint(cv, legs, outline_w=3)
    fur(cv, W, H, cx - 44, H - 48, 7, 18, BROWN, 155, angle=90, spread=50)
    fur(cv, W, H, cx + 44, H - 48, 7, 18, BROWN, 156, angle=90, spread=50)
    hooves = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 44
        hooves.poly([(x - 22, H - 6), (x - 18, H - 34), (x + 18, H - 34), (x + 24, H - 6)])
    paint(cv, hooves, base=(64, 48, 40), shadow=(30, 22, 18), light=(130, 110, 100), outline_w=3)
    split = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 44
        split.line([(x + 1, H - 22), (x + 2, H - 4)], 3)
    fill(cv, split, OUTLINE)
    anklet = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 44
        anklet.rrect(x - 17, H - 44, x + 17, H - 34, 4)
    paint(cv, anklet, outline_w=2, grain=False, **GOLD_KW)
    accent_dots(cv, W, H, [(cx - 44, H - 39), (cx + 44, H - 39)], fc["aura"], 3, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_legs_sentinel(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    hip = Layer(W, H)
    hip.poly([(cx - 74, top - 6), (cx + 74, top - 6), (cx + 62, top + 26), (cx - 62, top + 26)])
    paint(cv, hip, outline_w=3.2, **OBS_KW)
    plates = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 46
        plates.poly([(x - 26, top + 26), (x + 26, top + 26), (x + 20, top + 104), (x - 20, top + 104)])
        plates.poly([(x - 20, top + 124), (x + 20, top + 124), (x + 24, H - 50), (x - 24, H - 50)])
    paint(cv, plates, outline_w=3.2, **OBS_KW)
    knees = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 46
        knees.poly([(x, top + 92), (x + 20, top + 114), (x, top + 136), (x - 20, top + 114)])
    paint(cv, knees, outline_w=2.8, base=(76, 70, 96), shadow=(30, 28, 40), light=(160, 156, 190))
    feet = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 46
        feet.poly([(x - 26, H - 52), (x + 26, H - 52), (x + 30, H - 8), (x - 30, H - 8)])
        feet.poly([(x + side * 20, H - 40), (x + side * 46, H - 8), (x + side * 20, H - 8)])
    paint(cv, feet, outline_w=3.2, **OBS_KW)
    shine = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 46
        shine.line([(x - 16, top + 34), (x - 12, top + 80)], 2.2)
        shine.line([(x - 12, top + 132), (x - 10, H - 62)], 2)
    fill(cv, shine, (190, 186, 220), alpha=170)
    seams = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 46
        seams.line([(x - 22, top + 60), (x + 22, top + 64)], 2.6)
        seams.line([(x - 22, H - 90), (x + 22, H - 86)], 2.6)
    seams = inter(seams, plates)
    glow(cv, seams, fc["aura"], radius=4, strength=1.6)
    fill(cv, seams, _lt(fc["aura"], 60))
    runes(cv, W, H, cx, top + 10, 7, fc["aura"])
    accent_dots(cv, W, H, [(cx - 46, top + 114), (cx + 46, top + 114)], fc["aura"], 3.4, glow_r=5)
    finish(cv, W, H, _out(bone_id))


# ================================================================ costas

def draw_wings_moth(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    col = (146, 118, 156)
    dark = (84, 62, 96)

    def wing(root, ang, ln, wd, dim, spot_t):
        c = tuple(int(v * dim) for v in col)
        m = Layer(W, H)
        m.poly(leaf_pts(root, ang, ln, wd, power=0.45, base_w=wd * 0.2))
        paint(cv, m, base=c, shadow=_dk(c, 0.6), light=_lt(c, 50), outline_w=2.6, grain=False)
        band = Layer(W, H)
        band.poly(leaf_pts(root, ang, ln * 0.82, wd * 0.72, power=0.45))
        edge = m.copy()
        edge.cut(band)
        fill(cv, edge, tuple(int(v * dim) for v in dark), alpha=200)
        v = Layer(W, H)
        for k in (-0.5, 0, 0.5):
            v.line([root, leaf_axis(root, ang, ln, 0.8, k * wd)], 1.6)
        fill(cv, inter(v, m), _dk(c, 0.6), alpha=170)
        if spot_t:
            x, y = leaf_axis(root, ang, ln, spot_t, wd * 0.1)
            rs = wd * 0.32
            sp = Layer(W, H)
            sp.circle(x, y, rs)
            paint(cv, sp, base=tuple(int(v * dim) for v in (236, 206, 120)), shadow=(160, 120, 50), outline_w=1.8, grain=False)
            pupil = Layer(W, H)
            pupil.circle(x, y, rs * 0.6)
            fill(cv, pupil, (36, 22, 40))
            dot = Layer(W, H)
            dot.circle(x - rs * 0.15, y - rs * 0.15, rs * 0.25)
            glow(cv, dot, fc["aura"], radius=4, strength=1.6)
            fill(cv, dot, _lt(fc["aura"], 60))
    wing((px + 6, py - 8), -62, 118, 40, 0.68, 0.6)
    wing((px + 4, py - 2), -28, 86, 34, 0.68, 0)
    wing((px - 4, py + 4), -172, 140, 50, 1.0, 0.58)
    wing((px - 4, py - 4), -132, 186, 58, 1.0, 0.62)
    fur(cv, W, H, px, py, 9, 18, (180, 160, 180), 161, angle=-90, spread=90)
    root_knob(cv, W, H, px, py, 12)
    accent_dots(cv, W, H, [(px, py)], fc["aura"], 4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_fin_angler(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    spine = bezier([(px + 24, py + 6), (px - 40, py - 22), (px - 130, py - 16), (px - 180, py + 24)], 7)
    heights = [44, 96, 134, 150, 124, 86, 46]
    tips = [(x - h * 0.3, y - h) for (x, y), h in zip(spine, heights)]
    mem = Layer(W, H)
    poly = [spine[0]]
    for i, t in enumerate(tips):
        poly.append(t)
        if i < len(tips) - 1:
            n = tips[i + 1]
            b0, b1 = spine[i], spine[i + 1]
            mx, my = (t[0] + n[0]) / 2, (t[1] + n[1]) / 2
            bx, by = (b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2
            poly.append((mx + (bx - mx) * 0.32, my + (by - my) * 0.32))
    poly += [spine[-1]] + spine[::-1]
    mem.poly(poly)
    paint(cv, mem, base=(70, 160, 160), shadow=(30, 90, 96), light=(150, 225, 220), outline_w=2.6, grain=False, alpha=225)
    st = Layer(W, H)
    for (x, y), (tx, ty) in zip(spine, tips):
        st.tapered([(x, y), ((x + tx) / 2 + 3, (y + ty) / 2), (tx, ty)], 9, 2)
    paint(cv, st, outline_w=2.2)
    vert = Layer(W, H)
    for x, y in spine:
        vert.ellipse(x, y, 15, 12)
    paint(cv, vert, outline_w=2.6)
    accent_dots(cv, W, H, [tips[3]], fc["aura"], 5, glow_r=9)
    accent_dots(cv, W, H, [spine[2], spine[4]], (210, 240, 230), 3.2)
    finish(cv, W, H, _out(bone_id))


BAT_ELBOW = (-70, -112)
BAT_TIPS = [(-196, -150), (-204, -86), (-182, -26), (-128, 22)]


def draw_wings_gargoyle(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)

    def deco(mem, el, tps, f, dim):
        cr = Layer(W, H)
        cr.line([(el[0] - 20 * f, el[1] + 30 * f), (el[0] - 44 * f, el[1] + 50 * f), (el[0] - 40 * f, el[1] + 76 * f)], 2.2)
        cr.line([(el[0] + 10 * f, el[1] + 60 * f), (el[0] - 6 * f, el[1] + 90 * f)], 2)
        cr.line([(tps[1][0] + 30 * f, tps[1][1] + 6 * f), (tps[1][0] + 54 * f, tps[1][1] + 20 * f)], 2)
        fill(cv, inter(cr, mem), _dk(STONE, 0.45 * dim))
        moss = Layer(W, H)
        moss.ellipse(px - 30 * f, py + 14 * f, 14 * f, 5 * f)
        fill(cv, inter(moss, mem), (110, 150, 80), alpha=int(220 * dim))
    membrane_wings(cv, W, H, px, py, (126, 128, 138), STONE_KW, BAT_ELBOW, BAT_TIPS, k=0.96, decorate=deco,
                   bone_w=9.5, scallop=0.14)
    root_knob(cv, W, H, px, py, 13)
    runes(cv, W, H, px + 70 * 0.72 * 0.96 * -1, py - 112 * 0.72 * 0.96 + 26, 5, fc["aura"])
    finish(cv, W, H, _out(bone_id))


def draw_wings_wyvern(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    elbow = (-60, -124)
    tips = [(-200, -168), (-206, -100), (-182, -40), (-122, 14)]

    def deco(mem, el, tps, f, dim):
        v = Layer(W, H)
        for a, b in zip(tps, tps[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            v.curve([el, ((el[0] + mx) / 2 + 6, (el[1] + my) / 2 + 6), (mx, my)], 1.8)
        fill(cv, inter(v, mem), _dk((84, 128, 60), 0.5 * dim), alpha=200)
        sp = Layer(W, H)
        for i in range(4):
            t = 0.2 + i * 0.2
            x, y = px + (el[0] - px) * t, py + (el[1] - py) * t
            sp.poly([(x - 6 * f, y), (x + 4 * f, y - 16 * f), (x + 8 * f, y + 2 * f)])
        paint(cv, sp, base=tuple(int(c * dim) for c in (200, 56, 40)), shadow=(110, 20, 14), outline_w=1.8, grain=False)
    res = membrane_wings(cv, W, H, px, py, (84, 128, 60), dict(base=IVORY, shadow=IVORY_SHADOW, light=IVORY_LIGHT),
                         elbow, tips, k=0.92, decorate=deco)
    mem, el, tps, f, dim = res[-1]
    hooks = Layer(W, H)
    for tp in tps[:3]:
        hooks.tapered([tp, (tp[0] - 8, tp[1] + 2), (tp[0] - 10, tp[1] + 12)], 5, 1)
    paint(cv, hooks, base=(70, 56, 50), shadow=(30, 22, 20), outline_w=1.8, grain=False)
    accent_dots(cv, W, H, [el, (px + (el[0] - px) * 0.5, py + (el[1] - py) * 0.5)], GOLD, 4)
    root_knob(cv, W, H, px, py, 13)
    ember(cv, W, H, [(px - 150, py - 130, 3), (px - 90, py - 30, 2.5), (px + 70, py - 120, 2.5)], fc["aura"])
    finish(cv, W, H, _out(bone_id))


def draw_wings_obsidian(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    red = (255, 60, 30)
    elbow = (-64, -120)
    tips = [(-204, -164), (-208, -96), (-184, -32), (-126, 18)]
    # brilho vermelho por trás das asas
    gl = Layer(W, H)
    for sc in (0.72 * 0.9, 0.9):
        el = (px + elbow[0] * sc, py + elbow[1] * sc)
        gl.poly([(px, py), el] + [(px + x * sc, py + y * sc) for x, y in tips] + [(px, py + 30)])
    glow(cv, gl, red, radius=14, strength=1.1)

    def deco(mem, el, tps, f, dim):
        v = Layer(W, H)
        for a, b in zip(tps, tps[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            v.line([el, (mx + (el[0] - mx) * 0.25, my + (el[1] - my) * 0.25)], 2.2)
            v.line([((el[0] + mx) / 2, (el[1] + my) / 2), ((el[0] + mx) / 2 - 16 * f, (el[1] + my) / 2 + 14 * f)], 1.6)
        v = inter(v, mem)
        glow(cv, v, red, radius=4, strength=1.6 * dim)
        fill(cv, v, (255, 150, 90), alpha=int(230 * dim))
        sh = Layer(W, H)
        sh.line([(px - 30 * f, py - 30 * f), (el[0] - 20 * f, el[1] + 40 * f)], 3)
        fill(cv, inter(sh, mem), (150, 140, 170), alpha=int(120 * dim))
    res = membrane_wings(cv, W, H, px, py, (40, 30, 44), dict(base=(78, 70, 92), shadow=(30, 26, 38), light=(170, 160, 200)),
                         elbow, tips, k=0.9, decorate=deco, bone_w=9)
    mem, el, tps, f, dim = res[-1]
    spikes = Layer(W, H)
    for i in range(4):
        t = 0.2 + i * 0.2
        x, y = px + (el[0] - px) * t, py + (el[1] - py) * t
        spikes.poly([(x - 8, y + 2), (x + 2, y - 22), (x + 8, y + 4)])
    for tp in tps[:3]:
        spikes.tapered([tp, (tp[0] - 10, tp[1] - 2), (tp[0] - 14, tp[1] + 10)], 6, 1)
    glow(cv, spikes, red, radius=4, strength=0.9)
    paint(cv, spikes, base=(56, 48, 66), shadow=(20, 16, 26), light=(170, 160, 200), outline_w=2, grain=False)
    root_knob(cv, W, H, px, py, 14)
    gem = Layer(W, H)
    gem.poly([(px, py - 10), (px + 8, py), (px, py + 10), (px - 8, py)])
    glow(cv, gem, red, radius=6, strength=2.0)
    paint(cv, gem, base=(220, 40, 30), shadow=(120, 10, 10), light=(255, 160, 120), outline_w=1.8, grain=False)
    ember(cv, W, H, [(px - 120, py - 160, 3.5), (px - 190, py - 60, 3), (px - 60, py - 10, 2.5), (px + 60, py - 140, 3),
                     (px - 20, py - 180, 2.5), (px + 30, py - 40, 2.5)], red)
    finish(cv, W, H, _out(bone_id))


def draw_wings_hornet(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    col, vein = (255, 228, 168), (140, 84, 34)
    insect_wing(cv, W, H, (px + 6, py - 10), -80, 128, 24, col, vein, dim=0.85, alpha=160)
    insect_wing(cv, W, H, (px + 4, py - 4), -52, 88, 18, col, vein, dim=0.85, alpha=160)
    insect_wing(cv, W, H, (px - 4, py - 6), -122, 176, 30, col, vein, alpha=170, n_side=5)
    insect_wing(cv, W, H, (px - 4, py), -158, 118, 23, col, vein, alpha=170)
    stig = Layer(W, H)
    x, y = leaf_axis((px - 4, py - 6), -122, 176, 0.62, -30 * 0.55)
    stig.ellipse(x, y, 6, 4)
    fill(cv, stig, (110, 60, 24), alpha=230)
    th = Layer(W, H)
    th.circle(px, py, 15)
    paint(cv, th, base=(120, 66, 30), shadow=(60, 30, 12), light=(200, 130, 70), outline_w=2.6)
    band = Layer(W, H)
    band.rrect(px - 16, py - 3, px + 16, py + 4, 2)
    fill(cv, inter(band, th), (236, 170, 50))
    accent_dots(cv, W, H, [(px - 2, py - 8)], fc["aura"], 4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_shroud_wraith(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    cloth = (70, 44, 110)
    top = bezier([(px + 18, py - 26), (px - 60, py - 116), (px - 130, py - 160), (px - 166, py - 136)], 16)
    bot = bezier([(px + 12, py + 50), (px - 70, py + 56), (px - 130, py + 6), (px - 166, py - 70)], 16)
    ragged = []
    r = rng(171)
    left = bezier([(px - 166, py - 136), (px - 178, py - 104), (px - 166, py - 70)], 8)
    for i, (x, y) in enumerate(left):
        ragged.append((x - (16 if i % 2 else 0) - r.uniform(0, 6), y))
    bot_r = []
    for i, (x, y) in enumerate(bot[::-1]):
        dy = 22 if i % 2 else 0
        bot_r.append((x + r.uniform(-4, 4), y + dy * (0.3 + 0.7 * i / len(bot))))
    poly = top + ragged + bot_r
    m = Layer(W, H)
    m.poly(poly)
    glow(cv, m, fc["aura"], radius=14, strength=0.9)
    paint(cv, m, base=cloth, shadow=_dk(cloth, 0.5), light=(140, 104, 190), outline_w=2.8, grain=False, alpha=215)
    folds = Layer(W, H)
    for k in range(4):
        folds.curve([(px - 10 - k * 6, py - 10 + k * 12), (px - 90 - k * 10, py - 76 + k * 22), (px - 160 + k * 6, py - 116 + k * 26)], 3)
    fill(cv, inter(folds, m), (40, 22, 66), alpha=200)
    hl = Layer(W, H)
    hl.curve([(px - 30, py - 50), (px - 100, py - 106), (px - 170, py - 128)], 3)
    fill(cv, inter(hl, m), (170, 140, 220), alpha=150)
    wisps = Layer(W, H)
    for x, y, ex in ((px - 180, py - 120, -16), (px - 150, py + 10, -26), (px - 90, py + 62, -20)):
        wisps.tapered([(x, y), (x + ex * 0.6, y + 10), (x + ex, y + 4)], 8, 1)
    glow(cv, wisps, fc["aura"], radius=5, strength=1.3)
    fill(cv, wisps, (180, 150, 230), alpha=190)
    clasp = Layer(W, H)
    clasp.ellipse(px, py - 4, 16, 14)
    paint(cv, clasp, outline_w=2.6)
    eye = Layer(W, H)
    eye.circle(px - 5, py - 6, 3.4)
    eye.circle(px + 5, py - 6, 3.4)
    glow(cv, eye, fc["aura"], radius=4, strength=2)
    fill(cv, eye, _lt(fc["aura"], 60))
    finish(cv, W, H, _out(bone_id))


def draw_shell_behemoth(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    cx, cy = px - 40, py - 26
    rock = (130, 120, 104)
    # cristas de osso por trás
    horns = Layer(W, H)
    for i, a in enumerate((-160, -130, -100, -70, -40)):
        ux, uy = _dir(a)
        b = (cx + ux * 120, cy + 20 + uy * 104)
        t = (cx + ux * 160, cy + 20 + uy * 146)
        horns.tapered([b, ((b[0] + t[0]) / 2 - 4, (b[1] + t[1]) / 2), t], 26, 3)
    paint(cv, horns, base=IVORY_LIGHT, outline_w=2.8)
    shell = Layer(W, H)
    shell.ellipse(cx, cy + 20, 150, 120)
    cut = Layer(W, H)
    cut.rrect(cx - 220, cy + 60, cx + 220, cy + 260, 0)
    shell.cut(cut)
    glow(cv, shell, fc["aura"], radius=10, strength=0.6)
    paint(cv, shell, base=rock, shadow=_dk(rock, 0.5), light=_lt(rock, 50), outline_w=3.4)
    plates = Layer(W, H)
    for row, (y, xs, rad) in enumerate(((cy + 34, (-104, -52, 0, 52, 104), 25), (cy - 22, (-78, -26, 26, 78), 25), (cy - 74, (-48, 0, 48), 22))):
        for x in xs:
            plates.poly(hexagon(cx + x, y, rad, 30))
    plates = inter(plates, shell)
    paint(cv, plates, base=(100, 112, 108), shadow=(56, 62, 60), light=(170, 182, 176), outline_w=2.4, grain=False)
    seams = Layer(W, H)
    for x, y in ((-26, cy + 6), (26, cy + 6), (-52, cy + 58), (0, cy + 58), (52, cy + 58), (0, cy - 48)):
        seams.circle(cx + x, y, 3.4)
    glow(cv, seams, fc["aura"], radius=5, strength=2.0)
    fill(cv, seams, _lt(fc["aura"], 80))
    rim = Layer(W, H)
    rim.rrect(cx - 158, cy + 50, cx + 158, cy + 80, 14)
    paint(cv, rim, base=(110, 100, 86), shadow=(60, 54, 44), light=(170, 160, 140), outline_w=3)
    barn = Layer(W, H)
    for i in range(10):
        barn.ellipse(cx - 140 + i * 31, cy + 65, 11, 9)
    paint(cv, barn, base=(214, 206, 180), shadow=(150, 140, 110), outline_w=1.8, grain=False)
    bh = Layer(W, H)
    for i in range(10):
        bh.circle(cx - 140 + i * 31, cy + 63, 3)
    fill(cv, bh, (70, 60, 50))
    # musgo no topo, escorrendo
    moss = Layer(W, H)
    r = rng(181)
    for i in range(16):
        a = math.radians(-170 + i * 10.5)
        moss.circle(cx + math.cos(a) * 128, cy + 20 + math.sin(a) * 100, r.uniform(12, 20))
    moss.ellipse(cx - 10, cy - 84, 70, 22)
    moss = inter(moss, shell)
    paint(cv, moss, base=(84, 140, 60), shadow=(40, 80, 30), light=(150, 210, 110), outline_w=0, grain=True)
    sprouts = Layer(W, H)
    for x, y in ((cx - 40, cy - 100), (cx + 30, cy - 98), (cx + 80, cy - 70)):
        sprouts.tapered([(x, y + 6), (x - 4, y - 10), (x - 14, y - 18)], 5, 1)
        sprouts.tapered([(x, y + 6), (x + 6, y - 12), (x + 16, y - 16)], 5, 1)
    paint(cv, sprouts, base=(120, 190, 80), shadow=(60, 110, 40), outline_w=1.6, grain=False)
    accent_dots(cv, W, H, [(cx - 40, cy - 112), (cx + 30, cy - 110)], (250, 220, 120), 3.4)
    ember(cv, W, H, [(cx - 156, cy - 70, 3), (cx + 166, cy - 40, 2.5), (cx + 60, cy - 150, 3)], fc["aura"])
    finish(cv, W, H, _out(bone_id))


# ================================================================ caudas

def draw_tail_eel(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    n = 32
    path = []
    for i in range(n):
        t = i / (n - 1)
        path.append((px - 4 - 166 * t, py + math.sin(t * math.pi * 2.3) * 30 * (0.3 + t)))
    nrm = path_normals(path)

    def w(i):
        return 13 - 8 * i / (n - 1)
    fin = Layer(W, H)
    top = []
    bot = []
    for i in range(4, n):
        x, y = path[i]
        ux, uy, nx, ny = nrm[i]
        hgt = 8 + 4 * math.sin(i * 0.9)
        top.append((x + nx * (w(i) + hgt), y + ny * (w(i) + hgt)))
        bot.append((x, y))
    fin.poly(top + bot[::-1])
    ex, ey = path[-1]
    ux, uy, nx, ny = nrm[-1]
    fin.poly(leaf_pts((ex - ux * 6, ey - uy * 6), math.degrees(math.atan2(uy, ux)), 34, 14, power=0.6))
    paint(cv, fin, base=(70, 170, 170), shadow=(30, 96, 100), light=(160, 230, 225), outline_w=2.2, grain=False, alpha=220)
    rays = Layer(W, H)
    for i in range(6, n, 3):
        x, y = path[i]
        _, _, nx, ny = nrm[i]
        rays.line([(x, y), (x + nx * (w(i) + 10), y + ny * (w(i) + 10))], 1.4)
    fill(cv, inter(rays, fin), (30, 96, 100), alpha=200)
    body = Layer(W, H)
    for i, (x, y) in enumerate(path):
        body.circle(x, y, w(i))
    paint(cv, body, outline_w=2.8)
    joints = Layer(W, H)
    for i in range(2, n - 1, 3):
        x, y = path[i]
        _, _, nx, ny = nrm[i]
        rr = w(i) * 0.8
        joints.line([(x + nx * rr, y + ny * rr), (x - nx * rr, y - ny * rr)], 1.8)
    fill(cv, joints, (170, 150, 120), alpha=210)
    accent_dots(cv, W, H, [path[0]], fc["aura"], 3.4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_tail_salamander(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    ctrl = [(px + 4, py), (px - 70, py + 56), (px - 146, py + 52), (px - 200, py - 16)]
    m = Layer(W, H)
    m.tapered(ctrl, 30, 5)
    dark = (64, 52, 60)
    paint(cv, m, base=dark, shadow=(30, 24, 28), light=(130, 116, 124), outline_w=3)
    path = bezier(ctrl, 20)
    spots = Layer(W, H)
    for i, s in ((2, 9), (5, 8), (8, 7), (11, 6), (14, 5), (17, 4)):
        x, y = path[i]
        spots.ellipse(x + (3 if i % 2 else -3), y + (-4 if i % 2 else 4), s * 1.3, s)
    spots = inter(spots, m)
    glow(cv, spots, fc["aura"], radius=6, strength=1.6)
    paint(cv, spots, base=(255, 150, 40), shadow=(200, 80, 20), light=(255, 230, 140), outline_w=0, grain=False)
    vert = Layer(W, H)
    for i, (x, y) in enumerate([(px - 2, py), (px - 18, py + 8)]):
        vert.ellipse(x, y, 12 - i * 2, 11 - i * 2)
    paint(cv, vert, outline_w=2.6)
    ember(cv, W, H, [(px - 188, py - 40, 3.5), (px - 168, py - 58, 2.5), (px - 100, py + 20, 2.5), (px - 40, py + 60, 2)], fc["aura"])
    finish(cv, W, H, _out(bone_id))


def draw_tail_croc(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    ctrl = [(px + 6, py), (px - 78, py + 34), (px - 146, py + 32), (px - 192, py - 12)]
    path = bezier(ctrl, 18)
    nrm = path_normals(path)
    n = len(path)

    def wid(i):
        return 24 - 19 * i / (n - 1)
    sc = Layer(W, H)
    for i in range(1, n - 1):
        x, y = path[i]
        ux, uy, nx, ny = nrm[i]
        r = wid(i)
        h = 6 + r * 0.45
        sc.poly([(x - ux * 5 + nx * r * 0.7, y - uy * 5 + ny * r * 0.7), (x + nx * (r + h), y + ny * (r + h)),
                 (x + ux * 5 + nx * r * 0.7, y + uy * 5 + ny * r * 0.7)])
    paint(cv, sc, base=(150, 170, 120), shadow=(80, 100, 64), light=(200, 216, 170), outline_w=2.2, grain=False)
    body = Layer(W, H)
    for i, (x, y) in enumerate(path):
        body.circle(x, y, wid(i))
    paint(cv, body, outline_w=3, **CROC_KW)
    belly = Layer(W, H)
    belly.line([(x - nrm[i][2] * wid(i) * 0.7, y - nrm[i][3] * wid(i) * 0.7) for i, (x, y) in enumerate(path)], 8)
    fill(cv, inter(belly, body), (196, 186, 136), alpha=220)
    bands = Layer(W, H)
    for i in range(2, n - 1, 2):
        x, y = path[i]
        _, _, nx, ny = nrm[i]
        r = wid(i)
        bands.line([(x + nx * r, y + ny * r), (x - nx * r * 0.4, y - ny * r * 0.4)], 2)
    fill(cv, inter(bands, body), (50, 70, 44), alpha=200)
    studs = Layer(W, H)
    for i in range(2, n - 2, 3):
        x, y = path[i]
        _, _, nx, ny = nrm[i]
        studs.circle(x + nx * wid(i) * 0.35, y + ny * wid(i) * 0.35, 3)
    fill(cv, studs, (200, 210, 170))
    accent_dots(cv, W, H, [path[0]], fc["aura"], 3.6, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_tail_magma(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    ctrl = [(px + 4, py), (px - 80, py + 72), (px - 172, py + 52), (px - 168, py - 46)]
    path = bezier(ctrl, 14)
    n = len(path)
    nrm = path_normals(path)
    body = Layer(W, H)
    for i, (x, y) in enumerate(path):
        r = 22 - 13 * i / (n - 1)
        body.poly(rot_ellipse(x, y, r * 1.1, r, i * 23, n=7))
    glow(cv, body, LAVA, radius=10, strength=1.4)
    paint(cv, body, base=(70, 54, 52), shadow=(30, 22, 22), light=(140, 110, 100), outline_w=3)
    cracks = Layer(W, H)
    cracks.line([(x + nrm[i][2] * 3 * math.sin(i), y + nrm[i][3] * 3 * math.sin(i)) for i, (x, y) in enumerate(path)], 3.4)
    for i in range(1, n - 1, 2):
        x, y = path[i]
        _, _, nx, ny = nrm[i]
        r = 20 - 12 * i / (n - 1)
        cracks.line([(x, y), (x + nx * r * 0.8, y + ny * r * 0.8 - 2)], 2.4)
        cracks.line([(x, y), (x - nx * r * 0.7 + 3, y - ny * r * 0.7)], 2)
    cracks = inter(cracks, body)
    glow(cv, cracks, LAVA, radius=5, strength=2.0)
    fill(cv, cracks, (255, 210, 110))
    ex, ey = path[-1]
    ux, uy, _, _ = nrm[-1]
    fl = Layer(W, H)
    flame(fl, ex, ey + 4, 54, 30, 0.25)
    glow(cv, fl, LAVA, radius=12, strength=1.6)
    paint(cv, fl, base=(255, 120, 30), shadow=(200, 50, 20), light=(255, 220, 120), outline_w=2.4, grain=False)
    fl2 = Layer(W, H)
    flame(fl2, ex + 2, ey - 2, 30, 14, 0.25)
    fill(cv, fl2, (255, 240, 170))
    vert = Layer(W, H)
    vert.ellipse(px, py, 12, 11)
    paint(cv, vert, outline_w=2.6)
    ember(cv, W, H, [(px - 196, py - 104, 3.5), (px - 140, py - 90, 3), (px - 196, py - 40, 2.5), (px - 50, py + 80, 3),
                     (px - 120, py + 84, 2.5), (px - 30, py + 30, 2.5), (px - 110, py - 20, 2)], LAVA)
    finish(cv, W, H, _out(bone_id))


DRAW = {
    "bone_skull_hyena": draw_skull_hyena,
    "bone_tail_eel": draw_tail_eel,
    "bone_wings_moth": draw_wings_moth,
    "bone_legs_clockwork": draw_legs_clockwork,
    "bone_ribs_clockwork": draw_ribs_clockwork,
    "bone_skull_salamander": draw_skull_salamander,
    "bone_tail_salamander": draw_tail_salamander,
    "bone_ribs_ghoul": draw_ribs_ghoul,
    "bone_claw_ghoul": draw_claw_ghoul,
    "bone_skull_mammoth": draw_skull_mammoth,
    "bone_tusk_mammoth": draw_tusk_mammoth,
    "bone_skull_angler": draw_skull_angler,
    "bone_fin_angler": draw_fin_angler,
    "bone_wings_gargoyle": draw_wings_gargoyle,
    "bone_ribs_gargoyle": draw_ribs_gargoyle,
    "bone_legs_locust": draw_legs_locust,
    "bone_mandible_locust": draw_mandible_locust,
    "bone_skull_croc": draw_skull_croc,
    "bone_tail_croc": draw_tail_croc,
    "bone_skull_wraith": draw_skull_wraith,
    "bone_shroud_wraith": draw_shroud_wraith,
    "bone_wings_wyvern": draw_wings_wyvern,
    "bone_claw_wyvern": draw_claw_wyvern,
    "bone_skull_minotaur": draw_skull_minotaur,
    "bone_legs_minotaur": draw_legs_minotaur,
    "bone_fist_sentinel": draw_fist_sentinel,
    "bone_legs_sentinel": draw_legs_sentinel,
    "bone_stinger_hornet": draw_stinger_hornet,
    "bone_wings_hornet": draw_wings_hornet,
    "bone_crown_matriarch": draw_crown_matriarch,
    "bone_ribs_titan": draw_ribs_titan,
    "bone_tail_magma": draw_tail_magma,
    "bone_shell_behemoth": draw_shell_behemoth,
    "bone_skull_lich": draw_skull_lich,
    "bone_wings_obsidian": draw_wings_obsidian,
}


if __name__ == "__main__":
    fams = {b["id"]: b.get("family", "") for b in data("bones.json")}
    only = set(x for x in os.environ.get("BT_ONLY", "").split(",") if x)
    for bid, fn in DRAW.items():
        if only and bid not in only:
            continue
        fn(bid, fams.get(bid, ""))
        print("ok", bid)
