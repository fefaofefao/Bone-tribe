#!/usr/bin/env python3
"""Placeholders extras de braços e pernas do Bone Tribe (14 ossos).

Mesmo estilo de tools/gen_art.py (draw_arm_bone / draw_legs_bone): ossos marfim com
contorno escuro e detalhes da família. Tamanho e pivot vêm de data/skeleton.json.

Uso: python3 tools/art_extra_limbs.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa

FUR_GREY = (132, 130, 136)
SCALE_RED = (170, 50, 36)
SCALE_RED_SH = (100, 20, 16)
SCALE_RED_LT = (240, 110, 70)
TEAL = (70, 175, 170)
TEAL_SH = (30, 100, 100)
TEAL_LT = (150, 230, 220)
GOLD = (232, 184, 60)
GOLD_SH = (150, 104, 24)
GOLD_LT = (255, 236, 150)
STONE = (150, 156, 170)
STONE_SH = (84, 90, 106)
STONE_LT = (206, 212, 226)
IRON = (96, 104, 122)
IRON_SH = (56, 60, 74)


def _shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def _arm_canvas():
    s = slot_info("slot_arm_right")
    W, H = s["canvas"]
    return s, W, H, new_canvas(W, H), s["pivot"][0], s["pivot"][1]


def _legs_canvas():
    s = slot_info("slot_legs")
    W, H = s["canvas"]
    return s, W, H, new_canvas(W, H), s["pivot"][0], s["pivot"][1]


def _pelvis(W, H, cx, top, w=44, h=16):
    m = Layer(W, H)
    m.ellipse(cx, top + 4, w, h)
    return m



# A ossada do braço vai do ombro (pivot) até a borda de baixo do canvas; as coordenadas
# dos desenhos usam uma régua de 0..226 a partir do ombro, comprimida para caber em H.
K_ARM = 0.89


def Y(n):
    return ARM_TOP + n * K_ARM


ARM_TOP = slot_info("slot_arm_right")["pivot"][1]


def _arm_base(W, H, cx, top, lower_len=1.0):
    m = Layer(W, H)
    m.bone((cx, Y(6)), (cx + 2, Y(92)), 9)
    m.bone((cx + 2, Y(98)), (cx - 2, Y(98 + 70 * lower_len)), 7.5)
    return m

# ------------------------------------------------------------------ braços

def draw_claw_wolf(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    arm = _arm_base(W, H, cx, top, lower_len=0.85)
    paint(cv, arm, outline_w=3)
    # pata estreita e comprida
    paw = Layer(W, H)
    paw.ellipse(cx, Y(182), 20, 18)
    paw.ellipse(cx, Y(196), 22, 12)
    paint(cv, paw, base=(150, 148, 154), shadow=(86, 84, 92), light=(200, 198, 206), outline_w=3)
    pads = Layer(W, H)
    for dx in (-13, -4.5, 4.5, 13):
        pads.circle(cx + dx, Y(200), 3.6)
    fill(cv, pads, (70, 52, 60))
    claws = Layer(W, H)
    for dx, bend in ((-15, -6), (-5, -2), (5, 2), (15, 6)):
        claws.tapered([(cx + dx, Y(204)), (cx + dx + bend * 0.4, Y(216)), (cx + dx + bend, Y(226))], 7, 1)
    paint(cv, claws, base=IVORY_LIGHT, outline_w=2.2, grain=False)
    fur(cv, W, H, cx, Y(166), 11, 22, FUR_GREY, 11, angle=90, spread=75)
    accent_dots(cv, W, H, [(cx + 2, Y(98))], fc["aura"], 3.5)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_claw_bat(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    wrist = (cx - 2, Y(140))
    tips = [(cx - 50, Y(222)), (cx - 18, Y(226)), (cx + 18, Y(222)), (cx + 48, Y(206))]
    # membrana roxa rasgada entre os dedos
    mem = Layer(W, H)
    mem.poly([wrist, tips[0], (cx - 34, Y(206)), tips[1], (cx, Y(210)), tips[2], (cx + 30, Y(198)), tips[3]])
    paint(cv, mem, base=(110, 62, 160), shadow=(60, 30, 96), light=(170, 120, 220), outline_w=2.4, grain=False)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.6), outline_w=3)
    fingers = Layer(W, H)
    for i, t in enumerate(tips):
        mid = ((wrist[0] + t[0]) / 2 + (i - 1.5) * 4, (wrist[1] + t[1]) / 2 - 4)
        fingers.tapered([wrist, mid, t], 6.5, 3)
        fingers.circle(mid[0], mid[1], 4.2)
    fingers.circle(wrist[0], wrist[1], 9)
    paint(cv, fingers, outline_w=2.6)
    # polegar com gancho
    thumb = Layer(W, H)
    thumb.tapered([(cx - 6, Y(142)), (cx - 30, Y(140)), (cx - 38, Y(158))], 7, 1.2)
    paint(cv, thumb, base=IVORY_LIGHT, outline_w=2.2, grain=False)
    accent_dots(cv, W, H, [(cx - 2, Y(140))], fc["aura"], 3.5, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_claw_lizard(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.75), outline_w=3)
    scales = Layer(W, H)
    for i in range(4):
        y = Y(108) + i * 13
        scales.poly([(cx - 9, y), (cx - 1, y + 10), (cx + 7, y)])
    paint(cv, scales, base=SCALE_RED, shadow=SCALE_RED_SH, light=SCALE_RED_LT, outline_w=1.6, grain=False)
    hand = Layer(W, H)
    hand.ellipse(cx, Y(180), 22, 16)
    for dx, ex in ((-12, -30), (0, 0), (12, 30)):
        hand.tapered([(cx + dx, Y(184)), (cx + ex * 0.7, Y(200)), (cx + ex, Y(206))], 11, 7)
    paint(cv, hand, base=SCALE_RED, shadow=SCALE_RED_SH, light=SCALE_RED_LT, outline_w=3)
    bumps = Layer(W, H)
    for x, y in ((cx - 8, Y(175)), (cx + 6, Y(172)), (cx - 1, Y(184))):
        bumps.circle(x, y, 3.2)
    fill(cv, bumps, (220, 90, 60))
    claws = Layer(W, H)
    tipl = []
    for ex in (-30, 0, 30):
        b = (cx + ex, Y(204))
        e = (cx + ex * 1.15 + (0 if ex == 0 else (4 if ex > 0 else -4)), Y(226))
        claws.tapered([b, (b[0] + (e[0] - b[0]) * 0.3 + 3, (b[1] + e[1]) / 2), e], 8, 1)
        tipl.append(e)
    glow(cv, claws, fc["aura"], radius=5, strength=1.4)
    paint(cv, claws, base=IVORY_LIGHT, outline_w=2.2, grain=False)
    ember(cv, W, H, [(t[0], t[1] - 2, 2.4) for t in tipl] + [(cx + 18, Y(168), 2.2)], fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_fang_spider(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.45), outline_w=3)
    base = Layer(W, H)
    base.ellipse(cx, Y(146), 20, 18)
    paint(cv, base, base=(70, 60, 64), shadow=(36, 30, 34), light=(130, 116, 120), outline_w=3)
    fang = Layer(W, H)
    fang.tapered([(cx + 4, Y(150)), (cx + 34, Y(180)), (cx + 20, Y(212)), (cx - 10, Y(214))], 26, 2)
    paint(cv, fang, base=(56, 46, 52), shadow=(24, 18, 22), light=(140, 120, 130), outline_w=3)
    shine = Layer(W, H)
    shine.curve([(cx + 16, Y(162)), (cx + 30, Y(180)), (cx + 24, Y(196))], 3)
    fill(cv, shine, (180, 164, 172), alpha=200)
    accent_dots(cv, W, H, [(cx - 8, Y(142)), (cx + 6, Y(140))], fc["aura"], 3.4, glow_r=3)
    drop = Layer(W, H)
    drop.circle(cx - 14, Y(220), 6)
    drop.poly([(cx - 19.5, Y(218)), (cx - 8.5, Y(218)), (cx - 12, Y(208))])
    glow(cv, drop, fc["aura"], radius=5, strength=1.8)
    paint(cv, drop, base=fc["aura"], shadow=fc["detail"], light=(230, 255, 190), outline_w=2, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_flipper_turtle(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    up = Layer(W, H)
    up.bone((cx, Y(6)), (cx + 2, Y(74)), 10)
    up.bone((cx + 2, Y(80)), (cx, Y(118)), 9)
    paint(cv, up, outline_w=3)
    fl = Layer(W, H)
    fl.poly([(cx - 22, Y(116)), (cx + 24, Y(114)), (cx + 54, Y(166)), (cx + 42, Y(208)),
             (cx + 18, Y(222)), (cx - 4, Y(210)), (cx - 26, Y(172))])
    fl.ellipse(cx + 0, Y(126), 26, 16)
    fl.ellipse(cx + 26, Y(196), 22, 26)
    paint(cv, fl, base=TEAL, shadow=TEAL_SH, light=TEAL_LT, outline_w=3)
    ridges = Layer(W, H)
    for ex, ey in ((-6, 200), (14, 210), (34, 196), (46, 172)):
        ridges.tapered([(cx + 2, Y(130)), (cx + ex * 0.5 + 4, Y((130 + ey) / 2)), (cx + ex, top + ey)], 7, 3)
    paint(cv, ridges, base=IVORY, outline_w=1.8, shade=False, grain=False)
    accent_dots(cv, W, H, [(cx - 12, Y(150)), (cx + 30, Y(150))], (210, 240, 230), 3.6)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_scepter_rat_king(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    # cetro atrás da mão, de baixo até o topo à esquerda
    rod = Layer(W, H)
    rod.capsule((cx + 22, Y(226)), (cx - 30, Y(92)), 5.5)
    glow(cv, rod, GOLD, radius=6, strength=0.9)
    paint(cv, rod, base=GOLD, shadow=GOLD_SH, light=GOLD_LT, outline_w=2.6)
    bands = Layer(W, H)
    for t in (0.25, 0.6):
        x = cx + 22 + (-52) * t
        y = Y(226) - 134 * t
        bands.circle(x, y, 8)
    paint(cv, bands, base=GOLD, shadow=GOLD_SH, light=GOLD_LT, outline_w=2.2, grain=False)
    # crânio de rato no topo + gema roxa
    hx, hy = cx - 34, Y(76)
    sk = Layer(W, H)
    sk.ellipse(hx, hy, 15, 13)
    sk.poly([(hx + 8, hy - 8), (hx + 30, hy + 4), (hx + 8, hy + 10)])
    sk.circle(hx - 9, hy - 12, 6)
    sk.circle(hx + 5, hy - 14, 6)
    paint(cv, sk, outline_w=2.6)
    eye = Layer(W, H)
    eye.circle(hx + 4, hy - 1, 3.6)
    fill(cv, eye, (28, 16, 18))
    gem = Layer(W, H)
    gem.poly([(hx - 4, hy - 34), (hx + 6, hy - 24), (hx - 4, hy - 13), (hx - 14, hy - 24)])
    glow(cv, gem, fc["aura"], radius=8, strength=2.0)
    paint(cv, gem, base=(150, 70, 230), shadow=(80, 30, 140), light=(220, 170, 255), outline_w=2.2, grain=False)
    crown = Layer(W, H)
    crown.poly([(hx - 14, hy - 10), (hx - 16, hy - 20), (hx - 9, hy - 14), (hx - 4, hy - 22), (hx + 1, hy - 14), (hx + 8, hy - 20), (hx + 6, hy - 10)])
    paint(cv, crown, base=GOLD, shadow=GOLD_SH, light=GOLD_LT, outline_w=2, grain=False)
    # braço por cima e mão segurando
    paint(cv, _arm_base(W, H, cx, top, lower_len=0.85), outline_w=3)
    hand = Layer(W, H)
    hand.ellipse(cx + 2, Y(180), 15, 13)
    for i in range(3):
        hand.rrect(cx - 12 + i * 2, Y(184) + i * 8 - 4, cx + 18, Y(190) + i * 8, 4)
    paint(cv, hand, outline_w=2.8)
    ring = Layer(W, H)
    ring.circle(cx + 12, Y(186), 3.4)
    paint(cv, ring, base=GOLD, shadow=GOLD_SH, light=GOLD_LT, outline_w=1.4, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


# ------------------------------------------------------------------ pernas

def draw_legs_wolf(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    paint(cv, _pelvis(W, H, cx, top), outline_w=3)
    legs = Layer(W, H)
    for side in (-1, 1):
        hip = (cx + side * 30, top + 10)
        knee = (cx + side * 40, top + 92)
        hock = (cx + side * 22, top + 150)
        ankle = (cx + side * 30, H - 30)
        legs.bone(hip, knee, 10)
        legs.bone(knee, hock, 8)
        legs.capsule(hock, ankle, 7)
        legs.circle(hock[0], hock[1], 10)
    paint(cv, legs, outline_w=3)
    fur(cv, W, H, cx - 34, top + 30, 9, 26, FUR_GREY, 21, angle=150, spread=40)
    fur(cv, W, H, cx + 34, top + 30, 9, 26, FUR_GREY, 22, angle=30, spread=40)
    paws = Layer(W, H)
    for side in (-1, 1):
        paws.ellipse(cx + side * 36, H - 20, 22, 12)
    paint(cv, paws, base=(150, 148, 154), shadow=(86, 84, 92), light=(200, 198, 206), outline_w=3)
    claws = Layer(W, H)
    for side in (-1, 1):
        for k in range(3):
            x = cx + side * 36 + side * (6 + k * 7)
            claws.tapered([(x, H - 18), (x + side * 5, H - 12), (x + side * 7, H - 6)], 5, 1)
    paint(cv, claws, base=IVORY_LIGHT, outline_w=1.8, grain=False)
    accent_dots(cv, W, H, [(cx - 40, top + 92), (cx + 40, top + 92)], fc["aura"], 4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_legs_bear(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    paint(cv, _pelvis(W, H, cx, top, 58, 20), outline_w=3)
    fur(cv, W, H, cx - 40, top + 40, 10, 30, (110, 72, 40), 31, angle=180, spread=60)
    fur(cv, W, H, cx + 40, top + 40, 10, 30, (110, 72, 40), 32, angle=0, spread=60)
    legs = Layer(W, H)
    for side in (-1, 1):
        legs.bone((cx + side * 40, top + 14), (cx + side * 46, top + 110), 18, knob=1.35)
        legs.bone((cx + side * 46, top + 118), (cx + side * 48, H - 50), 16, knob=1.35)
    paint(cv, legs, outline_w=3.2)
    paws = Layer(W, H)
    for side in (-1, 1):
        paws.ellipse(cx + side * 50, H - 30, 38, 24)
    paint(cv, paws, base=(120, 80, 48), shadow=(70, 44, 24), light=(170, 120, 80), outline_w=3)
    pads = Layer(W, H)
    for side in (-1, 1):
        pads.ellipse(cx + side * 50, H - 34, 14, 9)
    fill(cv, pads, (70, 44, 30))
    claws = Layer(W, H)
    for side in (-1, 1):
        for dx in (-24, -8, 8, 24):
            x = cx + side * 50 + dx
            claws.tapered([(x, H - 16), (x + 2, H - 10), (x - 3, H - 4)], 9, 1)
    paint(cv, claws, base=IVORY_LIGHT, outline_w=2, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def _jointed(m, pts, w0, w1):
    n = len(pts) - 1
    for i in range(n):
        a = w0 + (w1 - w0) * i / n
        b = w0 + (w1 - w0) * (i + 1) / n
        m.tapered([pts[i], pts[i + 1]], a, b)


def draw_legs_crab(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    legs = Layer(W, H)
    tips = []
    joints = []
    for side in (-1, 1):
        for k, (kx, ky, fx) in enumerate(((104, 10, 112), (78, 30, 80), (48, 60, 46))):
            hip = (cx + side * (16 + k * 2), top + 8 + k * 10)
            knee = (cx + side * kx, top - 14 + ky)
            ft = (cx + side * fx, H - 8 - k * 4)
            mid = (knee[0] + side * (8 - k * 2), knee[1] + (ft[1] - knee[1]) * 0.45)
            _jointed(legs, [hip, knee, mid], 15 - k * 2, 11 - k * 2)
            legs.tapered([mid, ft], 11 - k * 2, 3)
            tips.append((mid, ft))
            joints += [knee, mid]
    paint(cv, legs, base=TEAL, shadow=TEAL_SH, light=TEAL_LT, outline_w=3)
    tipm = Layer(W, H)
    for mid, ft in tips:
        a = (mid[0] + (ft[0] - mid[0]) * 0.62, mid[1] + (ft[1] - mid[1]) * 0.62)
        tipm.tapered([a, ft], 7, 2.6)
    paint(cv, tipm, base=(214, 76, 56), shadow=(130, 36, 26), light=(250, 150, 110), outline_w=2, grain=False)
    body = Layer(W, H)
    body.ellipse(cx, top + 14, 40, 22)
    paint(cv, body, base=TEAL, shadow=TEAL_SH, light=TEAL_LT, outline_w=3)
    paint(cv, _pelvis(W, H, cx, top + 6, 26, 11), outline_w=2.4)
    accent_dots(cv, W, H, joints, (220, 236, 226), 3.6)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_legs_turtle(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    paint(cv, _pelvis(W, H, cx, top + 4, 62, 22), outline_w=3)
    legs = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 52
        legs.rrect(x - 30, top + 30, x + 30, H - 30, 26)
        legs.ellipse(x, top + 40, 34, 22)
    paint(cv, legs, base=(176, 190, 150), shadow=(104, 120, 86), light=(220, 232, 196), outline_w=3.2)
    patches = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 52
        for (dx, dy, r) in ((-10, 70, 11), (12, 96, 9), (-6, 124, 10), (14, 150, 8), (-12, 170, 7)):
            patches.circle(x + dx * side, top + dy, r)
    paint(cv, patches, base=TEAL, shadow=TEAL_SH, light=TEAL_LT, outline_w=1.8, grain=False)
    feet = Layer(W, H)
    for side in (-1, 1):
        feet.ellipse(cx + side * 52, H - 26, 36, 18)
    paint(cv, feet, base=(150, 164, 126), shadow=(90, 104, 72), light=(206, 220, 180), outline_w=3)
    toes = Layer(W, H)
    for side in (-1, 1):
        for dx in (-22, -7, 8, 23):
            toes.ellipse(cx + side * 52 + dx, H - 16, 7, 7)
    paint(cv, toes, base=IVORY, outline_w=2, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_legs_lizard(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    paint(cv, _pelvis(W, H, cx, top, 36, 14), outline_w=3)
    legs = Layer(W, H)
    feet = []
    for side in (-1, 1):
        hip = (cx + side * 26, top + 8)
        knee = (cx + side * 96, top + 60)
        ankle = (cx + side * 70, H - 40)
        legs.bone(hip, knee, 9)
        legs.bone(knee, ankle, 7.5)
        feet.append(ankle)
    paint(cv, legs, outline_w=3)
    scales = Layer(W, H)
    for side in (-1, 1):
        for t in (0.3, 0.55, 0.8):
            x = cx + side * (26 + 70 * t)
            y = top + 8 + 52 * t
            scales.poly([(x - 7, y - 8), (x + 7, y - 8), (x + side * 2, y - 20)])
    paint(cv, scales, base=SCALE_RED, shadow=SCALE_RED_SH, light=SCALE_RED_LT, outline_w=1.6, grain=False)
    ft = Layer(W, H)
    claws = Layer(W, H)
    for side, (ax, ay) in zip((-1, 1), feet):
        ft.ellipse(ax, ay + 8, 18, 12)
        for a in (-50, -10, 30):
            ang = math.radians(90 + side * a)
            ex, ey = ax + math.cos(ang) * 34, ay + 8 + math.sin(ang) * 30
            ft.tapered([(ax, ay + 8), (ex, ey)], 9, 6)
            claws.tapered([(ex, ey), (ex + math.cos(ang) * 10, ey + math.sin(ang) * 10 + 2)], 6, 1)
    paint(cv, ft, base=SCALE_RED, shadow=SCALE_RED_SH, light=SCALE_RED_LT, outline_w=3)
    paint(cv, claws, base=IVORY_LIGHT, outline_w=1.8, grain=False)
    ember(cv, W, H, [(cx - 96, top + 60, 3), (cx + 96, top + 60, 3)], fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_legs_beetle(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    green, green_sh, green_lt = (60, 110, 50), (28, 60, 24), (130, 190, 100)
    legs = Layer(W, H)
    hooks = Layer(W, H)
    joints = []
    for side in (-1, 1):
        for k, (kx, ky, fx) in enumerate(((70, -10, 108), (92, 30, 80), (60, 70, 34))):
            hip = (cx + side * 18, top + 4 + k * 12)
            knee = (cx + side * kx, top + ky)
            ft = (cx + side * fx, H - 16 - k * 3)
            mid = ((knee[0] + ft[0]) / 2 + side * 6, (knee[1] + ft[1]) / 2)
            _jointed(legs, [hip, knee, mid, ft], 9, 5)
            hooks.tapered([ft, (ft[0] + side * 10, ft[1] + 4), (ft[0] + side * 12, ft[1] - 4)], 4.5, 1.5)
            joints += [knee, mid]
    paint(cv, legs, base=green, shadow=green_sh, light=green_lt, outline_w=3)
    paint(cv, hooks, base=green, shadow=green_sh, light=green_lt, outline_w=2, grain=False)
    seg = Layer(W, H)
    for x, y in joints:
        seg.circle(x, y, 5)
    paint(cv, seg, base=(40, 80, 34), shadow=(20, 44, 16), light=(110, 170, 80), outline_w=1.8, grain=False)
    body = Layer(W, H)
    body.ellipse(cx, top + 18, 30, 26)
    paint(cv, body, base=green, shadow=green_sh, light=green_lt, outline_w=3)
    line = Layer(W, H)
    line.line([(cx, top - 4), (cx, top + 42)], 2.4)
    fill(cv, line, (24, 40, 20))
    accent_dots(cv, W, H, [(cx - 12, top + 14), (cx + 12, top + 14)], fc["aura"], 3.2, glow_r=3)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_legs_rat(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    tail = Layer(W, H)
    tail.tapered([(cx + 6, top + 10), (cx + 60, top + 30), (cx + 96, top - 20), (cx + 110, top + 30)], 6, 1.5)
    paint(cv, tail, base=(220, 170, 176), shadow=(150, 100, 110), light=(250, 210, 214), outline_w=2.2, grain=False)
    paint(cv, _pelvis(W, H, cx, top, 30, 12), outline_w=3)
    legs = Layer(W, H)
    feet = []
    for side in (-1, 1):
        hip = (cx + side * 20, top + 8)
        knee = (cx + side * 36, top + 84)
        ankle = (cx + side * 20, H - 46)
        legs.bone(hip, knee, 6.5)
        legs.bone(knee, ankle, 5)
        feet.append(ankle)
    paint(cv, legs, outline_w=3)
    toes = Layer(W, H)
    for side, (ax, ay) in zip((-1, 1), feet):
        toes.ellipse(ax + side * 6, ay + 10, 10, 8)
        for dx in (-6, 6, 18, 30):
            ex = ax + side * dx
            toes.tapered([(ax + side * 6, ay + 12), ((ax + side * 6 + ex) / 2, H - 18), (ex, H - 9)], 4, 2)
    paint(cv, toes, base=(220, 170, 176), shadow=(150, 100, 110), light=(250, 210, 214), outline_w=2.2, grain=False)
    fur(cv, W, H, cx - 26, top + 26, 6, 18, (90, 80, 96), 41, angle=160, spread=40)
    fur(cv, W, H, cx + 26, top + 26, 6, 18, (90, 80, 96), 42, angle=20, spread=40)
    accent_dots(cv, W, H, [(cx - 36, top + 84), (cx + 36, top + 84)], fc["aura"], 3.4, glow_r=3)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_legs_golem(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    hipblk = Layer(W, H)
    hipblk.rrect(cx - 80, top - 12, cx + 80, top + 24, 10)
    paint(cv, hipblk, base=STONE, shadow=STONE_SH, light=STONE_LT, outline_w=3.2)
    legs = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 50
        legs.rrect(x - 30, top + 22, x + 30, top + 108, 10)
        legs.rrect(x - 27, top + 114, x + 27, H - 44, 10)
    paint(cv, legs, base=STONE, shadow=STONE_SH, light=STONE_LT, outline_w=3.2)
    knees = Layer(W, H)
    for side in (-1, 1):
        knees.circle(cx + side * 50, top + 112, 18)
    paint(cv, knees, base=IRON, shadow=IRON_SH, light=(170, 180, 200), outline_w=2.8)
    bands = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 50
        for y in (top + 38, top + 150, top + 186):
            bands.rrect(x - 33, y, x + 33, y + 10, 3)
    paint(cv, bands, base=IRON, shadow=IRON_SH, light=(170, 180, 200), outline_w=2.2, grain=False)
    rivets = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 50
        for y in (top + 43, top + 155, top + 191):
            rivets.circle(x - 24, y, 2.2)
            rivets.circle(x + 24, y, 2.2)
    fill(cv, rivets, (210, 216, 230))
    feet = Layer(W, H)
    for side in (-1, 1):
        x = cx + side * 52
        feet.rrect(x - 40, H - 46, x + 40, H - 8, 8)
    paint(cv, feet, base=(126, 132, 148), shadow=(70, 76, 92), light=(190, 198, 214), outline_w=3.2)
    for side in (-1, 1):
        runes(cv, W, H, cx + side * 50, top + 76, 10, fc["aura"])
        runes(cv, W, H, cx + side * 50, top + 214, 7, fc["aura"])
    runes(cv, W, H, cx, top + 6, 8, fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


DRAW = {
    "bone_claw_wolf": draw_claw_wolf,
    "bone_claw_bat": draw_claw_bat,
    "bone_claw_lizard": draw_claw_lizard,
    "bone_fang_spider": draw_fang_spider,
    "bone_flipper_turtle": draw_flipper_turtle,
    "bone_scepter_rat_king": draw_scepter_rat_king,
    "bone_legs_wolf": draw_legs_wolf,
    "bone_legs_bear": draw_legs_bear,
    "bone_legs_crab": draw_legs_crab,
    "bone_legs_turtle": draw_legs_turtle,
    "bone_legs_lizard": draw_legs_lizard,
    "bone_legs_beetle": draw_legs_beetle,
    "bone_legs_rat": draw_legs_rat,
    "bone_legs_golem": draw_legs_golem,
}

FAMILY_OF = {
    "bone_claw_wolf": "family_beast",
    "bone_claw_bat": "family_shadow",
    "bone_claw_lizard": "family_dragon",
    "bone_fang_spider": "family_insect",
    "bone_flipper_turtle": "family_marine",
    "bone_scepter_rat_king": "family_shadow",
    "bone_legs_wolf": "family_beast",
    "bone_legs_bear": "family_beast",
    "bone_legs_crab": "family_marine",
    "bone_legs_turtle": "family_marine",
    "bone_legs_lizard": "family_dragon",
    "bone_legs_beetle": "family_insect",
    "bone_legs_rat": "family_shadow",
    "bone_legs_golem": "family_construct",
}

if __name__ == "__main__":
    for bid, fn in DRAW.items():
        fn(bid, FAMILY_OF[bid])
