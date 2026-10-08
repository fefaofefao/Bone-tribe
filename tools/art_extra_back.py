#!/usr/bin/env python3
"""Ossos extras de costas (slot_back) e caudas (slot_tail) do Bone Tribe.

Uso: python3 tools/art_extra_back.py  (gera art/bones/<bone_id>.png)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa
from PIL import ImageChops


# ------------------------------------------------------------- utilitários

def _dark(c, k=0.55):
    return tuple(int(v * k) for v in c)


def _lite(c, add=60):
    return tuple(min(255, v + add) for v in c)


def pc(cv, m, col, ow=3, **kw):
    """paint com sombra/luz derivadas da cor."""
    paint(cv, m, base=col, shadow=_dark(col), light=_lite(col), outline_w=ow, **kw)


def inter(a, b):
    """Interseção de duas máscaras."""
    r = a.copy()
    r.img = ImageChops.multiply(a.img, b.img)
    r.d = ImageDraw.Draw(r.img)
    return r


def _dir(ang):
    a = math.radians(ang)
    return math.cos(a), math.sin(a)


def leaf_pts(root, ang, length, width, n=32, power=0.75, base_w=0.0, bend=0.0):
    """Contorno de folha/asa: começa no root e aponta no ângulo ang (graus)."""
    ux, uy = _dir(ang)
    nx, ny = -uy, ux
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        w = width * (math.sin(math.pi * t) ** power) + base_w * (1 - t)
        off = bend * width * math.sin(math.pi * t) * t
        cx = root[0] + ux * length * t + nx * off
        cy = root[1] + uy * length * t + ny * off
        top.append((cx + nx * w, cy + ny * w))
        bot.append((cx - nx * w, cy - ny * w))
    return top + bot[::-1]


def leaf_axis(root, ang, length, t, side=0.0, width=0.0, bend=0.0):
    ux, uy = _dir(ang)
    nx, ny = -uy, ux
    off = bend * width * math.sin(math.pi * t) * t + side
    return (root[0] + ux * length * t + nx * off, root[1] + uy * length * t + ny * off)


def rot_rect(cx, cy, w, h, ang):
    ux, uy = _dir(ang)
    nx, ny = -uy, ux
    return [(cx + ux * a * w / 2 + nx * b * h / 2, cy + uy * a * w / 2 + ny * b * h / 2)
            for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def rot_ellipse(cx, cy, rx, ry, ang, n=48):
    ux, uy = _dir(ang)
    nx, ny = -uy, ux
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = math.cos(a) * rx, math.sin(a) * ry
        pts.append((cx + ux * x + nx * y, cy + uy * x + ny * y))
    return pts


def hexagon(cx, cy, r, rot=0):
    return [(cx + math.cos(math.radians(rot + 60 * i)) * r, cy + math.sin(math.radians(rot + 60 * i)) * r) for i in range(6)]


def path_normals(path):
    res = []
    for i in range(len(path)):
        a = path[max(0, i - 1)]
        b = path[min(len(path) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        res.append((dx / ln, dy / ln, -dy / ln, dx / ln))
    return res


def back_canvas():
    s = slot_info("slot_back")
    W, H = s["canvas"]
    return new_canvas(W, H), W, H, s["pivot"][0], s["pivot"][1]


def tail_canvas():
    s = slot_info("slot_tail")
    W, H = s["canvas"]
    return new_canvas(W, H), W, H, s["pivot"][0], s["pivot"][1]


def root_knob(cv, W, H, px, py, r=13):
    k = Layer(W, H)
    k.circle(px, py, r)
    paint(cv, k, outline_w=2.6)


def insect_wing(cv, W, H, root, ang, length, width, col, vein, dim=1.0, alpha=170, stripes=0, bend=0.0, power=0.75, n_side=4):
    col = tuple(int(c * dim) for c in col)
    vein = tuple(int(c * dim) for c in vein)
    m = Layer(W, H)
    m.poly(leaf_pts(root, ang, length, width, power=power, base_w=width * 0.12, bend=bend))
    paint(cv, m, base=col, shadow=_dark(col, 0.7), light=_lite(col, 70), outline_w=2.4, grain=False, alpha=alpha)
    if stripes:
        st = Layer(W, H)
        for i in range(stripes):
            t = 0.2 + i * (0.72 / stripes)
            a = leaf_axis(root, ang, length, t, -width * 1.2, width, bend)
            b = leaf_axis(root, ang, length, t + 0.03, width * 1.2, width, bend)
            st.line([a, b], width * 0.22)
        fill(cv, inter(st, m), _dark(col, 0.55), alpha=200)
    v = Layer(W, H)
    mid = [leaf_axis(root, ang, length, t / 10, 0, width, bend) for t in range(0, 10)]
    v.line(mid, 2.4)
    for i in range(n_side):
        t = 0.18 + i * (0.7 / n_side)
        for sgn in (-1, 1):
            a = leaf_axis(root, ang, length, t, 0, width, bend)
            b = leaf_axis(root, ang, length, t + 0.14, sgn * width * 0.7, width, bend)
            v.line([a, b], 1.6)
    fill(cv, inter(v, m), vein, alpha=230)
    gloss = Layer(W, H)
    gloss.poly(leaf_pts(leaf_axis(root, ang, length, 0.25, -width * 0.25, width, bend), ang, length * 0.45, width * 0.18))
    fill(cv, gloss, (255, 255, 240), alpha=90, blur=1.5)


# ------------------------------------------------------------- costas

def draw_wings_wasp(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    col, vein = (238, 250, 170), (96, 120, 40)
    # par de trás (mais escuro e menor), depois o par da frente
    insect_wing(cv, W, H, (px + 6, py - 10), -72, 120, 26, col, vein, dim=0.8, alpha=140)
    insect_wing(cv, W, H, (px + 4, py - 4), -45, 82, 20, col, vein, dim=0.8, alpha=140)
    insect_wing(cv, W, H, (px - 4, py - 6), -112, 150, 32, col, vein, alpha=160)
    insect_wing(cv, W, H, (px - 4, py), -148, 104, 23, col, vein, alpha=160)
    root_knob(cv, W, H, px, py, 14)
    accent_dots(cv, W, H, [(px - 4, py - 6)], fc["aura"], 5, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_wings_mantis(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    col, vein = (140, 206, 84), (60, 110, 36)
    insect_wing(cv, W, H, (px + 4, py - 8), -128, 200, 40, col, vein, dim=0.72, alpha=245, bend=0.6, power=0.6, n_side=6)
    insect_wing(cv, W, H, (px - 4, py + 2), -150, 220, 46, col, vein, alpha=245, bend=0.6, power=0.6, n_side=6)
    # mancha ocelar no meio da asa
    spot = Layer(W, H)
    sx, sy = leaf_axis((px - 4, py + 2), -150, 220, 0.55, 0, 46, 0.6)
    spot.circle(sx, sy, 9)
    paint(cv, spot, base=(250, 230, 120), shadow=(180, 140, 40), outline_w=1.8, grain=False)
    dot = Layer(W, H)
    dot.circle(sx, sy, 4)
    fill(cv, dot, (60, 40, 30))
    root_knob(cv, W, H, px, py, 14)
    accent_dots(cv, W, H, [(px - 2, py - 2)], fc["aura"], 5, glow_r=5)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_wings_grasshopper(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    # asa membranosa de trás, em leque rosado
    fan = Layer(W, H)
    fan.poly(leaf_pts((px, py - 4), -150, 150, 44, power=0.5))
    paint(cv, fan, base=(200, 150, 120), shadow=(130, 80, 60), light=(240, 200, 170), outline_w=2.2, grain=False, alpha=190)
    fv = Layer(W, H)
    for k in range(-3, 4):
        fv.line([(px, py - 4), leaf_axis((px, py - 4), -150, 150, 0.92, k * 13)], 1.4)
    fill(cv, inter(fv, fan), (110, 60, 50), alpha=200)
    # duas asas estreitas e listradas
    col, vein = (150, 150, 74), (70, 70, 30)
    insect_wing(cv, W, H, (px + 4, py - 10), -158, 196, 17, col, vein, dim=0.78, alpha=250, stripes=6, power=0.45, n_side=0)
    insect_wing(cv, W, H, (px - 2, py), -168, 200, 19, col, vein, alpha=250, stripes=6, power=0.45, n_side=0)
    root_knob(cv, W, H, px, py, 13)
    accent_dots(cv, W, H, [(px - 2, py - 2)], fc["aura"], 4.5, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_shell_turtle(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    cx, cy = px - 40, py - 20
    shell = Layer(W, H)
    shell.ellipse(cx, cy + 10, 132, 104)
    cut = Layer(W, H)
    cut.rrect(cx - 200, cy + 52, cx + 200, cy + 200, 0)
    shell.cut(cut)
    rim = Layer(W, H)
    rim.rrect(cx - 142, cy + 38, cx + 142, cy + 66, 14)
    pc(cv, rim, (50, 120, 116), ow=3)
    paint(cv, shell, base=(60, 150, 140), shadow=(26, 84, 84), light=(140, 220, 200), outline_w=3.2)
    plates = Layer(W, H)
    for row, (y, xs) in enumerate(((cy - 48, (-50, 0, 50)), (cy + 8, (-100, -50, 0, 50, 100)), (cy - 92, (-25, 25)))):
        for x in xs:
            plates.poly(hexagon(cx + x, y, 23 - row * 2, 30))
    plates = inter(plates, shell)
    paint(cv, plates, base=(110, 196, 170), shadow=(50, 120, 110), light=(190, 245, 225), outline_w=2.2, grain=False)
    sc = Layer(W, H)
    for i in range(9):
        sc.ellipse(cx - 120 + i * 30, cy + 54, 13, 9)
    paint(cv, sc, base=(214, 206, 170), shadow=(150, 140, 110), outline_w=1.8, grain=False)
    gloss = Layer(W, H)
    gloss.ellipse(cx - 60, cy - 60, 34, 14)
    fill(cv, gloss, (220, 255, 245), alpha=110, blur=2)
    accent_dots(cv, W, H, [(cx, cy - 48), (cx - 100, cy + 8), (cx + 100, cy + 8)], fc["aura"], 4.5, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_shell_crab(bone_id, family):
    cv, W, H, px, py = back_canvas()
    cx, cy = px - 36, py - 46
    spikes = Layer(W, H)
    for i in range(11):
        a = math.radians(-180 + i * 18)
        bx, by = cx + math.cos(a) * 128, cy + math.sin(a) * 84
        tx, ty = cx + math.cos(a) * 160, cy + math.sin(a) * 112
        ux, uy = -math.sin(a), math.cos(a)
        spikes.poly([(bx + ux * 11, by + uy * 11), (tx, ty), (bx - ux * 11, by - uy * 11)])
    pc(cv, spikes, (200, 80, 40), ow=2.6, grain=False)
    shell = Layer(W, H)
    shell.ellipse(cx, cy, 140, 92)
    cut = Layer(W, H)
    cut.rrect(cx - 200, cy + 40, cx + 200, cy + 200, 0)
    shell.cut(cut)
    shell.rrect(cx - 132, cy + 10, cx + 132, cy + 52, 22)
    paint(cv, shell, base=(226, 96, 50), shadow=(130, 40, 20), light=(255, 170, 110), outline_w=3.2)
    grooves = Layer(W, H)
    grooves.curve([(cx - 60, cy + 40), (cx - 40, cy - 30), (cx, cy - 50)], 4)
    grooves.curve([(cx + 60, cy + 40), (cx + 40, cy - 30), (cx, cy - 50)], 4)
    grooves.curve([(cx - 40, cy - 30), (cx, cy - 10), (cx + 40, cy - 30)], 4)
    fill(cv, grooves, (120, 36, 20), alpha=220)
    bumps = [(cx - 90, cy - 10, 9), (cx + 90, cy - 10, 9), (cx - 60, cy - 50, 7), (cx + 60, cy - 50, 7), (cx, cy + 14, 10), (cx - 100, cy + 30, 6), (cx + 100, cy + 30, 6)]
    b = Layer(W, H)
    for x, y, r in bumps:
        b.circle(x, y, r)
    paint(cv, b, base=(250, 200, 160), shadow=(190, 110, 70), outline_w=1.8, grain=False)
    accent_dots(cv, W, H, [(cx, cy + 14)], fam(family)["aura"], 5, glow_r=6)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_spikes_lizard(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    spine = bezier([(px + 30, py + 8), (px - 40, py - 30), (px - 130, py - 20), (px - 190, py + 30)], 6)
    heights = [64, 116, 148, 140, 104, 64, 32]
    tips = []
    for (x, y), hgt in zip(spine, heights):
        tips.append((x - hgt * 0.18, y - hgt))
    sail = Layer(W, H)
    sail.poly([spine[0]] + tips + [spine[-1]] + spine[::-1])
    paint(cv, sail, base=(170, 52, 40), shadow=(90, 20, 16), light=(240, 110, 80), outline_w=2.6, alpha=215)
    sp = Layer(W, H)
    for (x, y), (tx, ty) in zip(spine, tips):
        sp.tapered([(x, y), ((x + tx) / 2, (y + ty) / 2), (tx, ty)], 22, 4)
    paint(cv, sp, outline_w=2.6)
    red = Layer(W, H)
    for (x, y), (tx, ty) in zip(spine, tips):
        red.tapered([(x + (tx - x) * 0.66, y + (ty - y) * 0.66), (tx, ty)], 12, 3)
    paint(cv, red, base=(214, 56, 40), shadow=(120, 20, 14), light=(255, 140, 100), outline_w=0, grain=False)
    vert = Layer(W, H)
    for x, y in spine:
        vert.ellipse(x, y, 19, 15)
    paint(cv, vert, outline_w=2.8)
    ember(cv, W, H, [(px - 110, py - 176, 4), (px + 10, py - 140, 3), (px - 170, py - 110, 3), (px + 20, py - 90, 2.5)], fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_quiver_centaur(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    ang = -125  # eixo da aljava, da base (perto do pivot) para cima e para trás
    ux, uy = _dir(ang)
    QL = 160
    base = (px + 26, py + 40)
    top = (base[0] + ux * QL, base[1] + uy * QL)
    # flechas (atrás da boca da aljava): haste de osso + penas
    arrows = Layer(W, H)
    fl = Layer(W, H)
    for k, (da, ln) in enumerate(((-26, 62), (-9, 78), (8, 72), (24, 58))):
        aux, auy = _dir(ang + da)
        st = (top[0] - uy * (k - 1.5) * 13, top[1] + ux * (k - 1.5) * 13)
        en = (st[0] + aux * ln, st[1] + auy * ln)
        arrows.bone((st[0] - aux * 30, st[1] - auy * 30), en, 4, knob=1.5)
        fl.poly(leaf_pts((en[0] - aux * 38, en[1] - auy * 38), ang + da, 34, 11, power=0.6))
    pc(cv, fl, (250, 150, 50), ow=2.2, grain=False)
    paint(cv, arrows, outline_w=2.4)
    # tubo da aljava
    q = Layer(W, H)
    mid = ((base[0] + top[0]) / 2, (base[1] + top[1]) / 2)
    q.poly(rot_rect(mid[0], mid[1], QL, 60, ang))
    q.ellipse(base[0], base[1], 30, 30)
    paint(cv, q, base=(140, 86, 46), shadow=(80, 44, 22), light=(196, 140, 90), outline_w=3.2)
    mouth = Layer(W, H)
    mouth.poly(rot_ellipse(top[0], top[1], 10, 34, ang))
    paint(cv, mouth, base=(60, 34, 20), shadow=(30, 16, 10), outline_w=2.6, shade=False, grain=False)
    bands = Layer(W, H)
    for t in (0.18, 0.86):
        c = (base[0] + ux * QL * t, base[1] + uy * QL * t)
        bands.poly(rot_rect(c[0], c[1], 14, 70, ang))
    pc(cv, bands, (250, 150, 50), ow=2.2, grain=False)
    stitch = Layer(W, H)
    for i in range(7):
        t = 0.28 + i * 0.075
        c = (base[0] + ux * QL * t, base[1] + uy * QL * t)
        stitch.poly(rot_rect(c[0], c[1], 5, 3, ang + 90))
    fill(cv, stitch, (230, 200, 150))
    # alça cruzando para o corpo
    strap = Layer(W, H)
    strap.curve([(px - 40, py - 40), (px + 20, py + 0), (px + 80, py + 70)], 14)
    pc(cv, strap, (110, 66, 36), ow=2.6)
    buckle = Layer(W, H)
    buckle.rrect(px + 8, py - 14, px + 30, py + 8, 4)
    paint(cv, buckle, base=(240, 200, 90), shadow=(160, 110, 30), outline_w=2.2, grain=False)
    accent_dots(cv, W, H, [(mid[0] - uy * 4, mid[1] + ux * 4)], fc["aura"], 6, glow_r=5)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_lid_mimic(bone_id, family):
    cv, W, H, px, py = back_canvas()
    fc = fam(family)
    cx, cy, rw, rh = px - 40, py - 30, 140, 110
    lid = Layer(W, H)
    lid.ellipse(cx, cy, rw, rh)
    cut = Layer(W, H)
    cut.rrect(cx - 300, cy + 30, cx + 300, cy + 300, 0)
    lid.cut(cut)
    lid.rrect(cx - rw, cy - 10, cx + rw, cy + 40, 6)
    paint(cv, lid, base=(150, 96, 52), shadow=(84, 50, 24), light=(200, 146, 90), outline_w=3.2)
    slats = Layer(W, H)
    for k in (-1, 1):
        slats.line([(cx + k * 46, cy + 40), (cx + k * 46, cy - rh)], 3)
    for yy in (cy - 50, cy - 10):
        slats.line([(cx - rw, yy), (cx + rw, yy)], 3)
    fill(cv, inter(slats, lid), (70, 40, 20), alpha=220)
    trim = Layer(W, H)
    trim.rrect(cx - rw - 4, cy + 26, cx + rw + 4, cy + 42, 5)
    for k in (-1, 1):
        x = cx + k * 92
        band = Layer(W, H)
        band.rrect(x - 9, cy - rh - 20, x + 9, cy + 34, 4)
        trim.add(inter(band, lid))
    paint(cv, trim, base=(240, 196, 70), shadow=(160, 110, 30), light=(255, 240, 160), outline_w=2.4, grain=False)
    # dentes na borda
    tongue = Layer(W, H)
    tongue.ellipse(cx + 40, cy + 50, 24, 12)
    pc(cv, tongue, (200, 70, 90), ow=2, grain=False)
    teeth = Layer(W, H)
    for i in range(10):
        x = cx - rw + 18 + i * ((2 * rw - 36) / 9)
        hgt = 22 if i % 3 == 1 else 16
        teeth.poly([(x - 10, cy + 40), (x, cy + 40 + hgt), (x + 10, cy + 40)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=2.4, grain=False)
    rivets = Layer(W, H)
    for x in (cx - rw + 12, cx - 92, cx + 92, cx + rw - 12, cx - 46, cx + 46):
        rivets.circle(x, cy + 34, 3)
    fill(cv, rivets, (120, 80, 20))
    lock = Layer(W, H)
    lock.rrect(cx - 18, cy - 4, cx + 18, cy + 36, 6)
    paint(cv, lock, base=(240, 196, 70), shadow=(160, 110, 30), light=(255, 240, 160), outline_w=2.6, grain=False)
    eye = Layer(W, H)
    eye.circle(cx, cy + 12, 6)
    eye.poly([(cx - 4, cy + 14), (cx + 4, cy + 14), (cx, cy + 28)])
    glow(cv, eye, fc["aura"], radius=7, strength=2.2)
    fill(cv, eye, (180, 220, 255))
    glint = Layer(W, H)
    gx, gy = cx - 92, cy - 70
    glint.poly([(gx, gy - 12), (gx + 3, gy - 3), (gx + 12, gy), (gx + 3, gy + 3), (gx, gy + 12), (gx - 3, gy + 3), (gx - 12, gy), (gx - 3, gy - 3)])
    glow(cv, glint, fc["aura"], radius=5, strength=1.8)
    fill(cv, glint, (230, 245, 255))
    finish(cv, W, H, out("bones", bone_id + ".png"))


# ------------------------------------------------------------- caudas

def draw_tail_wolf(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    path = bezier([(px - 10, py), (px - 90, py + 50), (px - 180, py + 10), (px - 160, py - 100)], 18)
    fl = Layer(W, H)
    for i, (x, y) in enumerate(path):
        t = i / (len(path) - 1)
        fl.circle(x, y, 10 + 30 * math.sin(math.pi * min(1, t * 0.95 + 0.1)) ** 0.8)
    r = rng(7)
    tufts = Layer(W, H)
    nrm = path_normals(path)
    for i in range(2, len(path)):
        x, y = path[i]
        t = i / (len(path) - 1)
        rad = 10 + 30 * math.sin(math.pi * min(1, t * 0.95 + 0.1)) ** 0.8
        for s in (-1, 1):
            _, _, nx, ny = nrm[i]
            bx, by = x + nx * s * rad * 0.7, y + ny * s * rad * 0.7
            ex, ey = x + nx * s * (rad + 12) + r.uniform(-6, 6), y + ny * s * (rad + 12) + r.uniform(-6, 6)
            tufts.tapered([(bx, by), (ex, ey)], 14, 1)
    fl.add(tufts)
    paint(cv, fl, base=(140, 128, 118), shadow=(80, 70, 66), light=(200, 190, 180), outline_w=3)
    tip = Layer(W, H)
    for x, y in path[-4:]:
        tip.circle(x, y, 18)
    tip = inter(tip, fl)
    fill(cv, tip, (236, 226, 210))
    stripe = Layer(W, H)
    st = bezier([(px - 40, py + 14), (px - 120, py + 40), (px - 172, py - 10), (px - 166, py - 70)], 16)
    stripe.line(st, 10)
    fill(cv, inter(stripe, fl), (100, 76, 56), alpha=170, blur=2)
    vert = Layer(W, H)
    for x, y in path[:4]:
        vert.ellipse(x, y, 12, 10)
    paint(cv, vert, outline_w=2.6)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_centaur(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    r = rng(11)
    hair = Layer(W, H)
    hx, hy = px - 46, py - 6
    for k in range(9):
        dy = k * 9 - 20
        end = (hx - 140 + r.uniform(-20, 20) + k * 6, hy + 80 + dy * 0.6 + r.uniform(-6, 6))
        hair.tapered([(hx, hy + k * 2), (hx - 70, hy - 30 + dy * 0.4), (hx - 110, hy + 10 + dy), end], 18, 3)
    paint(cv, hair, base=(120, 76, 40), shadow=(66, 38, 18), light=(180, 126, 76), outline_w=3)
    lines = Layer(W, H)
    for k in range(6):
        dy = k * 12 - 24
        lines.curve([(hx - 10, hy + k * 2), (hx - 70, hy - 26 + dy * 0.4), (hx - 104, hy + 8 + dy), (hx - 126 + k * 8, hy + 70 + dy * 0.5)], 2)
    fill(cv, inter(lines, hair), (196, 146, 96), alpha=200)
    base = Layer(W, H)
    for i, (x, y) in enumerate([(px - 4, py), (px - 22, py - 2), (px - 38, py - 5)]):
        base.ellipse(x, y, 12 - i, 11 - i)
    paint(cv, base, outline_w=2.8)
    wrap = Layer(W, H)
    wrap.rrect(hx - 8, hy - 16, hx + 6, hy + 18, 4)
    pc(cv, wrap, (250, 150, 50), ow=2.2, grain=False)
    accent_dots(cv, W, H, [(hx - 1, hy + 1)], fc["aura"], 3.5, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_bat(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    path = bezier([(px, py), (px - 50, py + 26), (px - 100, py + 20)], 6)
    end = path[-1]
    struts = []
    for a in (-200, -170, -140, -110):
        ux, uy = _dir(a)
        struts.append((end[0] + ux * 90, end[1] + uy * 80))
    mem = Layer(W, H)
    poly = [path[2]]
    for i, tp in enumerate(struts):
        poly.append(tp)
        if i < len(struts) - 1:
            n = struts[i + 1]
            mx, my = (tp[0] + n[0]) / 2, (tp[1] + n[1]) / 2
            poly.append((mx + (end[0] - mx) * 0.3, my + (end[1] - my) * 0.3))
    poly.append(path[1])
    mem.poly(poly)
    pc(cv, mem, (96, 52, 136), ow=2.6)
    bones = Layer(W, H)
    for tp in struts:
        bones.tapered([end, tp], 6, 2)
    paint(cv, bones, outline_w=2.2)
    seg = Layer(W, H)
    for i, (x, y) in enumerate(path):
        seg.ellipse(x, y, 13 - i, 11 - i)
    paint(cv, seg, outline_w=2.8)
    accent_dots(cv, W, H, [struts[1], struts[2]], fc["aura"], 3.5, glow_r=5)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_skeleton_rat(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    base = bezier([(px, py), (px - 60, py + 40), (px - 150, py + 30), (px - 228, py - 30)], 26)
    nrm = path_normals(base)
    path = []
    for i, (x, y) in enumerate(base):
        w = math.sin(i * 0.55) * 10 * (i / len(base))
        path.append((x + nrm[i][2] * w, y + nrm[i][3] * w))
    seg = Layer(W, H)
    for i, (x, y) in enumerate(path):
        r = 9.5 - i * 0.24
        seg.ellipse(x, y, r * 0.95, r)
    paint(cv, seg, base=(236, 206, 210), shadow=(170, 120, 140), light=(255, 240, 244), outline_w=2.4)
    joints = Layer(W, H)
    for i in range(1, len(path) - 1, 2):
        x, y = path[i]
        _, _, nx, ny = nrm[i]
        r = 8.5 - i * 0.22
        joints.line([(x + nx * r * 0.8, y + ny * r * 0.8), (x - nx * r * 0.8, y - ny * r * 0.8)], 1.6)
    fill(cv, joints, (150, 100, 120), alpha=210)
    accent_dots(cv, W, H, [path[-1]], fc["aura"], 3, glow_r=6)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_turtle(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    m = Layer(W, H)
    m.tapered([(px + 4, py), (px - 50, py + 14), (px - 96, py + 34), (px - 118, py + 20)], 56, 8)
    paint(cv, m, base=(130, 176, 136), shadow=(70, 110, 80), light=(190, 230, 190), outline_w=3)
    path = bezier([(px - 2, py - 16), (px - 50, py - 4), (px - 92, py + 20), (px - 112, py + 14)], 4)
    plates = Layer(W, H)
    for i, (x, y) in enumerate(path[:-1]):
        r = 15 - i * 3
        plates.poly(hexagon(x, y, r, 30))
    paint(cv, plates, base=(60, 150, 140), shadow=(26, 84, 84), light=(140, 220, 200), outline_w=2.2, grain=False)
    sc = Layer(W, H)
    for x, y, r in [(px - 20, py + 14, 6), (px - 48, py + 20, 5), (px - 74, py + 30, 4), (px - 4, py + 10, 5)]:
        sc.circle(x, y, r)
    fill(cv, sc, (90, 140, 100), alpha=200)
    accent_dots(cv, W, H, [path[0]], fc["aura"], 4, glow_r=4)
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_wasp(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    cx, cy, ang = px - 84, py + 12, 168
    ux, uy = _dir(ang)
    tipb = (cx + ux * 56, cy + uy * 56)
    tip = (cx + ux * 100, cy + uy * 100 + 6)
    st = Layer(W, H)
    st.tapered([tipb, ((tipb[0] + tip[0]) / 2, (tipb[1] + tip[1]) / 2 + 2), tip], 16, 1.5)
    paint(cv, st, base=(50, 40, 34), shadow=(20, 16, 14), light=(120, 110, 100), outline_w=2.6)
    pet = Layer(W, H)
    pet.capsule((px, py), (cx - ux * 60, cy - uy * 60), 7)
    pc(cv, pet, (60, 48, 36), ow=2.6)
    ab = Layer(W, H)
    ab.poly(rot_ellipse(cx, cy, 66, 46, ang))
    paint(cv, ab, base=(240, 206, 60), shadow=(160, 120, 20), light=(255, 245, 170), outline_w=3.2)
    stripes = Layer(W, H)
    for d in (-26, 2, 30):
        c = (cx + ux * d, cy + uy * d)
        stripes.poly(rot_rect(c[0], c[1], 14, 120, ang + 8))
    stripes = inter(stripes, ab)
    fill(cv, stripes, (40, 30, 24))
    gloss = Layer(W, H)
    gloss.poly(rot_ellipse(cx + 4, cy - 26, 30, 7, ang))
    fill(cv, gloss, (255, 255, 230), alpha=150, blur=1.5)
    accent_dots(cv, W, H, [tip], fc["aura"], 4.5, glow_r=9)
    drop = Layer(W, H)
    drop.circle(tip[0] + 2, tip[1] + 14, 4)
    drop.poly([(tip[0] - 2, tip[1] + 12), (tip[0] + 6, tip[1] + 12), (tip[0] + 1, tip[1] + 4)])
    glow(cv, drop, fc["aura"], radius=5, strength=1.6)
    fill(cv, drop, (200, 255, 140))
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_golem(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    stone = dict(base=(150, 158, 172), shadow=(80, 88, 104), light=(210, 216, 230))
    blocks = [(px - 16, py, 26), (px - 74, py + 20, 22)]
    club = (px - 152, py + 6, 38)
    rings = [(px - 46, py + 11), (px - 104, py + 16)]
    ring = Layer(W, H)
    hole = Layer(W, H)
    for x, y in rings:
        ring.ellipse(x, y, 12, 17)
        hole.ellipse(x, y, 5, 10)
    ring.cut(hole)
    paint(cv, ring, base=(96, 100, 112), shadow=(50, 52, 62), light=(170, 176, 190), outline_w=2.4, grain=False)
    b = Layer(W, H)
    for x, y, r in blocks:
        b.rrect(x - r, y - r * 0.9, x + r, y + r * 0.9, 7)
    paint(cv, b, outline_w=3.2, **stone)
    c = Layer(W, H)
    x, y, r = club
    c.rrect(x - r, y - r, x + r, y + r, 16)
    for a in (-135, -45, 135, -90, 90):
        ux, uy = _dir(a)
        c.poly([(x + ux * r * 0.7 - uy * 10, y + uy * r * 0.7 + ux * 10), (x + ux * (r + 18), y + uy * (r + 18)), (x + ux * r * 0.7 + uy * 10, y + uy * r * 0.7 - ux * 10)])
    paint(cv, c, outline_w=3.4, **stone)
    cracks = Layer(W, H)
    cracks.line([(x - 20, y - 36), (x - 10, y - 20), (x - 22, y - 8)], 2.4)
    cracks.line([(px - 24, py - 18), (px - 16, py - 6)], 2)
    cracks.line([(px - 84, py + 30), (px - 70, py + 38)], 2)
    fill(cv, cracks, (70, 76, 90))
    moss = Layer(W, H)
    moss.ellipse(x + 20, y + 34, 16, 6)
    moss.ellipse(px - 70, py + 4, 9, 4)
    fill(cv, moss, (110, 150, 80), alpha=200)
    runes(cv, W, H, x + 2, y + 4, 13, fc["aura"])
    runes(cv, W, H, px - 76, py + 22, 6, fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


def draw_tail_dragon(bone_id, family):
    cv, W, H, px, py = tail_canvas()
    fc = fam(family)
    ctrl = [(px + 6, py), (px - 80, py + 76), (px - 170, py + 56), (px - 170, py - 30)]
    path = bezier(ctrl, 22)
    nrm = path_normals(path)
    n = len(path)
    def wid(i):
        return 17 - 12 * (i / (n - 1))
    # escamas por cima (lado de fora da curva)
    sc = Layer(W, H)
    for i in range(1, n - 3):
        x, y = path[i]
        ux, uy, nx, ny = nrm[i]
        side = 1
        r = wid(i)
        h = r * 1.3 + 6
        sc.poly([(x - ux * r * 0.8 + nx * side * r * 0.5, y - uy * r * 0.8 + ny * side * r * 0.5),
                 (x + ux * r * 0.2 + nx * side * (r + h), y + uy * r * 0.2 + ny * side * (r + h)),
                 (x + ux * r * 0.9 + nx * side * r * 0.5, y + uy * r * 0.9 + ny * side * r * 0.5)])
    paint(cv, sc, base=(196, 48, 36), shadow=(110, 20, 14), light=(255, 120, 80), outline_w=2.4, grain=False)
    # ponta em pá
    ex, ey = path[-1]
    ux, uy, nx, ny = nrm[-1]
    spade = Layer(W, H)
    spade.poly([(ex - ux * 4 + nx * 8, ey - uy * 4 + ny * 8), (ex + ux * 10 + nx * 26, ey + uy * 10 + ny * 26),
                (ex + ux * 44, ey + uy * 44), (ex + ux * 10 - nx * 26, ey + uy * 10 - ny * 26), (ex - ux * 4 - nx * 8, ey - uy * 4 - ny * 8)])
    glow(cv, spade, fc["aura"], radius=8, strength=1.0)
    paint(cv, spade, base=(196, 48, 36), shadow=(110, 20, 14), light=(255, 130, 90), outline_w=3)
    vein = Layer(W, H)
    vein.line([(ex + ux * 2, ey + uy * 2), (ex + ux * 36, ey + uy * 36)], 3)
    fill(cv, vein, (255, 200, 120))
    body = Layer(W, H)
    for i, (x, y) in enumerate(path):
        body.circle(x, y, wid(i))
    paint(cv, body, outline_w=3)
    joints = Layer(W, H)
    for i in range(1, n - 1, 2):
        x, y = path[i]
        _, _, nx2, ny2 = nrm[i]
        r = wid(i) * 0.75
        joints.line([(x + nx2 * r, y + ny2 * r), (x - nx2 * r, y - ny2 * r)], 2)
    fill(cv, joints, (150, 120, 90), alpha=200)
    gold = [path[i] for i in (3, 9, 15)]
    accent_dots(cv, W, H, gold, (250, 200, 80), 3.5)
    ember(cv, W, H, [(ex + ux * 50, ey + uy * 50 - 4, 3.5), (px - 120, py - 4, 3), (px - 60, py + 20, 2.5), (px - 200, py + 40, 3)], fc["aura"])
    finish(cv, W, H, out("bones", bone_id + ".png"))


DRAW = {
    "bone_wings_wasp": draw_wings_wasp,
    "bone_wings_mantis": draw_wings_mantis,
    "bone_shell_turtle": draw_shell_turtle,
    "bone_shell_crab": draw_shell_crab,
    "bone_wings_grasshopper": draw_wings_grasshopper,
    "bone_spikes_lizard": draw_spikes_lizard,
    "bone_quiver_centaur": draw_quiver_centaur,
    "bone_lid_mimic": draw_lid_mimic,
    "bone_tail_wolf": draw_tail_wolf,
    "bone_tail_centaur": draw_tail_centaur,
    "bone_tail_bat": draw_tail_bat,
    "bone_tail_skeleton_rat": draw_tail_skeleton_rat,
    "bone_tail_turtle": draw_tail_turtle,
    "bone_tail_wasp": draw_tail_wasp,
    "bone_tail_golem": draw_tail_golem,
    "bone_tail_dragon": draw_tail_dragon,
}

FAMILY_OF = {
    "bone_wings_wasp": "family_insect",
    "bone_wings_mantis": "family_insect",
    "bone_shell_turtle": "family_marine",
    "bone_shell_crab": "family_marine",
    "bone_wings_grasshopper": "family_insect",
    "bone_spikes_lizard": "family_dragon",
    "bone_quiver_centaur": "family_beast",
    "bone_lid_mimic": "family_construct",
    "bone_tail_wolf": "family_beast",
    "bone_tail_centaur": "family_beast",
    "bone_tail_bat": "family_shadow",
    "bone_tail_skeleton_rat": "family_shadow",
    "bone_tail_turtle": "family_marine",
    "bone_tail_wasp": "family_insect",
    "bone_tail_golem": "family_construct",
    "bone_tail_dragon": "family_dragon",
}

if __name__ == "__main__":
    for bid, fn in DRAW.items():
        fn(bid, FAMILY_OF[bid])
