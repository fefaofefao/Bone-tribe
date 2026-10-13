#!/usr/bin/env python3
"""Placeholders dos monstros da segunda leva do Bone Tribe.

Mesmo estilo de tools/gen_art.py (marfim, contorno escuro, brilho da família).
Cada função desenha o monstro virado para a direita; gen_art.gen_monsters espelha
e encaixa no tamanho de data/monsters.json.
Uso: BT_ONLY=monster_grave_hyena python3 tools/gen_art.py monsters
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa


# ------------------------------------------------------------ utilidades

def _dk(c, k=0.55):
    return tuple(int(v * k) for v in c)


def _lt(c, add=60, k=1.0):
    return tuple(min(255, int(v * k + add)) for v in c)


def pal(c, k=0.55, add=60):
    return dict(base=c, shadow=_dk(c, k), light=_lt(c, add))


def pc(cv, m, col, ow=3, **kw):
    """Pinta uma máscara numa cor sólida com sombra e luz derivadas."""
    args = pal(col)
    args.update(kw)
    paint(cv, m, outline_w=ow, **args)


def smooth(pts, it=3):
    """Suaviza um polígono fechado (Chaikin)."""
    p = list(pts)
    for _ in range(it):
        q = []
        n = len(p)
        for i in range(n):
            a, b = p[i], p[(i + 1) % n]
            q.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
            q.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
        p = q
    return p


def blob(m, pts, it=3):
    m.poly(smooth(pts, it))
    return m


def jag(a, b, n, amp, seed=1, down=True):
    """Pontos de uma borda rasgada entre a e b (pontas alternadas)."""
    r = rng(seed)
    out = []
    for i in range(1, n):
        t = i / n
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        if i % 2:
            y += amp * r.uniform(0.6, 1.2) * (1 if down else -1)
        out.append((x, y))
    return out


def gear(m, cx, cy, r, teeth=10, depth=0.22):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        rr = r if (i % 4) in (0, 1) else r * (1 - depth)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    m.poly(pts)


def shard(m, x, y, ang, length, width):
    """Cristal comprido (losango) saindo de (x, y) no ângulo ang (graus)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    m.poly([(x - nx * width * 0.5, y - ny * width * 0.5),
            (x + ux * length * 0.75 - nx * width * 0.5, y + uy * length * 0.75 - ny * width * 0.5),
            (x + ux * length, y + uy * length),
            (x + ux * length * 0.75 + nx * width * 0.5, y + uy * length * 0.75 + ny * width * 0.5),
            (x + nx * width * 0.5, y + ny * width * 0.5)])


def normals(path):
    out = []
    for i in range(len(path)):
        a = path[max(0, i - 1)]
        b = path[min(len(path) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        out.append((dy / ln, -dx / ln))
    return out


def mem_wing(cv, W, H, root, elbow, tips, col, k=1.0, dim=1.0, bone=IVORY, ow=3, thumb=True):
    """Asa de membrana com dedos de osso (estilo do dragão antigo)."""
    poly = [root, elbow]
    for i, tp in enumerate(tips):
        poly.append(tp)
        if i < len(tips) - 1:
            n = tips[i + 1]
            mx, my = (tp[0] + n[0]) / 2, (tp[1] + n[1]) / 2
            poly.append((mx + (elbow[0] - mx) * 0.25, my + (elbow[1] - my) * 0.25))
    mem = Layer(W, H)
    mem.poly(poly)
    c = _dk(col, dim)
    paint(cv, mem, base=c, shadow=_dk(c, 0.5), light=tuple(min(255, int(v * 1.6)) for v in c), outline_w=ow)
    b = Layer(W, H)
    b.capsule(root, elbow, 9 * k)
    for tp in tips:
        b.tapered([elbow, tp], 7.5 * k, 2.5)
    if thumb:
        b.tapered([elbow, (elbow[0] + 6 * k, elbow[1] - 26 * k)], 7 * k, 1)
    paint(cv, b, base=tuple(int(v * (0.75 + 0.25 * dim)) for v in bone), outline_w=ow * 0.85)


def bead_path(m, path, r0, r1):
    n = len(path)
    for i, (x, y) in enumerate(path):
        m.circle(x, y, r0 + (r1 - r0) * i / max(1, n - 1))


def wisps(cv, W, H, pts, color):
    m = Layer(W, H)
    for x, y, r in pts:
        m.circle(x, y, r)
    glow(cv, m, color, radius=8, strength=1.6)
    fill(cv, m, _lt(color, 70), alpha=200)


# --------------------------------------------------------- monstros comuns

def m_grave_hyena(cv, W, H, fc):
    by = H - 14
    sandy = (178, 140, 86)
    # pernas de trás (lado de lá, mais escuras)
    far = Layer(W, H)
    far.bone((100, by - 112), (80, by - 56), 7)
    far.bone((80, by - 52), (102, by - 4), 6)
    far.bone((226, by - 150), (236, by - 76), 7.5)
    far.bone((236, by - 72), (228, by - 4), 6.5)
    paint(cv, far, base=_dk(IVORY, 0.78), outline_w=2.6)
    # cauda com tufo
    tail = Layer(W, H)
    tail.tapered([(70, by - 114), (46, by - 106), (34, by - 78)], 9, 4)
    paint(cv, tail, outline_w=2.6)
    fur(cv, W, H, 34, by - 70, 9, 22, (70, 48, 30), 21, angle=95, spread=35)
    # manto de pelo pintado nos ombros
    mane = Layer(W, H)
    blob(mane, [(120, by - 150), (170, by - 186), (220, by - 194), (238, by - 160), (214, by - 124), (160, by - 128)])
    pc(cv, mane, sandy, ow=2.8)
    spots = Layer(W, H)
    for x, y, r in [(150, by - 150, 6), (172, by - 168, 7), (196, by - 150, 6), (210, by - 176, 5), (186, by - 134, 5), (226, by - 146, 4)]:
        spots.circle(x, y, r)
    fill(cv, spots, (82, 56, 34), alpha=230)
    # coluna inclinada (ombros altos, quadril baixo)
    spine = Layer(W, H)
    spine.curve([(68, by - 112), (130, by - 140), (220, by - 170)], 12)
    paint(cv, spine, outline_w=3)
    ribs = Layer(W, H)
    for i in range(5):
        x = 126 + i * 18
        y = by - 134 - i * 6
        ribs.curve([(x, y), (x + 14, y + 30), (x - 2, y + 58 - i * 2)], 7)
    paint(cv, ribs, outline_w=2.6)
    pelvis = Layer(W, H)
    pelvis.ellipse(84, by - 112, 20, 14)
    paint(cv, pelvis, outline_w=2.6)
    near = Layer(W, H)
    near.bone((86, by - 108), (64, by - 54), 8)
    near.bone((64, by - 50), (90, by - 4), 7)
    near.bone((206, by - 158), (216, by - 80), 8.5)
    near.bone((216, by - 76), (206, by - 4), 7.5)
    paint(cv, near, outline_w=2.8)
    fur(cv, W, H, 150, by - 158, 10, 24, (122, 88, 50), 17, angle=-105, spread=40)
    fur(cv, W, H, 200, by - 186, 14, 28, (122, 88, 50), 7, angle=-110, spread=45)
    # orelhas redondas
    ears = Layer(W, H)
    ears.ellipse(236, by - 200, 15, 19)
    ears.ellipse(264, by - 206, 14, 18)
    paint(cv, ears, outline_w=2.6)
    inner = Layer(W, H)
    inner.ellipse(236, by - 200, 8, 11)
    inner.ellipse(264, by - 206, 7, 10)
    fill(cv, inner, fc["detail"], alpha=220)
    cx, cy, r = 258, by - 158, 44
    draw_skull(cv, W, H, cx, cy, r, snout=0.55, jaw=1.35, eye_color=fc["aura"])
    # sorriso enorme
    grin = Layer(W, H)
    grin.curve([(cx - r * 0.25, cy + r * 0.58), (cx + r * 0.5, cy + r * 0.86), (cx + r * 1.35, cy + r * 0.5)], 4.5)
    fill(cv, grin, (40, 20, 20))
    teeth = Layer(W, H)
    for i in range(6):
        t = i / 5
        x = cx - r * 0.12 + r * 1.35 * t
        y = cy + r * (0.66 + 0.18 * math.sin(t * math.pi * 0.85)) - r * 0.06 * t
        teeth.poly([(x - 4, y - 2), (x, y + 9), (x + 4, y - 2)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=1.4, shade=False, grain=False)


def m_cave_eel(cv, W, H, fc):
    by = H - 18
    water = (40, 96, 104)
    pud = Layer(W, H)
    pud.ellipse(160, by, 140, 18)
    paint(cv, pud, base=water, shadow=_dk(water, 0.6), light=(110, 190, 190), outline_w=2.8, grain=False)
    shine = Layer(W, H)
    shine.ellipse(160, by - 2, 118, 11)
    inner = Layer(W, H)
    inner.ellipse(160, by, 112, 9)
    shine.cut(inner)
    fill(cv, shine, (150, 230, 225), alpha=150)
    path = bezier([(70, by - 4), (70, by - 200), (250, by - 230), (282, by - 110)], 34)
    nrm = normals(path)
    # barbatana dorsal (membrana translúcida em cima)
    fin = Layer(W, H)
    top = [(x + nx * 30, y + ny * 30) for (x, y), (nx, ny) in zip(path[3:-6], nrm[3:-6])]
    poly = []
    for i, p in enumerate(top):
        k = 1.0 if i % 3 else 0.72
        x0, y0 = path[3 + i]
        poly.append((x0 + (p[0] - x0) * k, y0 + (p[1] - y0) * k))
    poly += list(reversed(path[3:-6]))
    fin.poly(poly)
    paint(cv, fin, base=(60, 160, 160), shadow=(30, 90, 96), light=(140, 230, 220), outline_w=2.4, alpha=230)
    rays = Layer(W, H)
    for i in range(3, len(path) - 6, 3):
        (x, y), (nx, ny) = path[i], nrm[i]
        rays.tapered([(x, y), (x + nx * 27, y + ny * 27)], 4, 1.5)
    paint(cv, rays, outline_w=1.4, grain=False)
    # corpo de vértebras
    body = Layer(W, H)
    for i, (x, y) in enumerate(path):
        t = i / (len(path) - 1)
        body.circle(x, y, 17 - 6 * t + 3 * math.sin(t * math.pi))
    paint(cv, body, base=(214, 222, 204), shadow=(120, 140, 130), outline_w=3)
    sp = Layer(W, H)
    for i in range(2, len(path) - 3, 2):
        (x, y), (nx, ny) = path[i], nrm[i]
        sp.tapered([(x - nx * 8, y - ny * 8), (x - nx * 26, y - ny * 26 + 4)], 4.5, 1.5)
    paint(cv, sp, outline_w=1.8, grain=False)
    bands = Layer(W, H)
    for i in range(1, len(path) - 2, 2):
        (x, y), (nx, ny) = path[i], nrm[i]
        t = i / (len(path) - 1)
        rr = 15 - 6 * t + 3 * math.sin(t * math.pi)
        bands.line([(x + nx * rr, y + ny * rr), (x - nx * rr, y - ny * rr)], 2.2)
    fill(cv, bands, (110, 120, 110), alpha=170)
    # nadadeira peitoral
    pf = Layer(W, H)
    hx, hy = path[-6]
    pf.poly([(hx - 6, hy + 4), (hx - 40, hy + 26), (hx - 28, hy + 36), (hx - 12, hy + 30), (hx + 4, hy + 14)])
    paint(cv, pf, base=(60, 160, 160), shadow=(30, 90, 96), light=(140, 230, 220), outline_w=2.2)
    draw_skull(cv, W, H, 288, by - 120, 30, snout=0.95, jaw=0.9, eye_color=fc["aura"], base=(220, 228, 210))
    fang = Layer(W, H)
    fang.poly([(330, by - 102), (335, by - 88), (340, by - 102)])
    fang.poly([(312, by - 102), (316, by - 92), (320, by - 102)])
    paint(cv, fang, base=IVORY_LIGHT, outline_w=1.3, shade=False, grain=False)
    # ponta da cauda saindo da poça e respingos
    tail = Layer(W, H)
    tail.tapered([(214, by + 2), (226, by - 30), (250, by - 40)], 13, 3)
    paint(cv, tail, base=(214, 222, 204), shadow=(120, 140, 130), outline_w=2.6)
    tf = Layer(W, H)
    tf.poly([(240, by - 38), (262, by - 62), (266, by - 30)])
    paint(cv, tf, base=(60, 160, 160), shadow=(30, 90, 96), outline_w=2)
    accent_dots(cv, W, H, [(40, by - 26), (104, by - 30), (196, by - 22), (60, by - 44)], (150, 230, 225), 3.5)
    lip = Layer(W, H)
    lip.ellipse(70, by + 2, 30, 7)
    lip.ellipse(216, by + 3, 22, 6)
    fill(cv, lip, water)


def m_dusk_moth(cv, W, H, fc):
    cx, cy = W / 2, H / 2 - 10
    wing_c = (88, 58, 122)
    for side in (-1, 1):
        lo = Layer(W, H)
        blob(lo, [(cx, cy + 4), (cx + side * 70, cy + 6), (cx + side * 112, cy + 52), (cx + side * 80, cy + 104), (cx + side * 30, cy + 80), (cx + side * 8, cy + 30)])
        paint(cv, lo, base=_dk(wing_c, 0.85), shadow=_dk(wing_c, 0.45), light=_lt(wing_c, 50), outline_w=3)
        up = Layer(W, H)
        blob(up, [(cx, cy - 6), (cx + side * 40, cy - 90), (cx + side * 130, cy - 124), (cx + side * 160, cy - 80), (cx + side * 140, cy - 20), (cx + side * 70, cy + 14), (cx + side * 6, cy + 12)])
        paint(cv, up, base=wing_c, shadow=_dk(wing_c, 0.45), light=_lt(wing_c, 60), outline_w=3)
        edge = Layer(W, H)
        blob(edge, [(cx + side * 120, cy - 110), (cx + side * 156, cy - 80), (cx + side * 138, cy - 26), (cx + side * 128, cy - 40), (cx + side * 140, cy - 80)])
        fill(cv, edge, (52, 32, 74), alpha=200)
        veins = Layer(W, H)
        for tx, ty in [(40, -86), (110, -116), (150, -72), (128, -22)]:
            veins.tapered([(cx + side * 10, cy - 4), (cx + side * tx * 0.55, cy + ty * 0.55 - 6), (cx + side * tx, cy + ty)], 5, 1.5)
        for tx, ty in [(100, 50), (76, 98), (34, 82)]:
            veins.tapered([(cx + side * 8, cy + 8), (cx + side * tx, cy + ty)], 4, 1.5)
        paint(cv, veins, base=(220, 210, 190), outline_w=1.6, grain=False)
        # olho falso
        ex, ey = cx + side * 104, cy - 66
        ring = Layer(W, H)
        ring.circle(ex, ey, 21)
        paint(cv, ring, base=IVORY, outline_w=2.2)
        dark = Layer(W, H)
        dark.circle(ex, ey, 14)
        fill(cv, dark, (40, 24, 56))
        eye_glow(cv, W, H, [(ex, ey)], fc["aura"], 7)
        spot = Layer(W, H)
        spot.circle(cx + side * 70, cy + 60, 10)
        fill(cv, spot, (190, 160, 220), alpha=170)
        accent_dots(cv, W, H, [(cx + side * 150, cy - 74), (cx + side * 136, cy - 30), (cx + side * 96, cy + 92)], (210, 196, 230), 3.2)
    # corpo peludo
    abd = Layer(W, H)
    abd.ellipse(cx, cy + 58, 17, 44)
    paint(cv, abd, base=(120, 100, 130), shadow=(60, 46, 70), light=(180, 160, 190), outline_w=2.8)
    bands = Layer(W, H)
    for y in (cy + 46, cy + 66, cy + 84):
        bands.rrect(cx - 15, y, cx + 15, y + 5, 2)
    fill(cv, bands, (60, 44, 70), alpha=200)
    fur(cv, W, H, cx, cy + 10, 22, 22, (170, 150, 176), 5, angle=90, spread=180)
    ant = Layer(W, H)
    for side in (-1, 1):
        pts = bezier([(cx + side * 8, cy - 44), (cx + side * 20, cy - 90), (cx + side * 54, cy - 112)], 10)
        ant.line(pts, 3)
        for i in range(2, len(pts)):
            x, y = pts[i]
            ant.line([(x, y), (x + side * 9, y + 6)], 2)
            ant.line([(x, y), (x - side * 3, y - 9)], 2)
    paint(cv, ant, base=(190, 170, 140), outline_w=1.4, grain=False)
    draw_skull(cv, W, H, cx - 4, cy - 26, 26, snout=0.05, eye_color=fc["aura"])


def m_clockwork_spider(cv, W, H, fc):
    by = H - 16
    brass = dict(base=(204, 160, 70), shadow=(120, 84, 30), light=(250, 222, 140))
    hub = (190, by - 76)
    for layer_i, (dim, legs) in enumerate(((0.7, (1, 3)), (1.0, (0, 2)))):
        lg = Layer(W, H)
        joints = []
        for i in legs:
            for side in (-1, 1):
                hx = hub[0] + side * 10
                kx = hx + side * (34 + i * 16)
                ky = by - 160 + i * 14
                fx = hx + side * (96 + i * 28)
                mx, my = kx + (fx - kx) * 0.5 + side * 16, by - 66 + i * 6
                lg.tapered([(hx, hub[1]), (kx, ky)], 10, 7)
                lg.tapered([(kx, ky), (mx, my)], 7, 6)
                lg.tapered([(mx, my), (fx, by)], 6, 2)
                joints += [(kx, ky), (mx, my)]
        paint(cv, lg, base=_dk(IVORY, 0.72 + 0.28 * dim), outline_w=2.6)
        accent_dots(cv, W, H, joints, _dk(brass["base"], 0.75 + 0.25 * dim), 5)
    # abdômen de engrenagem
    g = Layer(W, H)
    gear(g, 110, by - 92, 62, 12)
    paint(cv, g, outline_w=3, **brass)
    inner = Layer(W, H)
    inner.circle(110, by - 92, 40)
    paint(cv, inner, base=(150, 112, 44), shadow=(90, 60, 20), light=(210, 170, 90), outline_w=2.2)
    holes = Layer(W, H)
    for k in range(4):
        a = math.radians(45 + k * 90)
        holes.circle(110 + math.cos(a) * 24, by - 92 + math.sin(a) * 24, 8)
    fill(cv, holes, (50, 34, 20))
    skull_mark = Layer(W, H)
    skull_mark.circle(110, by - 92, 13)
    paint(cv, skull_mark, outline_w=2)
    g2 = Layer(W, H)
    gear(g2, 70, by - 150, 24, 8, 0.3)
    paint(cv, g2, outline_w=2.4, base=(170, 176, 190), shadow=(90, 96, 112), light=(220, 226, 236))
    axle = Layer(W, H)
    axle.circle(70, by - 150, 6)
    fill(cv, axle, (60, 60, 70))
    # cefalotórax de osso
    th = Layer(W, H)
    th.ellipse(214, by - 80, 48, 38)
    paint(cv, th, outline_w=3)
    plate = Layer(W, H)
    plate.rrect(176, by - 112, 230, by - 100, 5)
    paint(cv, plate, outline_w=2, **brass)
    accent_dots(cv, W, H, [(182, by - 70), (196, by - 56), (186, by - 90)], (170, 176, 190), 3.5)
    lens = Layer(W, H)
    lens.circle(236, by - 84, 22)
    paint(cv, lens, outline_w=2.6, **brass)
    glass = Layer(W, H)
    glass.circle(238, by - 84, 14)
    glow(cv, glass, fc["aura"], radius=10, strength=1.8)
    fill(cv, glass, (30, 50, 90))
    eye_glow(cv, W, H, [(240, by - 84)], fc["aura"], 7)
    hl = Layer(W, H)
    hl.circle(233, by - 90, 3.5)
    fill(cv, hl, (255, 255, 255))
    fangs = Layer(W, H)
    fangs.tapered([(244, by - 54), (256, by - 40), (248, by - 26)], 8, 1)
    fangs.tapered([(226, by - 50), (234, by - 36), (228, by - 24)], 8, 1)
    paint(cv, fangs, outline_w=1.6, grain=False, **brass)


def m_magma_salamander(cv, W, H, fc):
    by = H - 14
    rock = (66, 42, 38)
    lava = (255, 130, 40)
    far = Layer(W, H)
    for lx in (134, 236):
        far.tapered([(lx, by - 50), (lx + 22, by - 40), (lx + 28, by - 4)], 12, 8)
    paint(cv, far, base=_dk(rock, 0.8), shadow=_dk(rock, 0.4), light=_lt(rock, 30), outline_w=2.6)
    tail = Layer(W, H)
    tail.tapered([(120, by - 50), (60, by - 30), (24, by - 46), (6, by - 80)], 34, 5)
    paint(cv, tail, base=rock, shadow=_dk(rock, 0.5), light=_lt(rock, 40), outline_w=3)
    body = Layer(W, H)
    body.ellipse(184, by - 52, 92, 30)
    paint(cv, body, base=rock, shadow=_dk(rock, 0.5), light=_lt(rock, 40), outline_w=3.2)
    cracks = Layer(W, H)
    for i in range(7):
        x = 110 + i * 24
        cracks.line([(x, by - 34), (x + 6, by - 52), (x - 2, by - 66)], 4)
    cracks.curve([(30, by - 50), (70, by - 38), (120, by - 46)], 3.5)
    glow(cv, cracks, lava, radius=6, strength=2.0)
    fill(cv, cracks, (255, 200, 90))
    spine = Layer(W, H)
    spine.curve([(40, by - 54), (120, by - 82), (260, by - 74)], 9)
    for i in range(8):
        x = 108 + i * 20
        y = by - 80 + abs(i - 3.5) * 1.2
        spine.curve([(x, y), (x + 10, y + 14), (x + 4, y + 30)], 5.5)
    paint(cv, spine, outline_w=2.6)
    spots = Layer(W, H)
    for x, y in [(130, by - 92), (176, by - 96), (222, by - 92), (80, by - 72), (40, by - 66)]:
        spots.circle(x, y, 5.5)
    glow(cv, spots, lava, radius=5, strength=1.8)
    fill(cv, spots, (255, 210, 110))
    near = Layer(W, H)
    for lx in (118, 222):
        near.bone((lx, by - 46), (lx - 22, by - 28), 7)
        near.bone((lx - 22, by - 26), (lx - 14, by - 6), 6)
    paint(cv, near, outline_w=2.6)
    toes = Layer(W, H)
    for lx in (104, 208):
        for d in (-10, 0, 10):
            toes.tapered([(lx, by - 6), (lx + d + 4, by + 2)], 5, 2.5)
    paint(cv, toes, outline_w=1.6, grain=False)
    draw_skull(cv, W, H, 286, by - 56, 32, snout=0.45, jaw=0.8, eye_color=fc["aura"])
    ember(cv, W, H, [(150, by - 116, 4), (210, by - 124, 3), (80, by - 104, 3), (300, by - 104, 2.5), (40, by - 100, 2.5)], fc["aura"])


def m_tomb_ghoul(cv, W, H, fc):
    by = H - 12
    skin = (128, 126, 136)
    # braço de trás
    back = Layer(W, H)
    back.bone((176, by - 224), (196, by - 150), 8)
    back.bone((196, by - 146), (210, by - 70), 7)
    paint(cv, back, base=_dk(IVORY, 0.72), outline_w=2.6)
    bcl = Layer(W, H)
    for d in (-8, 2, 12):
        bcl.tapered([(210, by - 70), (214 + d, by - 46), (206 + d * 1.6, by - 30)], 6, 1)
    paint(cv, bcl, base=_dk(IVORY, 0.72), outline_w=1.6, grain=False)
    legs = Layer(W, H)
    legs.bone((124, by - 140), (148, by - 86), 9)
    legs.bone((148, by - 82), (126, by - 18), 8)
    legs.bone((140, by - 136), (170, by - 80), 9)
    legs.bone((170, by - 76), (154, by - 18), 8)
    paint(cv, legs, outline_w=2.8)
    feet = Layer(W, H)
    for fx in (126, 154):
        for d in (0, 10, 20):
            feet.tapered([(fx, by - 16), (fx + d + 6, by - 4), (fx + d + 14, by)], 7, 2)
    paint(cv, feet, outline_w=1.8, grain=False)
    # pele cinza rasgada sobre as costas
    cloak = Layer(W, H)
    pts = [(214, by - 262), (176, by - 284), (124, by - 270), (92, by - 226), (82, by - 170)]
    pts += jag((82, by - 170), (156, by - 180), 7, 26, seed=4)
    pts += [(156, by - 180), (196, by - 222)]
    cloak.poly(smooth(pts[:5], 1) + pts[5:])
    pc(cv, cloak, (118, 124, 116), ow=3)
    tears = Layer(W, H)
    tears.circle(110, by - 220, 7)
    tears.circle(132, by - 252, 5)
    fill(cv, tears, (60, 54, 70))
    spine = Layer(W, H)
    spine.curve([(130, by - 140), (130, by - 210), (196, by - 250)], 10)
    paint(cv, spine, outline_w=2.8)
    ribs = Layer(W, H)
    for i in range(4):
        x = 150 + i * 12
        y = by - 228 + i * 18
        ribs.curve([(x - 10, y - 10), (x + 26, y), (x + 20, y + 26)], 6.5)
    paint(cv, ribs, outline_w=2.4)
    pel = Layer(W, H)
    pel.ellipse(132, by - 140, 22, 15)
    paint(cv, pel, outline_w=2.6)
    rag = Layer(W, H)
    rp = [(108, by - 156), (158, by - 156), (160, by - 128)] + jag((160, by - 126), (106, by - 126), 6, 18, seed=8) + [(106, by - 128)]
    rag.poly(rp)
    pc(cv, rag, (96, 84, 92), ow=2.4)
    hair = Layer(W, H)
    for i, (ex, ey) in enumerate([(150, by - 200), (164, by - 190), (176, by - 196)]):
        hair.tapered([(214, by - 282), (196 - i * 8, by - 262), (ex + 20, ey + 10)], 5, 1)
    paint(cv, hair, base=(150, 150, 160), outline_w=1.6, grain=False)
    draw_skull(cv, W, H, 228, by - 250, 36, snout=0.25, jaw=1.25, eye_color=fc["aura"])
    arm = Layer(W, H)
    arm.bone((198, by - 228), (244, by - 160), 8.5)
    arm.bone((244, by - 156), (250, by - 70), 7.5)
    paint(cv, arm, outline_w=2.8)
    cl = Layer(W, H)
    for d in (-10, 0, 10, 20):
        cl.tapered([(250, by - 70), (256 + d, by - 44), (248 + d * 1.6, by - 24)], 7, 1)
    paint(cv, cl, base=IVORY_LIGHT, outline_w=1.8, grain=False)
    rag2 = Layer(W, H)
    rag2.poly([(232, by - 196), (256, by - 160), (246, by - 140), (238, by - 152), (226, by - 132), (222, by - 176)])
    pc(cv, rag2, skin, ow=2.2)


def m_frost_mammoth(cv, W, H, fc):
    by = H - 12
    ice = (150, 196, 230)
    far = Layer(W, H)
    for lx in (114, 262):
        far.bone((lx, by - 150), (lx + 6, by - 76), 15)
        far.bone((lx + 6, by - 72), (lx + 2, by - 16), 14)
    paint(cv, far, base=_dk(IVORY, 0.72), outline_w=3)
    tail = Layer(W, H)
    tail.tapered([(70, by - 196), (52, by - 170), (50, by - 140)], 8, 3)
    paint(cv, tail, outline_w=2.4)
    fur(cv, W, H, 50, by - 136, 6, 18, _dk(ice, 0.8), 3, angle=90, spread=30)
    # pelagem gelada no lombo
    hump = Layer(W, H)
    blob(hump, [(70, by - 200), (120, by - 268), (190, by - 300), (260, by - 280), (300, by - 236), (280, by - 196), (180, by - 200), (90, by - 180)])
    paint(cv, hump, base=ice, shadow=(70, 110, 156), light=(225, 245, 255), outline_w=3.2)
    fur(cv, W, H, 120, by - 184, 12, 30, ice, 11, angle=95, spread=25)
    fur(cv, W, H, 230, by - 190, 12, 30, ice, 12, angle=95, spread=25)
    spine = Layer(W, H)
    spine.curve([(70, by - 196), (180, by - 290), (290, by - 236)], 17)
    for i in range(8):
        x = 100 + i * 24
        t = (x - 70) / 220
        y = by - 196 - math.sin(t * math.pi) * 70 - 10 * t
        spine.tapered([(x, y), (x - 4, y - 18)], 8, 4)
    paint(cv, spine, outline_w=3)
    ribs = Layer(W, H)
    for i in range(6):
        x = 120 + i * 26
        t = (x - 70) / 220
        y = by - 200 - math.sin(t * math.pi) * 60
        ribs.curve([(x, y), (x + 26, y + 50), (x + 2, by - 108 - abs(i - 2.5) * 4)], 10)
    paint(cv, ribs, outline_w=2.8)
    pel = Layer(W, H)
    pel.ellipse(96, by - 176, 30, 22)
    paint(cv, pel, outline_w=2.8)
    near = Layer(W, H)
    for lx in (92, 238):
        near.bone((lx, by - 160), (lx + 4, by - 80), 17)
        near.bone((lx + 4, by - 76), (lx, by - 18), 15)
    paint(cv, near, outline_w=3.2)
    pads = Layer(W, H)
    for lx in (92, 238):
        pads.rrect(lx - 24, by - 22, lx + 26, by, 9)
    for lx in (116, 264):
        pads.rrect(lx - 20, by - 18, lx + 22, by, 8)
    paint(cv, pads, base=(90, 110, 136), shadow=(50, 60, 80), light=(150, 176, 200), outline_w=2.6, grain=False)
    for lx in (92, 238):
        fur(cv, W, H, lx, by - 96, 7, 22, ice, 30 + lx, angle=90, spread=40)
    # tromba de vértebras
    tr = bezier([(334, by - 196), (360, by - 140), (352, by - 70), (318, by - 56)], 12)
    trm = Layer(W, H)
    bead_path(trm, tr, 17, 8)
    paint(cv, trm, outline_w=2.8)
    seg = Layer(W, H)
    for (x, y), (nx, ny) in list(zip(tr, normals(tr)))[1:-1]:
        seg.line([(x + nx * 12, y + ny * 12), (x - nx * 12, y - ny * 12)], 1.8)
    fill(cv, seg, (150, 130, 100), alpha=200)
    draw_skull(cv, W, H, 300, by - 236, 54, snout=0.15, jaw=0.7, eye_color=fc["aura"])
    tusk = Layer(W, H)
    tusk.tapered([(318, by - 186), (360, by - 120), (420, by - 112), (432, by - 168)], 20, 4)
    paint(cv, tusk, base=IVORY_LIGHT, outline_w=3)
    tusk2 = Layer(W, H)
    tusk2.tapered([(296, by - 190), (330, by - 130), (380, by - 124), (396, by - 160)], 15, 3)
    paint(cv, tusk2, base=_dk(IVORY_LIGHT, 0.82), outline_w=2.6)
    # cristais de gelo
    cr = Layer(W, H)
    for x, y, a, ln in [(150, by - 286, -110, 30), (196, by - 300, -84, 38), (240, by - 290, -60, 28), (120, by - 262, -140, 22)]:
        shard(cr, x, y, a, ln, 12)
    glow(cv, cr, (170, 220, 255), radius=6, strength=1.4)
    paint(cv, cr, base=(200, 236, 255), shadow=(110, 160, 210), light=(255, 255, 255), outline_w=2.2, grain=False)


def m_lantern_angler(cv, W, H, fc):
    cy = H / 2 + 10
    flesh = (54, 74, 96)
    # cauda
    tf = Layer(W, H)
    tf.poly([(66, cy), (14, cy - 56), (30, cy), (14, cy + 56)])
    paint(cv, tf, base=(70, 150, 156), shadow=(30, 80, 90), light=(140, 220, 220), outline_w=2.8)
    fins = Layer(W, H)
    fins.poly([(110, cy - 34), (150, cy - 86), (196, cy - 70), (210, cy - 40)])
    fins.poly([(110, cy + 30), (150, cy + 76), (196, cy + 60), (204, cy + 36)])
    paint(cv, fins, base=(70, 150, 156), shadow=(30, 80, 90), light=(140, 220, 220), outline_w=2.6)
    body = Layer(W, H)
    blob(body, [(70, cy - 10), (150, cy - 46), (230, cy - 74), (280, cy - 40), (270, cy + 44), (220, cy + 70), (150, cy + 40), (70, cy + 10)])
    paint(cv, body, base=flesh, shadow=_dk(flesh, 0.5), light=_lt(flesh, 50), outline_w=3)
    # espinha de peixe
    bones = Layer(W, H)
    bones.capsule((60, cy), (200, cy - 4), 6)
    for i in range(6):
        x = 82 + i * 20
        h = 18 + i * 6
        bones.tapered([(x, cy - 2), (x + 10, cy - h * 0.6), (x + 4, cy - h)], 5, 2)
        bones.tapered([(x, cy + 2), (x + 10, cy + h * 0.55), (x + 4, cy + h * 0.9)], 5, 2)
    paint(cv, bones, outline_w=2.2)
    # cabeça de osso e mandíbula aberta
    head = Layer(W, H)
    blob(head, [(196, cy - 30), (226, cy - 76), (284, cy - 72), (314, cy - 34), (296, cy - 6), (226, cy + 4)])
    paint(cv, head, outline_w=3)
    jaw = Layer(W, H)
    blob(jaw, [(206, cy + 6), (300, cy + 12), (334, cy + 4), (326, cy + 44), (280, cy + 70), (220, cy + 50)])
    paint(cv, jaw, outline_w=3)
    mouth = Layer(W, H)
    mouth.poly([(222, cy - 2), (306, cy - 14), (330, cy + 8), (300, cy + 30), (232, cy + 14)])
    fill(cv, mouth, (50, 14, 26))
    teeth = Layer(W, H)
    for i in range(6):
        x = 238 + i * 14
        yt = cy - 4 - i * 2
        teeth.poly([(x - 4, yt), (x + 1, yt + 16), (x + 4, yt)])
        yb = cy + 14 + i * 2 - (i * i) * 0.6
        teeth.poly([(x - 2, yb + 10), (x + 3, yb - 10), (x + 7, yb + 10)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=1.3, shade=False, grain=False)
    sock = Layer(W, H)
    sock.circle(262, cy - 44, 15)
    fill(cv, sock, (28, 16, 18))
    eye_glow(cv, W, H, [(264, cy - 44)], fc["aura"], 6)
    gill = Layer(W, H)
    gill.curve([(214, cy - 40), (204, cy - 10), (214, cy + 30)], 4)
    fill(cv, gill, (150, 130, 100))
    # isca
    stalk = Layer(W, H)
    stalk.tapered([(236, cy - 70), (238, cy - 140), (300, cy - 154), (322, cy - 112)], 7, 3)
    paint(cv, stalk, outline_w=2.2)
    bulb = Layer(W, H)
    bulb.circle(324, cy - 98, 13)
    glow(cv, bulb, fc["aura"], radius=18, strength=2.4)
    glow(cv, bulb, (255, 250, 200), radius=6, strength=1.6)
    paint(cv, bulb, base=(200, 255, 240), shadow=fc["aura"], light=(255, 255, 255), outline_w=2, grain=False)
    accent_dots(cv, W, H, [(120, cy + 74), (100, cy + 96), (140, cy + 104)], (170, 235, 235), 3.5)


def m_gargoyle(cv, W, H, fc):
    by = H - 10
    stone = (122, 124, 136)
    st = pal(stone, 0.55, 50)
    bone_stone = (204, 200, 190)
    # asa de trás
    mem_wing(cv, W, H, (180, by - 196), (214, by - 288), [(276, by - 300), (300, by - 252), (290, by - 200)], (96, 100, 118), k=0.8, dim=0.6, bone=bone_stone)
    # pedestal
    ped = Layer(W, H)
    ped.rrect(84, by - 64, 254, by, 6)
    paint(cv, ped, outline_w=3.2, base=(96, 96, 108), shadow=(52, 52, 62), light=(150, 150, 164))
    ledge = Layer(W, H)
    ledge.rrect(72, by - 78, 266, by - 58, 6)
    paint(cv, ledge, outline_w=3, base=(110, 110, 122), shadow=(60, 60, 70), light=(170, 170, 184))
    runes(cv, W, H, 168, by - 30, 10, fc["aura"])
    crack = Layer(W, H)
    crack.line([(100, by - 50), (112, by - 30), (104, by - 10)], 2.4)
    crack.line([(232, by - 54), (240, by - 36)], 2.4)
    fill(cv, crack, (40, 40, 50))
    # asa da frente
    mem_wing(cv, W, H, (164, by - 196), (110, by - 292), [(40, by - 280), (24, by - 220), (48, by - 162), (100, by - 140)], (100, 104, 122), k=1.0, dim=1.0, bone=bone_stone)
    tail = Layer(W, H)
    tail.tapered([(120, by - 100), (70, by - 96), (50, by - 70)], 14, 4)
    tail.poly([(56, by - 74), (34, by - 58), (56, by - 50)])
    paint(cv, tail, outline_w=2.6, **st)
    # corpo agachado
    haunch = Layer(W, H)
    haunch.ellipse(146, by - 116, 46, 42)
    paint(cv, haunch, outline_w=3, **st)
    torso = Layer(W, H)
    blob(torso, [(144, by - 140), (160, by - 220), (204, by - 226), (222, by - 170), (196, by - 112)])
    paint(cv, torso, outline_w=3, **st)
    ribs = rib_mask(W, H, 184, by - 214, 3, 30, 20, 6)
    paint(cv, ribs, base=bone_stone, outline_w=2.2)
    feet = Layer(W, H)
    feet.tapered([(160, by - 100), (184, by - 92), (192, by - 80)], 18, 12)
    for d in (0, 10, 20):
        feet.tapered([(182 + d, by - 82), (192 + d, by - 76)], 7, 3)
    paint(cv, feet, outline_w=2.4, **st)
    arm = Layer(W, H)
    arm.bone((206, by - 196), (232, by - 140), 8)
    arm.bone((232, by - 136), (236, by - 86), 7)
    paint(cv, arm, base=bone_stone, outline_w=2.6)
    cl = Layer(W, H)
    for d in (-8, 2, 12):
        cl.tapered([(236, by - 86), (242 + d, by - 78), (246 + d, by - 66)], 6, 2)
    paint(cv, cl, base=bone_stone, outline_w=1.6, grain=False)
    horns = [(-0.55, -0.55, -0.6, -1.0), (-0.05, -0.8, -0.2, -0.9)]
    draw_skull(cv, W, H, 222, by - 236, 36, snout=0.4, horns=horns, eye_color=fc["aura"], base=(196, 196, 196))
    moss = Layer(W, H)
    moss.ellipse(108, by - 78, 18, 6)
    moss.ellipse(244, by - 78, 14, 5)
    fill(cv, moss, (80, 112, 70))


def m_plague_locust(cv, W, H, fc):
    by = H - 12
    sick = (200, 206, 150)
    flesh = (120, 150, 60)
    green = fc["aura"]
    fume = Layer(W, H)
    for x, y, r in [(80, by - 110, 22), (140, by - 140, 16), (60, by - 70, 14), (220, by - 140, 12)]:
        fume.circle(x, y, r)
    glow(cv, fume, green, radius=16, strength=1.1)
    far = Layer(W, H)
    far.tapered([(150, by - 84), (110, by - 150), (96, by - 130)], 20, 9)
    far.capsule((96, by - 130), (82, by - 8), 5)
    far.tapered([(200, by - 64), (210, by - 34), (204, by - 4)], 6, 3)
    paint(cv, far, base=_dk(sick, 0.7), outline_w=2.6)
    # asas translúcidas abertas
    for k, (tip, dim) in enumerate((((40, by - 210), 0.8), ((70, by - 236), 1.0))):
        w = Layer(W, H)
        blob(w, [(188, by - 104), (150, by - 150), tip, (tip[0] - 12, tip[1] + 30), (120, by - 116)])
        fill(cv, w, (190, 240, 150), alpha=int(150 * dim))
        rim = w.copy()
        inner = Layer(W, H)
        blob(inner, [(186, by - 106), (150, by - 148), (tip[0] + 4, tip[1] + 4), (tip[0] - 7, tip[1] + 28), (122, by - 118)])
        rim.cut(inner)
        fill(cv, rim, (60, 80, 40))
        v = Layer(W, H)
        v.curve([(184, by - 106), (140, by - 150), (tip[0] + 6, tip[1] + 10)], 2.2)
        v.curve([(176, by - 108), (120, by - 130), (tip[0] - 4, tip[1] + 24)], 2)
        fill(cv, v, (90, 120, 60), alpha=220)
    # abdômen segmentado
    abd = Layer(W, H)
    for i in range(6):
        abd.ellipse(150 - i * 18, by - 72 + i * 2, 24 - i * 1.6, 20 - i * 1.2)
    paint(cv, abd, base=flesh, shadow=_dk(flesh, 0.5), light=_lt(flesh, 60), outline_w=3)
    seg = Layer(W, H)
    for i in range(5):
        x = 140 - i * 18
        seg.line([(x, by - 88 + i * 2), (x - 3, by - 56 + i * 2)], 3.4)
    paint(cv, seg, base=sick, outline_w=1.4, grain=False)
    th = Layer(W, H)
    th.ellipse(196, by - 82, 32, 28)
    paint(cv, th, base=flesh, shadow=_dk(flesh, 0.5), light=_lt(flesh, 60), outline_w=3)
    pron = Layer(W, H)
    blob(pron, [(170, by - 104), (214, by - 112), (228, by - 86), (190, by - 72)])
    paint(cv, pron, base=sick, outline_w=2.6)
    # pata de salto
    hind = Layer(W, H)
    hind.tapered([(166, by - 76), (124, by - 130), (96, by - 156)], 32, 14)
    paint(cv, hind, base=sick, outline_w=3)
    stripes = Layer(W, H)
    for t in (0.35, 0.55, 0.75):
        x = 166 + (96 - 166) * t
        y = by - 76 + (-80) * t
        stripes.line([(x - 8, y - 4), (x + 6, y + 6)], 2.6)
    fill(cv, stripes, (110, 120, 70))
    tib = Layer(W, H)
    tib.capsule((96, by - 156), (148, by - 8), 5)
    for i in range(4):
        t = (i + 1) / 5
        x, y = 96 + 52 * t, by - 156 + 148 * t
        tib.tapered([(x, y), (x - 9, y + 4)], 3, 1)
    tib.ellipse(156, by - 6, 14, 5)
    paint(cv, tib, base=sick, outline_w=2.4)
    front = Layer(W, H)
    front.tapered([(214, by - 62), (232, by - 34), (226, by - 4)], 7, 3)
    front.tapered([(192, by - 58), (184, by - 30), (192, by - 4)], 7, 3)
    paint(cv, front, base=sick, outline_w=2.2)
    ant = Layer(W, H)
    ant.tapered([(248, by - 122), (230, by - 172), (190, by - 196)], 3.5, 1.2)
    ant.tapered([(256, by - 120), (252, by - 176), (226, by - 210)], 3.5, 1.2)
    fill(cv, ant, (80, 100, 40))
    draw_skull(cv, W, H, 250, by - 98, 30, snout=0.15, jaw=0.85, eye_color=green, base=sick)
    drip = Layer(W, H)
    drip.ellipse(286, by - 62, 4, 6)
    drip.ellipse(270, by - 50, 3, 5)
    drip.ellipse(100, by - 50, 4, 6)
    glow(cv, drip, green, radius=6, strength=1.8)
    fill(cv, drip, (200, 255, 140))
    wisps(cv, W, H, [(60, by - 130, 3), (210, by - 150, 2.5), (300, by - 120, 2.5), (40, by - 90, 2)], green)


def m_swamp_crocodile(cv, W, H, fc):
    by = H - 12
    moss = (86, 122, 60)
    far = Layer(W, H)
    for lx in (128, 260):
        far.bone((lx, by - 50), (lx + 18, by - 28), 7)
        far.bone((lx + 18, by - 26), (lx + 26, by - 6), 6)
    paint(cv, far, base=_dk(IVORY, 0.72), outline_w=2.4)
    tail = bezier([(130, by - 56), (80, by - 50), (40, by - 44), (6, by - 66)], 14)
    tl = Layer(W, H)
    bead_path(tl, tail, 14, 4)
    paint(cv, tl, outline_w=2.8)
    sc = Layer(W, H)
    for i, (x, y) in enumerate(tail[:-2]):
        s = 11 - i * 0.65
        sc.poly([(x - s * 0.8, y - 8), (x, y - 10 - s), (x + s * 0.8, y - 8)])
    pc(cv, sc, moss, ow=2)
    ribs = Layer(W, H)
    for i in range(7):
        x = 140 + i * 20
        ribs.curve([(x, by - 66), (x + 12, by - 50), (x + 2, by - 30)], 6)
    paint(cv, ribs, outline_w=2.4)
    spine = Layer(W, H)
    spine.curve([(120, by - 58), (200, by - 74), (290, by - 64)], 11)
    paint(cv, spine, outline_w=2.8)
    scutes = Layer(W, H)
    for i in range(9):
        x = 132 + i * 18
        y = by - 74 - math.sin(i / 8 * math.pi) * 6
        scutes.ellipse(x, y, 10, 8)
    paint(cv, scutes, base=moss, shadow=_dk(moss, 0.5), light=_lt(moss, 50), outline_w=2.4)
    knobs = Layer(W, H)
    for i in range(9):
        x = 132 + i * 18
        y = by - 80 - math.sin(i / 8 * math.pi) * 6
        knobs.poly([(x - 4, y), (x, y - 7), (x + 4, y)])
    paint(cv, knobs, base=_lt(moss, 30), outline_w=1.6, grain=False)
    near = Layer(W, H)
    for lx in (144, 270):
        near.bone((lx, by - 50), (lx - 16, by - 26), 7.5)
        near.bone((lx - 16, by - 24), (lx - 8, by - 6), 6.5)
    paint(cv, near, outline_w=2.6)
    toes = Layer(W, H)
    for lx in (136, 262):
        for d in (-8, 2, 12):
            toes.tapered([(lx, by - 6), (lx + d, by + 2)], 5, 2)
    paint(cv, toes, outline_w=1.4, grain=False)
    cx, cy, r = 300, by - 58, 30
    draw_skull(cv, W, H, cx, cy, r, snout=1.65, jaw=0.75, eye_color=fc["aura"])
    teeth = Layer(W, H)
    for i in range(6):
        x = cx + r * 0.2 + i * 13
        teeth.poly([(x - 3, cy + r * 0.62), (x, cy + r * 0.92), (x + 3, cy + r * 0.62)])
        teeth.poly([(x + 3, cy + r * 1.0), (x + 6, cy + r * 0.72), (x + 9, cy + r * 1.0)])
    paint(cv, teeth, base=IVORY_LIGHT, outline_w=1.2, shade=False, grain=False)
    brow = Layer(W, H)
    brow.ellipse(cx + 8, cy - r * 0.86, 14, 7)
    pc(cv, brow, moss, ow=2)
    dr = Layer(W, H)
    for x, ln in ((350, 14), (372, 10)):
        y0 = cy + r * 0.96
        dr.tapered([(x, y0), (x + 2, y0 + ln)], 5, 2)
    pc(cv, dr, _dk(moss, 0.8), ow=1.4, grain=False)


def m_bell_wraith(cv, W, H, fc):
    by = H - 10
    cx = 150
    robe_c = (78, 66, 104)
    aura = fc["aura"]
    gl = Layer(W, H)
    gl.ellipse(cx, by - 120, 70, 110)
    glow(cv, gl, aura, radius=26, strength=0.6)
    robe = Layer(W, H)
    pts = [(cx + 10, 34), (cx + 66, 70), (cx + 80, 150), (cx + 70, 220), (cx + 40, 250), (cx + 6, 290), (cx - 6, by),
           (cx - 30, 280), (cx - 60, 250), (cx - 46, 236), (cx - 84, 230), (cx - 70, 150), (cx - 50, 70)]
    blob(robe, pts, 2)
    paint(cv, robe, base=robe_c, shadow=_dk(robe_c, 0.45), light=_lt(robe_c, 50), outline_w=3)
    tat = Layer(W, H)
    for x, y in [(cx - 40, 236), (cx + 30, 246), (cx + 60, 214)]:
        tat.poly([(x - 6, y), (x, y - 26), (x + 6, y)])
    fill(cv, tat, _dk(robe_c, 0.5), alpha=220)
    fade = Layer(W, H)
    fade.ellipse(cx, by - 30, 50, 50)
    glow(cv, fade, _lt(aura, 40), radius=14, strength=0.5)
    hood_in = Layer(W, H)
    hood_in.ellipse(cx + 12, 98, 38, 44)
    fill(cv, hood_in, (24, 14, 34))
    rim = Layer(W, H)
    rim.ellipse(cx + 12, 98, 44, 50)
    rim.cut(hood_in)
    paint(cv, rim, base=_lt(robe_c, 20), outline_w=1.6, grain=False)
    draw_skull(cv, W, H, cx + 10, 100, 27, snout=0.05, eye_color=aura)
    # braço de trás chamando
    arm2 = Layer(W, H)
    arm2.bone((cx - 40, 150), (cx - 70, 196), 6)
    for d in (-10, 0, 10):
        arm2.tapered([(cx - 70, 196), (cx - 82 + d, 210), (cx - 90 + d, 206)], 4.5, 1.5)
    paint(cv, arm2, base=_dk(IVORY, 0.8), outline_w=2.2)
    sleeve = Layer(W, H)
    sleeve.poly([(cx + 30, 140), (cx + 92, 176), (cx + 88, 200), (cx + 60, 196), (cx + 24, 176)])
    paint(cv, sleeve, base=robe_c, shadow=_dk(robe_c, 0.45), light=_lt(robe_c, 50), outline_w=2.6)
    hand = Layer(W, H)
    hand.bone((cx + 86, 190), (cx + 104, 206), 5)
    paint(cv, hand, outline_w=2)
    # sino
    bx, btop = cx + 112, 204
    handle = Layer(W, H)
    handle.capsule((bx, btop - 6), (bx, btop + 10), 5)
    paint(cv, handle, base=(120, 80, 50), outline_w=2)
    bell = Layer(W, H)
    blob(bell, [(bx - 16, btop + 8), (bx + 16, btop + 8), (bx + 20, btop + 34), (bx + 32, btop + 62), (bx - 32, btop + 62), (bx - 20, btop + 34)], 2)
    paint(cv, bell, base=(196, 150, 70), shadow=(110, 76, 30), light=(250, 220, 140), outline_w=2.8)
    lip = Layer(W, H)
    lip.ellipse(bx, btop + 60, 33, 7)
    paint(cv, lip, base=(170, 124, 50), shadow=(100, 66, 24), outline_w=2.2, grain=False)
    clap = Layer(W, H)
    clap.circle(bx + 2, btop + 70, 6)
    paint(cv, clap, base=(90, 70, 50), outline_w=1.8, grain=False)
    runes(cv, W, H, bx, btop + 36, 6, aura)
    waves = Layer(W, H)
    for k in range(2):
        rr = 46 + k * 16
        pts = [(bx + math.cos(math.radians(a)) * rr, btop + 40 + math.sin(math.radians(a)) * rr) for a in range(-40, 41, 8)]
        waves.line(pts, 3)
    glow(cv, waves, aura, radius=4, strength=1.6)
    fill(cv, waves, _lt(aura, 60), alpha=200)
    wisps(cv, W, H, [(cx - 70, 270, 4), (cx + 50, 290, 3), (cx - 20, 310, 3), (cx + 80, 120, 2.5)], aura)


def m_young_wyvern(cv, W, H, fc):
    by = H - 12
    mem = (196, 84, 44)
    mem_wing(cv, W, H, (216, by - 196), (262, by - 300), [(330, by - 320), (370, by - 270), (360, by - 216)], mem, k=0.75, dim=0.6)
    leg2 = Layer(W, H)
    leg2.bone((196, by - 140), (222, by - 86), 9)
    leg2.bone((222, by - 82), (206, by - 30), 7.5)
    leg2.bone((206, by - 28), (224, by - 6), 5.5)
    paint(cv, leg2, base=_dk(IVORY, 0.72), outline_w=2.6)
    tail = Layer(W, H)
    tail.tapered([(140, by - 150), (80, by - 110), (40, by - 120), (14, by - 180)], 24, 5)
    paint(cv, tail, base=(206, 160, 136), shadow=(130, 84, 64), outline_w=3)
    spade = Layer(W, H)
    spade.poly([(14, by - 178), (-6, by - 196), (8, by - 222), (26, by - 200)])
    paint(cv, spade, base=(170, 60, 40), shadow=(100, 30, 20), light=(230, 120, 80), outline_w=2.6)
    body = Layer(W, H)
    blob(body, [(130, by - 150), (170, by - 196), (236, by - 206), (250, by - 160), (210, by - 120), (150, by - 126)])
    paint(cv, body, base=(170, 64, 42), shadow=(100, 30, 20), light=(230, 120, 80), outline_w=3)
    ribs = Layer(W, H)
    for i in range(4):
        x = 176 + i * 18
        ribs.curve([(x, by - 196), (x + 14, by - 170), (x + 2, by - 134)], 7)
    paint(cv, ribs, outline_w=2.4)
    sp = Layer(W, H)
    sp.curve([(130, by - 152), (190, by - 204), (250, by - 196)], 9)
    paint(cv, sp, outline_w=2.6)
    leg = Layer(W, H)
    leg.bone((176, by - 146), (206, by - 90), 10)
    leg.bone((206, by - 86), (186, by - 32), 8)
    leg.bone((186, by - 30), (204, by - 8), 6)
    paint(cv, leg, outline_w=2.8)
    claws = Layer(W, H)
    for fx, k in ((204, 1.0), (224, 0.8)):
        for d in (0, 12, 24):
            claws.tapered([(fx - 6, by - 8), (fx + d, by - 4), (fx + d + 6, by + 2)], 6 * k, 1.5)
    paint(cv, claws, base=IVORY_LIGHT, outline_w=1.6, grain=False)
    neck = Layer(W, H)
    neck.tapered([(236, by - 196), (276, by - 240), (284, by - 270)], 22, 15)
    paint(cv, neck, base=(206, 160, 136), shadow=(130, 84, 64), outline_w=2.8)
    mem_wing(cv, W, H, (200, by - 196), (130, by - 312), [(40, by - 318), (10, by - 250), (36, by - 186), (92, by - 158)], mem, k=0.95, dim=1.0)
    horns = [(-0.6, -0.55, -0.8, -0.6), (-0.2, -0.75, -0.45, -0.75)]
    draw_skull(cv, W, H, 300, by - 286, 38, snout=0.75, horns=horns, eye_color=fc["aura"])
    ember(cv, W, H, [(352, by - 252, 4), (364, by - 270, 3), (100, by - 110, 3), (250, by - 330, 3), (60, by - 220, 2.5)], fc["aura"])


def m_bone_minotaur(cv, W, H, fc):
    by = H - 12
    cx = 170
    # braço de trás
    arm2 = Layer(W, H)
    arm2.bone((cx - 74, by - 300), (cx - 96, by - 210), 12)
    arm2.bone((cx - 96, by - 206), (cx - 90, by - 140), 10)
    paint(cv, arm2, base=_dk(IVORY, 0.75), outline_w=2.8)
    fist2 = Layer(W, H)
    fist2.ellipse(cx - 90, by - 126, 16, 18)
    paint(cv, fist2, base=_dk(IVORY, 0.75), outline_w=2.4)
    legs = Layer(W, H)
    for lx, d in ((cx - 30, -6), (cx + 30, 6)):
        legs.bone((lx, by - 150), (lx + d, by - 84), 13)
        legs.bone((lx + d, by - 80), (lx, by - 28), 11)
    paint(cv, legs, outline_w=3)
    hoof = Layer(W, H)
    for lx in (cx - 30, cx + 30):
        hoof.rrect(lx - 18, by - 30, lx + 18, by, 6)
    paint(cv, hoof, base=(66, 46, 38), shadow=(36, 24, 20), light=(120, 90, 70), outline_w=2.6, grain=False)
    split = Layer(W, H)
    for lx in (cx - 30, cx + 30):
        split.line([(lx + 2, by - 20), (lx + 2, by)], 2.4)
    fill(cv, split, (24, 16, 14))
    pel = Layer(W, H)
    pel.ellipse(cx, by - 158, 52, 22)
    paint(cv, pel, outline_w=3)
    fur(cv, W, H, cx - 20, by - 150, 14, 40, (110, 74, 44), 13, angle=90, spread=30)
    fur(cv, W, H, cx + 20, by - 150, 14, 40, (100, 66, 40), 23, angle=90, spread=30)
    spine = Layer(W, H)
    spine.capsule((cx, by - 160), (cx, by - 320), 10)
    paint(cv, spine, outline_w=2.6)
    paint(cv, rib_mask(W, H, cx, by - 330, 5, 96, 30, 14), outline_w=3)
    shoulders = Layer(W, H)
    shoulders.capsule((cx - 80, by - 306), (cx + 80, by - 306), 13)
    paint(cv, shoulders, outline_w=3)
    fur(cv, W, H, cx - 4, by - 330, 18, 30, (96, 62, 36), 14, angle=-90, spread=80)
    # machado de osso
    axe = Layer(W, H)
    axe.capsule((cx + 144, by - 356), (cx + 136, by - 20), 7)
    paint(cv, axe, base=(120, 84, 50), shadow=(70, 46, 24), light=(170, 130, 90), outline_w=2.6)
    blade = Layer(W, H)
    blob(blade, [(cx + 142, by - 360), (cx + 186, by - 400), (cx + 202, by - 340), (cx + 188, by - 290), (cx + 142, by - 316)], 2)
    blob(blade, [(cx + 142, by - 360), (cx + 112, by - 380), (cx + 106, by - 340), (cx + 112, by - 304), (cx + 142, by - 316)], 2)
    paint(cv, blade, base=IVORY_LIGHT, outline_w=3)
    arm = Layer(W, H)
    arm.bone((cx + 78, by - 300), (cx + 118, by - 232), 12)
    arm.bone((cx + 118, by - 228), (cx + 138, by - 182), 10)
    paint(cv, arm, outline_w=3)
    fist = Layer(W, H)
    fist.ellipse(cx + 140, by - 174, 17, 19)
    paint(cv, fist, outline_w=2.6)
    # chifres e crânio de touro
    horns = Layer(W, H)
    horns.tapered([(cx - 14, by - 400), (cx - 96, by - 404), (cx - 126, by - 456), (cx - 104, by - 494)], 28, 5)
    horns.tapered([(cx + 30, by - 408), (cx + 110, by - 420), (cx + 140, by - 468), (cx + 126, by - 504)], 28, 5)
    paint(cv, horns, base=(226, 206, 166), shadow=(150, 124, 90), outline_w=3)
    tips = Layer(W, H)
    tips.tapered([(cx - 124, by - 462), (cx - 104, by - 494)], 11, 3)
    tips.tapered([(cx + 138, by - 474), (cx + 126, by - 504)], 11, 3)
    fill(cv, tips, (70, 52, 40))
    draw_skull(cv, W, H, cx + 10, by - 372, 58, snout=0.5, jaw=1.1, eye_color=fc["aura"])
    ring = Layer(W, H)
    ring.ellipse(cx + 92, by - 334, 12, 14)
    hole = Layer(W, H)
    hole.ellipse(cx + 92, by - 334, 7, 9)
    ring.cut(hole)
    paint(cv, ring, base=(250, 200, 70), shadow=(170, 120, 30), outline_w=1.8, grain=False)


def m_obsidian_sentinel(cv, W, H, fc):
    by = H - 10
    cx = 150
    obs = dict(base=(52, 50, 70), shadow=(18, 16, 28), light=(130, 130, 176))
    aura = fc["aura"]
    # perna e braço de trás
    back = Layer(W, H)
    back.rrect(cx - 54, by - 260, cx - 26, by - 180, 10)
    paint(cv, back, outline_w=3, base=(40, 38, 54), shadow=(14, 12, 22), light=(100, 100, 140))
    legs = Layer(W, H)
    for lx in (cx - 34, cx + 22):
        legs.poly([(lx - 18, by - 150), (lx + 18, by - 150), (lx + 14, by - 100), (lx - 14, by - 100)])
        legs.poly([(lx - 16, by - 84), (lx + 16, by - 84), (lx + 20, by - 26), (lx - 18, by - 26)])
        legs.poly([(lx - 22, by - 30), (lx + 34, by - 22), (lx + 36, by), (lx - 22, by)])
    paint(cv, legs, outline_w=3, **obs)
    knees = Layer(W, H)
    for lx in (cx - 34, cx + 22):
        knees.bone((lx, by - 104), (lx, by - 80), 6)
    paint(cv, knees, outline_w=2.4)
    accent_dots(cv, W, H, [(cx - 34, by - 92), (cx + 22, by - 92)], IVORY, 7)
    belt = Layer(W, H)
    belt.poly([(cx - 64, by - 166), (cx + 64, by - 166), (cx + 50, by - 140), (cx - 50, by - 140)])
    paint(cv, belt, outline_w=2.8, **obs)
    pelvis = Layer(W, H)
    pelvis.ellipse(cx, by - 152, 26, 12)
    paint(cv, pelvis, outline_w=2.2)
    chest = Layer(W, H)
    chest.poly([(cx - 70, by - 290), (cx + 70, by - 290), (cx + 58, by - 210), (cx + 30, by - 168), (cx - 30, by - 168), (cx - 58, by - 210)])
    paint(cv, chest, outline_w=3.4, **obs)
    facet = Layer(W, H)
    facet.poly([(cx - 60, by - 284), (cx - 10, by - 284), (cx - 40, by - 220)])
    fill(cv, facet, (150, 150, 196), alpha=90)
    cracks = Layer(W, H)
    cracks.line([(cx - 46, by - 270), (cx - 30, by - 238), (cx - 40, by - 206)], 2.6)
    cracks.line([(cx + 44, by - 276), (cx + 30, by - 250)], 2.6)
    glow(cv, cracks, aura, radius=4, strength=1.8)
    fill(cv, cracks, _lt(aura, 80))
    ribs = rib_mask(W, H, cx, by - 280, 3, 34, 20, 6)
    paint(cv, ribs, outline_w=2.2)
    core = Layer(W, H)
    core.poly([(cx, by - 252), (cx + 14, by - 228), (cx, by - 204), (cx - 14, by - 228)])
    glow(cv, core, aura, radius=14, strength=2.0)
    fill(cv, core, (210, 235, 255))
    # pauldrons com espinhos de obsidiana
    for sx, dim in ((-1, 0.8), (1, 1.0)):
        p = Layer(W, H)
        p.poly([(cx + sx * 40, by - 300), (cx + sx * 84, by - 312), (cx + sx * 108, by - 280), (cx + sx * 100, by - 262), (cx + sx * 44, by - 270)])
        paint(cv, p, outline_w=3, base=_dk(obs["base"], dim), shadow=obs["shadow"], light=_dk(obs["light"], dim))
        p2 = Layer(W, H)
        p2.poly([(cx + sx * 56, by - 274), (cx + sx * 104, by - 268), (cx + sx * 110, by - 246), (cx + sx * 60, by - 252)])
        paint(cv, p2, outline_w=2.6, base=_dk(obs["base"], dim * 0.9), shadow=obs["shadow"], light=_dk(obs["light"], dim))
        accent_dots(cv, W, H, [(cx + sx * 76, by - 292)], _dk(IVORY, dim), 5)
    elbow = Layer(W, H)
    elbow.bone((cx + 82, by - 266), (cx + 92, by - 214), 7)
    paint(cv, elbow, outline_w=2.4)
    gaunt = Layer(W, H)
    gaunt.poly([(cx + 76, by - 214), (cx + 108, by - 214), (cx + 112, by - 166), (cx + 80, by - 160)])
    gaunt.rrect(cx + 78, by - 170, cx + 116, by - 140, 8)
    paint(cv, gaunt, outline_w=3, **obs)
    # espada fincada
    blade = Layer(W, H)
    blade.poly([(cx + 88, by - 140), (cx + 106, by - 140), (cx + 104, by - 20), (cx + 97, by), (cx + 90, by - 20)])
    paint(cv, blade, outline_w=2.8, base=(60, 60, 84), shadow=(20, 20, 34), light=(150, 160, 210))
    edge = Layer(W, H)
    edge.line([(cx + 102, by - 134), (cx + 101, by - 24)], 2)
    glow(cv, edge, aura, radius=4, strength=1.6)
    fill(cv, edge, _lt(aura, 80))
    guard = Layer(W, H)
    guard.bone((cx + 72, by - 146), (cx + 124, by - 146), 5)
    paint(cv, guard, outline_w=2.2)
    pommel = Layer(W, H)
    pommel.rrect(cx + 104, by - 170, cx + 120, by - 146, 4)
    paint(cv, pommel, outline_w=2, **obs)
    # elmo
    helm = Layer(W, H)
    helm.poly([(cx - 40, by - 300), (cx - 44, by - 352), (cx - 20, by - 384), (cx + 30, by - 384), (cx + 48, by - 352), (cx + 44, by - 300)])
    shard(helm, cx - 30, by - 370, -120, 46, 16)
    shard(helm, cx + 20, by - 380, -84, 36, 14)
    paint(cv, helm, outline_w=3.2, **obs)
    jaw = Layer(W, H)
    jaw.rrect(cx - 12, by - 316, cx + 40, by - 298, 4)
    paint(cv, jaw, outline_w=2)
    teeth = Layer(W, H)
    for i in range(5):
        teeth.rrect(cx - 6 + i * 10, by - 314, cx - 4 + i * 10, by - 302, 1)
    fill(cv, teeth, (40, 30, 30))
    slit = Layer(W, H)
    slit.rrect(cx - 20, by - 348, cx + 44, by - 336, 4)
    fill(cv, slit, (10, 10, 20))
    eye_glow(cv, W, H, [(cx + 2, by - 342), (cx + 30, by - 342)], aura, 5)
    runes(cv, W, H, cx, by - 152, 7, aura)


def m_royal_hornet(cv, W, H, fc):
    cx, cy = W / 2 + 10, H / 2 - 20
    amber = (240, 172, 44)
    for k, dim in ((0, 0.75), (1, 1.0)):
        w = Layer(W, H)
        ox = -14 if k == 0 else 4
        blob(w, [(cx + ox, cy - 20), (cx + ox - 40, cy - 110), (cx + ox - 90, cy - 120), (cx + ox - 70, cy - 60)])
        fill(cv, w, (255, 236, 170), alpha=int(120 * dim))
        rim = w.copy()
        inn = Layer(W, H)
        blob(inn, [(cx + ox - 2, cy - 24), (cx + ox - 41, cy - 106), (cx + ox - 86, cy - 116), (cx + ox - 67, cy - 62)])
        rim.cut(inn)
        fill(cv, rim, (90, 60, 30))
        v = Layer(W, H)
        v.curve([(cx + ox - 4, cy - 26), (cx + ox - 40, cy - 80), (cx + ox - 82, cy - 112)], 2)
        fill(cv, v, (150, 110, 50), alpha=200)
    # abdômen curvado com listras
    path = bezier([(cx - 30, cy + 10), (cx - 96, cy + 30), (cx - 80, cy + 100), (cx - 20, cy + 104)], 6)
    for i in range(len(path) - 1, -1, -1):
        x, y = path[i]
        seg = Layer(W, H)
        seg.circle(x, y, 32 - i * 3.2)
        col = amber if i % 2 == 0 else (60, 40, 24)
        paint(cv, seg, base=col, shadow=_dk(col, 0.55), light=_lt(col, 50), outline_w=2.8)
    st = Layer(W, H)
    st.tapered([path[-1], (path[-1][0] + 28, path[-1][1] + 4), (path[-1][0] + 44, path[-1][1] - 6)], 12, 1)
    paint(cv, st, base=IVORY_LIGHT, outline_w=2)
    accent_dots(cv, W, H, [(path[-1][0] + 45, path[-1][1] - 7)], fc["aura"], 3, glow_r=5)
    legs = Layer(W, H)
    for i in range(3):
        legs.tapered([(cx - 4 + i * 14, cy + 20), (cx + 6 + i * 14, cy + 54), (cx - 4 + i * 16, cy + 82)], 6, 2)
    paint(cv, legs, base=(70, 50, 34), outline_w=2)
    th = Layer(W, H)
    th.ellipse(cx + 4, cy, 36, 32)
    paint(cv, th, base=(70, 50, 34), shadow=(36, 24, 16), light=(140, 110, 70), outline_w=3)
    fur(cv, W, H, cx + 4, cy - 20, 12, 16, (200, 150, 60), 6, angle=-90, spread=70)
    ribs = rib_mask(W, H, cx + 4, cy - 26, 2, 22, 16, 5)
    paint(cv, ribs, outline_w=1.8)
    ant = Layer(W, H)
    ant.tapered([(cx + 50, cy - 46), (cx + 56, cy - 84), (cx + 80, cy - 96)], 3.5, 1.4)
    ant.tapered([(cx + 64, cy - 44), (cx + 78, cy - 76), (cx + 102, cy - 80)], 3.5, 1.4)
    fill(cv, ant, (60, 40, 24))
    draw_skull(cv, W, H, cx + 54, cy - 14, 30, snout=0.05, eye_color=fc["aura"])
    mand = Layer(W, H)
    mand.tapered([(cx + 76, cy + 12), (cx + 92, cy + 20), (cx + 84, cy + 30)], 7, 2)
    paint(cv, mand, base=(70, 50, 34), outline_w=1.6, grain=False)
    crown = Layer(W, H)
    x0, y0 = cx + 30, cy - 40
    crown.poly([(x0, y0), (x0 - 2, y0 - 24), (x0 + 10, y0 - 12), (x0 + 20, y0 - 30), (x0 + 30, y0 - 12), (x0 + 42, y0 - 24), (x0 + 40, y0)])
    paint(cv, crown, base=(250, 200, 70), shadow=(170, 120, 30), light=(255, 240, 160), outline_w=2.2)
    accent_dots(cv, W, H, [(x0 + 20, y0 - 8)], (220, 40, 60), 4)


# ----------------------------------------------------------------- chefes

def m_ghoul_matriarch(cv, W, H, fc):
    by = H - 12
    cx = 220
    cloak_c = (66, 44, 88)
    skin = (132, 128, 142)
    aura = fc["aura"]
    gl = Layer(W, H)
    gl.ellipse(cx, by - 220, 150, 200)
    glow(cv, gl, aura, radius=30, strength=0.35)
    # manto atrás
    cloak = Layer(W, H)
    pts = [(cx - 10, by - 400), (cx - 80, by - 380), (cx - 140, by - 280), (cx - 190, by - 120), (cx - 210, by - 10)]
    pts += jag((cx - 210, by - 10), (cx + 70, by - 10), 12, -40, seed=6)
    pts += [(cx + 70, by - 10), (cx + 50, by - 200), (cx + 60, by - 360)]
    cloak.poly(pts)
    paint(cv, cloak, base=cloak_c, shadow=_dk(cloak_c, 0.45), light=_lt(cloak_c, 50), outline_w=3.4)
    holes = Layer(W, H)
    for x, y, r in [(cx - 120, by - 200, 10), (cx - 60, by - 120, 7), (cx - 150, by - 90, 8)]:
        holes.circle(x, y, r)
    fill(cv, holes, _dk(cloak_c, 0.35))
    # braço de trás
    arm2 = Layer(W, H)
    arm2.bone((cx - 30, by - 330), (cx - 70, by - 240), 9)
    arm2.bone((cx - 70, by - 236), (cx - 74, by - 140), 8)
    paint(cv, arm2, base=_dk(IVORY, 0.72), outline_w=2.8)
    cl2 = Layer(W, H)
    for d in (-12, 0, 12):
        cl2.tapered([(cx - 74, by - 140), (cx - 74 + d, by - 104), (cx - 82 + d * 1.6, by - 80)], 7, 1)
    paint(cv, cl2, base=_dk(IVORY, 0.72), outline_w=1.8, grain=False)
    legs = Layer(W, H)
    legs.bone((cx - 20, by - 170), (cx - 4, by - 90), 11)
    legs.bone((cx - 4, by - 86), (cx - 28, by - 20), 10)
    legs.bone((cx + 20, by - 170), (cx + 44, by - 90), 11)
    legs.bone((cx + 44, by - 86), (cx + 30, by - 20), 10)
    paint(cv, legs, outline_w=3)
    feet = Layer(W, H)
    for fx in (cx - 28, cx + 30):
        for d in (0, 12, 24):
            feet.tapered([(fx, by - 18), (fx + d + 8, by - 4), (fx + d + 16, by + 2)], 8, 2)
    paint(cv, feet, outline_w=2, grain=False)
    # tronco magro com pele rasgada
    torso = Layer(W, H)
    pts = [(cx - 50, by - 350), (cx + 54, by - 350), (cx + 40, by - 220), (cx + 30, by - 170)]
    pts += jag((cx + 30, by - 170), (cx - 30, by - 170), 6, 22, seed=3)
    pts += [(cx - 30, by - 170), (cx - 40, by - 220)]
    torso.poly(pts)
    pc(cv, torso, skin, ow=3)
    paint(cv, rib_mask(W, H, cx, by - 346, 5, 54, 28, 10), outline_w=2.8)
    # colar de ossos
    col = Layer(W, H)
    for i in range(7):
        a = math.radians(200 + i * 22)
        x = cx + 10 + math.cos(a) * 70
        y = by - 356 - math.sin(a) * 26
        shard(col, x, y + 10, 90 + (i - 3) * 14, 30, 13)
    paint(cv, col, outline_w=2.4)
    # braço erguido com garras
    arm = Layer(W, H)
    arm.bone((cx + 50, by - 330), (cx + 130, by - 330), 10)
    arm.bone((cx + 130, by - 326), (cx + 168, by - 400), 9)
    paint(cv, arm, outline_w=3)
    cl = Layer(W, H)
    for k, a in enumerate((-130, -105, -80, -55)):
        ax = cx + 172 + math.cos(math.radians(a)) * 50
        ay = by - 404 + math.sin(math.radians(a)) * 50
        cl.tapered([(cx + 170, by - 404), ((cx + 170 + ax) / 2 + 6, (by - 404 + ay) / 2), (ax, ay)], 9, 1)
    paint(cv, cl, base=IVORY_LIGHT, outline_w=2)
    sleeve = Layer(W, H)
    sleeve.poly([(cx + 36, by - 352), (cx + 112, by - 344), (cx + 110, by - 322)] + jag((cx + 110, by - 322), (cx + 36, by - 290), 6, 24, seed=9) + [(cx + 36, by - 290)])
    paint(cv, sleeve, base=cloak_c, shadow=_dk(cloak_c, 0.45), light=_lt(cloak_c, 50), outline_w=2.8)
    draw_skull(cv, W, H, cx + 14, by - 404, 56, snout=0.25, jaw=1.3, eye_color=aura)
    # coroa de ossos
    crown = Layer(W, H)
    base_y = by - 448
    crown.rrect(cx - 34, base_y - 6, cx + 54, base_y + 10, 6)
    for i, hgt in enumerate((30, 44, 56, 44, 30)):
        x = cx - 26 + i * 19
        crown.tapered([(x, base_y), (x - 2, base_y - hgt * 0.6), (x + 2, base_y - hgt)], 12, 2)
    paint(cv, crown, outline_w=2.6)
    accent_dots(cv, W, H, [(cx + 12, base_y + 2)], aura, 6, glow_r=8)
    wisps(cv, W, H, [(cx - 170, by - 300, 5), (cx + 160, by - 250, 4), (cx + 100, by - 460, 4), (cx - 120, by - 420, 3.5), (cx + 200, by - 160, 3)], aura)


def m_frost_titan(cv, W, H, fc):
    by = H - 12
    cx = 240
    ice = dict(base=(166, 208, 234), shadow=(80, 124, 166), light=(236, 250, 255))
    aura = fc["aura"]
    # braço de trás
    a2 = Layer(W, H)
    a2.bone((cx - 120, by - 340), (cx - 160, by - 230), 16)
    paint(cv, a2, base=_dk(IVORY, 0.72), outline_w=3)
    g2 = Layer(W, H)
    blob(g2, [(cx - 200, by - 240), (cx - 130, by - 246), (cx - 120, by - 120), (cx - 150, by - 70), (cx - 210, by - 80), (cx - 214, by - 160)], 2)
    paint(cv, g2, outline_w=3.2, base=_dk(ice["base"], 0.78), shadow=_dk(ice["shadow"], 0.8), light=_dk(ice["light"], 0.85))
    # pernas: fêmur de osso, botas de gelo
    legs = Layer(W, H)
    for lx in (cx - 66, cx + 66):
        legs.bone((lx, by - 200), (lx, by - 120), 16)
    paint(cv, legs, outline_w=3)
    boots = Layer(W, H)
    for lx in (cx - 66, cx + 66):
        blob(boots, [(lx - 44, by - 130), (lx + 40, by - 136), (lx + 54, by - 40), (lx + 60, by), (lx - 60, by), (lx - 50, by - 50)], 2)
    paint(cv, boots, outline_w=3.4, **ice)
    pel = Layer(W, H)
    pel.ellipse(cx, by - 200, 80, 26)
    paint(cv, pel, outline_w=3)
    # tronco de gelo com janela para as costelas
    body = Layer(W, H)
    blob(body, [(cx - 150, by - 380), (cx - 60, by - 420), (cx + 70, by - 420), (cx + 160, by - 376), (cx + 120, by - 260), (cx + 80, by - 200), (cx - 80, by - 200), (cx - 124, by - 260)], 2)
    paint(cv, body, outline_w=3.6, **ice)
    win = Layer(W, H)
    blob(win, [(cx - 80, by - 380), (cx + 80, by - 380), (cx + 70, by - 240), (cx - 70, by - 240)], 2)
    fill(cv, win, (40, 60, 90))
    core = Layer(W, H)
    core.circle(cx, by - 300, 30)
    glow(cv, core, aura, radius=22, strength=2.0)
    fill(cv, core, (210, 236, 255))
    paint(cv, rib_mask(W, H, cx, by - 384, 4, 76, 34, 13), outline_w=3)
    facet = Layer(W, H)
    facet.poly([(cx - 140, by - 372), (cx - 96, by - 396), (cx - 104, by - 300)])
    facet.poly([(cx + 150, by - 370), (cx + 104, by - 396), (cx + 110, by - 300)])
    fill(cv, facet, (255, 255, 255), alpha=90)
    # ombro de gelo com cristais
    crys = Layer(W, H)
    for x, y, a, ln, wd in [(cx - 140, by - 390, -120, 80, 26), (cx - 110, by - 410, -96, 96, 30), (cx - 170, by - 370, -150, 60, 22),
                            (cx + 130, by - 400, -70, 90, 28), (cx + 160, by - 380, -40, 70, 24), (cx + 100, by - 414, -90, 60, 22)]:
        shard(crys, x, y, a, ln, wd)
    glow(cv, crys, (160, 220, 255), radius=10, strength=1.2)
    paint(cv, crys, base=(200, 236, 255), shadow=(100, 150, 210), light=(255, 255, 255), outline_w=2.8, grain=False)
    # braço da frente
    a1 = Layer(W, H)
    a1.bone((cx + 130, by - 340), (cx + 170, by - 236), 17)
    paint(cv, a1, outline_w=3)
    g1 = Layer(W, H)
    blob(g1, [(cx + 120, by - 250), (cx + 214, by - 256), (cx + 224, by - 150), (cx + 214, by - 60), (cx + 120, by - 64), (cx + 116, by - 160)], 2)
    paint(cv, g1, outline_w=3.4, **ice)
    knuck = Layer(W, H)
    for i in range(4):
        knuck.rrect(cx + 124 + i * 23, by - 92, cx + 144 + i * 23, by - 60, 7)
    paint(cv, knuck, outline_w=2.2)
    icic = Layer(W, H)
    for x in (cx - 190, cx - 160, cx + 140, cx + 180, cx - 40, cx + 40):
        y = by - 200 if abs(x - cx) < 60 else (by - 80 if x > cx else by - 82)
        ln = 22 if abs(x - cx) < 60 else 18
        icic.poly([(x - 6, y - 2), (x, y + ln), (x + 6, y - 2)])
    paint(cv, icic, base=(210, 240, 255), shadow=(120, 170, 210), outline_w=1.8, grain=False)
    runes(cv, W, H, cx + 170, by - 160, 14, aura)
    draw_skull(cv, W, H, cx + 10, by - 446, 56, snout=0.2, eye_color=aura, base=(226, 230, 232))
    crown = Layer(W, H)
    for x, a, ln in [(cx - 30, -110, 50), (cx, -94, 64), (cx + 30, -78, 50)]:
        shard(crown, x, by - 488, a, ln, 18)
    glow(cv, crown, (160, 220, 255), radius=8, strength=1.2)
    paint(cv, crown, base=(200, 236, 255), shadow=(100, 150, 210), light=(255, 255, 255), outline_w=2.4, grain=False)
    snow = Layer(W, H)
    for x, y in [(cx - 220, by - 420), (cx + 220, by - 440), (cx - 200, by - 300), (cx + 240, by - 300), (cx + 60, by - 520), (cx - 90, by - 500)]:
        snow.circle(x, y, 4)
    glow(cv, snow, (170, 220, 255), radius=5, strength=1.8)
    fill(cv, snow, (255, 255, 255))


def m_magma_wyrm(cv, W, H, fc):
    by = H - 12
    rock = (62, 38, 34)
    lava = (255, 120, 30)
    aura = fc["aura"]
    pool = Layer(W, H)
    pool.ellipse(260, by - 10, 230, 22)
    glow(cv, pool, lava, radius=16, strength=1.2)
    paint(cv, pool, base=(255, 140, 40), shadow=(200, 60, 20), light=(255, 230, 140), outline_w=3, grain=False)
    crust = Layer(W, H)
    for x, w in ((120, 36), (240, 30), (360, 40), (60, 20), (430, 22)):
        crust.ellipse(x, by - 10, w, 7)
    paint(cv, crust, base=(70, 40, 34), shadow=(30, 16, 14), outline_w=1.8, grain=False)
    segs = [[(10, by - 40), (100, by + 6), (250, by + 4), (330, by - 40)],
            [(330, by - 40), (420, by - 90), (430, by - 220), (330, by - 236)],
            [(330, by - 236), (220, by - 250), (200, by - 360), (300, by - 390)],
            [(300, by - 390), (340, by - 400), (370, by - 396), (390, by - 392)]]
    path = []
    for k, sg in enumerate(segs):
        pts = bezier(sg, (20, 18, 18, 6)[k])
        path += pts if not path else pts[1:]
    nrm = normals(path)
    n = len(path)

    def rad(i):
        t = i / (n - 1)
        return 8 + 40 * math.sin(min(1.0, t * 1.6) * math.pi * 0.5) - 10 * max(0, t - 0.7) / 0.3

    # espinhos nas costas
    sp = Layer(W, H)
    for i in range(4, n - 4, 3):
        (x, y), (nx, ny) = path[i], nrm[i]
        r = rad(i)
        if ny > 0:
            nx, ny = -nx, -ny
        b1 = (x + nx * r * 0.7 - ny * 7, y + ny * r * 0.7 + nx * 7)
        b2 = (x + nx * r * 0.7 + ny * 7, y + ny * r * 0.7 - nx * 7)
        tp = (x + nx * (r + 16 + r * 0.3), y + ny * (r + 16 + r * 0.3))
        sp.poly([b1, tp, b2])
    paint(cv, sp, outline_w=2.4)
    body = Layer(W, H)
    for i, (x, y) in enumerate(path):
        body.circle(x, y, rad(i))
    glow(cv, body, lava, radius=12, strength=0.8)
    paint(cv, body, base=rock, shadow=_dk(rock, 0.5), light=_lt(rock, 40), outline_w=3.4)
    cr = Layer(W, H)
    for i in range(2, n - 2, 4):
        (x, y), (nx, ny) = path[i], nrm[i]
        r = rad(i) * 0.82
        cr.line([(x + nx * r, y + ny * r), (x + nx * r * 0.2 + ny * 4, y + ny * r * 0.2 - nx * 4), (x - nx * r, y - ny * r)], 4)
    glow(cv, cr, lava, radius=6, strength=2.0)
    fill(cv, cr, (255, 210, 110))
    vb = Layer(W, H)
    for i in range(4, n - 3, 4):
        (x, y), (nx, ny) = path[i], nrm[i]
        r = rad(i) * 0.95
        if ny > 0:
            nx, ny = -nx, -ny
        vb.circle(x + nx * r * 0.55, y + ny * r * 0.55, r * 0.34)
    paint(cv, vb, outline_w=2.4)
    horns = [(-0.7, -0.4, -1.2, -0.5), (-0.4, -0.75, -0.9, -0.9), (-0.05, -0.85, -0.4, -1.0)]
    cx, cy, r = 440, by - 390, 58
    draw_skull(cv, W, H, cx, cy, r, snout=0.9, horns=horns, crest=True, jaw=1.3, eye_color=aura, base=(226, 206, 190))
    fire = Layer(W, H)
    fire.poly([(cx + r * 1.3, cy + r * 0.72), (cx + r * 2.2, cy + r * 0.4), (cx + r * 2.0, cy + r * 0.8), (cx + r * 2.35, cy + r * 1.1), (cx + r * 1.3, cy + r * 0.95)])
    glow(cv, fire, lava, radius=10, strength=2.0)
    fill(cv, fire, (255, 200, 90), alpha=230)
    ember(cv, W, H, [(100, by - 120, 5), (200, by - 160, 4), (480, by - 220, 5), (340, by - 470, 4), (60, by - 80, 3), (160, by - 260, 3)], aura)


def m_swamp_behemoth(cv, W, H, fc):
    by = H - 12
    moss = (82, 116, 58)
    shell_c = (64, 74, 52)
    flesh = (88, 104, 96)
    aura = fc["aura"]
    far = Layer(W, H)
    for lx in (120, 330):
        far.rrect(lx - 30, by - 120, lx + 30, by - 10, 18)
    paint(cv, far, base=_dk(flesh, 0.7), shadow=_dk(flesh, 0.35), light=_dk(flesh, 1.0), outline_w=3)
    tail = Layer(W, H)
    tail.tapered([(70, by - 110), (30, by - 90), (14, by - 60)], 30, 6)
    paint(cv, tail, base=flesh, shadow=_dk(flesh, 0.5), light=_lt(flesh, 40), outline_w=3)
    neck = Layer(W, H)
    neck.tapered([(360, by - 150), (400, by - 180), (420, by - 200)], 70, 60)
    paint(cv, neck, base=flesh, shadow=_dk(flesh, 0.5), light=_lt(flesh, 40), outline_w=3.2)
    shell = Layer(W, H)
    blob(shell, [(40, by - 110), (80, by - 260), (210, by - 330), (340, by - 290), (400, by - 170), (380, by - 110), (220, by - 90)], 2)
    paint(cv, shell, base=shell_c, shadow=_dk(shell_c, 0.45), light=_lt(shell_c, 40), outline_w=3.6)
    rim = Layer(W, H)
    rim.curve([(40, by - 116), (200, by - 86), (390, by - 118)], 26)
    paint(cv, rim, outline_w=3)
    notches = Layer(W, H)
    for i in range(9):
        t = (i + 0.5) / 9
        p = bezier([(40, by - 116), (200, by - 86), (390, by - 118)], 9)[i]
        notches.line([(p[0], p[1] - 10), (p[0], p[1] + 10)], 2.4)
    fill(cv, notches, (150, 130, 100))
    plates = Layer(W, H)
    for x, y, r in [(210, by - 250, 38), (130, by - 210, 32), (290, by - 215, 32), (80, by - 150, 22), (210, by - 160, 30), (350, by - 160, 24), (150, by - 290, 20), (270, by - 290, 20)]:
        pts = [(x + math.cos(math.radians(30 + 60 * k)) * r, y + math.sin(math.radians(30 + 60 * k)) * r * 0.8) for k in range(6)]
        plates.poly(pts)
    paint(cv, plates, base=(214, 206, 172), shadow=(140, 130, 100), outline_w=2.6)
    spikes = Layer(W, H)
    for x, y, a in [(150, by - 300, -110), (210, by - 330, -90), (270, by - 310, -70), (100, by - 260, -130), (320, by - 270, -50)]:
        shard(spikes, x, y + 8, a, 36, 18)
    paint(cv, spikes, outline_w=2.6)
    # musgo pendurado e por cima
    for x, y, s in [(100, by - 270, 1), (180, by - 326, 2), (300, by - 300, 3), (60, by - 200, 4)]:
        mb = Layer(W, H)
        mb.ellipse(x, y, 26, 10)
        pc(cv, mb, moss, ow=2.2)
    for x, s in [(70, 5), (150, 6), (250, 7), (340, 8)]:
        fur(cv, W, H, x, by - 100, 6, 28, moss, s, angle=90, spread=20)
    accent_dots(cv, W, H, [(110, by - 190), (250, by - 196), (330, by - 230), (170, by - 150)], aura, 4.5, glow_r=6)
    legs = Layer(W, H)
    for lx in (90, 300):
        legs.rrect(lx - 34, by - 110, lx + 34, by - 6, 20)
    paint(cv, legs, base=flesh, shadow=_dk(flesh, 0.5), light=_lt(flesh, 40), outline_w=3.2)
    toes = Layer(W, H)
    for lx in (90, 300):
        for d in (-20, 0, 20):
            toes.ellipse(lx + d, by - 6, 10, 8)
    paint(cv, toes, outline_w=2, grain=False)
    knee = Layer(W, H)
    for lx in (90, 300):
        knee.ellipse(lx, by - 80, 12, 8)
    paint(cv, knee, outline_w=2.4)
    cx, cy, r = 430, by - 220, 66
    draw_skull(cv, W, H, cx, cy, r, snout=0.55, jaw=1.4, eye_color=aura)
    tusks = Layer(W, H)
    tusks.tapered([(cx + r * 1.15, cy + r * 0.95), (cx + r * 1.4, cy + r * 0.6), (cx + r * 1.42, cy + r * 0.2)], 16, 3)
    tusks.tapered([(cx + r * 0.75, cy + r * 0.98), (cx + r * 0.9, cy + r * 0.7), (cx + r * 0.88, cy + r * 0.45)], 11, 2.5)
    paint(cv, tusks, base=IVORY_LIGHT, outline_w=2.6)
    weed = Layer(W, H)
    weed.tapered([(cx + r * 0.6, cy + r * 1.0), (cx + r * 0.65, cy + r * 1.4)], 7, 2)
    pc(cv, weed, moss, ow=1.8, grain=False)
    water = Layer(W, H)
    water.ellipse(230, by, 230, 12)
    fill(cv, water, (60, 110, 100), alpha=170)
    ripple = Layer(W, H)
    ripple.ellipse(230, by - 1, 200, 8)
    ri = Layer(W, H)
    ri.ellipse(230, by, 194, 6)
    ripple.cut(ri)
    fill(cv, ripple, (150, 220, 210), alpha=170)


def m_bell_lich(cv, W, H, fc):
    by = H - 12
    cx = 230
    robe_c = (70, 44, 96)
    gold = dict(base=(232, 188, 80), shadow=(150, 110, 30), light=(255, 236, 160))
    aura = fc["aura"]
    collar = Layer(W, H)
    collar.poly([(cx - 70, by - 360), (cx - 96, by - 470), (cx - 20, by - 400), (cx + 40, by - 404), (cx + 100, by - 470), (cx + 80, by - 360)])
    paint(cv, collar, base=_dk(robe_c, 0.8), shadow=_dk(robe_c, 0.4), light=_lt(robe_c, 40), outline_w=3)
    robe = Layer(W, H)
    pts = [(cx - 70, by - 370), (cx + 80, by - 370), (cx + 120, by - 200), (cx + 140, by - 10)]
    pts += jag((cx + 140, by - 10), (cx - 140, by - 10), 12, 16, seed=11)
    pts += [(cx - 140, by - 10), (cx - 110, by - 200)]
    robe.poly(pts)
    paint(cv, robe, base=robe_c, shadow=_dk(robe_c, 0.45), light=_lt(robe_c, 50), outline_w=3.4)
    hem = Layer(W, H)
    hem.rrect(cx - 136, by - 44, cx + 136, by - 30, 5)
    hem.rrect(cx - 6, by - 300, cx + 16, by - 30, 5)
    paint(cv, hem, outline_w=2.4, **gold)
    opening = Layer(W, H)
    opening.poly([(cx - 48, by - 368), (cx + 60, by - 368), (cx + 6, by - 270)])
    fill(cv, opening, (24, 14, 34))
    paint(cv, rib_mask(W, H, cx + 6, by - 372, 3, 38, 22, 7), outline_w=2.4)
    for sx in (-1, 1):
        pd = Layer(W, H)
        pd.ellipse(cx + 6 + sx * 80, by - 360, 40, 26)
        paint(cv, pd, outline_w=3)
        sp = Layer(W, H)
        shard(sp, cx + 6 + sx * 90, by - 372, -90 + sx * 36, 40, 14)
        paint(cv, sp, outline_w=2.2)
    # sino enorme na mão esquerda
    sleeve2 = Layer(W, H)
    sleeve2.poly([(cx - 86, by - 340), (cx - 150, by - 280), (cx - 140, by - 250), (cx - 96, by - 280)])
    paint(cv, sleeve2, base=robe_c, shadow=_dk(robe_c, 0.45), light=_lt(robe_c, 50), outline_w=2.8)
    hand2 = Layer(W, H)
    hand2.bone((cx - 148, by - 266), (cx - 166, by - 244), 6)
    paint(cv, hand2, outline_w=2.2)
    bx, btop = cx - 170, by - 236
    chain = Layer(W, H)
    for i in range(3):
        chain.ellipse(bx, btop + 6 + i * 13, 5, 8)
    hole = Layer(W, H)
    for i in range(3):
        hole.ellipse(bx, btop + 6 + i * 13, 2.2, 5)
    chain.cut(hole)
    paint(cv, chain, outline_w=1.6, grain=False, base=(150, 150, 160), shadow=(80, 80, 90))
    bell = Layer(W, H)
    blob(bell, [(bx - 34, btop + 40), (bx + 34, btop + 40), (bx + 42, btop + 110), (bx + 70, btop + 196), (bx - 70, btop + 196), (bx - 42, btop + 110)], 2)
    glow(cv, bell, aura, radius=14, strength=0.7)
    paint(cv, bell, base=(186, 136, 64), shadow=(100, 66, 26), light=(250, 214, 140), outline_w=3.4)
    blip = Layer(W, H)
    blip.ellipse(bx, btop + 194, 72, 13)
    paint(cv, blip, base=(160, 112, 46), shadow=(90, 60, 20), outline_w=2.8, grain=False)
    band = Layer(W, H)
    band.rrect(bx - 46, btop + 120, bx + 46, btop + 132, 4)
    paint(cv, band, outline_w=2, grain=False, **gold)
    draw_skull(cv, W, H, bx - 4, btop + 80, 20, snout=0.0, eye_color=aura)
    runes(cv, W, H, bx - 32, btop + 160, 8, aura)
    runes(cv, W, H, bx + 32, btop + 160, 8, aura)
    # chamas roxas
    fl = Layer(W, H)
    for x, y, s in [(bx - 60, btop + 196, 1.0), (bx + 62, btop + 196, 0.9), (cx + 6, by - 470, 1.5), (cx - 30, by - 456, 1.0), (cx + 44, by - 458, 1.1)]:
        fl.tapered([(x, y), (x - 8 * s, y - 20 * s), (x + 4 * s, y - 44 * s)], 18 * s, 1)
    glow(cv, fl, aura, radius=10, strength=2.0)
    fill(cv, fl, _lt(aura, 60))
    draw_skull(cv, W, H, cx + 14, by - 420, 50, snout=0.15, jaw=1.0, eye_color=aura)
    # cajado
    staff = Layer(W, H)
    staff.capsule((cx + 150, by - 470), (cx + 140, by - 6), 7)
    paint(cv, staff, outline_w=2.8)
    knots = Layer(W, H)
    for y in (by - 380, by - 260, by - 140):
        knots.ellipse(cx + 146 - (by - y) * -0.02, y, 11, 7)
    paint(cv, knots, outline_w=2.2)
    head = Layer(W, H)
    head.curve([(cx + 150, by - 470), (cx + 120, by - 510), (cx + 150, by - 540), (cx + 186, by - 510)], 9)
    paint(cv, head, outline_w=2.6)
    orb = Layer(W, H)
    orb.circle(cx + 152, by - 506, 14)
    glow(cv, orb, aura, radius=18, strength=2.4)
    fill(cv, orb, _lt(aura, 90))
    sleeve = Layer(W, H)
    sleeve.poly([(cx + 70, by - 350), (cx + 130, by - 300), (cx + 128, by - 266), (cx + 76, by - 296)])
    paint(cv, sleeve, base=robe_c, shadow=_dk(robe_c, 0.45), light=_lt(robe_c, 50), outline_w=2.8)
    hand = Layer(W, H)
    for d in (0, 10, 20):
        hand.capsule((cx + 128, by - 290 + d), (cx + 156, by - 292 + d), 4.5)
    paint(cv, hand, outline_w=2)
    wisps(cv, W, H, [(cx - 60, by - 120, 4), (cx + 100, by - 160, 4), (cx - 230, by - 300, 3.5), (cx + 200, by - 420, 3)], aura)


def m_obsidian_dragon(cv, W, H, fc):
    by = H - 12
    obs_bone = dict(base=(78, 72, 92), shadow=(30, 26, 40), light=(160, 150, 186))
    mem_c = (54, 30, 44)
    red = (255, 60, 40)
    aura = fc["aura"]

    def wing(root, elbow, tips, dim):
        poly = [root, elbow]
        for i, tp in enumerate(tips):
            poly.append(tp)
            if i < len(tips) - 1:
                nn = tips[i + 1]
                mx, my = (tp[0] + nn[0]) / 2, (tp[1] + nn[1]) / 2
                poly.append((mx + (elbow[0] - mx) * 0.3, my + (elbow[1] - my) * 0.3))
        mem = Layer(W, H)
        mem.poly(poly)
        c = _dk(mem_c, dim)
        paint(cv, mem, base=c, shadow=_dk(c, 0.5), light=_lt(c, 40), outline_w=3)
        veins = Layer(W, H)
        for tp in tips[:-1]:
            veins.line([(elbow[0] * 0.4 + tp[0] * 0.6, elbow[1] * 0.4 + tp[1] * 0.6), ((elbow[0] + root[0]) * 0.25 + tp[0] * 0.5, (elbow[1] + root[1]) * 0.25 + tp[1] * 0.5)], 2)
        glow(cv, veins, red, radius=3, strength=1.2 * dim)
        fill(cv, veins, _dk((255, 110, 80), 0.6 + 0.4 * dim), alpha=200)
        b = Layer(W, H)
        b.capsule(root, elbow, 11)
        for tp in tips:
            b.tapered([elbow, tp], 9, 3)
        paint(cv, b, outline_w=2.8, base=_dk(obs_bone["base"], 0.7 + 0.3 * dim), shadow=obs_bone["shadow"], light=_dk(obs_bone["light"], 0.7 + 0.3 * dim))
        cr = Layer(W, H)
        shard(cr, elbow[0], elbow[1], -90, 44, 20)
        shard(cr, elbow[0], elbow[1], -60, 30, 14)
        paint(cv, cr, base=_dk((96, 70, 130), dim), shadow=(36, 22, 56), light=(200, 170, 240), outline_w=2.4, grain=False)

    root = (230, by - 250)
    wing(root, (330, by - 400), [(440, by - 470), (500, by - 400), (510, by - 320), (440, by - 250)], 0.6)
    tail = bezier([(150, by - 120), (60, by - 80), (10, by - 160), (50, by - 260)], 18)
    tl = Layer(W, H)
    bead_path(tl, tail, 24, 7)
    paint(cv, tl, outline_w=3, **obs_bone)
    tc = Layer(W, H)
    for i, (x, y) in enumerate(tail[:-1:2]):
        shard(tc, x, y - 8, -100 - i * 8, 26 - i, 12)
    x, y = tail[-1]
    shard(tc, x, y, -70, 50, 22)
    paint(cv, tc, base=(96, 70, 130), shadow=(36, 22, 56), light=(200, 170, 240), outline_w=2.4, grain=False)
    far = Layer(W, H)
    for lx in (186, 330):
        far.bone((lx, by - 150), (lx + 26, by - 80), 15)
        far.bone((lx + 26, by - 76), (lx + 10, by - 12), 13)
    paint(cv, far, outline_w=3, base=_dk(obs_bone["base"], 0.7), shadow=obs_bone["shadow"], light=_dk(obs_bone["light"], 0.7))
    body = Layer(W, H)
    body.ellipse(250, by - 160, 126, 66)
    paint(cv, body, base=(40, 30, 40), shadow=(16, 10, 18), light=(100, 70, 90), outline_w=3.4)
    cracks = Layer(W, H)
    cracks.line([(160, by - 170), (190, by - 130), (180, by - 104)], 4)
    cracks.line([(310, by - 120), (340, by - 150), (360, by - 140)], 4)
    cracks.line([(230, by - 108), (250, by - 120), (270, by - 100)], 3.5)
    glow(cv, cracks, red, radius=6, strength=2.0)
    fill(cv, cracks, (255, 170, 110))
    paint(cv, rib_mask(W, H, 250, by - 218, 4, 92, 24, 12), outline_w=3, **obs_bone)
    spine = Layer(W, H)
    for i in range(7):
        x = 150 + i * 32
        y = by - 218 - math.sin(i / 6 * math.pi) * 14
        shard(spine, x, y, -95 + (i - 3) * 6, 34 + (3 - abs(i - 3)) * 8, 16)
    glow(cv, spine, red, radius=8, strength=0.9)
    paint(cv, spine, base=(96, 70, 130), shadow=(36, 22, 56), light=(200, 170, 240), outline_w=2.6, grain=False)
    near = Layer(W, H)
    for lx in (160, 304):
        near.bone((lx, by - 140), (lx + 30, by - 74), 17)
        near.bone((lx + 30, by - 70), (lx + 12, by - 12), 14)
    paint(cv, near, outline_w=3, **obs_bone)
    claws = Layer(W, H)
    for lx in (172, 316):
        for d in (0, 14, 28):
            claws.tapered([(lx - 8, by - 10), (lx + d, by - 6), (lx + d + 8, by + 2)], 8, 2)
    paint(cv, claws, base=(200, 180, 220), shadow=(100, 80, 120), outline_w=1.8, grain=False)
    neck = bezier([(340, by - 190), (410, by - 230), (420, by - 300), (400, by - 330)], 12)
    nk = Layer(W, H)
    bead_path(nk, neck, 30, 22)
    paint(cv, nk, outline_w=3, **obs_bone)
    ncr = Layer(W, H)
    for (x, y), (nx, ny) in list(zip(neck, normals(neck)))[1:-1:3]:
        ncr.line([(x - nx * 12, y - ny * 12), (x + nx * 12, y + ny * 12)], 3)
    glow(cv, ncr, red, radius=4, strength=1.8)
    fill(cv, ncr, (255, 150, 100))
    wing((250, by - 236), (150, by - 400), [(20, by - 440), (-20, by - 360), (0, by - 270), (60, by - 200)], 1.0)
    horns = [(-0.65, -0.5, -1.1, -0.9), (-0.3, -0.75, -0.7, -1.2)]
    draw_skull(cv, W, H, 420, by - 360, 60, snout=0.85, horns=horns, crest=True, jaw=1.1, eye_color=red, base=(108, 100, 124))
    hc = Layer(W, H)
    shard(hc, 380, by - 420, -120, 40, 16)
    shard(hc, 404, by - 424, -100, 30, 12)
    paint(cv, hc, base=(96, 70, 130), shadow=(36, 22, 56), light=(200, 170, 240), outline_w=2.2, grain=False)
    ember(cv, W, H, [(500, by - 320, 5), (520, by - 300, 4), (120, by - 300, 4), (300, by - 460, 4), (40, by - 120, 3), (460, by - 200, 3)], red)


DRAW = {
    "monster_grave_hyena": m_grave_hyena,
    "monster_cave_eel": m_cave_eel,
    "monster_dusk_moth": m_dusk_moth,
    "monster_clockwork_spider": m_clockwork_spider,
    "monster_magma_salamander": m_magma_salamander,
    "monster_tomb_ghoul": m_tomb_ghoul,
    "monster_frost_mammoth": m_frost_mammoth,
    "monster_lantern_angler": m_lantern_angler,
    "monster_gargoyle": m_gargoyle,
    "monster_plague_locust": m_plague_locust,
    "monster_swamp_crocodile": m_swamp_crocodile,
    "monster_bell_wraith": m_bell_wraith,
    "monster_young_wyvern": m_young_wyvern,
    "monster_bone_minotaur": m_bone_minotaur,
    "monster_obsidian_sentinel": m_obsidian_sentinel,
    "monster_royal_hornet": m_royal_hornet,
    "boss_ghoul_matriarch": m_ghoul_matriarch,
    "boss_frost_titan": m_frost_titan,
    "boss_magma_wyrm": m_magma_wyrm,
    "boss_swamp_behemoth": m_swamp_behemoth,
    "boss_bell_lich": m_bell_lich,
    "boss_obsidian_dragon": m_obsidian_dragon,
}
