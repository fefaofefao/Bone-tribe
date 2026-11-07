#!/usr/bin/env python3
"""Monstros e chefes da terceira leva (1.4) do Bone Tribe.

Mesmo estilo de tools/gen_art.py e art_wave2_monsters.py: marfim com contorno escuro,
detalhes na cor da família, desenhados virados para a direita (gen_art espelha).
Uso: BT_ONLY=monster_bone_scarab python3 tools/gen_art.py monsters
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa
from art_wave2_monsters import _dk, _lt, pc, blob, mem_wing, wisps  # noqa

IRON = (104, 110, 128)
IRON_KW = dict(base=IRON, shadow=(56, 60, 74), light=(172, 182, 202))
RUST = (150, 70, 50)
JELLY = (150, 200, 230)


def _legs6(cv, W, H, cx, by, span, lift, thick, col=IVORY, dim=1.0):
    """Seis patas de inseto (três de cada lado, as de trás mais escuras)."""
    for side, d in ((-1, 0.78), (1, 1.0)):
        m = Layer(W, H)
        for i, dx in enumerate((-span, 0, span)):
            hip = (cx + dx * 0.4, by - lift)
            knee = (cx + dx + side * 8, by - lift - 22 + i * 4)
            foot = (cx + dx * 1.25 + side * 4, by)
            m.tapered([hip, knee], thick, thick * 0.8)
            m.tapered([knee, foot], thick * 0.8, thick * 0.35)
        paint(cv, m, base=tuple(int(c * d * dim) for c in col), outline_w=2.4)


# ------------------------------------------------------------- monstros

def m_bone_scarab(cv, W, H, fc):
    by = H - 12
    cx = W * 0.48
    _legs6(cv, W, H, cx, by, 62, 46, 8)
    shell = Layer(W, H)
    blob(shell, [(cx - 112, by - 60), (cx - 70, by - 150), (cx + 10, by - 170), (cx + 92, by - 130), (cx + 108, by - 64), (cx, by - 42)])
    pc(cv, shell, (196, 170, 120), ow=3.2)
    seam = Layer(W, H)
    seam.curve([(cx + 6, by - 168), (cx - 8, by - 104), (cx - 2, by - 46)], 4)
    fill(cv, seam, (80, 60, 40))
    runes(cv, W, H, cx - 54, by - 112, 18, fc["aura"])
    runes(cv, W, H, cx + 40, by - 110, 16, fc["aura"])
    head = Layer(W, H)
    head.ellipse(cx + 118, by - 70, 34, 28)
    paint(cv, head, outline_w=2.8)
    horn = Layer(W, H)
    horn.tapered([(cx + 132, by - 88), (cx + 156, by - 140), (cx + 146, by - 168)], 12, 2)
    paint(cv, horn, outline_w=2.6)
    eye_glow(cv, W, H, [(cx + 130, by - 76)], fc["aura"], 7)
    mand = Layer(W, H)
    mand.tapered([(cx + 140, by - 56), (cx + 172, by - 50), (cx + 168, by - 34)], 7, 2)
    paint(cv, mand, outline_w=2.2)


def m_skeleton_knight(cv, W, H, fc):
    by = H - 10
    cx = W * 0.46
    legs = Layer(W, H)
    legs.bone((cx - 18, by - 150), (cx - 30, by - 76), 10)
    legs.bone((cx - 30, by - 72), (cx - 26, by - 6), 9)
    legs.bone((cx + 22, by - 150), (cx + 36, by - 76), 10)
    legs.bone((cx + 36, by - 72), (cx + 30, by - 6), 9)
    paint(cv, legs, outline_w=3)
    boots = Layer(W, H)
    boots.rrect(cx - 50, by - 22, cx - 4, by, 6)
    boots.rrect(cx + 10, by - 22, cx + 56, by, 6)
    paint(cv, boots, outline_w=2.6, **IRON_KW)
    torso = Layer(W, H)
    torso.rrect(cx - 46, by - 262, cx + 48, by - 150, 18)
    paint(cv, torso, outline_w=3.2, **IRON_KW)
    belt = Layer(W, H)
    belt.rrect(cx - 48, by - 162, cx + 50, by - 146, 5)
    paint(cv, belt, base=RUST, shadow=_dk(RUST), outline_w=2, grain=False)
    plate = Layer(W, H)
    plate.poly([(cx - 30, by - 250), (cx + 32, by - 250), (cx + 2, by - 190)])
    fill(cv, plate, fc["detail"], alpha=200)
    # escudo (frente) e espada (trás)
    sword = Layer(W, H)
    sword.tapered([(cx - 40, by - 200), (cx - 78, by - 330)], 11, 3)
    sword.rrect(cx - 58, by - 210, cx - 22, by - 198, 3)
    paint(cv, sword, outline_w=2.4, **IRON_KW)
    shield = Layer(W, H)
    blob(shield, [(cx + 30, by - 250), (cx + 100, by - 246), (cx + 102, by - 170), (cx + 66, by - 120), (cx + 30, by - 170)], 2)
    paint(cv, shield, outline_w=3, **IRON_KW)
    emb = Layer(W, H)
    emb.bone((cx + 50, by - 222), (cx + 82, by - 160), 4)
    emb.bone((cx + 82, by - 222), (cx + 50, by - 160), 4)
    paint(cv, emb, outline_w=1.8)
    draw_skull(cv, W, H, cx + 6, by - 300, 40, eye_color=fc["aura"])
    helm = Layer(W, H)
    helm.poly([(cx - 36, by - 316), (cx - 20, by - 352), (cx + 30, by - 356), (cx + 50, by - 318), (cx + 40, by - 304), (cx - 30, by - 304)])
    paint(cv, helm, outline_w=2.8, **IRON_KW)
    plume = Layer(W, H)
    plume.tapered([(cx + 4, by - 354), (cx - 30, by - 384), (cx - 70, by - 372)], 12, 3)
    paint(cv, plume, base=RUST, shadow=_dk(RUST), light=_lt(RUST), outline_w=2.2, grain=False)


def m_ghost_jelly(cv, W, H, fc):
    cx, top = W * 0.5, 30
    tent = Layer(W, H)
    for i, dx in enumerate((-60, -30, 0, 30, 60)):
        pts = []
        for k in range(8):
            t = k / 7
            pts.append((cx + dx + math.sin(t * 5 + i) * 14, top + 120 + t * 150))
        tent.tapered(pts, 9, 2)
    paint(cv, tent, base=_dk(JELLY, 0.8), shadow=_dk(JELLY, 0.5), light=JELLY, outline_w=2.2, grain=False, alpha=200)
    bell = Layer(W, H)
    bell.ellipse(cx, top + 90, 104, 74)
    cut = Layer(W, H)
    cut.rrect(cx - 120, top + 120, cx + 120, top + 200, 4)
    bell.cut(cut)
    paint(cv, bell, base=JELLY, shadow=_dk(JELLY, 0.6), light=(230, 250, 255), outline_w=3, grain=False, alpha=190)
    inner = Layer(W, H)
    inner.ellipse(cx, top + 92, 70, 44)
    inner.cut(cut)
    glow(cv, inner, fc["aura"], radius=14, strength=1.0)
    draw_skull(cv, W, H, cx - 6, top + 86, 38, eye_color=fc["aura"])
    dots = Layer(W, H)
    for a in range(9):
        ang = math.pi * (0.1 + 0.8 * a / 8)
        dots.circle(cx - math.cos(ang) * 96, top + 92 - math.sin(ang) * 64, 4)
    glow(cv, dots, fc["aura"], radius=5, strength=1.5)


def m_carrion_vulture(cv, W, H, fc):
    by = H - 16
    cx = W * 0.44
    mem_wing(cv, W, H, (cx + 10, by - 150), (cx - 70, by - 230), [(cx - 150, by - 240), (cx - 170, by - 200), (cx - 160, by - 160)], (86, 64, 58), dim=0.7)
    legs = Layer(W, H)
    legs.bone((cx - 6, by - 92), (cx - 14, by - 40), 7)
    legs.bone((cx - 14, by - 36), (cx - 4, by - 4), 6)
    legs.bone((cx + 26, by - 92), (cx + 32, by - 40), 7)
    legs.bone((cx + 32, by - 36), (cx + 42, by - 4), 6)
    paint(cv, legs, outline_w=2.6)
    talon = Layer(W, H)
    for x in (cx - 4, cx + 42):
        for k in (-14, 0, 14):
            talon.tapered([(x, by - 6), (x + k, by + 4)], 4, 1)
    paint(cv, talon, base=(70, 60, 50), outline_w=1.6, grain=False)
    body = Layer(W, H)
    blob(body, [(cx - 50, by - 110), (cx - 10, by - 170), (cx + 60, by - 160), (cx + 70, by - 100), (cx + 20, by - 82)])
    pc(cv, body, (110, 86, 74), ow=3)
    ribs = Layer(W, H)
    for i in range(4):
        ribs.curve([(cx - 10 + i * 16, by - 160), (cx + 2 + i * 16, by - 128), (cx - 6 + i * 16, by - 98)], 5)
    paint(cv, ribs, outline_w=2.2)
    ruff = Layer(W, H)
    ruff.ellipse(cx + 70, by - 170, 34, 22)
    pc(cv, ruff, (200, 190, 176), ow=2.4)
    neck = Layer(W, H)
    neck.tapered([(cx + 74, by - 176), (cx + 106, by - 214), (cx + 136, by - 208)], 12, 8)
    paint(cv, neck, base=(200, 120, 110), shadow=(130, 70, 60), outline_w=2.4, grain=False)
    draw_skull(cv, W, H, cx + 150, by - 214, 28, snout=0.3, eye_color=fc["aura"])
    beak = Layer(W, H)
    beak.poly([(cx + 170, by - 214), (cx + 206, by - 204), (cx + 196, by - 186), (cx + 170, by - 196)])
    paint(cv, beak, base=(230, 200, 120), shadow=(150, 120, 60), outline_w=2.2, grain=False)
    mem_wing(cv, W, H, (cx + 20, by - 140), (cx - 40, by - 250), [(cx - 110, by - 280), (cx - 140, by - 236), (cx - 130, by - 186)], (110, 82, 72))


def m_frost_imp(cv, W, H, fc):
    by = H - 12
    cx = W * 0.5
    ice = (170, 220, 255)
    tail = Layer(W, H)
    tail.tapered([(cx - 30, by - 80), (cx - 90, by - 70), (cx - 120, by - 120)], 8, 2)
    paint(cv, tail, outline_w=2.4)
    tip = Layer(W, H)
    tip.poly([(cx - 128, by - 136), (cx - 108, by - 120), (cx - 130, by - 110)])
    paint(cv, tip, base=ice, shadow=_dk(ice, 0.6), light=(240, 250, 255), outline_w=2, grain=False)
    mem_wing(cv, W, H, (cx - 10, by - 150), (cx - 60, by - 210), [(cx - 110, by - 230), (cx - 116, by - 190), (cx - 96, by - 160)], (120, 160, 200), dim=0.75)
    legs = Layer(W, H)
    legs.bone((cx - 12, by - 82), (cx - 26, by - 40), 7)
    legs.bone((cx - 26, by - 36), (cx - 14, by - 4), 6)
    legs.bone((cx + 16, by - 82), (cx + 30, by - 40), 7)
    legs.bone((cx + 30, by - 36), (cx + 22, by - 4), 6)
    paint(cv, legs, outline_w=2.6)
    body = Layer(W, H)
    body.ellipse(cx, by - 118, 36, 44)
    paint(cv, body, outline_w=2.8)
    ribs = Layer(W, H)
    for i in range(3):
        ribs.curve([(cx - 20, by - 140 + i * 16), (cx, by - 132 + i * 16), (cx + 22, by - 140 + i * 16)], 4)
    fill(cv, ribs, (120, 100, 90), alpha=160)
    arm = Layer(W, H)
    arm.bone((cx + 20, by - 140), (cx + 60, by - 120), 6)
    arm.bone((cx + 60, by - 120), (cx + 84, by - 150), 5)
    paint(cv, arm, outline_w=2.4)
    shard = Layer(W, H)
    shard.poly([(cx + 80, by - 150), (cx + 100, by - 210), (cx + 108, by - 150)])
    glow(cv, shard, ice, radius=8, strength=1.2)
    paint(cv, shard, base=ice, shadow=_dk(ice, 0.6), light=(245, 252, 255), outline_w=2, grain=False)
    draw_skull(cv, W, H, cx + 6, by - 190, 34, horns=[(-0.35, -0.7, -0.35, -0.75), (0.25, -0.8, 0.3, -0.8)], eye_color=ice)
    mem_wing(cv, W, H, (cx, by - 146), (cx - 40, by - 230), [(cx - 86, by - 262), (cx - 104, by - 222), (cx - 84, by - 176)], (140, 180, 220))


def m_bone_serpent(cv, W, H, fc):
    by = H - 14
    n = 40
    path = []
    for i in range(n):
        t = i / (n - 1)
        path.append((30 + t * (W - 140), by - 20 - math.sin(t * math.pi * 2.2) * 34 - t * 120))
    body = Layer(W, H)
    for i, (x, y) in enumerate(path):
        body.circle(x, y, 8 + 14 * (i / (n - 1)))
    paint(cv, body, outline_w=3)
    ribs = Layer(W, H)
    for i in range(4, n - 4, 3):
        x, y = path[i]
        r = 8 + 14 * (i / (n - 1))
        ribs.curve([(x, y - r * 0.8), (x + r * 0.5, y), (x, y + r * 0.9)], 3)
    fill(cv, ribs, (110, 90, 80), alpha=170)
    spikes = Layer(W, H)
    for i in range(6, n - 2, 4):
        x, y = path[i]
        r = 8 + 14 * (i / (n - 1))
        spikes.poly([(x - 6, y - r + 2), (x, y - r - 14), (x + 6, y - r + 2)])
    pc(cv, spikes, fc["detail"], ow=2)
    hx, hy = path[-1]
    draw_skull(cv, W, H, hx + 40, hy - 6, 42, snout=0.7, jaw=1.2, eye_color=fc["aura"])
    fang = Layer(W, H)
    fang.poly([(hx + 70, hy + 22), (hx + 76, hy + 46), (hx + 82, hy + 22)])
    paint(cv, fang, base=IVORY_LIGHT, outline_w=1.6, shade=False, grain=False)
    wisps(cv, W, H, [(path[10][0], path[10][1], 14), (path[22][0], path[22][1], 16), (path[32][0], path[32][1], 18)], fc["aura"])


# ---------------------------------------------------------------- chefes

def m_spider_queen(cv, W, H, fc):
    by = H - 14
    cx = W * 0.46
    # oito patas longas
    for side, d in ((-1, 0.75), (1, 1.0)):
        m = Layer(W, H)
        for i, dx in enumerate((-150, -70, 20, 110)):
            hip = (cx + dx * 0.25, by - 170)
            knee = (cx + dx * 0.9, by - 280 + abs(dx) * 0.2)
            foot = (cx + dx * 1.35 + side * 10, by)
            m.tapered([hip, knee], 13, 10)
            m.tapered([knee, foot], 10, 3)
        paint(cv, m, base=tuple(int(c * d) for c in IVORY), outline_w=3)
    abd = Layer(W, H)
    abd.ellipse(cx - 120, by - 170, 110, 84)
    pc(cv, abd, (90, 60, 100), ow=3.4)
    mark = Layer(W, H)
    mark.poly([(cx - 150, by - 210), (cx - 110, by - 170), (cx - 150, by - 130), (cx - 190, by - 170)])
    glow(cv, mark, fc["aura"], radius=12, strength=1.4)
    fill(cv, mark, _lt(fc["aura"], 40))
    thorax = Layer(W, H)
    thorax.ellipse(cx + 20, by - 200, 70, 56)
    paint(cv, thorax, outline_w=3.2)
    ribs = Layer(W, H)
    for i in range(4):
        ribs.curve([(cx - 20 + i * 24, by - 246), (cx - 8 + i * 24, by - 200), (cx - 16 + i * 24, by - 154)], 5)
    fill(cv, ribs, (120, 100, 90), alpha=170)
    draw_skull(cv, W, H, cx + 120, by - 240, 56, eye_color=fc["aura"])
    eyes = [(cx + 140, by - 266), (cx + 160, by - 252), (cx + 152, by - 280)]
    eye_glow(cv, W, H, eyes, fc["aura"], 6)
    crown = Layer(W, H)
    crown.poly([(cx + 80, by - 286), (cx + 84, by - 330), (cx + 104, by - 304), (cx + 120, by - 344), (cx + 136, by - 304), (cx + 156, by - 330), (cx + 160, by - 286)])
    paint(cv, crown, base=(236, 190, 64), shadow=(150, 106, 24), light=(255, 240, 160), outline_w=2.6)
    fang = Layer(W, H)
    fang.tapered([(cx + 150, by - 200), (cx + 176, by - 170), (cx + 166, by - 146)], 9, 2)
    fang.tapered([(cx + 124, by - 196), (cx + 136, by - 160), (cx + 124, by - 140)], 9, 2)
    paint(cv, fang, outline_w=2.2)


def m_bone_kraken(cv, W, H, fc):
    by = H - 12
    cx = W * 0.5
    sea = (70, 120, 150)
    tent = Layer(W, H)
    for i, dx in enumerate((-190, -120, -50, 30, 110, 180)):
        pts = []
        for k in range(10):
            t = k / 9
            pts.append((cx + dx * (0.3 + 0.7 * t) + math.sin(t * 4 + i) * 22, by - 160 + t * 150 - math.sin(t * 3) * 20))
        tent.tapered(pts, 24, 5)
    paint(cv, tent, outline_w=3)
    suck = Layer(W, H)
    for i, dx in enumerate((-190, -120, -50, 30, 110, 180)):
        for k in range(2, 9, 2):
            t = k / 9
            suck.circle(cx + dx * (0.3 + 0.7 * t) + math.sin(t * 4 + i) * 22, by - 160 + t * 150 - math.sin(t * 3) * 20, 5)
    fill(cv, suck, (150, 120, 110), alpha=200)
    head = Layer(W, H)
    blob(head, [(cx - 130, by - 170), (cx - 110, by - 330), (cx, by - 420), (cx + 110, by - 330), (cx + 130, by - 170)])
    pc(cv, head, sea, ow=3.6)
    plates = Layer(W, H)
    for i in range(5):
        plates.curve([(cx - 90 + i * 10, by - 330 + i * 34), (cx, by - 344 + i * 34), (cx + 90 - i * 10, by - 330 + i * 34)], 6)
    paint(cv, plates, outline_w=2.2)
    draw_skull(cv, W, H, cx - 10, by - 220, 66, eye_color=fc["aura"])
    wisps(cv, W, H, [(cx - 160, by - 300, 24), (cx + 170, by - 280, 22)], fc["aura"])


def m_death_knight(cv, W, H, fc):
    by = H - 10
    cx = W * 0.44
    cape = Layer(W, H)
    blob(cape, [(cx - 90, by - 380), (cx + 60, by - 390), (cx + 90, by - 120), (cx + 40, by - 20), (cx - 160, by - 30), (cx - 150, by - 200)], 2)
    pc(cv, cape, (70, 30, 50), ow=3)
    legs = Layer(W, H)
    legs.bone((cx - 26, by - 190), (cx - 40, by - 100), 13)
    legs.bone((cx - 40, by - 96), (cx - 34, by - 8), 12)
    legs.bone((cx + 30, by - 190), (cx + 48, by - 100), 13)
    legs.bone((cx + 48, by - 96), (cx + 40, by - 8), 12)
    paint(cv, legs, outline_w=3.2)
    greaves = Layer(W, H)
    greaves.rrect(cx - 66, by - 30, cx - 8, by, 8)
    greaves.rrect(cx + 14, by - 30, cx + 72, by, 8)
    greaves.rrect(cx - 56, by - 120, cx - 22, by - 60, 8)
    greaves.rrect(cx + 30, by - 120, cx + 64, by - 60, 8)
    paint(cv, greaves, base=(60, 56, 72), shadow=(30, 28, 38), light=(130, 126, 150), outline_w=2.8)
    torso = Layer(W, H)
    torso.rrect(cx - 66, by - 340, cx + 70, by - 190, 24)
    paint(cv, torso, base=(60, 56, 72), shadow=(30, 28, 38), light=(130, 126, 150), outline_w=3.4)
    runes(cv, W, H, cx - 30, by - 290, 26, fc["aura"])
    runes(cv, W, H, cx + 30, by - 250, 22, fc["aura"])
    pa = Layer(W, H)
    pa.ellipse(cx - 70, by - 330, 40, 30)
    pa.ellipse(cx + 74, by - 330, 40, 30)
    paint(cv, pa, base=(80, 76, 96), shadow=(40, 38, 50), light=(150, 146, 170), outline_w=3)
    blade = Layer(W, H)
    blade.poly([(cx + 100, by - 260), (cx + 120, by - 270), (cx + 230, by - 470), (cx + 212, by - 470)])
    glow(cv, blade, fc["aura"], radius=12, strength=1.0)
    paint(cv, blade, base=(180, 190, 210), shadow=(90, 96, 116), light=(240, 245, 255), outline_w=2.6)
    guard = Layer(W, H)
    guard.rrect(cx + 80, by - 262, cx + 140, by - 248, 4)
    guard.bone((cx + 96, by - 250), (cx + 74, by - 210), 8)
    paint(cv, guard, outline_w=2.4)
    draw_skull(cv, W, H, cx + 4, by - 390, 52, horns=[(-0.45, -0.65, -0.7, -0.9), (0.3, -0.8, 0.6, -0.95)], eye_color=fc["aura"])
    helm = Layer(W, H)
    helm.poly([(cx - 46, by - 410), (cx - 30, by - 460), (cx + 40, by - 466), (cx + 62, by - 412), (cx + 50, by - 392), (cx - 40, by - 392)])
    paint(cv, helm, base=(60, 56, 72), shadow=(30, 28, 38), light=(130, 126, 150), outline_w=3)
    slit = Layer(W, H)
    slit.rrect(cx - 18, by - 420, cx + 44, by - 408, 3)
    glow(cv, slit, fc["aura"], radius=8, strength=1.6)
    fill(cv, slit, _lt(fc["aura"], 50))


DRAW = {
    "monster_bone_scarab": m_bone_scarab,
    "monster_skeleton_knight": m_skeleton_knight,
    "monster_ghost_jelly": m_ghost_jelly,
    "monster_carrion_vulture": m_carrion_vulture,
    "monster_frost_imp": m_frost_imp,
    "monster_bone_serpent": m_bone_serpent,
    "boss_spider_queen": m_spider_queen,
    "boss_bone_kraken": m_bone_kraken,
    "boss_death_knight": m_death_knight,
}
