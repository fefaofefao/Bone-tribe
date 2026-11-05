#!/usr/bin/env python3
"""Ícones dos tipos de evento da versão 1.3 (elite, aposta, santuário, enigma, arena).

Uso: python3 tools/art_events_v13.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_art import *  # noqa

S = 96


def ev_icon(name, fn):
    cv, _ = icon_canvas(S)
    fn(cv)
    finish(cv, S, S, out("ui", "ui_event_" + name + ".png"))


def elite(cv):
    # caveira com chifres e aura dourada
    o = Layer(S, S)
    o.circle(48, 50, 34)
    glow(cv, o, (255, 200, 70), radius=10, strength=1.2)
    h = Layer(S, S)
    h.poly([(22, 40), (8, 8), (34, 30)])
    h.poly([(74, 40), (88, 8), (62, 30)])
    paint(cv, h, base=(250, 205, 80), shadow=(170, 120, 30), outline_w=2.6)
    draw_skull(cv, S, S, 48, 54, 26, eye_color=(255, 200, 60))


def gamble(cv):
    # dois dados de osso
    for (x, y, pips) in ((14, 34, [(30, 50)]), (46, 22, [(56, 32), (72, 48), (64, 40)])):
        m = Layer(S, S)
        m.rrect(x, y, x + 36, y + 36, 8)
        paint(cv, m, outline_w=3)
        p = Layer(S, S)
        for (px, py) in pips:
            p.circle(px, py, 4)
        fill(cv, p, (60, 30, 30))
    c = Layer(S, S)
    c.circle(30, 82, 9)
    c.circle(54, 84, 9)
    paint(cv, c, base=(250, 210, 90), shadow=(170, 120, 30), outline_w=2)


def shrine(cv):
    # mãos unidas / chama sagrada sobre pedestal
    m = Layer(S, S)
    m.rrect(22, 62, 74, 84, 5)
    m.rrect(32, 50, 64, 64, 4)
    paint(cv, m, base=(150, 140, 120), shadow=(80, 72, 60), outline_w=3)
    fl = Layer(S, S)
    fl.ellipse(48, 36, 13, 15)
    fl.poly([(36, 34), (48, 4), (60, 34)])
    glow(cv, fl, (255, 220, 120), radius=10, strength=1.5)
    fill(cv, fl, (255, 236, 170))


def riddle(cv):
    # esfinge: olho dentro de um triângulo
    m = Layer(S, S)
    m.poly([(48, 8), (88, 82), (8, 82)])
    paint(cv, m, base=(200, 170, 110), shadow=(130, 100, 60), outline_w=3)
    e = Layer(S, S)
    e.ellipse(48, 58, 18, 10)
    fill(cv, e, (40, 24, 30))
    i = Layer(S, S)
    i.circle(48, 58, 6)
    glow(cv, i, (120, 220, 255), radius=6, strength=1.4)
    fill(cv, i, (170, 240, 255))


def arena(cv):
    # escudo redondo com duas espadas de osso
    s = Layer(S, S)
    s.circle(48, 50, 26)
    paint(cv, s, base=(170, 70, 60), shadow=(100, 36, 34), outline_w=3)
    m = Layer(S, S)
    m.bone((10, 88), (66, 16), 5)
    m.bone((86, 88), (30, 16), 5)
    paint(cv, m, outline_w=2.6)


if __name__ == "__main__":
    for n, f in (("elite", elite), ("gamble", gamble), ("shrine", shrine), ("riddle", riddle), ("arena", arena)):
        ev_icon(n, f)
    print("ícones de evento 1.3 ok")
