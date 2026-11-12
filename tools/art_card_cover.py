#!/usr/bin/env python3
"""Capa do Cartão do Coveiro (topo da loja): cemitério à noite, lua cheia,
lápides, pá cravada na terra, lanternas fantasma verdes e névoa.
O Ossinho com a skin do Coveiro é desenhado por cima, no jogo (lado esquerdo).
Uso: python3 tools/art_card_cover.py  ->  art/ui/ui_card_cover.png
"""
import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from artlib import Layer, new_canvas, paint, fill, glow, finish  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "art", "ui", "ui_card_cover.png")
INK = (24, 16, 26)
W, H = 680, 300


def sky(c):
    w, h = c.size
    top, bot = (26, 14, 44), (40, 22, 58)
    px = Image.new("RGBA", (1, h))
    for y in range(h):
        t = y / (h - 1)
        px.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    c.alpha_composite(px.resize((w, h)))
    r = random.Random(7)
    d = ImageDraw.Draw(c)
    s = w // W
    for _ in range(90):
        x, y = r.randint(0, w), r.randint(0, int(h * 0.6))
        rad = r.choice([1, 1, 1, 2]) * s
        a = r.randint(120, 255)
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(255, 246, 220, a))


def moon(c):
    m = Layer(W, H)
    m.circle(560, 78, 46)
    glow(c, m, (255, 236, 190), radius=40, strength=0.9)
    paint(c, m, base=(250, 238, 206), shadow=(214, 196, 158), light=(255, 252, 238), outline=INK, outline_w=0, grain=False)
    for (x, y, r) in [(545, 66, 9), (575, 92, 7), (562, 58, 5)]:
        cr = Layer(W, H)
        cr.circle(x, y, r)
        fill(c, cr, (220, 200, 160), alpha=150)


def hills(c):
    far = Layer(W, H)
    far.poly([(0, 210), (120, 188), (260, 200), (400, 180), (540, 196), (680, 186), (680, 300), (0, 300)])
    fill(c, far, (44, 30, 62))
    near = Layer(W, H)
    near.poly([(0, 248), (150, 232), (330, 244), (500, 230), (680, 240), (680, 300), (0, 300)])
    fill(c, near, (28, 20, 38))


def tombstone(c, x, y, w, h, tilt=0):
    t = Layer(W, H)
    t.rrect(x, y, x + w, y + h, w // 2)
    paint(c, t, base=(108, 100, 120), shadow=(66, 60, 78), light=(150, 142, 162), outline=INK, outline_w=2)
    cr = Layer(W, H)
    cx = x + w // 2
    cr.rrect(cx - 2, y + 8, cx + 2, y + 26, 1)
    cr.rrect(cx - 8, y + 13, cx + 8, y + 17, 1)
    fill(c, cr, (60, 54, 72))


def cross(c, x, y, s):
    t = Layer(W, H)
    t.rrect(x - 4 * s, y, x + 4 * s, y + 46 * s, 2)
    t.rrect(x - 16 * s, y + 10 * s, x + 16 * s, y + 18 * s, 2)
    paint(c, t, base=(96, 84, 100), shadow=(58, 50, 64), light=(140, 128, 146), outline=INK, outline_w=2)


def shovel(c):
    h = Layer(W, H)
    h.line([(468, 150), (452, 236)], 6)
    paint(c, h, base=(120, 80, 44), shadow=(80, 50, 26), light=(170, 120, 74), outline=INK, outline_w=2)
    grip = Layer(W, H)
    grip.rrect(458, 142, 482, 150, 3)
    paint(c, grip, base=(120, 80, 44), shadow=(80, 50, 26), light=(170, 120, 74), outline=INK, outline_w=2)
    blade = Layer(W, H)
    blade.poly([(440, 228), (466, 232), (462, 268), (450, 276), (436, 264)])
    paint(c, blade, base=(150, 158, 170), shadow=(96, 102, 114), light=(214, 220, 228), outline=INK, outline_w=2)


def mound(c):
    m = Layer(W, H)
    m.ellipse(452, 268, 70, 22)
    paint(c, m, base=(70, 52, 40), shadow=(44, 32, 24), light=(104, 80, 60), outline=INK, outline_w=2)


def lantern(c, x, y, s=1.0):
    g = Layer(W, H)
    g.circle(x, y, int(10 * s))
    glow(c, g, (125, 255, 176), radius=int(26 * s), strength=1.0)
    paint(c, g, base=(160, 255, 196), shadow=(70, 190, 120), light=(235, 255, 242), outline=INK, outline_w=2, grain=False)
    cap = Layer(W, H)
    cap.rrect(x - int(9 * s), y - int(16 * s), x + int(9 * s), y - int(10 * s), 2)
    paint(c, cap, base=(60, 50, 64), shadow=(36, 30, 40), light=(96, 84, 100), outline=INK, outline_w=1.5, grain=False)


def fog(c):
    w, h = c.size
    f = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(f)
    s = w // W
    r = random.Random(3)
    for _ in range(9):
        x = r.randint(-100, W) * s
        y = r.randint(200, 270) * s
        d.ellipse([x, y, x + r.randint(160, 300) * s, y + r.randint(24, 40) * s], fill=(190, 170, 220, 46))
    f = f.filter(ImageFilter.GaussianBlur(10 * s))
    c.alpha_composite(f)


def sparkles(c):
    d = ImageDraw.Draw(c)
    s = c.size[0] // W
    r = random.Random(11)
    for _ in range(18):
        x, y = r.randint(300, 680) * s, r.randint(110, 230) * s
        a = r.randint(140, 230)
        k = r.choice([2, 3]) * s
        d.line([x - k * 2, y, x + k * 2, y], fill=(255, 214, 120, a), width=s)
        d.line([x, y - k * 2, x, y + k * 2], fill=(255, 214, 120, a), width=s)


def main():
    c = new_canvas(W, H)
    sky(c)
    moon(c)
    hills(c)
    cross(c, 330, 168, 1)
    tombstone(c, 380, 186, 34, 52)
    tombstone(c, 600, 196, 30, 46)
    cross(c, 646, 182, 0.8)
    mound(c)
    shovel(c)
    lantern(c, 520, 214, 1.0)
    lantern(c, 300, 230, 0.8)
    lantern(c, 640, 150, 0.7)
    fog(c)
    sparkles(c)
    img = finish(c, W, H, OUT)
    print("ui_card_cover", img.size)


if __name__ == "__main__":
    main()
