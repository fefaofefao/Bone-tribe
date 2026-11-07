#!/usr/bin/env python3
"""Ossos da terceira leva (1.4, 15 ossos novos) do Bone Tribe.

Mesmo estilo dos módulos anteriores: marfim com contorno escuro, detalhe na cor da
família e mais enfeite conforme a raridade. Tamanho e pivot vêm de data/skeleton.json.
Uso: BT_ONLY=bone_shell_scarab python3 tools/gen_art.py bones
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa
from art_extra_back import inter, leaf_pts, rot_rect, path_normals, back_canvas, tail_canvas, root_knob  # noqa
from art_extra_limbs import Y, _arm_canvas, _legs_canvas  # noqa
from art_extra_head import _skull_setup, _ribs_setup  # noqa
from art_wave2_bones import (_dk, _lt, _out, membrane_wings, IRON_KW, GOLD_KW, IRON, HOLE)  # noqa

BAT_ELBOW = (-70, -112)
BAT_TIPS = [(-170, -96), (-176, -40), (-150, 4)]
SHELL = (196, 170, 120)
SHELL_KW = dict(base=SHELL, shadow=(120, 98, 60), light=(240, 222, 170))
JELLY = (150, 200, 230)
JELLY_KW = dict(base=JELLY, shadow=(80, 120, 150), light=(225, 245, 255))
ICE = (170, 220, 255)
ICE_KW = dict(base=ICE, shadow=(90, 130, 170), light=(240, 250, 255))
DARK_IRON_KW = dict(base=(60, 56, 72), shadow=(30, 28, 38), light=(130, 126, 150))
FEATHER = (110, 86, 74)


# ------------------------------------------------------------- crânios

def draw_helm_knight(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    draw_skull(cv, W, H, cx, cy, r * 0.92, eye_color=fc["aura"])
    helm = Layer(W, H)
    helm.poly([(cx - r * 0.95, cy - r * 0.05), (cx - r * 0.7, cy - r * 0.95), (cx + r * 0.6, cy - r * 1.0), (cx + r * 1.0, cy - r * 0.2),
               (cx + r * 0.95, cy + r * 0.05), (cx - r * 0.9, cy + r * 0.1)])
    paint(cv, helm, outline_w=3, **IRON_KW)
    visor = Layer(W, H)
    visor.rrect(cx - r * 0.2, cy - r * 0.18, cx + r * 0.95, cy - r * 0.02, 3)
    fill(cv, visor, HOLE)
    plume = Layer(W, H)
    plume.tapered([(cx - r * 0.1, cy - r * 0.98), (cx - r * 0.6, cy - r * 1.5), (cx - r * 1.2, cy - r * 1.35)], 13, 3)
    paint(cv, plume, base=(150, 70, 50), shadow=(80, 34, 24), light=(210, 120, 90), outline_w=2.2, grain=False)
    accent_dots(cv, W, H, [(cx + r * 0.3, cy - r * 0.1)], fc["aura"], 3.4, glow_r=5)
    finish(cv, W, H, _out(bone_id))


def draw_bell_jelly(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    bell = Layer(W, H)
    bell.ellipse(cx, cy - r * 0.1, r * 1.25, r * 1.05)
    cut = Layer(W, H)
    cut.rrect(cx - r * 1.4, cy + r * 0.55, cx + r * 1.4, cy + r * 1.6, 3)
    bell.cut(cut)
    paint(cv, bell, outline_w=3, grain=False, alpha=190, **JELLY_KW)
    inner = Layer(W, H)
    inner.ellipse(cx, cy, r * 0.8, r * 0.6)
    glow(cv, inner, fc["aura"], radius=12, strength=1.0)
    draw_skull(cv, W, H, cx, cy + r * 0.05, r * 0.6, eye_color=fc["aura"])
    tent = Layer(W, H)
    for dx in (-0.8, -0.3, 0.3, 0.8):
        tent.tapered([(cx + r * dx, cy + r * 0.5), (cx + r * dx + 6, cy + r * 0.9), (cx + r * dx - 4, cy + r * 1.2)], 5, 1.5)
    paint(cv, tent, outline_w=1.8, grain=False, alpha=200, **JELLY_KW)
    finish(cv, W, H, _out(bone_id))


def draw_skull_vulture(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    ruff = Layer(W, H)
    ruff.ellipse(cx - r * 0.4, cy + r * 0.7, r * 0.9, r * 0.38)
    paint(cv, ruff, base=(200, 190, 176), shadow=(120, 110, 96), outline_w=2.4, grain=False)
    draw_skull(cv, W, H, cx - 6, cy, r * 0.88, snout=0.25, eye_color=fc["aura"])
    beak = Layer(W, H)
    beak.poly([(cx + r * 0.75, cy - r * 0.05), (cx + r * 1.55, cy + r * 0.25), (cx + r * 1.38, cy + r * 0.62), (cx + r * 0.75, cy + r * 0.45)])
    paint(cv, beak, base=(230, 200, 120), shadow=(150, 120, 60), light=(255, 236, 170), outline_w=2.4, grain=False)
    hook = Layer(W, H)
    hook.tapered([(cx + r * 1.45, cy + r * 0.3), (cx + r * 1.6, cy + r * 0.55), (cx + r * 1.42, cy + r * 0.72)], 6, 1.5)
    paint(cv, hook, base=(200, 170, 90), shadow=(130, 100, 40), outline_w=2, grain=False)
    finish(cv, W, H, _out(bone_id))


def draw_skull_imp(bone_id, family):
    s, W, H, cv, cx, cy, r = _skull_setup()
    fc = fam(family)
    horns = [(-0.35, -0.7, -0.45, -0.85), (0.25, -0.8, 0.4, -0.9)]
    draw_skull(cv, W, H, cx, cy, r * 0.9, horns=horns, eye_color=ICE)
    frost = Layer(W, H)
    for (hx, hy, ex, ey) in horns:
        frost.circle(cx + r * 0.9 * (hx + ex), cy + r * 0.9 * (hy + ey), 6)
    glow(cv, frost, ICE, radius=7, strength=1.4)
    fill(cv, frost, (240, 250, 255))
    fang = Layer(W, H)
    fang.poly([(cx + r * 0.45, cy + r * 0.62), (cx + r * 0.52, cy + r * 0.95), (cx + r * 0.6, cy + r * 0.62)])
    paint(cv, fang, base=IVORY_LIGHT, outline_w=1.6, shade=False, grain=False)
    finish(cv, W, H, _out(bone_id))


# -------------------------------------------------------------- braços

def _forearm(W, H, cx, w0=7, w1=6):
    arm = Layer(W, H)
    arm.bone((cx, Y(6)), (cx + 2, Y(88)), w0)
    arm.bone((cx + 2, Y(94)), (cx - 2, Y(150)), w1)
    return arm


def draw_shield_knight(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _forearm(W, H, cx), outline_w=2.8)
    sh = Layer(W, H)
    sh.poly([(cx - 40, Y(130)), (cx + 40, Y(130)), (cx + 38, Y(196)), (cx, Y(234)), (cx - 38, Y(196))])
    paint(cv, sh, outline_w=3, **IRON_KW)
    emb = Layer(W, H)
    emb.bone((cx - 18, Y(150)), (cx + 18, Y(206)), 4)
    emb.bone((cx + 18, Y(150)), (cx - 18, Y(206)), 4)
    paint(cv, emb, outline_w=1.8)
    accent_dots(cv, W, H, [(cx, Y(178))], fc["aura"], 4, glow_r=5)
    finish(cv, W, H, _out(bone_id))


def draw_tentacle_jelly(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    pts = []
    for k in range(12):
        t = k / 11
        pts.append((cx + math.sin(t * 6) * 16 * t, Y(6 + t * 220)))
    m = Layer(W, H)
    m.tapered(pts, 12, 3)
    paint(cv, m, outline_w=2.4, grain=False, alpha=210, **JELLY_KW)
    sp = Layer(W, H)
    for k in range(2, 11, 2):
        x, y = pts[k]
        sp.circle(x, y, 3.2)
    glow(cv, sp, fc["aura"], radius=5, strength=1.4)
    fill(cv, sp, _lt(fc["aura"], 60))
    finish(cv, W, H, _out(bone_id))


def draw_fang_serpent(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _forearm(W, H, cx, 6.5, 5.5), outline_w=2.8)
    fang = Layer(W, H)
    fang.tapered([(cx - 2, Y(150)), (cx + 14, Y(190)), (cx + 4, Y(236))], 16, 2)
    paint(cv, fang, base=IVORY_LIGHT, outline_w=2.4)
    groove = Layer(W, H)
    groove.curve([(cx + 2, Y(158)), (cx + 10, Y(190)), (cx + 4, Y(222))], 2.4)
    fill(cv, groove, fc["aura"], alpha=220)
    drop = Layer(W, H)
    drop.circle(cx + 4, Y(242), 5)
    glow(cv, drop, (150, 230, 80), radius=6, strength=1.4)
    fill(cv, drop, (190, 255, 120))
    finish(cv, W, H, _out(bone_id))


def draw_blade_death_knight(bone_id, family):
    s, W, H, cv, cx, top = _arm_canvas()
    fc = fam(family)
    paint(cv, _forearm(W, H, cx, 7.5, 6.5), outline_w=2.8)
    gauntlet = Layer(W, H)
    gauntlet.rrect(cx - 16, Y(132), cx + 14, Y(168), 7)
    paint(cv, gauntlet, outline_w=2.6, **DARK_IRON_KW)
    blade = Layer(W, H)
    blade.poly([(cx - 8, Y(166)), (cx + 8, Y(166)), (cx + 4, Y(250)), (cx, Y(266)), (cx - 4, Y(250))])
    glow(cv, blade, fc["aura"], radius=10, strength=1.1)
    paint(cv, blade, base=(180, 190, 210), shadow=(90, 96, 116), light=(240, 245, 255), outline_w=2.4)
    guard = Layer(W, H)
    guard.rrect(cx - 26, Y(162), cx + 26, Y(172), 4)
    paint(cv, guard, outline_w=2, **GOLD_KW)
    runes(cv, W, H, cx, Y(210), 6, fc["aura"])
    accent_dots(cv, W, H, [(cx, Y(91))], fc["aura"], 3.6, glow_r=5)
    finish(cv, W, H, _out(bone_id))


# -------------------------------------------------------------- pernas

def draw_legs_scarab(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    hip = Layer(W, H)
    hip.ellipse(cx, top + 6, 52, 18)
    paint(cv, hip, outline_w=3, **SHELL_KW)
    legs = Layer(W, H)
    for side in (-1, 1):
        h = (cx + side * 34, top + 10)
        k = (cx + side * 58, top + 100)
        a = (cx + side * 42, H - 22)
        legs.tapered([h, k], 11, 9)
        legs.tapered([k, a], 9, 6)
        legs.tapered([a, (a[0] + side * 24, H - 8)], 6, 2)
    paint(cv, legs, outline_w=2.8, **SHELL_KW)
    spikes = Layer(W, H)
    for side in (-1, 1):
        for t in (0.35, 0.65):
            x = cx + side * (34 + 24 * t)
            y = top + 10 + 90 * t
            spikes.poly([(x, y - 6), (x + side * 14, y), (x, y + 6)])
    paint(cv, spikes, outline_w=1.6, **SHELL_KW)
    accent_dots(cv, W, H, [(cx - 58, top + 100), (cx + 58, top + 100)], fc["aura"], 3, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_legs_spider_queen(bone_id, family):
    s, W, H, cv, cx, top = _legs_canvas()
    fc = fam(family)
    hip = Layer(W, H)
    hip.ellipse(cx, top + 6, 54, 20)
    paint(cv, hip, base=(110, 80, 120), shadow=(60, 40, 70), light=(170, 140, 180), outline_w=3)
    for side, d in ((-1, 0.78), (1, 1.0)):
        legs = Layer(W, H)
        for i, dx in enumerate((-30, -10, 10, 30)):
            h = (cx + dx * 0.6, top + 8)
            k = (cx + dx * 1.4 + side * 40, top + 60 + i * 10)
            a = (cx + dx * 1.2 + side * 22, H - 10)
            legs.tapered([h, k], 7, 6)
            legs.tapered([k, a], 6, 1.5)
        paint(cv, legs, base=tuple(int(c * d) for c in IVORY), outline_w=2.4)
    crown = Layer(W, H)
    crown.poly([(cx - 26, top - 4), (cx - 22, top - 26), (cx - 10, top - 12), (cx, top - 30), (cx + 10, top - 12), (cx + 22, top - 26), (cx + 26, top - 4)])
    paint(cv, crown, outline_w=2.2, **GOLD_KW)
    mark = Layer(W, H)
    mark.poly([(cx, top - 4), (cx + 10, top + 6), (cx, top + 16), (cx - 10, top + 6)])
    glow(cv, mark, fc["aura"], radius=8, strength=1.4)
    fill(cv, mark, _lt(fc["aura"], 40))
    finish(cv, W, H, _out(bone_id))


# -------------------------------------------------------------- costas

def draw_shell_scarab(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    shell = Layer(W, H)
    shell.ellipse(px - 30, py - 18, 104, 116)
    paint(cv, shell, outline_w=3.2, **SHELL_KW)
    seam = Layer(W, H)
    seam.line([(px - 30, py - 134), (px - 30, py + 96)], 4)
    fill(cv, seam, (90, 66, 36))
    # sulcos e o escaravelho sagrado gravado
    grooves = Layer(W, H)
    for k in (-1, 1):
        grooves.curve([(px - 30 + k * 30, py - 110), (px - 30 + k * 60, py - 20), (px - 30 + k * 34, py + 70)], 3)
    fill(cv, inter(grooves, shell), (140, 112, 66), alpha=220)
    runes(cv, W, H, px - 64, py - 40, 12, fc["aura"])
    runes(cv, W, H, px + 4, py - 40, 12, fc["aura"])
    gloss = Layer(W, H)
    gloss.ellipse(px - 74, py - 66, 16, 36)
    fill(cv, gloss, (255, 245, 210), alpha=110, blur=2)
    finish(cv, W, H, _out(bone_id))


def draw_wings_vulture(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)

    def deco(mem, el, tps, f, dim):
        fe = Layer(W, H)
        for i in range(6):
            t = i / 5
            x = el[0] + (tps[-1][0] - el[0]) * t
            y = el[1] + (tps[-1][1] - el[1]) * t + 30 * f
            fe.poly(leaf_pts((x, y), -100, 44 * f, 12 * f, power=0.6))
        fill(cv, inter(fe, mem), _dk(FEATHER, 0.6 * dim), alpha=200)
    membrane_wings(cv, W, H, px, py, FEATHER, dict(base=IVORY, shadow=IVORY_SHADOW, light=IVORY_LIGHT), BAT_ELBOW, BAT_TIPS,
                   k=1.0, decorate=deco, bone_w=8, scallop=0.1)
    root_knob(cv, W, H, px, py, 12)
    accent_dots(cv, W, H, [(px, py)], fc["aura"], 4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_tentacles_kraken(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    m = Layer(W, H)
    tips = []
    for i, ang in enumerate((-170, -140, -110, -80)):
        pts = []
        for k in range(10):
            t = k / 9
            a = math.radians(ang + math.sin(t * 3 + i) * 18)
            pts.append((px + math.cos(a) * 190 * t, py + math.sin(a) * 160 * t))
        m.tapered(pts, 17, 4)
        tips.append(pts)
    paint(cv, m, outline_w=3)
    suck = Layer(W, H)
    for pts in tips:
        for k in range(2, 9, 2):
            suck.circle(pts[k][0], pts[k][1], 4)
    fill(cv, suck, (150, 120, 110), alpha=220)
    gems = Layer(W, H)
    for pts in tips:
        gems.circle(pts[-1][0], pts[-1][1], 5)
    glow(cv, gems, fc["aura"], radius=8, strength=1.5)
    fill(cv, gems, _lt(fc["aura"], 60))
    root_knob(cv, W, H, px, py, 15)
    finish(cv, W, H, _out(bone_id))


# -------------------------------------------------------------- caudas

def _bead_tail(cv, W, H, px, py, n, length, wave, w0, w1, ow=2.8, **kw):
    path = []
    for i in range(n):
        t = i / (n - 1)
        path.append((px - 4 - length * t, py + math.sin(t * math.pi * 2.0) * wave * (0.3 + t)))
    m = Layer(W, H)
    for i, (x, y) in enumerate(path):
        m.circle(x, y, w0 + (w1 - w0) * i / (n - 1))
    paint(cv, m, outline_w=ow, **kw)
    return path


def draw_tail_imp(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    path = _bead_tail(cv, W, H, px, py, 26, 170, 22, 10, 4)
    ex, ey = path[-1]
    tip = Layer(W, H)
    tip.poly([(ex + 6, ey - 4), (ex - 30, ey - 18), (ex - 20, ey + 4), (ex - 30, ey + 20)])
    glow(cv, tip, ICE, radius=7, strength=1.2)
    paint(cv, tip, outline_w=2.2, grain=False, **ICE_KW)
    accent_dots(cv, W, H, [path[0]], fc["aura"], 3.4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


def draw_spine_serpent(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    path = _bead_tail(cv, W, H, px, py, 34, 200, 30, 13, 5)
    sp = Layer(W, H)
    nrm = path_normals(path)
    for i in range(3, len(path) - 2, 4):
        x, y = path[i]
        _, _, nx, ny = nrm[i]
        r = 13 - 8 * i / len(path) + 2
        sp.poly([(x - 4, y), (x - nx * (r + 12), y - ny * (r + 12)), (x + 4, y)])
    paint(cv, sp, base=fc["detail"], shadow=_dk(fc["detail"], 0.6), light=_lt(fc["detail"], 50), outline_w=2, grain=False)
    accent_dots(cv, W, H, [path[0], path[16]], fc["aura"], 3.4, glow_r=4)
    finish(cv, W, H, _out(bone_id))


DRAW = {
    "bone_helm_knight": draw_helm_knight,
    "bone_bell_jelly": draw_bell_jelly,
    "bone_skull_vulture": draw_skull_vulture,
    "bone_skull_imp": draw_skull_imp,
    "bone_shield_knight": draw_shield_knight,
    "bone_tentacle_jelly": draw_tentacle_jelly,
    "bone_fang_serpent": draw_fang_serpent,
    "bone_blade_death_knight": draw_blade_death_knight,
    "bone_legs_scarab": draw_legs_scarab,
    "bone_legs_spider_queen": draw_legs_spider_queen,
    "bone_shell_scarab": draw_shell_scarab,
    "bone_wings_vulture": draw_wings_vulture,
    "bone_tentacles_kraken": draw_tentacles_kraken,
    "bone_tail_imp": draw_tail_imp,
    "bone_spine_serpent": draw_spine_serpent,
}
