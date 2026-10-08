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
