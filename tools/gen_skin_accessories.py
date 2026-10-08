#!/usr/bin/env python3
"""Acessórios das skins (placeholders no estilo do jogo, no tamanho final).

Gera em art/skins/: chapéu e tapa-olho da skin Pirata, coroa do Fundador e o
amuleto da Lua de Âmbar. As posições ficam em data/accessories.json.
Uso: python3 tools/gen_skin_accessories.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artlib import Layer, new_canvas, paint, fill, glow, finish  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "art", "skins")
INK = (32, 20, 18)


def pirate_hat():
    w, h = 230, 130
    c = new_canvas(w, h)
    hat = Layer(w, h)
    # copa
    hat.poly([(52, 92), (70, 30), (115, 14), (160, 30), (178, 92)])
    # aba em três pontas (tricórnio)
    brim = Layer(w, h)
    brim.poly([(6, 82), (60, 70), (115, 78), (170, 70), (224, 82), (190, 112), (115, 100), (40, 112)])
    paint(c, brim, base=(40, 30, 36), shadow=(22, 16, 20), light=(78, 62, 70), outline=INK, outline_w=3)
    paint(c, hat, base=(52, 38, 46), shadow=(28, 20, 26), light=(96, 76, 86), outline=INK, outline_w=3)
    trim = Layer(w, h)
    trim.curve([(14, 84), (60, 72), (115, 80), (170, 72), (216, 84)], 6)
    paint(c, trim, base=(232, 178, 64), shadow=(170, 110, 30), light=(255, 230, 140), outline=INK, outline_w=1.5, grain=False)
    # caveira e ossos cruzados
    sk = Layer(w, h)
    sk.circle(115, 48, 15)
    sk.rrect(106, 56, 124, 68, 4)
    paint(c, sk, base=(240, 232, 210), shadow=(190, 176, 150), light=(255, 255, 246), outline=INK, outline_w=1.5, grain=False)
    cross = Layer(w, h)
    cross.bone((92, 72), (138, 54), 4.5)
    cross.bone((92, 54), (138, 72), 4.5)
    paint(c, cross, base=(240, 232, 210), shadow=(190, 176, 150), light=(255, 255, 246), outline=INK, outline_w=1.5, grain=False)
    eyes = Layer(w, h)
    eyes.circle(109, 47, 4)
    eyes.circle(121, 47, 4)
    fill(c, eyes, INK)
    return finish(c, w, h, os.path.join(OUT, "acc_pirate_hat.png"))


def eyepatch():
    w, h = 120, 90
    c = new_canvas(w, h)
    strap = Layer(w, h)
    strap.curve([(4, 22), (40, 34), (70, 42), (116, 60)], 5)
    paint(c, strap, base=(30, 22, 24), shadow=(16, 10, 12), light=(70, 56, 60), outline=INK, outline_w=1.5, grain=False)
    patch = Layer(w, h)
    patch.ellipse(64, 50, 24, 20)
    paint(c, patch, base=(36, 26, 30), shadow=(18, 12, 16), light=(84, 66, 72), outline=INK, outline_w=2.5)
    return finish(c, w, h, os.path.join(OUT, "acc_eyepatch.png"))


def founder_crown():
    w, h = 170, 120
    c = new_canvas(w, h)
    crown = Layer(w, h)
    crown.poly([(20, 100), (14, 34), (50, 66), (85, 18), (120, 66), (156, 34), (150, 100)])
    glow(c, crown, (200, 120, 255), radius=10, strength=0.8)
    paint(c, crown, base=(240, 190, 70), shadow=(176, 116, 30), light=(255, 238, 150), outline=INK, outline_w=3)
    band = Layer(w, h)
    band.rrect(18, 84, 152, 104, 6)
    paint(c, band, base=(222, 168, 54), shadow=(160, 100, 24), light=(255, 230, 140), outline=INK, outline_w=2)
    gems = Layer(w, h)
    for x, y, r in [(85, 94, 8), (50, 94, 6), (120, 94, 6), (14, 34, 6), (85, 18, 7), (156, 34, 6)]:
        gems.circle(x, y, r)
    paint(c, gems, base=(176, 90, 255), shadow=(110, 40, 190), light=(236, 196, 255), outline=INK, outline_w=1.5, grain=False)
    return finish(c, w, h, os.path.join(OUT, "acc_founder_crown.png"))


def moon_charm():
    w, h = 90, 120
    c = new_canvas(w, h)
    cord = Layer(w, h)
    cord.curve([(45, 2), (44, 30), (45, 52)], 3)
    paint(c, cord, base=(120, 70, 30), shadow=(80, 44, 18), light=(170, 110, 60), outline=INK, outline_w=1, grain=False)
    moon = Layer(w, h)
    moon.circle(45, 80, 30)
    bite = Layer(w, h)
    bite.circle(60, 70, 26)
    moon.cut(bite)
    glow(c, moon, (255, 170, 60), radius=9, strength=1.0)
    paint(c, moon, base=(255, 186, 84), shadow=(206, 118, 36), light=(255, 230, 170), outline=INK, outline_w=2.5, grain=False)
    return finish(c, w, h, os.path.join(OUT, "acc_moon_charm.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (pirate_hat, eyepatch, founder_crown, moon_charm):
        img = f()
        print(f.__name__, img.size)
