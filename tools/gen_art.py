#!/usr/bin/env python3
"""Gera todos os placeholders de arte do Bone Tribe.

Cada arquivo leva o ID do GDD no nome (ex.: art/bones/bone_skull_wolf.png) e usa o
tamanho e o ponto de encaixe finais definidos em data/skeleton.json e data/monsters.json.
Para trocar pela arte final, basta substituir o PNG mantendo tamanho e pivot.

Uso: python3 tools/gen_art.py [icon|bones|monsters|env|ui|fx|all]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artlib import *  # noqa
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def data(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def out(*parts):
    p = os.path.join(ROOT, "art", *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# --------------------------------------------------------------- crânios

def skull_mask(w, h, cx, cy, size, snout=0.0, horns=None, jaw=1.0, crest=False, cyclops=False):
    """Máscara de crânio fofo virado para a direita. size = raio do crânio."""
    m = Layer(w, h)
    r = size
    m.ellipse(cx, cy, r * 1.0, r * 0.92)
    # bochecha / maxilar superior
    m.ellipse(cx + r * 0.25, cy + r * 0.45, r * 0.78, r * 0.5)
    if snout > 0:
        m.rrect(cx + r * 0.2, cy + r * 0.1, cx + r * (0.95 + snout), cy + r * 0.75, r * 0.3)
    # mandíbula
    jx0, jx1 = cx - r * 0.25, cx + r * (0.7 + snout * 0.9)
    m.rrect(jx0, cy + r * 0.62, jx1, cy + r * (0.62 + 0.38 * jaw), r * 0.18)
    if crest:
        m.poly([(cx - r * 0.5, cy - r * 0.6), (cx - r * 1.25, cy - r * 1.05), (cx - r * 0.85, cy - r * 0.2)])
    if horns:
        for hx, hy, ex, ey in horns:
            m.tapered([(cx + r * hx, cy + r * hy), (cx + r * (hx + ex * 0.4), cy + r * (hy + ey * 0.7)), (cx + r * (hx + ex), cy + r * (hy + ey))], r * 0.32, r * 0.05)
    return m


def skull_holes(w, h, cx, cy, size, snout=0.0, cyclops=False, jaw=1.0):
    holes = Layer(w, h)
    r = size
    if cyclops:
        holes.ellipse(cx + r * 0.28, cy + r * 0.02, r * 0.36, r * 0.34)
    else:
        holes.ellipse(cx + r * 0.52, cy + r * 0.05, r * 0.25, r * 0.29)
        holes.ellipse(cx - r * 0.02, cy + r * 0.02, r * 0.27, r * 0.31)
    # nariz
    nx = cx + r * (0.42 + snout * 0.9)
    holes.poly([(nx - r * 0.07, cy + r * 0.48), (nx + r * 0.07, cy + r * 0.48), (nx, cy + r * 0.34)])
    # dentes (frestas)
    ty = cy + r * 0.66
    x = cx - r * 0.1
    while x < cx + r * (0.62 + snout * 0.85):
        holes.rrect(x, ty - r * 0.02, x + r * 0.035, ty + r * 0.2 * jaw, r * 0.01)
        x += r * 0.15
    return holes


def draw_skull(cv, w, h, cx, cy, size, family="", snout=0.0, horns=None, cyclops=False, crest=False,
               eye_color=None, jaw=1.0, base=IVORY):
    m = skull_mask(w, h, cx, cy, size, snout, horns, jaw, crest, cyclops)
    holes = skull_holes(w, h, cx, cy, size, snout, cyclops, jaw)
    paint(cv, m, base=base, outline_w=max(2.5, size * 0.07))
    hole_fill = Layer(w, h)
    hole_fill.img = holes.img
    fill(cv, hole_fill, (28, 16, 18))
    # brilho dos olhos
    if eye_color:
        r = size
        eyes = Layer(w, h)
        if cyclops:
            eyes.circle(cx + r * 0.3, cy + r * 0.05, r * 0.13)
        else:
            eyes.circle(cx + r * 0.55, cy + r * 0.09, r * 0.09)
            eyes.circle(cx + r * 0.02, cy + r * 0.07, r * 0.1)
        glow(cv, eyes, eye_color, radius=size * 0.12, strength=2.2)
        fill(cv, eyes, tuple(min(255, c + 80) for c in eye_color))
    return m



# ---------------------------------------------------------------- ossos

def slot_info(slot_id):
    sk = data("skeleton.json")
    for s in sk["slots"] + sk["base_parts"]:
        if s["id"] == slot_id:
            return s
    raise KeyError(slot_id)


def fam(family):
    return FAMILY.get(family or "", FAMILY[""])


def accent_dots(cv, w, h, pts, color, r, glow_r=0):
    m = Layer(w, h)
    for x, y in pts:
        m.circle(x, y, r)
    if glow_r:
        glow(cv, m, color, radius=glow_r, strength=1.6)
    paint(cv, m, base=color, shadow=tuple(int(c * 0.6) for c in color), light=tuple(min(255, c + 60) for c in color), outline_w=1.6, grain=False)


def runes(cv, w, h, x, y, size, color):
    m = Layer(w, h)
    m.line([(x - size, y - size), (x, y + size), (x + size, y - size)], size * 0.35)
    m.line([(x, y - size * 1.1), (x, y + size)], size * 0.3)
    glow(cv, m, color, radius=size * 0.8, strength=2.0)
    fill(cv, m, tuple(min(255, c + 90) for c in color))


def fur(cv, w, h, x, y, n, length, color, rng_seed=1, angle=-90, spread=60):
    r = rng(rng_seed)
    m = Layer(w, h)
    for i in range(n):
        a = math.radians(angle + r.uniform(-spread, spread))
        l = length * r.uniform(0.6, 1.1)
        bx, by = x + r.uniform(-length * 0.4, length * 0.4), y + r.uniform(-length * 0.2, length * 0.2)
        ex, ey = bx + math.cos(a) * l, by + math.sin(a) * l
        m.tapered([(bx, by), ((bx + ex) / 2 + r.uniform(-4, 4), (by + ey) / 2), (ex, ey)], length * 0.28, 1)
    paint(cv, m, base=color, shadow=tuple(int(c * 0.55) for c in color), light=tuple(min(255, c + 50) for c in color), outline_w=1.8, grain=False)


def ember(cv, w, h, pts, color):
    m = Layer(w, h)
    for x, y, r in pts:
        m.circle(x, y, r)
    glow(cv, m, color, radius=6, strength=2.2)
    fill(cv, m, (255, 230, 160))


def draw_skull_bone(bone_id, family):
    s = slot_info("slot_skull")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    cx, cy, r = s["pivot"][0], s["pivot"][1] - 82, 70
    fc = fam(family)
    if bone_id == "bone_skull_basic":
        draw_skull(cv, W, H, cx, cy, r, eye_color=(255, 176, 66))
    elif bone_id == "bone_skull_wolf":
        ears = Layer(W, H)
        ears.poly([(cx - 52, cy - 40), (cx - 70, cy - 112), (cx - 10, cy - 62)])
        ears.poly([(cx - 8, cy - 62), (cx + 4, cy - 122), (cx + 40, cy - 58)])
        paint(cv, ears, outline_w=3)
        inner = Layer(W, H)
        inner.poly([(cx - 46, cy - 52), (cx - 60, cy - 98), (cx - 22, cy - 64)])
        inner.poly([(cx - 2, cy - 66), (cx + 6, cy - 106), (cx + 30, cy - 64)])
        fill(cv, inner, fc["detail"], alpha=200)
        fur(cv, W, H, cx - 60, cy + 10, 9, 26, (120, 78, 44), 3, angle=180, spread=50)
        draw_skull(cv, W, H, cx - 8, cy, r * 0.92, snout=0.5, eye_color=fc["aura"])
        fang = Layer(W, H)
        fang.poly([(cx + 62, cy + 52), (cx + 70, cy + 82), (cx + 76, cy + 52)])
        fang.poly([(cx + 30, cy + 54), (cx + 37, cy + 78), (cx + 43, cy + 54)])
        paint(cv, fang, base=IVORY_LIGHT, outline_w=1.8, shade=False, grain=False)
    elif bone_id == "bone_skull_cyclops":
        draw_skull(cv, W, H, cx, cy, r * 1.04, cyclops=True, eye_color=fc["aura"], base=(222, 216, 204))
        plate = Layer(W, H)
        plate.rrect(cx - 70, cy - 70, cx + 40, cy - 46, 8)
        paint(cv, plate, base=(120, 132, 150), shadow=(70, 80, 100), light=(190, 200, 220), outline_w=2.5)
        for i in range(4):
            accent_dots(cv, W, H, [(cx - 60 + i * 30, cy - 58)], (160, 170, 190), 4)
        runes(cv, W, H, cx - 40, cy + 30, 9, fc["aura"])
    elif bone_id == "bone_skull_dragon":
        horns = [(-0.6, -0.55, -0.9, -0.8), (-0.2, -0.75, -0.55, -1.0)]
        draw_skull(cv, W, H, cx - 12, cy + 4, r * 0.86, snout=0.75, horns=horns, eye_color=fc["aura"], crest=True)
        ember(cv, W, H, [(cx - 50, cy - 70, 4), (cx + 40, cy - 40, 3), (cx - 80, cy + 10, 3)], fc["aura"])
        scales = Layer(W, H)
        for i in range(5):
            scales.poly([(cx - 40 + i * 18, cy - 54 + abs(i - 2) * 4), (cx - 32 + i * 18, cy - 70 + abs(i - 2) * 4), (cx - 24 + i * 18, cy - 54 + abs(i - 2) * 4)])
        paint(cv, scales, base=(170, 50, 36), shadow=(100, 20, 16), light=(240, 110, 70), outline_w=1.8, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def rib_mask(W, H, cx, top, n, width, gap, thick):
    m = Layer(W, H)
    m.capsule((cx, top), (cx, top + gap * n + 6), thick * 0.75)
    for i in range(n):
        y = top + 14 + i * gap
        ww = width * (1 - 0.12 * i)
        for side in (-1, 1):
            m.curve([(cx, y), (cx + side * ww * 0.65, y - 10), (cx + side * ww, y + 14), (cx + side * ww * 0.75, y + gap * 0.9)], thick)
    return m


def draw_ribs_bone(bone_id, family):
    s = slot_info("slot_ribs")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    cx = s["pivot"][0]
    fc = fam(family)
    if bone_id == "bone_ribs_basic":
        paint(cv, rib_mask(W, H, cx, 18, 4, 62, 27, 11), outline_w=3)
    elif bone_id == "bone_ribs_turtle":
        shell = Layer(W, H)
        shell.ellipse(cx, 78, 76, 66)
        paint(cv, shell, base=(80, 150, 140), shadow=(40, 90, 90), light=(150, 220, 200), outline_w=3)
        plates = Layer(W, H)
        for (x, y, r) in [(cx, 60, 20), (cx - 36, 78, 16), (cx + 36, 78, 16), (cx - 18, 104, 15), (cx + 18, 104, 15), (cx, 30, 14)]:
            plates.circle(x, y, r)
        paint(cv, plates, base=(214, 206, 170), shadow=(150, 140, 110), outline_w=2)
        accent_dots(cv, W, H, [(cx - 52, 50), (cx + 56, 60), (cx - 10, 128), (cx + 46, 112)], (210, 240, 230), 5)
    elif bone_id == "bone_ribs_golem":
        paint(cv, rib_mask(W, H, cx, 18, 4, 70, 27, 14), base=(150, 160, 178), shadow=(80, 90, 110), light=(210, 220, 236), outline_w=3)
        bars = Layer(W, H)
        bars.rrect(cx - 72, 30, cx + 72, 40, 4)
        bars.rrect(cx - 64, 96, cx + 64, 106, 4)
        paint(cv, bars, base=(100, 110, 130), shadow=(60, 66, 80), outline_w=2.2)
        runes(cv, W, H, cx, 70, 11, fc["aura"])
        runes(cv, W, H, cx - 44, 64, 7, fc["aura"])
        runes(cv, W, H, cx + 44, 64, 7, fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def arm_base(W, H, cx, top, color=IVORY, lower_len=1.0, cv=None):
    m = Layer(W, H)
    m.bone((cx, top + 6), (cx + 2, top + 92), 9)
    m.bone((cx + 2, top + 98), (cx - 2, top + 98 + 70 * lower_len), 7.5)
    return m


def draw_arm_bone(bone_id, family):
    s = slot_info("slot_arm_right")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    cx, top = s["pivot"][0], s["pivot"][1]
    fc = fam(family)
    if bone_id == "bone_claw_bear":
        paint(cv, arm_base(W, H, cx, top), outline_w=3)
        fur(cv, W, H, cx, top + 170, 10, 30, (110, 72, 40), 5, angle=90, spread=70)
        paw = Layer(W, H)
        paw.ellipse(cx, top + 185, 30, 22)
        paint(cv, paw, base=(120, 80, 48), shadow=(70, 44, 24), light=(170, 120, 80), outline_w=3)
        claws = Layer(W, H)
        for dx in (-20, 0, 20):
            claws.tapered([(cx + dx, top + 196), (cx + dx + 4, top + 214), (cx + dx - 6, top + 228)], 11, 1)
        paint(cv, claws, base=IVORY_LIGHT, outline_w=2.2)
    elif bone_id == "bone_pincer_crab":
        paint(cv, arm_base(W, H, cx, top, lower_len=0.6), outline_w=3)
        claw = Layer(W, H)
        claw.ellipse(cx, top + 170, 30, 26)
        claw.tapered([(cx - 20, top + 175), (cx - 34, top + 200), (cx - 18, top + 226)], 22, 4)
        claw.tapered([(cx + 18, top + 180), (cx + 30, top + 200), (cx + 12, top + 220)], 16, 3)
        paint(cv, claw, base=(70, 175, 170), shadow=(30, 100, 100), light=(150, 230, 220), outline_w=3)
        accent_dots(cv, W, H, [(cx - 14, top + 160), (cx + 10, top + 168), (cx - 2, top + 182)], (220, 236, 226), 4.5)
    elif bone_id == "bone_stinger_wasp":
        paint(cv, arm_base(W, H, cx, top, lower_len=0.55), outline_w=3)
        st = Layer(W, H)
        st.tapered([(cx, top + 140), (cx + 4, top + 180), (cx, top + 226)], 30, 2)
        paint(cv, st, base=(214, 196, 70), shadow=(130, 110, 30), light=(250, 240, 150), outline_w=3)
        bands = Layer(W, H)
        for y in (top + 150, top + 172, top + 192):
            bands.rrect(cx - 13, y, cx + 13, y + 8, 3)
        fill(cv, bands, (40, 30, 20))
        accent_dots(cv, W, H, [(cx + 2, top + 226)], fc["aura"], 4, glow_r=6)
    elif bone_id == "bone_blade_mantis":
        paint(cv, arm_base(W, H, cx, top, lower_len=0.4), outline_w=3)
        blade = Layer(W, H)
        blade.poly([(cx - 8, top + 120), (cx + 26, top + 140), (cx + 34, top + 190), (cx + 10, top + 228), (cx + 12, top + 180), (cx - 6, top + 140)])
        paint(cv, blade, base=(150, 210, 90), shadow=(70, 120, 40), light=(220, 255, 170), outline_w=3)
        edge = Layer(W, H)
        edge.line([(cx + 30, top + 150), (cx + 30, top + 190), (cx + 12, top + 222)], 3)
        fill(cv, edge, (240, 255, 220))
    elif bone_id == "bone_fist_golem":
        paint(cv, arm_base(W, H, cx, top, color=(160, 170, 186), lower_len=0.6), base=(170, 176, 190), shadow=(90, 96, 112), outline_w=3)
        fist = Layer(W, H)
        fist.rrect(cx - 40, top + 150, cx + 40, top + 222, 16)
        paint(cv, fist, base=(130, 140, 160), shadow=(70, 76, 94), light=(200, 210, 230), outline_w=3.2)
        knuck = Layer(W, H)
        for i in range(4):
            knuck.rrect(cx - 36 + i * 19, top + 200, cx - 22 + i * 19, top + 220, 5)
        paint(cv, knuck, base=(110, 120, 140), shadow=(60, 66, 84), outline_w=1.8, grain=False)
        runes(cv, W, H, cx, top + 178, 10, fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_legs_bone(bone_id, family):
    s = slot_info("slot_legs")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    cx, top = s["pivot"][0], s["pivot"][1]
    fc = fam(family)
    if bone_id == "bone_legs_spider":
        m = Layer(W, H)
        pts = []
        for side in (-1, 1):
            for k, (reach, knee_up, out_x, foot) in enumerate(((84, 44, 112, 104), (52, 30, 76, 44))):
                hip = (cx + side * 12, top + 4)
                knee = (cx + side * reach, top - knee_up)
                mid = (cx + side * out_x, top + 70)
                ft = (cx + side * foot, H - 8)
                m.tapered([hip, knee], 13 - k * 2, 10 - k * 2)
                m.tapered([knee, mid], 10 - k * 2, 8 - k * 2)
                m.tapered([mid, ft], 8 - k * 2, 3)
                pts += [knee, mid]
        paint(cv, m, base=(210, 204, 160), shadow=(124, 122, 82), outline_w=3)
        accent_dots(cv, W, H, pts, fc["aura"], 4.5, glow_r=3)
    elif bone_id == "bone_legs_grasshopper":
        m = Layer(W, H)
        for side, dx in ((-1, -26), (1, 26)):
            knee = (cx + dx + side * 6, top + 60)
            back = (cx + dx - 34, top + 120)
            m.tapered([(cx + dx * 0.4, top + 12), knee], 26, 14)
            m.capsule(knee, back, 6)
            m.capsule(back, (cx + dx + 10, H - 10), 5.5)
            m.ellipse(cx + dx + 16, H - 10, 16, 7)
        paint(cv, m, base=(186, 214, 110), shadow=(100, 130, 50), light=(230, 250, 170), outline_w=3)
    elif bone_id == "bone_legs_centaur":
        body = Layer(W, H)
        body.ellipse(cx - 10, top + 50, 80, 40)
        paint(cv, body, base=(150, 100, 60), shadow=(90, 56, 30), light=(200, 150, 100), outline_w=3)
        ribs = rib_mask(W, H, cx - 10, top + 20, 3, 50, 16, 7)
        paint(cv, ribs, outline_w=2)
        legs = Layer(W, H)
        for x in (cx - 70, cx - 40, cx + 20, cx + 50):
            legs.bone((x, top + 70), (x + 2, top + 150), 7)
            legs.bone((x + 2, top + 154), (x - 2, H - 22), 6)
        paint(cv, legs, outline_w=3)
        hooves = Layer(W, H)
        for x in (cx - 72, cx - 42, cx + 18, cx + 48):
            hooves.rrect(x - 9, H - 24, x + 11, H - 4, 4)
        paint(cv, hooves, base=(70, 50, 40), shadow=(40, 26, 20), outline_w=2, grain=False)
        fur(cv, W, H, cx - 92, top + 40, 7, 26, (110, 70, 40), 9, angle=180, spread=40)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def wing(m, root, span, droop, fingers=4, up=1.0):
    rx, ry = root
    tips = []
    for i in range(fingers):
        a = math.radians(-160 + i * 26 * up)
        tx = rx + math.cos(a) * span * (1 - i * 0.08)
        ty = ry + math.sin(a) * span * 0.75 * (1 - i * 0.05)
        tips.append((tx, ty))
    return tips


def draw_back_bone(bone_id, family):
    s = slot_info("slot_back")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    px, py = s["pivot"]
    fc = fam(family)
    if bone_id in ("bone_wings_bat", "bone_wings_dragon"):
        big = bone_id == "bone_wings_dragon"
        mem_col = (160, 44, 32) if big else (84, 46, 118)
        k = 1.0 if big else 0.94
        near = {"elbow": (-70, -112), "tips": [(-196, -150), (-204, -86), (-182, -26), (-128, 22)]}
        # asa de trás (direita, menor e mais escura) e asa da frente (esquerda)
        for side, sc, dim in ((1, 0.72, 0.6), (-1, 1.0, 1.0)):
            f = sc * k
            root = (px, py)
            def P(v):
                return (px - v[0] * f * side * -1 if side > 0 else px + v[0] * f, py + v[1] * f)
            elbow = P(near["elbow"])
            tips = [P(v) for v in near["tips"]]
            poly = [root, elbow]
            for i, tp in enumerate(tips):
                poly.append(tp)
                if i < len(tips) - 1:
                    n = tips[i + 1]
                    mx, my = (tp[0] + n[0]) / 2, (tp[1] + n[1]) / 2
                    poly.append((mx + (elbow[0] - mx) * 0.22, my + (elbow[1] - my) * 0.22))
            poly.append((px + side * 4, py + 30))
            mem = Layer(W, H)
            mem.poly(poly)
            col = tuple(int(c * dim) for c in mem_col)
            paint(cv, mem, base=col, shadow=tuple(int(c * 0.5) for c in col), light=tuple(min(255, int(c * 1.7)) for c in col), outline_w=2.6)
            bones = Layer(W, H)
            bones.capsule(root, elbow, 8 * f)
            for tp in tips:
                bones.tapered([elbow, tp], 7 * f, 2.5)
            claw = (elbow[0] + 4 * side, elbow[1] - 24 * f)
            bones.tapered([elbow, claw], 7 * f, 1)
            paint(cv, bones, base=tuple(int(c * (0.78 + 0.22 * dim)) for c in IVORY), outline_w=2.4)
        if big:
            ember(cv, W, H, [(px - 110, py - 90, 4), (px - 150, py - 30, 3), (px - 60, py - 150, 3), (px + 90, py - 110, 2.5)], fc["aura"])
    elif bone_id == "bone_shell_beetle":
        shell = Layer(W, H)
        shell.ellipse(px - 30, py - 20, 100, 120)
        paint(cv, shell, base=(60, 110, 50), shadow=(26, 56, 24), light=(160, 220, 120), outline_w=3.2)
        seam = Layer(W, H)
        seam.line([(px - 30, py - 140), (px - 30, py + 98)], 4)
        fill(cv, seam, (20, 40, 20))
        gloss = Layer(W, H)
        gloss.ellipse(px - 70, py - 70, 18, 40)
        fill(cv, gloss, (220, 255, 200), alpha=120, blur=2)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_bone(bone_id, family):
    s = slot_info("slot_tail")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    px, py = s["pivot"]
    fc = fam(family)
    if bone_id == "bone_tail_scorpion":
        path = bezier([(px, py), (px - 120, py + 60), (px - 210, py - 30), (px - 120, py - 130)], 11)
        seg = Layer(W, H)
        for i, (x, y) in enumerate(path):
            seg.circle(x, y, 16 - i * 0.55)
        paint(cv, seg, base=(220, 196, 126), shadow=(140, 110, 60), outline_w=3)
        tip = path[-1]
        st = Layer(W, H)
        st.tapered([tip, (tip[0] + 34, tip[1] + 2), (tip[0] + 54, tip[1] + 24)], 24, 2)
        paint(cv, st, base=(110, 170, 60), shadow=(50, 90, 30), light=(190, 240, 130), outline_w=3)
        accent_dots(cv, W, H, [(tip[0] + 56, tip[1] + 30)], fc["aura"], 5, glow_r=8)
    elif bone_id == "bone_tail_lizard":
        seg = Layer(W, H)
        seg.tapered([(px, py), (px - 80, py + 50), (px - 160, py + 60), (px - 228, py + 10)], 30, 4)
        paint(cv, seg, base=(214, 170, 140), shadow=(140, 90, 70), outline_w=3)
        spikes = Layer(W, H)
        for i, (x, y) in enumerate(bezier([(px - 20, py - 6), (px - 90, py + 34), (px - 170, py + 40), (px - 220, py - 2)], 6)[:-1]):
            spikes.poly([(x - 8, y + 4), (x, y - 16 + i), (x + 8, y + 4)])
        paint(cv, spikes, base=(190, 60, 40), shadow=(110, 30, 20), outline_w=2, grain=False)
        ember(cv, W, H, [(px - 226, py + 8, 4), (px - 120, py + 40, 2.5)], fc["aura"])
    elif bone_id == "bone_tail_rat":
        path = bezier([(px, py), (px - 70, py + 80), (px - 170, py + 90), (px - 236, py + 20)], 22)
        seg = Layer(W, H)
        for i, (x, y) in enumerate(path):
            seg.circle(x, y, 9 - i * 0.28)
        paint(cv, seg, base=(220, 196, 200), shadow=(150, 120, 130), outline_w=2.6)
        ring = Layer(W, H)
        x, y = path[-6]
        ring.ellipse(x, y, 9, 6)
        paint(cv, ring, base=(240, 200, 80), shadow=(160, 120, 30), outline_w=1.8, grain=False)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_extra_bone(bone_id, family):
    s = slot_info("slot_extra")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    px, py = s["pivot"]
    fc = fam(family)
    col = Layer(W, H)
    for i in range(8):
        y = py - 10 - i * 27
        col.rrect(px - 22, y - 12, px + 22, y + 12, 8)
        col.poly([(px - 20, y - 4), (px - 40, y - 16), (px - 18, y + 8)])
        col.poly([(px + 20, y - 4), (px + 40, y - 16), (px + 18, y + 8)])
    paint(cv, col, base=(220, 170, 150), shadow=(150, 80, 70), outline_w=3)
    ember(cv, W, H, [(px, py - 60, 4), (px, py - 140, 4), (px, py - 200, 3)], fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_base_parts():
    s = slot_info("ossinho_spine")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    px, py = s["pivot"]
    col = Layer(W, H)
    for i in range(8):
        y = py - 8 - i * 27
        col.rrect(px - 13, y - 11, px + 13, y + 11, 7)
    col.capsule((px, py), (px, 8), 6)
    paint(cv, col, outline_w=2.6)
    finish(cv, W, H, out("bones", "ossinho_spine.png"))
    s = slot_info("ossinho_pelvis")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    px, py = s["pivot"]
    m = Layer(W, H)
    m.ellipse(px - 30, py + 6, 34, 24)
    m.ellipse(px + 30, py + 6, 34, 24)
    m.rrect(px - 16, py - 20, px + 16, py + 30, 10)
    holes = Layer(W, H)
    holes.ellipse(px - 30, py + 10, 12, 9)
    holes.ellipse(px + 30, py + 10, 12, 9)
    m.cut(holes)
    paint(cv, m, outline_w=2.8)
    finish(cv, W, H, out("bones", "ossinho_pelvis.png"))


KNOWN_BONES = {
    "bone_skull_basic", "bone_skull_wolf", "bone_skull_cyclops", "bone_skull_dragon",
    "bone_ribs_basic", "bone_ribs_turtle", "bone_ribs_golem",
    "bone_claw_bear", "bone_pincer_crab", "bone_stinger_wasp", "bone_blade_mantis", "bone_fist_golem",
    "bone_legs_spider", "bone_legs_grasshopper", "bone_legs_centaur",
    "bone_wings_bat", "bone_shell_beetle", "bone_wings_dragon",
    "bone_tail_scorpion", "bone_tail_lizard", "bone_tail_rat", "bone_spine_hydra",
}


def draw_generic_bone(bone_id, slot, family):
    """Placeholder automático para ossos novos: forma básica do encaixe na cor da família."""
    s = slot_info(slot)
    W, H = s["canvas"]
    px, py = s["pivot"]
    fc = fam(family)
    cv = new_canvas(W, H)
    tint = tuple(int(0.75 * a + 0.25 * b) for a, b in zip(IVORY, fc["aura"]))
    if slot == "slot_skull":
        draw_skull(cv, W, H, px, py - 82, 66, eye_color=fc["aura"], base=tint)
    elif slot == "slot_ribs":
        paint(cv, rib_mask(W, H, px, 18, 4, 62, 27, 11), base=tint, outline_w=3)
    elif slot.startswith("slot_arm"):
        paint(cv, arm_base(W, H, px, py), base=tint, outline_w=3)
        accent_dots(cv, W, H, [(px, py + 180)], fc["aura"], 12, glow_r=6)
    elif slot == "slot_legs":
        m = Layer(W, H)
        for side in (-1, 1):
            m.bone((px + side * 14, py + 6), (px + side * 24, py + 110), 8)
            m.bone((px + side * 24, py + 114), (px + side * 18, H - 12), 7)
        paint(cv, m, base=tint, outline_w=3)
    elif slot == "slot_back":
        m = Layer(W, H)
        m.ellipse(px - 30, py - 40, 80, 90)
        paint(cv, m, base=tuple(int(c * 0.6) for c in fc["aura"]), outline_w=3)
    elif slot == "slot_tail":
        m = Layer(W, H)
        m.tapered([(px, py), (px - 90, py + 50), (px - 200, py)], 22, 4)
        paint(cv, m, base=tint, outline_w=3)
    else:
        m = Layer(W, H)
        m.capsule((px, py - 10), (px, 20), 16)
        paint(cv, m, base=tint, outline_w=3)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def gen_bones():
    draw_base_parts()
    for b in data("bones.json"):
        slot = b.get("slot") or b["slots"][0]
        if b["id"] not in KNOWN_BONES:
            draw_generic_bone(b["id"], slot, b.get("family", ""))
            continue
        fn = {"slot_skull": draw_skull_bone, "slot_ribs": draw_ribs_bone, "slot_arm_left": draw_arm_bone,
              "slot_legs": draw_legs_bone, "slot_back": draw_back_bone, "slot_tail": draw_tail_bone,
              "slot_extra": draw_extra_bone}[slot]
        fn(b["id"], b.get("family", ""))
    print("bones ok")


# -------------------------------------------------------------- monstros
# Desenhados virados para a direita e espelhados no fim (encaram o Ossinho).

def eye_glow(cv, W, H, pts, color, r):
    m = Layer(W, H)
    for x, y in pts:
        m.circle(x, y, r)
    glow(cv, m, color, radius=r * 1.6, strength=2.4)
    fill(cv, m, tuple(min(255, c + 90) for c in color))


def quad_skeleton(cv, W, H, x0, x1, back_y, leg_len, thick, color=IVORY, legs=4):
    """Esqueleto de quadrúpede: coluna, costelas penduradas e pernas."""
    spine = Layer(W, H)
    spine.curve([(x0, back_y + 10), ((x0 + x1) / 2, back_y - 12), (x1, back_y + 4)], thick)
    paint(cv, spine, base=color, outline_w=3)
    ribs = Layer(W, H)
    n = 5
    for i in range(n):
        x = x0 + (x1 - x0) * (0.3 + 0.12 * i)
        ribs.curve([(x, back_y), (x + 14, back_y + leg_len * 0.25), (x - 4, back_y + leg_len * 0.48)], thick * 0.55)
    paint(cv, ribs, base=color, outline_w=2.6)
    lg = Layer(W, H)
    feet = []
    for lx in ([x0 + 10, x0 + 34, x1 - 30, x1 - 6] if legs == 4 else [x0 + 20, x1 - 20]):
        knee = (lx + 10, back_y + leg_len * 0.5)
        foot = (lx - 4, back_y + leg_len)
        lg.bone((lx, back_y + 6), knee, thick * 0.6)
        lg.bone(knee, foot, thick * 0.5)
        feet.append(foot)
    paint(cv, lg, base=color, outline_w=2.8)
    return feet


def m_crypt_wolf(cv, W, H, fc):
    by = H - 150
    fur(cv, W, H, 120, by - 6, 14, 34, (96, 62, 36), 2, angle=-100, spread=70)
    feet = quad_skeleton(cv, W, H, 70, 220, by, 136, 13)
    tail = Layer(W, H)
    tail.tapered([(72, by + 6), (40, by - 30), (14, by - 70)], 14, 3)
    paint(cv, tail, outline_w=2.6)
    ears = Layer(W, H)
    ears.poly([(222, by - 70), (214, by - 132), (250, by - 84)])
    ears.poly([(252, by - 78), (262, by - 136), (282, by - 80)])
    paint(cv, ears, outline_w=2.6)
    draw_skull(cv, W, H, 256, by - 30, 52, snout=0.65, eye_color=fc["aura"])
    fang = Layer(W, H)
    fang.poly([(290, by + 8), (296, by + 30), (302, by + 8)])
    paint(cv, fang, base=IVORY_LIGHT, outline_w=1.6, shade=False, grain=False)


def m_corpse_bear(cv, W, H, fc):
    by = H - 140
    body = Layer(W, H)
    body.ellipse(160, by - 10, 120, 90)
    paint(cv, body, base=(86, 58, 44), shadow=(46, 30, 24), light=(140, 100, 74), outline_w=3.2)
    fur(cv, W, H, 150, by - 90, 18, 30, (70, 46, 34), 4, angle=-90, spread=80)
    ribs = rib_mask(W, H, 150, by - 70, 4, 60, 24, 10)
    paint(cv, ribs, outline_w=2.6)
    legs = Layer(W, H)
    for lx in (70, 120, 200, 250):
        legs.rrect(lx - 20, by + 30, lx + 20, H - 18, 14)
    paint(cv, legs, base=(78, 52, 40), shadow=(40, 26, 20), light=(130, 90, 66), outline_w=3)
    claws = Layer(W, H)
    for lx in (70, 120, 200, 250):
        for d in (-12, 0, 12):
            claws.tapered([(lx + d, H - 20), (lx + d + 6, H - 8), (lx + d + 12, H - 6)], 7, 1)
    paint(cv, claws, base=IVORY_LIGHT, outline_w=1.6, grain=False)
    ears = Layer(W, H)
    ears.circle(236, by - 112, 18)
    ears.circle(292, by - 104, 16)
    paint(cv, ears, outline_w=2.6)
    draw_skull(cv, W, H, 270, by - 66, 56, snout=0.4, eye_color=(255, 110, 70))


def m_weaver_spider(cv, W, H, fc):
    by = H - 90
    legs = Layer(W, H)
    for i in range(4):
        for side in (-1, 1):
            hx = 170 + i * 8
            kx = hx + side * (60 + i * 24)
            ky = by - 90 + i * 8
            fx = hx + side * (40 + i * 34)
            legs.tapered([(hx, by - 20), (kx, ky)], 10, 7)
            legs.tapered([(kx, ky), (fx, H - 10)], 7, 2.5)
    paint(cv, legs, base=(206, 200, 160), shadow=(120, 118, 84), outline_w=2.6)
    abd = Layer(W, H)
    abd.ellipse(110, by - 40, 82, 66)
    paint(cv, abd, base=(56, 44, 70), shadow=(28, 20, 40), light=(110, 90, 140), outline_w=3.2)
    mark = Layer(W, H)
    mark.ellipse(104, by - 46, 26, 24)
    mark.rrect(92, by - 30, 116, by - 14, 5)
    fill(cv, mark, (226, 214, 180))
    holes = Layer(W, H)
    holes.circle(96, by - 50, 7)
    holes.circle(113, by - 50, 7)
    fill(cv, holes, (40, 30, 50))
    draw_skull(cv, W, H, 214, by - 40, 40, snout=0.1, eye_color=fc["aura"])
    eye_glow(cv, W, H, [(222, by - 68), (236, by - 64), (206, by - 66)], fc["aura"], 3.5)
    fangs = Layer(W, H)
    fangs.tapered([(240, by - 6), (252, by + 8), (244, by + 22)], 8, 1)
    fangs.tapered([(222, by - 4), (232, by + 10), (226, by + 22)], 8, 1)
    paint(cv, fangs, base=IVORY_LIGHT, outline_w=1.6, grain=False)


def m_vampire_bat(cv, W, H, fc):
    cx, cy = W / 2, H / 2 - 4
    for side in (-1, 1):
        mem = Layer(W, H)
        pts = [(cx, cy - 10), (cx + side * 60, cy - 70), (cx + side * 150, cy - 50), (cx + side * 120, cy - 10), (cx + side * 140, cy + 30),
               (cx + side * 96, cy + 14), (cx + side * 92, cy + 56), (cx + side * 50, cy + 24), (cx, cy + 30)]
        mem.poly(pts)
        paint(cv, mem, base=(80, 44, 110), shadow=(40, 20, 60), light=(150, 100, 190), outline_w=2.8)
        bones = Layer(W, H)
        bones.capsule((cx, cy - 10), (cx + side * 60, cy - 70), 6)
        for tp in [(cx + side * 150, cy - 50), (cx + side * 140, cy + 30), (cx + side * 92, cy + 56)]:
            bones.tapered([(cx + side * 60, cy - 70), tp], 5, 2)
        paint(cv, bones, outline_w=2)
    body = Layer(W, H)
    body.ellipse(cx, cy + 20, 34, 40)
    paint(cv, body, base=(60, 40, 70), shadow=(30, 18, 40), light=(110, 80, 130), outline_w=2.8)
    ears = Layer(W, H)
    ears.poly([(cx - 30, cy - 30), (cx - 34, cy - 74), (cx - 6, cy - 40)])
    ears.poly([(cx + 6, cy - 40), (cx + 34, cy - 76), (cx + 30, cy - 28)])
    paint(cv, ears, outline_w=2.4)
    draw_skull(cv, W, H, cx - 4, cy - 12, 34, snout=0.05, eye_color=(255, 70, 90))
    fangs = Layer(W, H)
    fangs.poly([(cx + 2, cy + 18), (cx + 6, cy + 32), (cx + 10, cy + 18)])
    fangs.poly([(cx + 16, cy + 18), (cx + 20, cy + 30), (cx + 24, cy + 18)])
    paint(cv, fangs, base=IVORY_LIGHT, outline_w=1.4, shade=False, grain=False)


def m_dune_scorpion(cv, W, H, fc):
    by = H - 70
    tail_pts = bezier([(90, by - 10), (20, by - 60), (40, by - 180), (140, by - 190)], 10)
    seg = Layer(W, H)
    for i, (x, y) in enumerate(tail_pts):
        seg.circle(x, y, 18 - i * 0.8)
    paint(cv, seg, base=(214, 180, 110), shadow=(140, 104, 56), outline_w=3)
    tip = tail_pts[-1]
    st = Layer(W, H)
    st.tapered([tip, (tip[0] + 30, tip[1] + 8), (tip[0] + 40, tip[1] + 36)], 22, 2)
    paint(cv, st, base=(110, 170, 60), shadow=(50, 90, 30), outline_w=2.8)
    eye_glow(cv, W, H, [(tip[0] + 40, tip[1] + 40)], fc["aura"], 4)
    legs = Layer(W, H)
    for i in range(4):
        lx = 110 + i * 34
        legs.tapered([(lx, by - 6), (lx - 10, by + 30), (lx - 22, H - 8)], 8, 3)
    paint(cv, legs, base=(196, 164, 104), shadow=(120, 96, 50), outline_w=2.4)
    body = Layer(W, H)
    for i in range(5):
        body.ellipse(110 + i * 36, by - 14, 30, 24 - i)
    paint(cv, body, base=(222, 190, 120), shadow=(150, 112, 60), outline_w=3)
    claw = Layer(W, H)
    for dy, sc in ((-30, 0.9), (10, 1.0)):
        claw.tapered([(250, by - 10), (290, by + dy), (300, by + dy - 20)], 14 * sc, 10 * sc)
        claw.ellipse(306, by + dy - 26, 22 * sc, 16 * sc)
        claw.tapered([(316, by + dy - 34), (338, by + dy - 40), (328, by + dy - 22)], 9, 2)
    paint(cv, claw, base=(214, 176, 104), shadow=(140, 100, 50), outline_w=2.8)
    draw_skull(cv, W, H, 262, by - 36, 26, eye_color=fc["aura"])


def m_skeleton_rat(cv, W, H, fc):
    by = H - 60
    tail = Layer(W, H)
    tail.tapered([(40, by), (10, by - 20), (8, by - 60)], 8, 2)
    paint(cv, tail, base=(226, 200, 200), outline_w=2)
    quad_skeleton(cv, W, H, 40, 120, by, 56, 8)
    ears = Layer(W, H)
    ears.circle(124, by - 40, 12)
    paint(cv, ears, base=(230, 190, 196), outline_w=2)
    draw_skull(cv, W, H, 140, by - 18, 26, snout=0.7, eye_color=(255, 70, 70))


def m_hungry_mimic(cv, W, H, fc):
    by = H - 20
    box = Layer(W, H)
    box.rrect(40, by - 120, 260, by, 14)
    paint(cv, box, base=(120, 74, 44), shadow=(70, 40, 22), light=(170, 116, 72), outline_w=3.4)
    lid = Layer(W, H)
    lid.poly([(36, by - 128), (268, by - 128), (250, by - 236), (60, by - 210)])
    paint(cv, lid, base=(130, 82, 48), shadow=(74, 44, 24), light=(180, 124, 80), outline_w=3.4)
    mouth = Layer(W, H)
    mouth.poly([(52, by - 124), (252, by - 124), (240, by - 200), (66, by - 186)])
    fill(cv, mouth, (60, 14, 22))
    teeth = Layer(W, H)
    for i in range(8):
        x = 62 + i * 25
        teeth.poly([(x, by - 124), (x + 12, by - 150), (x + 22, by - 124)])
        teeth.poly([(x + 4, by - 188 - i * 1.6), (x + 14, by - 160 - i * 1.6), (x + 22, by - 190 - i * 1.6)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=1.8, grain=False)
    tongue = Layer(W, H)
    tongue.tapered([(150, by - 140), (200, by - 120), (250, by - 70), (230, by - 40)], 30, 14)
    paint(cv, tongue, base=(220, 80, 110), shadow=(140, 40, 60), outline_w=2.6)
    bands = Layer(W, H)
    bands.rrect(36, by - 70, 264, by - 56, 4)
    bands.rrect(130, by - 110, 170, by - 40, 6)
    paint(cv, bands, base=(150, 150, 160), shadow=(80, 80, 96), outline_w=2.2)
    eye_glow(cv, W, H, [(110, by - 214), (190, by - 222)], (255, 200, 60), 7)


def m_rat_king(cv, W, H, fc):
    cx, by = W / 2, H - 20
    cape = Layer(W, H)
    cape.poly([(cx - 70, by - 300), (cx + 60, by - 300), (cx + 130, by - 10), (cx - 160, by - 10)])
    paint(cv, cape, base=(100, 40, 120), shadow=(50, 16, 66), light=(160, 80, 190), outline_w=3.4)
    trim = Layer(W, H)
    trim.rrect(cx - 164, by - 30, cx + 134, by - 4, 10)
    paint(cv, trim, base=(236, 230, 220), shadow=(170, 160, 150), outline_w=2.6)
    tail = Layer(W, H)
    tail.tapered([(cx - 120, by - 30), (cx - 200, by - 60), (cx - 210, by - 160), (cx - 170, by - 220)], 14, 3)
    paint(cv, tail, base=(226, 196, 200), outline_w=2.6)
    legs = Layer(W, H)
    legs.bone((cx - 30, by - 110), (cx - 40, by - 10), 12)
    legs.bone((cx + 30, by - 110), (cx + 40, by - 10), 12)
    paint(cv, legs, outline_w=3)
    ribs = rib_mask(W, H, cx, by - 290, 5, 70, 30, 12)
    paint(cv, ribs, outline_w=3)
    arm = Layer(W, H)
    arm.bone((cx + 50, by - 270), (cx + 110, by - 200), 10)
    arm.bone((cx + 110, by - 200), (cx + 150, by - 260), 9)
    paint(cv, arm, outline_w=3)
    scepter = Layer(W, H)
    scepter.capsule((cx + 160, by - 330), (cx + 140, by - 120), 7)
    paint(cv, scepter, base=(230, 190, 80), shadow=(150, 110, 30), outline_w=2.6)
    draw_skull(cv, W, H, cx + 160, by - 352, 24, eye_color=(255, 80, 80))
    ears = Layer(W, H)
    ears.circle(cx - 30, by - 390, 30)
    ears.circle(cx + 40, by - 396, 26)
    paint(cv, ears, base=(232, 196, 204), outline_w=3)
    draw_skull(cv, W, H, cx + 10, by - 338, 62, snout=0.75, eye_color=(255, 70, 70))
    crown = Layer(W, H)
    crown.poly([(cx - 40, by - 392), (cx - 36, by - 432), (cx - 16, by - 410), (cx + 4, by - 440), (cx + 22, by - 410), (cx + 44, by - 432), (cx + 44, by - 392)])
    paint(cv, crown, base=(250, 200, 70), shadow=(170, 120, 30), light=(255, 240, 160), outline_w=2.8)
    accent_dots(cv, W, H, [(cx + 4, by - 404)], (220, 40, 60), 6)


def m_stone_turtle(cv, W, H, fc):
    by = H - 40
    legs = Layer(W, H)
    for lx in (90, 140, 210, 255):
        legs.rrect(lx - 18, by - 40, lx + 18, by + 10, 10)
    paint(cv, legs, base=(150, 140, 120), shadow=(90, 82, 70), outline_w=3)
    shell = Layer(W, H)
    shell.ellipse(170, by - 70, 130, 80)
    paint(cv, shell, base=(110, 108, 100), shadow=(60, 58, 54), light=(170, 166, 156), outline_w=3.4)
    plates = Layer(W, H)
    for (x, y, r) in [(170, by - 100, 28), (120, by - 80, 22), (220, by - 80, 22), (90, by - 50, 16), (250, by - 50, 16), (170, by - 50, 20)]:
        plates.circle(x, y, r)
    paint(cv, plates, base=(140, 136, 124), shadow=(80, 78, 70), outline_w=2.4)
    accent_dots(cv, W, H, [(110, by - 110), (230, by - 110), (150, by - 30)], (90, 200, 190), 6)
    neck = Layer(W, H)
    neck.capsule((280, by - 50), (310, by - 70), 16)
    paint(cv, neck, base=(150, 140, 120), outline_w=2.6)
    draw_skull(cv, W, H, 320, by - 80, 32, snout=0.3, eye_color=fc["aura"])


def m_abyssal_crab(cv, W, H, fc):
    by = H - 30
    legs = Layer(W, H)
    for i in range(3):
        for side in (-1, 1):
            hx = 170 + side * 40
            legs.tapered([(hx, by - 60), (hx + side * (60 + i * 20), by - 90 + i * 14), (hx + side * (70 + i * 26), by)], 9, 3)
    paint(cv, legs, base=(60, 150, 150), shadow=(26, 80, 84), outline_w=2.6)
    body = Layer(W, H)
    body.ellipse(170, by - 70, 90, 50)
    paint(cv, body, base=(50, 130, 140), shadow=(20, 66, 76), light=(130, 220, 220), outline_w=3.2)
    for side in (-1, 1):
        claw = Layer(W, H)
        bx = 170 + side * 70
        claw.tapered([(bx, by - 90), (bx + side * 40, by - 140)], 16, 12)
        claw.ellipse(bx + side * 54, by - 162, 34, 26)
        claw.tapered([(bx + side * 60, by - 180), (bx + side * 96, by - 196), (bx + side * 88, by - 170)], 14, 3)
        paint(cv, claw, base=(70, 170, 168), shadow=(28, 90, 94), light=(150, 230, 220), outline_w=3)
    accent_dots(cv, W, H, [(140, by - 100), (205, by - 92), (172, by - 60)], (220, 240, 230), 6)
    eye_glow(cv, W, H, [(155, by - 118), (190, by - 118)], fc["aura"], 6)
    stalks = Layer(W, H)
    stalks.capsule((155, by - 100), (155, by - 116), 3)
    stalks.capsule((190, by - 100), (190, by - 116), 3)
    fill(cv, stalks, (40, 100, 100))


def m_bone_wasp(cv, W, H, fc):
    cx, cy = W / 2, H / 2 - 10
    for side in (-1, 1):
        wing = Layer(W, H)
        wing.ellipse(cx + side * 20 - 10, cy - 70, 40, 70)
        fill(cv, wing, (220, 250, 255), alpha=110)
        edge = Layer(W, H)
        edge.ellipse(cx + side * 20 - 10, cy - 70, 40, 70)
        inner = Layer(W, H)
        inner.ellipse(cx + side * 20 - 10, cy - 70, 37, 67)
        edge.cut(inner)
        fill(cv, edge, (60, 60, 70))
    abd = Layer(W, H)
    abd.ellipse(cx - 60, cy + 20, 64, 40)
    paint(cv, abd, base=(230, 200, 70), shadow=(150, 120, 30), outline_w=3)
    bands = Layer(W, H)
    for x in (cx - 90, cx - 60, cx - 30):
        bands.rrect(x - 7, cy - 14, x + 7, cy + 56, 4)
    fill(cv, bands, (40, 30, 26))
    st = Layer(W, H)
    st.tapered([(cx - 120, cy + 26), (cx - 150, cy + 40)], 14, 1)
    paint(cv, st, base=(230, 220, 200), outline_w=2)
    thorax = Layer(W, H)
    thorax.ellipse(cx + 20, cy + 10, 34, 30)
    paint(cv, thorax, base=(60, 50, 40), shadow=(30, 24, 20), outline_w=3)
    legs = Layer(W, H)
    for i in range(3):
        legs.tapered([(cx + 10 + i * 12, cy + 30), (cx + i * 16, cy + 70), (cx - 6 + i * 18, cy + 96)], 6, 2)
    paint(cv, legs, base=(70, 60, 50), outline_w=2)
    draw_skull(cv, W, H, cx + 66, cy, 30, snout=0.0, eye_color=fc["aura"])


def m_giant_mantis(cv, W, H, fc):
    by = H - 20
    legs = Layer(W, H)
    for lx in (90, 140, 190):
        legs.tapered([(lx, by - 120), (lx - 20, by - 60), (lx - 10, by)], 9, 4)
    paint(cv, legs, base=(140, 200, 90), shadow=(70, 110, 40), outline_w=2.6)
    abd = Layer(W, H)
    abd.ellipse(110, by - 130, 80, 34)
    paint(cv, abd, base=(150, 210, 100), shadow=(70, 120, 40), light=(210, 250, 160), outline_w=3)
    thorax = Layer(W, H)
    thorax.tapered([(180, by - 140), (220, by - 210), (230, by - 260)], 26, 18)
    paint(cv, thorax, base=(150, 210, 100), shadow=(70, 120, 40), outline_w=3)
    for dy, k in ((0, 1.0), (24, 0.85)):
        arm = Layer(W, H)
        arm.tapered([(226, by - 220 + dy), (290, by - 250 + dy), (300, by - 190 + dy)], 16 * k, 10 * k)
        arm.poly([(296, by - 196 + dy), (320, by - 160 + dy), (286, by - 186 + dy)])
        paint(cv, arm, base=(170, 225, 110), shadow=(80, 130, 50), outline_w=3)
    head = Layer(W, H)
    head.poly([(220, by - 300), (276, by - 290), (244, by - 250)])
    paint(cv, head, base=(170, 225, 110), shadow=(80, 130, 50), outline_w=3)
    eye_glow(cv, W, H, [(232, by - 290), (262, by - 288)], fc["aura"], 7)
    ant = Layer(W, H)
    ant.tapered([(240, by - 300), (230, by - 330), (210, by - 336)], 3, 1)
    ant.tapered([(256, by - 298), (262, by - 330), (282, by - 340)], 3, 1)
    fill(cv, ant, (60, 90, 30))


def m_bone_grasshopper(cv, W, H, fc):
    by = H - 20
    hind = Layer(W, H)
    hind.tapered([(140, by - 80), (90, by - 150), (70, by - 120)], 24, 10)
    hind.capsule((70, by - 120), (100, by), 6)
    paint(cv, hind, base=(180, 210, 100), shadow=(100, 130, 50), outline_w=3)
    body = Layer(W, H)
    body.ellipse(170, by - 90, 90, 34)
    paint(cv, body, base=(170, 200, 90), shadow=(90, 120, 40), light=(220, 240, 150), outline_w=3)
    ribs = rib_mask(W, H, 160, by - 120, 3, 34, 16, 6)
    paint(cv, ribs, outline_w=2)
    legs = Layer(W, H)
    for lx in (200, 230):
        legs.tapered([(lx, by - 70), (lx + 10, by - 30), (lx + 4, by)], 7, 3)
    paint(cv, legs, base=(170, 200, 90), outline_w=2.4)
    draw_skull(cv, W, H, 270, by - 100, 34, snout=0.2, eye_color=fc["aura"])
    ant = Layer(W, H)
    ant.tapered([(270, by - 130), (290, by - 180), (320, by - 190)], 4, 1)
    fill(cv, ant, (90, 110, 40))


def m_bony_centaur(cv, W, H, fc):
    by = H - 20
    body = Layer(W, H)
    body.ellipse(150, by - 130, 100, 50)
    paint(cv, body, base=(140, 96, 60), shadow=(80, 52, 30), light=(190, 140, 100), outline_w=3)
    ribs = rib_mask(W, H, 150, by - 170, 3, 60, 18, 7)
    paint(cv, ribs, outline_w=2)
    legs = Layer(W, H)
    for lx in (80, 110, 190, 220):
        legs.bone((lx, by - 100), (lx + 4, by - 50), 7)
        legs.bone((lx + 4, by - 48), (lx - 2, by - 10), 6)
    paint(cv, legs, outline_w=2.8)
    hooves = Layer(W, H)
    for lx in (78, 108, 188, 218):
        hooves.rrect(lx - 10, by - 14, lx + 10, by + 4, 4)
    paint(cv, hooves, base=(60, 44, 36), outline_w=2, grain=False)
    fur(cv, W, H, 50, by - 140, 8, 34, (110, 70, 40), 7, angle=160, spread=40)
    torso = rib_mask(W, H, 240, by - 270, 3, 40, 22, 9)
    paint(cv, torso, outline_w=2.6)
    spine = Layer(W, H)
    spine.capsule((240, by - 160), (240, by - 270), 8)
    paint(cv, spine, outline_w=2.4)
    arm = Layer(W, H)
    arm.bone((256, by - 256), (300, by - 210), 7)
    arm.capsule((300, by - 210), (320, by - 300), 4)
    paint(cv, arm, outline_w=2.4)
    spear = Layer(W, H)
    spear.poly([(312, by - 330), (322, by - 300), (330, by - 330), (322, by - 350)])
    paint(cv, spear, base=(180, 190, 200), outline_w=2)
    draw_skull(cv, W, H, 246, by - 304, 36, eye_color=fc["aura"])


def m_armored_beetle(cv, W, H, fc):
    by = H - 30
    legs = Layer(W, H)
    for i in range(3):
        for side in (-1, 1):
            lx = 120 + i * 50
            legs.tapered([(lx, by - 40), (lx + side * 12, by - 10), (lx + side * 20, by)], 8, 3)
    paint(cv, legs, base=(50, 70, 50), outline_w=2.4)
    shell = Layer(W, H)
    shell.ellipse(160, by - 80, 110, 70)
    paint(cv, shell, base=(50, 100, 60), shadow=(20, 50, 26), light=(140, 210, 140), outline_w=3.4)
    seam = Layer(W, H)
    seam.line([(70, by - 90), (250, by - 90)], 4)
    fill(cv, seam, (16, 36, 20))
    gloss = Layer(W, H)
    gloss.ellipse(130, by - 120, 40, 12)
    fill(cv, gloss, (220, 255, 220), alpha=120, blur=2)
    horn = Layer(W, H)
    horn.tapered([(270, by - 70), (320, by - 120), (330, by - 160)], 18, 3)
    paint(cv, horn, base=IVORY, outline_w=3)
    draw_skull(cv, W, H, 274, by - 56, 30, eye_color=fc["aura"])


def m_ash_lizard(cv, W, H, fc):
    by = H - 20
    tail = Layer(W, H)
    tail.tapered([(110, by - 50), (60, by - 40), (20, by - 70)], 26, 4)
    paint(cv, tail, base=(190, 120, 90), shadow=(110, 60, 40), outline_w=3)
    body = Layer(W, H)
    body.ellipse(170, by - 55, 80, 32)
    paint(cv, body, base=(170, 100, 70), shadow=(90, 50, 30), light=(230, 160, 120), outline_w=3)
    spikes = Layer(W, H)
    for i in range(6):
        x = 110 + i * 22
        spikes.poly([(x - 8, by - 80), (x, by - 100 - (i % 2) * 8), (x + 8, by - 80)])
    paint(cv, spikes, base=(200, 70, 40), shadow=(120, 30, 20), outline_w=2, grain=False)
    legs = Layer(W, H)
    for lx in (120, 210):
        legs.tapered([(lx, by - 40), (lx - 20, by - 10), (lx - 10, by)], 12, 6)
    paint(cv, legs, base=(170, 100, 70), outline_w=2.6)
    draw_skull(cv, W, H, 268, by - 60, 34, snout=0.8, eye_color=fc["aura"])
    ember(cv, W, H, [(60, by - 100, 4), (130, by - 120, 3), (210, by - 110, 3), (30, by - 90, 2)], fc["aura"])


def m_bony_cyclops(cv, W, H, fc):
    by = H - 20
    legs = Layer(W, H)
    legs.bone((130, by - 140), (120, by - 10), 16)
    legs.bone((210, by - 140), (222, by - 10), 16)
    paint(cv, legs, outline_w=3)
    torso = rib_mask(W, H, 170, by - 300, 5, 80, 30, 13)
    paint(cv, torso, outline_w=3)
    belt = Layer(W, H)
    belt.rrect(100, by - 160, 240, by - 136, 8)
    paint(cv, belt, base=(110, 120, 140), shadow=(60, 66, 84), outline_w=2.6)
    runes(cv, W, H, 170, by - 148, 8, fc["aura"])
    for side in (-1, 1):
        arm = Layer(W, H)
        arm.bone((170 + side * 80, by - 280), (170 + side * 110, by - 190), 13)
        arm.bone((170 + side * 110, by - 186), (170 + side * 100, by - 110), 11)
        paint(cv, arm, outline_w=3)
    club = Layer(W, H)
    club.tapered([(268, by - 120), (300, by - 40), (310, by - 10)], 14, 30)
    paint(cv, club, base=(120, 90, 60), shadow=(70, 50, 30), outline_w=3)
    draw_skull(cv, W, H, 176, by - 350, 62, cyclops=True, eye_color=fc["aura"], base=(222, 216, 204))
    plate = Layer(W, H)
    plate.rrect(120, by - 420, 220, by - 400, 8)
    paint(cv, plate, base=(120, 132, 150), shadow=(70, 80, 100), outline_w=2.4)


def m_forgotten_golem(cv, W, H, fc):
    by = H - 20
    stone = dict(base=(120, 120, 134), shadow=(64, 64, 78), light=(180, 180, 196))
    legs = Layer(W, H)
    legs.rrect(150, by - 160, 210, by, 16)
    legs.rrect(270, by - 160, 330, by, 16)
    paint(cv, legs, outline_w=3.4, **stone)
    body = Layer(W, H)
    body.rrect(110, by - 360, 370, by - 140, 40)
    paint(cv, body, outline_w=3.6, **stone)
    cracks = Layer(W, H)
    cracks.line([(160, by - 330), (190, by - 280), (170, by - 240)], 3)
    cracks.line([(320, by - 320), (300, by - 270)], 3)
    fill(cv, cracks, (40, 40, 52))
    cage = rib_mask(W, H, 240, by - 340, 4, 80, 40, 12)
    paint(cv, cage, base=(150, 160, 178), shadow=(80, 90, 110), outline_w=3)
    core = Layer(W, H)
    core.circle(240, by - 250, 26)
    glow(cv, core, fc["aura"], radius=20, strength=1.8)
    fill(cv, core, (200, 230, 255))
    for side in (-1, 1):
        arm = Layer(W, H)
        arm.rrect(240 + side * 150 - 30, by - 340, 240 + side * 150 + 30, by - 150, 24)
        arm.rrect(240 + side * 150 - 46, by - 170, 240 + side * 150 + 46, by - 80, 22)
        paint(cv, arm, outline_w=3.4, **stone)
        runes(cv, W, H, 240 + side * 150, by - 125, 12, fc["aura"])
    head = Layer(W, H)
    head.rrect(180, by - 440, 300, by - 350, 26)
    paint(cv, head, outline_w=3.4, **stone)
    eye_glow(cv, W, H, [(215, by - 400), (265, by - 400)], fc["aura"], 10)
    moss = Layer(W, H)
    for x in (130, 200, 330, 350):
        moss.ellipse(x, by - 360, 22, 10)
    fill(cv, moss, (70, 110, 60))


def m_ancient_dragon(cv, W, H, fc):
    by = H - 20
    root = (250, by - 230)
    for side, k, dim in ((1, 0.8, 0.6), (-1, 1.0, 1.0)):
        elbow = (root[0] + side * 90 * k, root[1] - 150 * k)
        tips = [(root[0] + side * 230 * k, root[1] - 200 * k), (root[0] + side * 250 * k, root[1] - 110 * k),
                (root[0] + side * 230 * k, root[1] - 30 * k), (root[0] + side * 160 * k, root[1] + 30 * k)]
        poly = [root, elbow]
        for i, tp in enumerate(tips):
            poly.append(tp)
            if i < len(tips) - 1:
                n = tips[i + 1]
                mx, my = (tp[0] + n[0]) / 2, (tp[1] + n[1]) / 2
                poly.append((mx + (elbow[0] - mx) * 0.25, my + (elbow[1] - my) * 0.25))
        mem = Layer(W, H)
        mem.poly(poly)
        col = tuple(int(c * dim) for c in (160, 44, 32))
        paint(cv, mem, base=col, shadow=tuple(int(c * 0.5) for c in col), light=tuple(min(255, int(c * 1.6)) for c in col), outline_w=3)
        bones = Layer(W, H)
        bones.capsule(root, elbow, 10 * k)
        for tp in tips:
            bones.tapered([elbow, tp], 8 * k, 3)
        paint(cv, bones, base=tuple(int(c * (0.75 + 0.25 * dim)) for c in IVORY), outline_w=2.6)
    tail = Layer(W, H)
    tail.tapered([(160, by - 100), (80, by - 60), (20, by - 120), (40, by - 200)], 40, 6)
    paint(cv, tail, base=(200, 150, 130), shadow=(130, 80, 60), outline_w=3)
    legs = Layer(W, H)
    for lx in (170, 300):
        legs.bone((lx, by - 150), (lx - 10, by - 70), 18)
        legs.bone((lx - 10, by - 66), (lx + 10, by - 10), 15)
    paint(cv, legs, outline_w=3)
    body = Layer(W, H)
    body.ellipse(240, by - 170, 120, 70)
    paint(cv, body, base=(170, 60, 40), shadow=(100, 30, 20), light=(230, 120, 80), outline_w=3.4)
    ribs = rib_mask(W, H, 240, by - 230, 4, 90, 26, 12)
    paint(cv, ribs, outline_w=3)
    neck = Layer(W, H)
    neck.tapered([(330, by - 200), (380, by - 290), (400, by - 340)], 40, 26)
    paint(cv, neck, base=(200, 150, 130), shadow=(130, 80, 60), outline_w=3)
    horns = [(-0.6, -0.55, -0.9, -0.8), (-0.2, -0.75, -0.55, -1.0)]
    draw_skull(cv, W, H, 410, by - 370, 62, snout=0.85, horns=horns, eye_color=fc["aura"], crest=True)
    ember(cv, W, H, [(470, by - 330, 6), (490, by - 350, 4), (120, by - 300, 4), (300, by - 420, 4), (60, by - 220, 3)], fc["aura"])


def m_hydra(cv, W, H, fc):
    by = H - 20
    body = Layer(W, H)
    body.ellipse(240, by - 120, 150, 90)
    paint(cv, body, base=(150, 50, 40), shadow=(90, 24, 18), light=(220, 110, 80), outline_w=3.4)
    ribs = rib_mask(W, H, 240, by - 190, 4, 110, 26, 12)
    paint(cv, ribs, outline_w=3)
    legs = Layer(W, H)
    for lx in (140, 340):
        legs.rrect(lx - 28, by - 80, lx + 28, by, 18)
    paint(cv, legs, base=(140, 50, 40), shadow=(80, 24, 18), outline_w=3)
    for i, (nx, ny, ang) in enumerate(((150, by - 380, -0.4), (250, by - 430, 0.0), (350, by - 380, 0.4))):
        neck = Layer(W, H)
        neck.tapered([(200 + i * 40, by - 170), (nx - 20 + i * 20, by - 280), (nx, ny + 40)], 34, 22)
        paint(cv, neck, base=(200, 150, 130), shadow=(130, 80, 60), outline_w=3)
        draw_skull(cv, W, H, nx, ny, 46, snout=0.6, horns=[(-0.5, -0.6, -0.6, -0.6)], eye_color=fc["aura"])
    ember(cv, W, H, [(100, by - 260, 4), (400, by - 250, 4), (250, by - 300, 3)], fc["aura"])


MONSTER_DRAW = {
    "monster_crypt_wolf": m_crypt_wolf,
    "monster_corpse_bear": m_corpse_bear,
    "monster_weaver_spider": m_weaver_spider,
    "monster_vampire_bat": m_vampire_bat,
    "monster_dune_scorpion": m_dune_scorpion,
    "minion_skeleton_rat": m_skeleton_rat,
    "minion_hungry_mimic": m_hungry_mimic,
    "boss_rat_king": m_rat_king,
    "monster_stone_turtle": m_stone_turtle,
    "monster_abyssal_crab": m_abyssal_crab,
    "monster_bone_wasp": m_bone_wasp,
    "monster_giant_mantis": m_giant_mantis,
    "monster_bone_grasshopper": m_bone_grasshopper,
    "monster_bony_centaur": m_bony_centaur,
    "monster_armored_beetle": m_armored_beetle,
    "monster_ash_lizard": m_ash_lizard,
    "monster_bony_cyclops": m_bony_cyclops,
    "boss_forgotten_golem": m_forgotten_golem,
    "boss_ancient_dragon": m_ancient_dragon,
    "boss_hydra": m_hydra,
}


def fit_bottom(cv, W, H, margin_px=6):
    """Reduz o desenho (em alta resolução) para caber em W x H com os pés no fundo e centralizado."""
    bbox = cv.getbbox()
    if not bbox:
        return Image.new("RGBA", (W * SS, H * SS))
    crop = cv.crop(bbox)
    avail_w, avail_h = (W - 2 * margin_px) * SS, (H - margin_px) * SS
    k = min(1.0, avail_w / crop.width, avail_h / crop.height)
    if k < 1.0:
        crop = crop.resize((int(crop.width * k), int(crop.height * k)), Image.LANCZOS)
    outimg = Image.new("RGBA", (W * SS, H * SS))
    outimg.alpha_composite(crop, ((W * SS - crop.width) // 2, H * SS - crop.height - SS * 2))
    return outimg


def gen_monsters():
    import artlib
    from PIL import ImageOps
    for m in data("monsters.json"):
        W, H = m["art"]["size"]
        fn = MONSTER_DRAW.get(m["id"])
        if fn is None:
            if m.get("kind") != "ally":
                print("sem desenho:", m["id"])
            continue
        mg = int(max(W, H) * 0.3)
        artlib.ORIGIN[0], artlib.ORIGIN[1] = mg, mg
        cv = new_canvas(W + 2 * mg, H + 2 * mg)
        fn(cv, W, H, fam(m.get("family", "")))
        artlib.ORIGIN[0], artlib.ORIGIN[1] = 0, 0
        cv = ImageOps.mirror(fit_bottom(cv, W, H))
        finish(cv, W, H, out("monsters", m["id"] + ".png"))
    print("monsters ok")


# ---------------------------------------------------------------- cenário

def gen_env():
    from PIL import ImageFont
    import random as _r
    W, H = 720, 1280
    r = _r.Random(42)
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = (int(30 + 18 * t), int(22 + 10 * t), int(36 + 6 * t), 255)
        d.line([(0, y), (W, y)], fill=c)
    # tijolos da parede
    wall = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wall)
    bh = 46
    for row in range(0, 20):
        y = row * bh
        off = (row % 2) * 40
        x = -off
        while x < W:
            bw = r.randint(70, 110)
            tone = r.randint(-10, 10)
            base = (58 + tone, 46 + tone, 62 + tone, 255)
            wd.rounded_rectangle([x + 3, y + 3, x + bw - 3, y + bh - 3], radius=6, fill=base)
            wd.line([(x + 6, y + 6), (x + bw - 8, y + 6)], fill=(80 + tone, 66 + tone, 84 + tone, 255), width=2)
            if r.random() < 0.25:
                cx0 = x + r.randint(10, bw - 20)
                wd.line([(cx0, y + 8), (cx0 + r.randint(-8, 8), y + bh - 10)], fill=(34, 26, 38, 255), width=2)
            x += bw
    wall = wall.filter(ImageFilter.GaussianBlur(0.8))
    # escurece a parede para o fundo e de cima para baixo
    fade = Image.new("L", (W, H))
    fd = ImageDraw.Draw(fade)
    for y in range(H):
        fd.line([(0, y), (W, y)], fill=int(170 if y < 760 else max(0, 170 - (y - 760) * 2)))
    img.alpha_composite(Image.composite(wall, Image.new("RGBA", (W, H)), fade))
    # arcos escuros
    arch = Image.new("RGBA", (W, H))
    ad = ImageDraw.Draw(arch)
    for ax, aw, top in ((150, 170, 330), (560, 170, 330)):
        ad.rectangle([ax - aw / 2, top + aw / 2, ax + aw / 2, 770], fill=(14, 10, 18, 235))
        ad.ellipse([ax - aw / 2, top, ax + aw / 2, top + aw], fill=(14, 10, 18, 235))
    arch = arch.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(arch)
    # moldura de pedra dos arcos
    frame = Image.new("RGBA", (W, H))
    fr = ImageDraw.Draw(frame)
    for ax, aw, top in ((150, 170, 330), (560, 170, 330)):
        fr.arc([ax - aw / 2 - 12, top - 12, ax + aw / 2 + 12, top + aw + 12], 180, 360, fill=(92, 78, 96, 255), width=16)
        fr.rectangle([ax - aw / 2 - 20, top + aw / 2, ax - aw / 2 - 4, 770], fill=(86, 72, 90, 255))
        fr.rectangle([ax + aw / 2 + 4, top + aw / 2, ax + aw / 2 + 20, 770], fill=(86, 72, 90, 255))
    img.alpha_composite(frame.filter(ImageFilter.GaussianBlur(1)))
    # brilho distante dentro dos arcos
    gl = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(gl)
    for ax in (150, 560):
        gd.ellipse([ax - 40, 600, ax + 40, 680], fill=(255, 150, 60, 90))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(28)))
    # piso em perspectiva
    floor = Image.new("RGBA", (W, H))
    fl = ImageDraw.Draw(floor)
    fl.polygon([(0, 760), (W, 760), (W, H), (0, H)], fill=(40, 32, 42, 255))
    vx, vy = W / 2, 300
    for i in range(-8, 9):
        x = W / 2 + i * 120
        fl.line([(vx + (x - vx) * 0.36, 760), (x, H)], fill=(24, 18, 28, 255), width=3)
    yy = 760
    step = 18
    while yy < H:
        fl.line([(0, yy), (W, yy)], fill=(26, 20, 30, 255), width=3)
        yy += step
        step *= 1.32
    img.alpha_composite(floor.filter(ImageFilter.GaussianBlur(0.7)))
    # borda do piso
    ed = ImageDraw.Draw(img)
    ed.rectangle([0, 752, W, 764], fill=(70, 58, 72, 255))
    # teias nos cantos
    web = Image.new("RGBA", (W, H))
    wb = ImageDraw.Draw(web)
    for cx, cy, sx, sy in ((0, 0, 1, 1), (W, 0, -1, 1)):
        for k in range(7):
            a = math.radians(k * 15)
            wb.line([(cx, cy), (cx + sx * math.cos(a) * 200, cy + sy * math.sin(a) * 200)], fill=(200, 200, 210, 60), width=2)
        for rr in range(40, 200, 34):
            pts = [(cx + sx * math.cos(math.radians(k * 15)) * rr, cy + sy * math.sin(math.radians(k * 15)) * rr) for k in range(7)]
            wb.line(pts, fill=(200, 200, 210, 50), width=2)
    img.alpha_composite(web)
    # vinheta
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-260, -120, W + 260, H + 120], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(140))
    dark = Image.new("RGBA", (W, H), (6, 4, 8, 255))
    img = Image.composite(img, dark, vig)
    img.convert("RGB").save(out("env", "env_forgotten_crypt.png"), optimize=True)

    # vela
    W2, H2 = 64, 150
    cv = new_canvas(W2, H2)
    wax = Layer(W2, H2)
    wax.rrect(14, 40, 50, 140, 8)
    wax.ellipse(32, 40, 18, 7)
    wax.capsule((18, 44), (16, 74), 5)
    wax.capsule((44, 44), (46, 62), 4)
    paint(cv, wax, base=(240, 228, 200), shadow=(170, 150, 120), outline_w=2.6)
    wick = Layer(W2, H2)
    wick.capsule((32, 26), (32, 38), 2)
    fill(cv, wick, (30, 20, 20))
    base = Layer(W2, H2)
    base.rrect(4, 132, 60, 146, 6)
    paint(cv, base, base=(110, 90, 70), shadow=(60, 46, 34), outline_w=2.4)
    finish(cv, W2, H2, out("env", "env_candle.png"))

    # pilha de ossos
    W3, H3 = 260, 120
    cv = new_canvas(W3, H3)
    m = Layer(W3, H3)
    rr = _r.Random(3)
    for i in range(14):
        x = rr.uniform(30, 230)
        y = rr.uniform(60, 100)
        a = rr.uniform(0, math.pi)
        l = rr.uniform(26, 46)
        m.bone((x - math.cos(a) * l, y - math.sin(a) * l * 0.4), (x + math.cos(a) * l, y + math.sin(a) * l * 0.4), 6)
    paint(cv, m, base=(200, 188, 160), shadow=(120, 104, 84), outline_w=2.4)
    draw_skull(cv, W3, H3, 130, 54, 30, base=(214, 202, 176))
    finish(cv, W3, H3, out("env", "env_bone_pile.png"))

    # lápide
    W4, H4 = 150, 180
    cv = new_canvas(W4, H4)
    m = Layer(W4, H4)
    m.rrect(20, 40, 130, 176, 10)
    m.ellipse(75, 50, 55, 40)
    paint(cv, m, base=(110, 104, 120), shadow=(60, 56, 70), light=(160, 156, 170), outline_w=3)
    cross = Layer(W4, H4)
    cross.rrect(68, 48, 82, 120, 3)
    cross.rrect(50, 66, 100, 80, 3)
    fill(cv, cross, (70, 64, 80))
    finish(cv, W4, H4, out("env", "env_tombstone.png"))
    print("env ok")



# ------------------------------------------------- props de evento e aliados

def prop_gravedigger(cv, W, H):
    by = H - 16
    coat = Layer(W, H)
    coat.poly([(W/2 - 60, by), (W/2 + 60, by), (W/2 + 40, by - 200), (W/2 - 40, by - 200)])
    paint(cv, coat, base=(70, 60, 80), shadow=(36, 30, 44), light=(120, 110, 130), outline_w=3)
    shovel = Layer(W, H)
    shovel.capsule((W/2 + 70, by - 260), (W/2 + 80, by - 20), 5)
    paint(cv, shovel, base=(120, 90, 60), outline_w=2.4)
    blade = Layer(W, H)
    blade.rrect(W/2 + 64, by - 40, W/2 + 98, by + 4, 8)
    paint(cv, blade, base=(150, 150, 160), outline_w=2.4)
    draw_skull(cv, W, H, W/2 - 4, by - 236, 40, eye_color=(255, 190, 80))
    hat = Layer(W, H)
    hat.rrect(W/2 - 60, by - 284, W/2 + 56, by - 270, 6)
    hat.rrect(W/2 - 34, by - 340, W/2 + 30, by - 278, 10)
    paint(cv, hat, base=(50, 44, 56), shadow=(26, 22, 30), outline_w=2.6)
    lamp = Layer(W, H)
    lamp.rrect(W/2 - 96, by - 150, W/2 - 66, by - 110, 6)
    glow(cv, lamp, (255, 180, 70), radius=16, strength=1.4)
    paint(cv, lamp, base=(255, 210, 120), outline_w=2.2, shade=False)
    bag = Layer(W, H)
    bag.ellipse(W/2 - 40, by - 60, 34, 30)
    paint(cv, bag, base=(150, 110, 70), outline_w=2.4)
    bn = Layer(W, H)
    bn.bone((W/2 - 56, by - 92), (W/2 - 20, by - 110), 5)
    paint(cv, bn, outline_w=2)


def prop_tailor(cv, W, H):
    prop_gravedigger(cv, W, H)
    tape = Layer(W, H)
    tape.curve([(W/2 - 40, by_ := H - 216), (W/2, H - 160), (W/2 + 40, H - 216)], 6)
    fill(cv, tape, (240, 200, 80))


def prop_witch(cv, W, H):
    by = H - 16
    pot = Layer(W, H)
    pot.ellipse(W/2 + 40, by - 50, 70, 50)
    paint(cv, pot, base=(50, 50, 60), shadow=(24, 24, 30), outline_w=3)
    brew = Layer(W, H)
    brew.ellipse(W/2 + 40, by - 92, 58, 12)
    glow(cv, brew, (140, 255, 120), radius=14, strength=1.4)
    fill(cv, brew, (160, 255, 140))
    robe = Layer(W, H)
    robe.poly([(W/2 - 90, by), (W/2 - 10, by), (W/2 - 30, by - 200), (W/2 - 70, by - 200)])
    paint(cv, robe, base=(80, 40, 100), shadow=(40, 16, 56), outline_w=3)
    draw_skull(cv, W, H, W/2 - 50, by - 226, 34, eye_color=(160, 255, 120))
    hat = Layer(W, H)
    hat.poly([(W/2 - 110, by - 250), (W/2 + 10, by - 250), (W/2 - 40, by - 360)])
    paint(cv, hat, base=(60, 30, 80), shadow=(30, 12, 44), outline_w=3)


def prop_cage(cv, W, H):
    by = H - 16
    draw_skull(cv, W, H, W/2, by - 160, 40, eye_color=(255, 190, 80))
    ribs = rib_mask(W, H, W/2, by - 120, 3, 40, 22, 8)
    paint(cv, ribs, outline_w=2.4)
    bars = Layer(W, H)
    for i in range(7):
        x = W/2 - 90 + i * 30
        bars.rrect(x - 5, by - 260, x + 5, by, 3)
    bars.rrect(W/2 - 100, by - 270, W/2 + 100, by - 250, 6)
    bars.rrect(W/2 - 100, by - 12, W/2 + 100, by + 4, 6)
    paint(cv, bars, base=(110, 110, 124), shadow=(60, 60, 72), outline_w=2.6)
    chain = Layer(W, H)
    chain.capsule((W/2, by - 270), (W/2, 4), 4)
    fill(cv, chain, (90, 90, 100))


def prop_altar(cv, W, H):
    by = H - 16
    m = Layer(W, H)
    m.rrect(W/2 - 110, by - 90, W/2 + 110, by, 12)
    m.rrect(W/2 - 80, by - 130, W/2 + 80, by - 86, 10)
    paint(cv, m, base=(110, 104, 124), shadow=(60, 56, 72), light=(160, 156, 176), outline_w=3)
    runes(cv, W, H, W/2, by - 46, 14, (190, 120, 255))
    orb = Layer(W, H)
    orb.circle(W/2, by - 180, 34)
    glow(cv, orb, (190, 120, 255), radius=26, strength=1.6)
    paint(cv, orb, base=(200, 160, 255), shadow=(120, 70, 190), outline_w=2.6)
    for x in (W/2 - 90, W/2 + 90):
        draw_skull(cv, W, H, x, by - 150, 20, base=(214, 202, 176))


def prop_campfire(cv, W, H):
    by = H - 16
    logs = Layer(W, H)
    logs.bone((W/2 - 80, by - 10), (W/2 + 80, by - 30), 10)
    logs.bone((W/2 - 80, by - 30), (W/2 + 80, by - 10), 10)
    paint(cv, logs, outline_w=2.6)
    fl = Layer(W, H)
    fl.ellipse(W/2, by - 70, 44, 50)
    fl.poly([(W/2 - 40, by - 76), (W/2, by - 200), (W/2 + 40, by - 76)])
    glow(cv, fl, (70, 150, 255), radius=30, strength=1.3)
    fill(cv, fl, (120, 190, 255), blur=2)
    core = Layer(W, H)
    core.ellipse(W/2, by - 66, 20, 28)
    fill(cv, core, (230, 245, 255), blur=2)
    for x in (W/2 - 110, W/2 + 110):
        c = Layer(W, H)
        c.rrect(x - 12, by - 70, x + 12, by, 5)
        paint(cv, c, base=(240, 228, 200), outline_w=2)
        f = Layer(W, H)
        f.ellipse(x, by - 84, 7, 12)
        glow(cv, f, (90, 160, 255), radius=8, strength=1.5)
        fill(cv, f, (170, 215, 255))


def prop_chest(cv, W, H):
    by = H - 16
    m = Layer(W, H)
    m.rrect(W/2 - 100, by - 110, W/2 + 100, by, 14)
    paint(cv, m, base=(130, 82, 48), shadow=(74, 44, 24), light=(180, 124, 80), outline_w=3.2)
    lid = Layer(W, H)
    lid.rrect(W/2 - 106, by - 160, W/2 + 106, by - 100, 26)
    paint(cv, lid, base=(140, 90, 52), shadow=(80, 48, 26), light=(190, 130, 84), outline_w=3.2)
    band = Layer(W, H)
    band.rrect(W/2 - 106, by - 108, W/2 + 106, by - 94, 4)
    band.rrect(W/2 - 18, by - 130, W/2 + 18, by - 70, 6)
    paint(cv, band, base=(230, 190, 80), shadow=(150, 110, 30), outline_w=2.4)
    sp = Layer(W, H)
    sp.poly([(W/2 + 60, by - 200), (W/2 + 66, by - 184), (W/2 + 82, by - 180), (W/2 + 66, by - 176), (W/2 + 60, by - 160), (W/2 + 54, by - 176), (W/2 + 38, by - 180), (W/2 + 54, by - 184)])
    glow(cv, sp, (255, 230, 150), radius=6, strength=1.5)
    fill(cv, sp, (255, 250, 220))


def prop_coffin(cv, W, H):
    by = H - 16
    m = Layer(W, H)
    m.poly([(W/2 - 60, by), (W/2 + 60, by), (W/2 + 86, by - 230), (W/2 + 40, by - 330), (W/2 - 40, by - 330), (W/2 - 86, by - 230)])
    paint(cv, m, base=(90, 60, 50), shadow=(46, 28, 22), light=(140, 100, 80), outline_w=3.2)
    cross = Layer(W, H)
    cross.rrect(W/2 - 8, by - 290, W/2 + 8, by - 170, 3)
    cross.rrect(W/2 - 36, by - 260, W/2 + 36, by - 244, 3)
    paint(cv, cross, base=(230, 190, 80), outline_w=2.2)


def prop_gambler(cv, W, H):
    by = H - 16
    table = Layer(W, H)
    table.rrect(W/2 - 110, by - 110, W/2 + 110, by - 90, 6)
    table.rrect(W/2 - 90, by - 92, W/2 - 74, by, 4)
    table.rrect(W/2 + 74, by - 92, W/2 + 90, by, 4)
    paint(cv, table, base=(110, 70, 44), shadow=(60, 36, 20), outline_w=2.6)
    ribs = rib_mask(W, H, W/2, by - 230, 3, 44, 24, 9)
    paint(cv, ribs, outline_w=2.4)
    draw_skull(cv, W, H, W/2, by - 270, 40, eye_color=(255, 210, 80))
    hat = Layer(W, H)
    hat.rrect(W/2 - 50, by - 316, W/2 + 46, by - 304, 4)
    hat.rrect(W/2 - 30, by - 350, W/2 + 26, by - 310, 8)
    paint(cv, hat, base=(40, 36, 44), outline_w=2.4)
    for i, x in enumerate((W/2 - 40, W/2 + 30)):
        d = Layer(W, H)
        d.rrect(x - 14, by - 140, x + 14, by - 112, 5)
        paint(cv, d, base=IVORY_LIGHT, outline_w=2)
        dot = Layer(W, H)
        dot.circle(x, by - 126, 3)
        fill(cv, dot, (30, 20, 20))


def prop_lake(cv, W, H):
    by = H - 16
    water = Layer(W, H)
    water.ellipse(W/2, by - 30, 150, 34)
    glow(cv, water, (120, 200, 255), radius=16, strength=0.9)
    paint(cv, water, base=(40, 80, 120), shadow=(20, 40, 70), light=(120, 190, 240), outline_w=2.6, grain=False)
    refl = Layer(W, H)
    refl.ellipse(W/2, by - 30, 30, 14)
    fill(cv, refl, (220, 240, 255), alpha=150, blur=2)
    for x in (W/2 - 160, W/2 + 160):
        st = Layer(W, H)
        st.ellipse(x, by - 20, 26, 18)
        paint(cv, st, base=(100, 96, 110), outline_w=2.4)


def prop_fountain(cv, W, H):
    by = H - 16
    b = Layer(W, H)
    b.ellipse(W/2, by - 40, 120, 40)
    b.rrect(W/2 - 20, by - 180, W/2 + 20, by - 40, 8)
    b.ellipse(W/2, by - 180, 60, 20)
    paint(cv, b, base=(120, 116, 130), shadow=(64, 60, 74), light=(170, 166, 180), outline_w=3)
    w = Layer(W, H)
    w.ellipse(W/2, by - 48, 100, 24)
    w.ellipse(W/2, by - 186, 46, 12)
    fill(cv, w, (90, 140, 100))
    drops = Layer(W, H)
    for dx in (-36, 0, 36):
        drops.capsule((W/2 + dx, by - 180), (W/2 + dx * 1.6, by - 60), 3)
    fill(cv, drops, (140, 200, 150), alpha=180)


def prop_abyss(cv, W, H):
    by = H - 16
    pit = Layer(W, H)
    pit.ellipse(W/2, by - 20, 170, 30)
    fill(cv, pit, (8, 4, 10))
    bridge = Layer(W, H)
    for i in range(9):
        x = W/2 - 160 + i * 40
        bridge.rrect(x, by - 34 + (i % 3) * 2, x + 30, by - 20, 4)
    paint(cv, bridge, base=(110, 80, 50), shadow=(60, 40, 24), outline_w=2)
    rope = Layer(W, H)
    rope.curve([(W/2 - 170, by - 80), (W/2, by - 40), (W/2 + 170, by - 80)], 3)
    fill(cv, rope, (160, 130, 80))
    for x in (W/2 - 170, W/2 + 170):
        post = Layer(W, H)
        post.rrect(x - 8, by - 100, x + 8, by - 10, 3)
        paint(cv, post, base=(100, 70, 40), outline_w=2)
    sp = Layer(W, H)
    sp.circle(W/2 + 150, by - 120, 10)
    glow(cv, sp, (255, 220, 120), radius=12, strength=1.6)
    fill(cv, sp, (255, 250, 210))


def prop_gate(cv, W, H):
    by = H - 16
    frame = Layer(W, H)
    frame.rrect(W/2 - 130, by - 300, W/2 - 100, by, 6)
    frame.rrect(W/2 + 100, by - 300, W/2 + 130, by, 6)
    frame.rrect(W/2 - 130, by - 310, W/2 + 130, by - 280, 8)
    paint(cv, frame, base=(100, 96, 110), shadow=(54, 50, 64), outline_w=3)
    bars = Layer(W, H)
    for i in range(6):
        x = W/2 - 80 + i * 32
        bars.rrect(x - 5, by - 280, x + 5, by, 3)
    bars.rrect(W/2 - 100, by - 160, W/2 + 100, by - 148, 4)
    paint(cv, bars, base=(90, 90, 104), shadow=(50, 50, 60), outline_w=2.4)
    draw_skull(cv, W, H, W/2, by - 150, 22, base=(220, 190, 90), eye_color=(255, 120, 60))


def prop_cat(cv, W, H):
    by = H - 16
    tail = Layer(W, H)
    tail.curve([(W/2 - 50, by - 30), (W/2 - 100, by - 60), (W/2 - 80, by - 140)], 8)
    paint(cv, tail, outline_w=2.4)
    feet = quad_skeleton(cv, W, H, W/2 - 50, W/2 + 40, by - 70, 66, 8)
    ears = Layer(W, H)
    ears.poly([(W/2 + 40, by - 120), (W/2 + 44, by - 160), (W/2 + 62, by - 128)])
    ears.poly([(W/2 + 70, by - 124), (W/2 + 84, by - 160), (W/2 + 92, by - 120)])
    paint(cv, ears, outline_w=2.4)
    draw_skull(cv, W, H, W/2 + 66, by - 96, 30, snout=0.2, eye_color=(160, 255, 140))


PROPS = {
    "prop_gravedigger": (prop_gravedigger, 280, 380), "prop_tailor": (prop_tailor, 280, 380),
    "prop_witch": (prop_witch, 300, 380), "prop_cage": (prop_cage, 260, 360),
    "prop_altar": (prop_altar, 300, 280), "prop_campfire": (prop_campfire, 300, 260),
    "prop_chest": (prop_chest, 260, 240), "prop_coffin": (prop_coffin, 220, 360),
    "prop_gambler": (prop_gambler, 260, 380), "prop_lake": (prop_lake, 380, 160),
    "prop_fountain": (prop_fountain, 280, 260), "prop_abyss": (prop_abyss, 400, 180),
    "prop_gate": (prop_gate, 300, 340), "prop_cat": (prop_cat, 260, 240),
}


def ally_skeleton(cv, W, H, fc, shield=False):
    by = H - 16
    legs = Layer(W, H)
    legs.bone((W/2 - 14, by - 100), (W/2 - 18, by - 6), 7)
    legs.bone((W/2 + 14, by - 100), (W/2 + 18, by - 6), 7)
    paint(cv, legs, outline_w=2.4)
    paint(cv, rib_mask(W, H, W/2, by - 190, 3, 44, 24, 9), outline_w=2.4)
    arm = Layer(W, H)
    arm.bone((W/2 + 30, by - 180), (W/2 + 60, by - 120), 6)
    paint(cv, arm, outline_w=2.2)
    sword = Layer(W, H)
    sword.rrect(W/2 + 56, by - 200, W/2 + 66, by - 110, 3)
    paint(cv, sword, base=(190, 196, 210), outline_w=2)
    draw_skull(cv, W, H, W/2 + 4, by - 216, 34, eye_color=(255, 200, 90))
    if shield:
        sh = Layer(W, H)
        sh.poly([(W/2 - 60, by - 180), (W/2 - 10, by - 180), (W/2 - 14, by - 110), (W/2 - 36, by - 90), (W/2 - 58, by - 110)])
        paint(cv, sh, base=(140, 60, 50), shadow=(80, 30, 24), outline_w=2.6)


def ally_hound(cv, W, H, fc):
    m = Layer(W, H)
    by = H - 16
    m.ellipse(W/2 - 10, by - 70, 70, 34)
    m.capsule((W/2 + 50, by - 80), (W/2 + 70, by - 110), 16)
    for lx in (W/2 - 60, W/2 - 30, W/2 + 20, W/2 + 46):
        m.capsule((lx, by - 50), (lx, by - 6), 7)
    m.tapered([(W/2 - 76, by - 76), (W/2 - 110, by - 110)], 12, 3)
    glow(cv, m, (140, 200, 255), radius=10, strength=1.0)
    fill(cv, m, (170, 210, 255), alpha=170)
    draw_skull(cv, W, H, W/2 + 76, by - 118, 26, snout=0.6, base=(200, 225, 255), eye_color=(120, 200, 255))


def ally_insect(cv, W, H, fc):
    cx, cy = W/2, H/2
    for side in (-1, 1):
        w = Layer(W, H)
        w.ellipse(cx - 6 + side * 6, cy - 26, 18, 30)
        fill(cv, w, (230, 250, 255), alpha=110)
    b = Layer(W, H)
    b.ellipse(cx - 18, cy + 6, 26, 16)
    paint(cv, b, base=(200, 230, 120), shadow=(110, 140, 50), outline_w=2.4)
    draw_skull(cv, W, H, cx + 20, cy, 18, eye_color=(160, 255, 120))


def gen_props():
    import artlib
    from PIL import ImageOps
    for pid, (fn, W, H) in PROPS.items():
        cv = new_canvas(W, H)
        fn(cv, W, H)
        finish(cv, W, H, out("props", pid + ".png"))
    for m in data("monsters.json"):
        if m.get("kind") != "ally":
            continue
        W, H = m["art"]["size"]
        cv = new_canvas(W, H)
        fc = fam(m.get("family", ""))
        if m["id"] == "ally_ghost_hound":
            ally_hound(cv, W, H, fc)
        elif m["id"] == "ally_bone_insect":
            ally_insect(cv, W, H, fc)
        else:
            ally_skeleton(cv, W, H, fc, shield=m["id"] == "ally_lost_squire")
        cv = ImageOps.mirror(cv)  # monstros são espelhados de novo ao exibir aliados
        finish(cv, W, H, out("monsters", m["id"] + ".png"))
    print("props ok")



# ------------------------------------------- companheiros, relíquias, gabinete

def comp_ossudo(cv, W, H):
    by = H - 20
    tail = Layer(W, H)
    tail.curve([(60, by - 90), (30, by - 130), (40, by - 170)], 9)
    paint(cv, tail, outline_w=2.6)
    quad_skeleton(cv, W, H, 60, 150, by - 80, 76, 10)
    ears = Layer(W, H)
    ears.ellipse(150, by - 140, 16, 26)
    paint(cv, ears, base=(200, 180, 150), outline_w=2.4)
    draw_skull(cv, W, H, 176, by - 112, 36, snout=0.55, eye_color=(255, 190, 80))
    bn = Layer(W, H)
    bn.bone((196, by - 70), (240, by - 80), 6)
    paint(cv, bn, outline_w=2.2)
    collar = Layer(W, H)
    collar.rrect(140, by - 96, 166, by - 84, 4)
    fill(cv, collar, (200, 60, 60))


def comp_lumi(cv, W, H):
    cx, by = W / 2, H - 20
    gh = Layer(W, H)
    gh.ellipse(cx, by - 110, 60, 70)
    gh.poly([(cx - 60, by - 110), (cx + 60, by - 110), (cx + 50, by - 30), (cx + 25, by - 50), (cx, by - 26), (cx - 25, by - 50), (cx - 50, by - 30)])
    glow(cv, gh, (110, 180, 255), radius=18, strength=1.0)
    fill(cv, gh, (180, 220, 255), alpha=200)
    eyes = Layer(W, H)
    eyes.ellipse(cx - 18, by - 120, 9, 13)
    eyes.ellipse(cx + 18, by - 120, 9, 13)
    fill(cv, eyes, (30, 40, 80))
    candle = Layer(W, H)
    candle.rrect(cx - 16, by - 210, cx + 16, by - 168, 6)
    paint(cv, candle, base=(240, 230, 210), outline_w=2.4)
    fl = Layer(W, H)
    fl.ellipse(cx, by - 226, 10, 16)
    glow(cv, fl, (90, 170, 255), radius=12, strength=1.8)
    fill(cv, fl, (200, 230, 255))


def comp_bigorna(cv, W, H):
    cx, by = W / 2, H - 20
    anvil = Layer(W, H)
    anvil.poly([(cx + 10, by - 60), (cx + 110, by - 60), (cx + 90, by - 40), (cx + 70, by - 40), (cx + 74, by), (cx + 40, by), (cx + 44, by - 40), (cx + 24, by - 40)])
    paint(cv, anvil, base=(90, 96, 110), shadow=(50, 54, 64), light=(150, 156, 170), outline_w=2.8)
    apron = Layer(W, H)
    apron.poly([(cx - 70, by), (cx - 10, by), (cx - 20, by - 140), (cx - 60, by - 140)])
    paint(cv, apron, base=(120, 80, 50), shadow=(70, 44, 24), outline_w=2.8)
    paint(cv, rib_mask(W, H, cx - 40, by - 190, 3, 36, 18, 7), outline_w=2.2)
    arm = Layer(W, H)
    arm.bone((cx - 20, by - 180), (cx + 20, by - 210), 6)
    paint(cv, arm, outline_w=2.2)
    hammer = Layer(W, H)
    hammer.capsule((cx + 20, by - 210), (cx + 40, by - 250), 4)
    hammer.rrect(cx + 26, by - 270, cx + 66, by - 244, 5)
    paint(cv, hammer, base=(140, 140, 150), outline_w=2.2)
    draw_skull(cv, W, H, cx - 40, by - 214, 34, eye_color=(255, 150, 60))
    beard = Layer(W, H)
    beard.poly([(cx - 60, by - 190), (cx - 16, by - 190), (cx - 38, by - 150)])
    fill(cv, beard, (220, 120, 60))
    ember(cv, W, H, [(cx + 60, by - 70, 4), (cx + 80, by - 90, 3)], (255, 140, 40))


RAR_COL = {"common": (200, 190, 170), "rare": (90, 170, 255), "legendary": (255, 180, 60)}


def relic_icon(cv, W, H, slot, rarity):
    c = RAR_COL[rarity]
    cx, cy = W / 2, H / 2
    if slot == "relic_amulet":
        ch = Layer(W, H)
        ch.curve([(cx - 30, cy - 34), (cx, cy - 10), (cx + 30, cy - 34)], 4)
        fill(cv, ch, (180, 170, 150))
        g = Layer(W, H)
        g.ellipse(cx, cy + 10, 22, 26)
        if rarity != "common":
            glow(cv, g, c, radius=10, strength=1.0)
        paint(cv, g, base=c, shadow=tuple(int(v * 0.55) for v in c), outline_w=3)
        b = Layer(W, H)
        b.bone((cx - 10, cy + 12), (cx + 10, cy + 6), 3)
        paint(cv, b, outline_w=1.6)
    elif slot == "relic_ring":
        ring = Layer(W, H)
        ring.circle(cx, cy + 8, 28)
        inner = Layer(W, H)
        inner.circle(cx, cy + 8, 18)
        ring.cut(inner)
        paint(cv, ring, base=(220, 200, 150), shadow=(150, 130, 80), outline_w=2.6)
        gem = Layer(W, H)
        gem.poly([(cx - 14, cy - 22), (cx, cy - 36), (cx + 14, cy - 22), (cx, cy - 10)])
        if rarity != "common":
            glow(cv, gem, c, radius=8, strength=1.2)
        paint(cv, gem, base=c, shadow=tuple(int(v * 0.55) for v in c), outline_w=2.4)
    elif slot == "relic_cloak":
        m = Layer(W, H)
        m.poly([(cx - 18, cy - 34), (cx + 18, cy - 34), (cx + 38, cy + 36), (cx, cy + 28), (cx - 38, cy + 36)])
        col = {"common": (90, 80, 100), "rare": (60, 70, 140), "legendary": (90, 40, 110)}[rarity]
        paint(cv, m, base=col, shadow=tuple(int(v * 0.5) for v in col), light=tuple(min(255, int(v * 1.6)) for v in col), outline_w=3)
        clasp = Layer(W, H)
        clasp.circle(cx, cy - 28, 7)
        paint(cv, clasp, base=c, outline_w=1.8)
    else:
        m = Layer(W, H)
        m.rrect(cx - 20, cy - 24, cx + 20, cy + 30, 6)
        m.rrect(cx - 26, cy - 32, cx + 26, cy - 22, 4)
        handle = Layer(W, H)
        handle.curve([(cx - 14, cy - 32), (cx, cy - 50), (cx + 14, cy - 32)], 4)
        fill(cv, handle, (120, 110, 100))
        paint(cv, m, base=(110, 100, 90), shadow=(60, 54, 46), outline_w=2.6)
        fl = Layer(W, H)
        fl.ellipse(cx, cy + 4, 11, 16)
        glow(cv, fl, c if rarity != "common" else (255, 180, 70), radius=12, strength=1.6)
        fill(cv, fl, (255, 240, 200))


def cur_icon(cv, W, H, item):
    cx, cy = W / 2, H / 2
    def P(m, base, out=2.6):
        paint(cv, m, base=base, shadow=tuple(int(v * 0.55) for v in base), light=tuple(min(255, int(v * 1.4) + 20) for v in base), outline_w=out)
    m = Layer(W, H)
    k = item
    if k in ("cur_melted_candle", "cur_black_candle"):
        m.rrect(cx - 14, cy - 10, cx + 14, cy + 34, 5); m.ellipse(cx - 18, cy + 34, 10, 5); m.capsule((cx + 12, cy - 6), (cx + 16, cy + 14), 4)
        P(m, (240, 228, 200) if k == "cur_melted_candle" else (50, 40, 60))
        f = Layer(W, H); f.ellipse(cx, cy - 22, 7, 12); glow(cv, f, (255, 170, 60) if k == "cur_melted_candle" else (170, 90, 255), 8, 1.6); fill(cv, f, (255, 240, 200))
    elif k in ("cur_holed_coin",):
        m.circle(cx, cy, 30); h = Layer(W, H); h.circle(cx, cy, 8); m.cut(h); P(m, (230, 190, 70))
    elif k in ("cur_gold_tooth", "cur_hydra_tooth"):
        m.poly([(cx - 20, cy - 26), (cx + 20, cy - 26), (cx + 14, cy + 10), (cx + 4, cy + 34), (cx, cy + 12), (cx - 4, cy + 34), (cx - 14, cy + 10)])
        P(m, (250, 200, 70) if k == "cur_gold_tooth" else (220, 120, 100))
    elif k == "cur_rusty_shovel":
        m.capsule((cx + 26, cy - 34), (cx - 6, cy + 6), 5); m.poly([(cx - 4, cy), (cx - 30, cy + 20), (cx - 22, cy + 38), (cx + 6, cy + 18)]); P(m, (170, 110, 70))
    elif k == "cur_old_lantern":
        relic_icon(cv, W, H, "relic_lantern", "common"); return
    elif k == "cur_torn_map":
        m.poly([(cx - 30, cy - 26), (cx + 26, cy - 30), (cx + 30, cy + 24), (cx + 8, cy + 30), (cx + 2, cy + 18), (cx - 28, cy + 28)]); P(m, (220, 200, 150))
        x = Layer(W, H); x.line([(cx - 8, cy - 8), (cx + 8, cy + 8)], 4); x.line([(cx + 8, cy - 8), (cx - 8, cy + 8)], 4); fill(cv, x, (200, 40, 40))
    elif k == "cur_holed_hat":
        m.poly([(cx - 34, cy + 22), (cx + 34, cy + 22), (cx + 6, cy - 36)]); m.ellipse(cx, cy + 22, 38, 8); P(m, (70, 40, 90))
        h = Layer(W, H); h.circle(cx + 4, cy - 2, 5); fill(cv, h, (20, 10, 20))
    elif k == "cur_cracked_cauldron":
        m.ellipse(cx, cy + 8, 32, 26); P(m, (60, 60, 70)); b = Layer(W, H); b.ellipse(cx, cy - 14, 26, 6); glow(cv, b, (140, 255, 120), 8, 1.2); fill(cv, b, (170, 255, 150))
    elif k == "cur_bald_broom":
        m.capsule((cx + 26, cy - 36), (cx - 10, cy + 10), 4); P(m, (150, 110, 70)); b = Layer(W, H); b.poly([(cx - 12, cy + 4), (cx - 30, cy + 36), (cx - 14, cy + 38), (cx - 2, cy + 14)]); P(b, (210, 180, 100))
    elif k == "cur_broken_rune":
        m.poly([(cx - 26, cy - 30), (cx + 22, cy - 26), (cx + 4, cy + 4), (cx + 26, cy + 30), (cx - 24, cy + 30)]); P(m, (120, 120, 134)); runes(cv, W, H, cx - 4, cy, 9, (90, 160, 255))
    elif k == "cur_eternal_moss":
        m.ellipse(cx, cy + 14, 30, 16); m.circle(cx - 12, cy, 14); m.circle(cx + 12, cy + 2, 12); P(m, (80, 140, 70))
    elif k == "cur_bent_gear":
        for i in range(8):
            a = i * math.pi / 4; m.circle(cx + math.cos(a) * 26, cy + math.sin(a) * 26, 7)
        m.circle(cx, cy, 24); h = Layer(W, H); h.circle(cx, cy, 9); m.cut(h); P(m, (150, 150, 160))
    elif k in ("cur_scorched_scale", "cur_triple_scale"):
        n = 3 if k == "cur_triple_scale" else 1
        for i in range(n):
            m.poly([(cx - 22 + i * 10, cy - 20 + i * 8), (cx + 22 + i * 10, cy - 20 + i * 8), (cx + i * 10, cy + 26 + i * 8)])
        P(m, (180, 60, 40) if n == 1 else (60, 150, 90))
    elif k == "cur_eternal_ember":
        m.circle(cx, cy, 20); glow(cv, m, (255, 120, 40), 14, 1.6); P(m, (255, 150, 60))
    elif k == "cur_chipped_claw":
        m.tapered([(cx - 20, cy - 30), (cx + 10, cy - 10), (cx + 16, cy + 30)], 22, 3); P(m, (230, 220, 200))
    elif k == "cur_endless_book":
        m.rrect(cx - 30, cy - 24, cx + 30, cy + 28, 5); P(m, (110, 50, 50)); pg = Layer(W, H); pg.rrect(cx - 24, cy - 20, cx + 24, cy + 22, 3); fill(cv, pg, (240, 230, 210)); l = Layer(W, H); l.line([(cx, cy - 20), (cx, cy + 22)], 3); fill(cv, l, (110, 50, 50))
    elif k == "cur_crow_quill":
        m.tapered([(cx + 24, cy - 34), (cx + 4, cy - 4), (cx - 22, cy + 34)], 16, 2); P(m, (40, 40, 60))
    elif k == "cur_cracked_glasses":
        for x in (cx - 16, cx + 16):
            r = Layer(W, H); r.circle(x, cy, 14); h = Layer(W, H); h.circle(x, cy, 10); r.cut(h); P(r, (200, 170, 80), 2)
        g = Layer(W, H); g.line([(cx + 10, cy - 8), (cx + 18, cy + 6)], 2); fill(cv, g, (255, 255, 255))
    elif k == "cur_rigged_scale":
        m.capsule((cx, cy - 30), (cx, cy + 30), 4); m.capsule((cx - 30, cy - 18), (cx + 30, cy - 26), 3); m.ellipse(cx - 30, cy, 14, 6); m.ellipse(cx + 30, cy - 8, 14, 6); P(m, (220, 180, 80), 2.2)
    elif k == "cur_ancient_receipt":
        m.poly([(cx - 22, cy - 34), (cx + 22, cy - 34), (cx + 22, cy + 30), (cx + 14, cy + 36), (cx + 6, cy + 30), (cx - 2, cy + 36), (cx - 10, cy + 30), (cx - 22, cy + 36)]); P(m, (230, 220, 190))
        l = Layer(W, H)
        for i in range(4):
            l.line([(cx - 14, cy - 22 + i * 12), (cx + 14, cy - 22 + i * 12)], 2)
        fill(cv, l, (120, 100, 80))
    elif k == "cur_empty_purse":
        m.ellipse(cx, cy + 10, 28, 24); m.poly([(cx - 14, cy - 12), (cx + 14, cy - 12), (cx + 6, cy - 26), (cx - 6, cy - 26)]); P(m, (150, 110, 70))
    elif k == "cur_loaded_die":
        m.rrect(cx - 26, cy - 26, cx + 26, cy + 26, 8); P(m, (240, 236, 220)); d = Layer(W, H)
        for (dx, dy) in ((-12, -12), (12, 12), (0, 0), (12, -12), (-12, 12)):
            d.circle(cx + dx, cy + dy, 4)
        fill(cv, d, (40, 20, 20))
    elif k == "cur_bone_goblet":
        m.poly([(cx - 24, cy - 30), (cx + 24, cy - 30), (cx + 8, cy + 4), (cx - 8, cy + 4)]); m.capsule((cx, cy + 4), (cx, cy + 26), 4); m.ellipse(cx, cy + 30, 18, 6); P(m, (230, 220, 190))
    elif k == "cur_grinning_mask":
        m.ellipse(cx, cy, 30, 34); P(m, (240, 230, 210)); f = Layer(W, H); f.ellipse(cx - 11, cy - 8, 6, 8); f.ellipse(cx + 11, cy - 8, 6, 8); f.curve([(cx - 16, cy + 10), (cx, cy + 22), (cx + 16, cy + 10)], 4); fill(cv, f, (40, 20, 20))
    elif k == "cur_murky_mirror":
        m.ellipse(cx, cy - 4, 24, 30); m.capsule((cx, cy + 24), (cx, cy + 38), 5); P(m, (150, 120, 70)); g = Layer(W, H); g.ellipse(cx, cy - 4, 18, 24); fill(cv, g, (90, 80, 130))
    elif k == "cur_silent_bell":
        m.poly([(cx - 26, cy + 22), (cx + 26, cy + 22), (cx + 18, cy - 10), (cx, cy - 30), (cx - 18, cy - 10)]); P(m, (200, 170, 80)); c = Layer(W, H); c.circle(cx, cy + 28, 6); fill(cv, c, (120, 100, 60))
    elif k == "cur_serpent_eye":
        m.ellipse(cx, cy, 32, 20); P(m, (230, 210, 120)); p2 = Layer(W, H); p2.ellipse(cx, cy, 6, 18); fill(cv, p2, (20, 20, 20))
    else:
        m.circle(cx, cy, 24); P(m, (200, 200, 200))


def hunter_hood():
    s = slot_info("slot_skull")
    W, H = s["canvas"]
    cv = new_canvas(W, H)
    px, py = s["pivot"]
    cx, cy = px, py - 82
    hood = Layer(W, H)
    hood.ellipse(cx - 6, cy - 6, 92, 88)
    hood.poly([(cx - 96, cy), (cx - 70, cy + 110), (cx - 20, cy + 80)])
    face = Layer(W, H)
    face.ellipse(cx + 14, cy + 12, 70, 66)
    hood.cut(face)
    paint(cv, hood, base=(60, 30, 40), shadow=(30, 12, 20), light=(120, 60, 70), outline_w=3)
    finish(cv, W, H, out("monsters", "boss_bone_hunter_hood.png"))


def gen_meta_art():
    from PIL import ImageOps
    for cid, fn in (("companion_ossudo", comp_ossudo), ("companion_lumi", comp_lumi), ("companion_bigorna", comp_bigorna)):
        W, H = 260, 280
        cv = new_canvas(W, H)
        fn(cv, W, H)
        finish(cv, W, H, out("ui", cid + ".png"))
    for r in data("relics.json"):
        W = H = 96
        cv = new_canvas(W, H)
        relic_icon(cv, W, H, r["slot"], r["rarity"])
        finish(cv, W, H, out("ui", r["id"] + ".png"))
    cab = data("curiosities.json")
    for it in cab["items"]:
        W = H = 96
        cv = new_canvas(W, H)
        cur_icon(cv, W, H, it["id"])
        finish(cv, W, H, out("ui", it["id"] + ".png"))
    for slot in ("relic_amulet", "relic_ring", "relic_cloak", "relic_lantern"):
        W = H = 96
        cv = new_canvas(W, H)
        relic_icon(cv, W, H, slot, "common")
        finish(cv, W, H, out("ui", "ui_" + slot + ".png"))
    hunter_hood()
    # baú de ossos
    W = H = 160
    cv = new_canvas(W, H)
    prop_chest(cv, W, H) if False else None
    m = Layer(W, H)
    m.rrect(20, 70, 140, 140, 12)
    paint(cv, m, base=(110, 80, 120), shadow=(60, 40, 70), light=(170, 130, 180), outline_w=3)
    lid = Layer(W, H)
    lid.rrect(14, 40, 146, 80, 20)
    paint(cv, lid, base=(120, 90, 130), shadow=(66, 46, 76), outline_w=3)
    draw_skull(cv, W, H, 80, 86, 18, eye_color=(255, 190, 80))
    finish(cv, W, H, out("ui", "ui_bone_chest.png"))
    print("meta art ok")


# ----------------------------------------------------------------- UI e FX

def radial(size, inner=(255, 255, 255, 255), power=2.0, path=None):
    img = Image.new("RGBA", (size, size))
    px = img.load()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / c
            a = max(0.0, 1.0 - d) ** power
            px[x, y] = (inner[0], inner[1], inner[2], int(inner[3] * a))
    if path:
        img.save(path)
    return img


def gen_fx():
    radial(256, power=1.6, path=out("fx", "fx_light.png"))
    radial(64, power=2.2, path=out("fx", "fx_soft.png"))
    # faísca (estrela de 4 pontas)
    W = H = 48
    cv = new_canvas(W, H)
    m = Layer(W, H)
    m.poly([(24, 2), (28, 20), (46, 24), (28, 28), (24, 46), (20, 28), (2, 24), (20, 20)])
    glow(cv, m, (255, 255, 255), radius=3, strength=1.4)
    fill(cv, m, (255, 255, 255))
    finish(cv, W, H, out("fx", "fx_spark.png"))
    # brasa
    radial(24, power=1.2, path=out("fx", "fx_ember.png"))
    # poeira (blob irregular)
    W = H = 40
    cv = new_canvas(W, H)
    m = Layer(W, H)
    rr = rng(5)
    for i in range(6):
        m.circle(20 + rr.uniform(-7, 7), 20 + rr.uniform(-7, 7), rr.uniform(5, 9))
    fill(cv, m, (255, 255, 255), blur=3)
    finish(cv, W, H, out("fx", "fx_dust.png"))
    # lasca de osso
    W, H = 40, 20
    cv = new_canvas(W, H)
    m = Layer(W, H)
    m.bone((8, 10), (32, 10), 3.2)
    paint(cv, m, outline_w=1.6, grain=False)
    finish(cv, W, H, out("fx", "fx_bone_chip.png"))
    # anel de onda de choque
    W = H = 160
    cv = new_canvas(W, H)
    m = Layer(W, H)
    m.circle(80, 80, 72)
    inner = Layer(W, H)
    inner.circle(80, 80, 62)
    m.cut(inner)
    fill(cv, m, (255, 255, 255), blur=2)
    finish(cv, W, H, out("fx", "fx_ring.png"))
    # corte (arco de golpe)
    W, H = 160, 160
    cv = new_canvas(W, H)
    m = Layer(W, H)
    pts = bezier([(20, 130), (40, 30), (140, 20)], 30)
    for i in range(len(pts) - 1):
        w = 2 + 16 * math.sin(math.pi * i / (len(pts) - 1))
        m.line([pts[i], pts[i + 1]], w)
    glow(cv, m, (255, 255, 255), radius=4, strength=1.2)
    fill(cv, m, (255, 255, 255))
    finish(cv, W, H, out("fx", "fx_slash.png"))
    # fumaça
    W = H = 96
    cv = new_canvas(W, H)
    m = Layer(W, H)
    rr = rng(9)
    for i in range(9):
        m.circle(48 + rr.uniform(-18, 18), 48 + rr.uniform(-18, 18), rr.uniform(12, 22))
    fill(cv, m, (255, 255, 255), alpha=200, blur=7)
    finish(cv, W, H, out("fx", "fx_smoke.png"))
    # chama
    W, H = 48, 80
    cv = new_canvas(W, H)
    m = Layer(W, H)
    m.ellipse(24, 54, 14, 20)
    m.poly([(11, 52), (24, 6), (37, 52)])
    glow(cv, m, (255, 140, 40), radius=6, strength=1.3)
    fill(cv, m, (255, 190, 80), blur=1.5)
    core = Layer(W, H)
    core.ellipse(24, 58, 7, 11)
    fill(cv, core, (255, 250, 220), blur=1.5)
    finish(cv, W, H, out("fx", "fx_flame.png"))
    print("fx ok")


def icon_canvas(size=96):
    return new_canvas(size, size), size


def gen_ui():
    from PIL import ImageFont
    S = 96
    # pó de osso
    cv, _ = icon_canvas(S)
    m = Layer(S, S)
    m.ellipse(48, 70, 36, 16)
    m.ellipse(48, 56, 24, 18)
    m.ellipse(40, 44, 12, 10)
    paint(cv, m, base=(224, 210, 176), shadow=(150, 130, 100), outline_w=3)
    bn = Layer(S, S)
    bn.bone((52, 30), (74, 16), 4.5)
    paint(cv, bn, outline_w=2.2)
    finish(cv, S, S, out("ui", "ui_icon_dust.png"))
    # diamante
    cv, _ = icon_canvas(S)
    m = Layer(S, S)
    m.poly([(20, 36), (34, 16), (62, 16), (76, 36), (48, 82)])
    paint(cv, m, base=(110, 214, 255), shadow=(40, 120, 200), light=(220, 250, 255), outline_w=3)
    f = Layer(S, S)
    f.poly([(34, 16), (48, 36), (62, 16)])
    f.poly([(20, 36), (76, 36), (48, 82)])
    fill(cv, f, (255, 255, 255), alpha=60)
    finish(cv, S, S, out("ui", "ui_icon_diamond.png"))
    # coração de osso (vida)
    cv, _ = icon_canvas(S)
    m = Layer(S, S)
    m.circle(34, 38, 20)
    m.circle(62, 38, 20)
    m.poly([(15, 44), (81, 44), (48, 84)])
    paint(cv, m, base=(230, 86, 80), shadow=(140, 30, 36), light=(255, 170, 160), outline_w=3)
    bn = Layer(S, S)
    bn.bone((30, 50), (66, 50), 4)
    paint(cv, bn, outline_w=2)
    finish(cv, S, S, out("ui", "ui_icon_heart.png"))
    # ataque (fêmur cruzado)
    cv, _ = icon_canvas(S)
    m = Layer(S, S)
    m.bone((20, 76), (76, 20), 7)
    paint(cv, m, outline_w=3)
    finish(cv, S, S, out("ui", "ui_icon_attack.png"))
    # escudo
    cv, _ = icon_canvas(S)
    m = Layer(S, S)
    m.poly([(48, 10), (82, 24), (76, 60), (48, 86), (20, 60), (14, 24)])
    paint(cv, m, base=(120, 170, 220), shadow=(60, 90, 140), outline_w=3)
    finish(cv, S, S, out("ui", "ui_icon_shield.png"))
    # tipos de evento
    def ev_icon(name, fn):
        cv, _ = icon_canvas(S)
        fn(cv)
        finish(cv, S, S, out("ui", "ui_event_" + name + ".png"))
    def combat(cv):
        m = Layer(S, S)
        m.bone((18, 78), (72, 24), 6)
        m.bone((24, 24), (78, 78), 6)
        paint(cv, m, outline_w=3)
    def choice(cv):
        m = Layer(S, S)
        m.circle(48, 34, 22)
        inner = Layer(S, S)
        inner.circle(48, 34, 10)
        m.cut(inner)
        m.rrect(40, 48, 56, 64, 4)
        m.circle(48, 78, 8)
        paint(cv, m, base=(255, 196, 90), shadow=(180, 120, 40), outline_w=3)
    def chest(cv):
        m = Layer(S, S)
        m.rrect(14, 40, 82, 82, 8)
        m.ellipse(48, 40, 34, 18)
        paint(cv, m, base=(150, 96, 56), shadow=(90, 54, 30), outline_w=3)
        b = Layer(S, S)
        b.rrect(42, 44, 54, 62, 3)
        paint(cv, b, base=(250, 200, 80), shadow=(170, 120, 30), outline_w=2)
    def boss(cv):
        draw_skull(cv, S, S, 44, 52, 28, eye_color=(255, 70, 70))
        c = Layer(S, S)
        c.poly([(24, 28), (26, 6), (38, 18), (48, 2), (58, 18), (70, 6), (72, 28)])
        paint(cv, c, base=(250, 200, 70), shadow=(170, 120, 30), outline_w=2.6)
    def merchant(cv):
        m = Layer(S, S)
        m.ellipse(48, 58, 30, 26)
        m.rrect(36, 20, 60, 36, 6)
        paint(cv, m, base=(170, 130, 80), shadow=(100, 70, 40), outline_w=3)
        c = Layer(S, S)
        c.circle(48, 60, 10)
        paint(cv, c, base=(250, 210, 90), outline_w=2)
    def ally(cv):
        m = Layer(S, S)
        for x in (24, 40, 56, 72):
            m.rrect(x - 4, 14, x + 4, 82, 3)
        m.rrect(14, 12, 82, 20, 3)
        m.rrect(14, 76, 82, 84, 3)
        paint(cv, m, base=(140, 140, 156), shadow=(70, 70, 86), outline_w=2.6)
        draw_skull(cv, S, S, 46, 46, 16, eye_color=(255, 180, 60))
    def altar(cv):
        m = Layer(S, S)
        m.rrect(16, 50, 80, 84, 6)
        m.rrect(26, 40, 70, 54, 4)
        paint(cv, m, base=(120, 110, 130), shadow=(60, 54, 70), outline_w=3)
        o = Layer(S, S)
        o.circle(48, 26, 12)
        glow(cv, o, (190, 120, 255), radius=8, strength=1.6)
        fill(cv, o, (220, 180, 255))
    def rest(cv):
        m = Layer(S, S)
        m.bone((18, 80), (78, 70), 6)
        m.bone((18, 70), (78, 80), 6)
        paint(cv, m, outline_w=2.6)
        fl = Layer(S, S)
        fl.ellipse(48, 52, 16, 20)
        fl.poly([(34, 50), (48, 10), (62, 50)])
        glow(cv, fl, (80, 160, 255), radius=8, strength=1.4)
        fill(cv, fl, (150, 210, 255))
    def rare(cv):
        m = Layer(S, S)
        m.poly([(48, 6), (58, 36), (90, 38), (64, 56), (74, 88), (48, 70), (22, 88), (32, 56), (6, 38), (38, 36)])
        glow(cv, m, (190, 120, 255), radius=6, strength=1.2)
        paint(cv, m, base=(210, 170, 255), shadow=(120, 70, 190), outline_w=3)
    for n, f in (("combat", combat), ("choice", choice), ("chest", chest), ("boss", boss), ("merchant", merchant), ("ally", ally), ("altar", altar), ("rest", rest), ("rare", rare)):
        ev_icon(n, f)
    # ícones de bônus de nível
    def lv(name, fn):
        cv, _ = icon_canvas(S)
        fn(cv)
        finish(cv, S, S, out("ui", name + ".png"))
    def marrow(cv):
        m = Layer(S, S)
        m.bone((20, 48), (76, 48), 10)
        paint(cv, m, outline_w=3)
        c = Layer(S, S)
        c.ellipse(48, 48, 18, 5)
        fill(cv, c, (230, 80, 80))
    def femur(cv):
        m = Layer(S, S)
        m.bone((22, 76), (66, 32), 7)
        m.poly([(62, 36), (86, 8), (72, 42)])
        paint(cv, m, outline_w=3)
    def eye(cv):
        m = Layer(S, S)
        m.ellipse(48, 48, 36, 22)
        paint(cv, m, base=(60, 40, 70), shadow=(30, 18, 40), outline_w=3)
        e = Layer(S, S)
        e.circle(48, 48, 10)
        glow(cv, e, (255, 180, 60), radius=8, strength=2)
        fill(cv, e, (255, 220, 140))
    def knees(cv):
        m = Layer(S, S)
        m.bone((26, 20), (40, 52), 6)
        m.bone((40, 52), (24, 84), 6)
        m.circle(40, 52, 9)
        paint(cv, m, outline_w=2.6)
        w = Layer(S, S)
        for y in (34, 50, 66):
            w.line([(56, y), (82, y)], 3)
        fill(cv, w, (190, 230, 255))
    def jaw(cv):
        m = Layer(S, S)
        m.rrect(16, 40, 80, 70, 14)
        h = Layer(S, S)
        for x in range(22, 76, 12):
            h.poly([(x, 40), (x + 10, 40), (x + 5, 54)])
        paint(cv, m, outline_w=3)
        fill(cv, h, (40, 20, 20))
        d = Layer(S, S)
        d.ellipse(48, 80, 8, 10)
        fill(cv, d, (220, 60, 70))
    def warm(cv):
        m = Layer(S, S)
        m.bone((20, 56), (76, 56), 9)
        paint(cv, m, outline_w=3)
        f = Layer(S, S)
        f.ellipse(48, 30, 10, 16)
        glow(cv, f, (255, 140, 60), radius=8, strength=1.6)
        fill(cv, f, (255, 210, 140))
    def heavy(cv):
        draw_skull(cv, S, S, 46, 50, 30, eye_color=(255, 90, 60), base=(210, 200, 190))
        m = Layer(S, S)
        m.poly([(70, 12), (82, 24), (66, 26)])
        fill(cv, m, (255, 220, 120))
    lv("ui_levelup_quick_knees", knees)
    lv("ui_levelup_hungry_jaw", jaw)
    lv("ui_levelup_warm_marrow", warm)
    lv("ui_levelup_heavy_skull", heavy)
    lv("ui_levelup_strong_marrow", marrow)
    lv("ui_levelup_sharp_femur", femur)
    lv("ui_levelup_empty_eye", eye)
    # logo Bone Tribe
    font = ImageFont.truetype(os.path.join(ROOT, "art", "fonts", "PirataOne-Regular.ttf"), 136 * SS)
    W, H = 640, 260
    cv = new_canvas(W, H)
    txt = Image.new("L", (W * SS, H * SS))
    td = ImageDraw.Draw(txt)
    td.text((W * SS / 2, H * SS * 0.52), "Bone Tribe", font=font, anchor="mm", fill=255)
    m = Layer(W, H)
    m.img = txt
    m.d = ImageDraw.Draw(m.img)
    bn = Layer(W, H)
    bn.bone((120, 214), (520, 214), 9)
    glow(cv, m, (255, 150, 50), radius=16, strength=0.7)
    paint(cv, bn, outline_w=4)
    paint(cv, m, base=(240, 228, 200), shadow=(170, 150, 120), light=(255, 252, 240), outline_w=5)
    finish(cv, W, H, out("ui", "ui_logo.png"))
    print("ui ok")


# ------------------------------------------------------------------ ícone

def gen_icon():
    for name, size in (("ui_app_icon", 192), ("ui_app_icon_foreground", 432), ("ui_app_icon_background", 432), ("ui_app_icon_512", 512)):
        W = H = size
        cv = new_canvas(W, H)
        if name != "ui_app_icon_foreground":
            bg = Image.new("RGBA", (W * SS, H * SS))
            d = ImageDraw.Draw(bg)
            for i in range(H * SS):
                t = i / (H * SS)
                c = (int(28 + 30 * (1 - t)), int(18 + 14 * (1 - t)), int(34 + 20 * (1 - t)), 255)
                d.line([(0, i), (W * SS, i)], fill=c)
            cv.alpha_composite(bg)
            halo = Layer(W, H)
            halo.circle(W * 0.5, H * 0.55, W * 0.36)
            glow(cv, halo, (255, 170, 70), radius=W * 0.12, strength=0.55)
        if name != "ui_app_icon_background":
            sc = 0.62 if name == "ui_app_icon_foreground" else 1.0
            r = W * 0.27 * sc
            draw_skull(cv, W, H, W * 0.47, H * 0.46, r, eye_color=(255, 180, 60))
        finish(cv, W, H, out("ui", name + ".png"))
    print("icon ok")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("icon", "all"):
        gen_icon()
    if what in ("bones", "all"):
        gen_bones()
    if what in ("monsters", "all"):
        gen_monsters()
    if what in ("env", "all"):
        gen_env()
    if what in ("props", "all"):
        gen_props()
    if what in ("meta", "all"):
        gen_meta_art()
    if what in ("fx", "all"):
        gen_fx()
    if what in ("ui", "all"):
        gen_ui()
