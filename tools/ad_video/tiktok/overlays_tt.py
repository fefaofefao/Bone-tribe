#!/usr/bin/env python3
"""Textos do vídeo do TikTok (pt-BR, vertical 1080x1920)."""
import os, sys
sys.path.insert(0, "/home/user/Bone-tribe/tools/ad_video/en")
from overlays_base import *  # noqa
from PIL import Image, ImageDraw, ImageFilter

OUTD = sys.argv[1]
os.makedirs(OUTD, exist_ok=True)
W, H = 1080, 1920


def cap(name, title, sub="", big=104, subsz=50, tc=BONE, sc=CANDLE):
    lines = [(title, font(PIRATA, big), tc)]
    if sub:
        lines.append((sub, font(FREDOKA, subsz, True), sc))
    text_block(lines, W - 60).save(f"{OUTD}/{name}.png")


cap("c1", "POV: você é um esqueleto", "que rouba os ossos dos monstros", 96, 50)
cap("c2", "CADA OSSO MUDA SEU CORPO", "", 92)
cap("c3", "MONSTROS DE ELITE", "mais fortes, prêmio raro", 104, 48, CANDLE, BONE)
cap("c4", "40 TORRES", "neve, pântano, maldições...", 120, 48)
cap("c5", "FORMA SECRETA!", "Manticora Noturna", 116, 56, CANDLE, (215, 170, 255))
cap("c6", "E OS CHEFES...", "", 112)

# tela final (sem botão falso: no TikTok o clique é pelo perfil/link)
bg = Image.new("RGBA", (W, H), (14, 11, 16, 225))
icon = Image.open(ROOT + "/art/ui/ui_app_icon_512.png").resize((320, 320), Image.LANCZOS)
mask = Image.new("L", (320, 320), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, 319, 319), radius=64, fill=255)
icon.putalpha(mask)
logo = Image.open(ROOT + "/art/ui/ui_logo.png")
logo = logo.resize((int(logo.width * 1.5), int(logo.height * 1.5)), Image.LANCZOS)
head = text_block([("Monte seu monstro com ossos!", font(FREDOKA, 56, True), BONE)], W - 80, 10)
free = text_block([("GRÁTIS na Play Store", font(PIRATA, 104), CANDLE)], W - 80, 10)
sub = text_block([("procure: Bone Tribe", font(FREDOKA, 50, True), BONE)], W - 80, 10)
y = 300
bg.alpha_composite(icon, ((W - 320) // 2, y)); y += 340
bg.alpha_composite(logo, ((W - logo.width) // 2, y)); y += logo.height + 10
bg.alpha_composite(head, ((W - head.width) // 2, y)); y += head.height + 40
bg.alpha_composite(free, ((W - free.width) // 2, y)); y += free.height
bg.alpha_composite(sub, ((W - sub.width) // 2, y))
bg.save(f"{OUTD}/end.png")
print("ok")

# ---- vídeos 2 a 10
cap("f1", "1ª PARTIDA:", "perdi pro Rei Rato...", 110, 56, BONE, (226, 85, 75))
cap("f2", "PEGUEI OS OSSOS", "dos monstros que venci", 104, 50)
cap("f3", "VINGANÇA!", "", 140, 50, CANDLE)
cap("r1", "E SE EU JUNTAR", "esses 3 ossos?", 110, 56)
cap("r3", "9 formas secretas", "você acha todas?", 100, 54)
cap("e1", "ESSE MONSTRO DOURADO", "é bem mais forte...", 88, 54)
cap("e2", "VALE A PENA?", "", 120)
cap("e3", "OSSO RARO!", "", 130, 50, (95, 180, 255))
cap("q1", "RESPONDE AÍ:", "o que tem dentes, mas não morde?", 110, 50)
cap("q2", "COMENTA A RESPOSTA", "antes de ver!", 96, 56, CANDLE, BONE)
cap("q3", "UM PENTE!", "acertou?", 130, 56, CANDLE)
cap("g1", "EM QUAL CRÂNIO", "está o osso?", 110, 60)
cap("g2", "esquerda, meio", "ou direita?", 100, 60, CANDLE, BONE)
cap("g3", "comenta antes de ver!", "", 90)
cap("g4", "ERREI!", "e você, qual escolheria?", 130, 54, (226, 85, 75), BONE)
cap("q4", "ERREI FEIO!", "e você? comenta!", 130, 56, (226, 85, 75), BONE)
cap("t1", "40 TORRES", "cada uma com um mundo", 130, 52)
cap("t2", "Torre 1: Cripta", "", 100)
cap("t3", "Torre 4: Gelo", "", 100, 50, (190, 225, 255))
cap("t4", "Torre 7: Pântano", "", 100, 50, (170, 235, 130))
cap("t5", "Torre 23: Maldição", "inimigos amaldiçoados", 96, 50, (215, 170, 255), BONE)
cap("a1", "ARENA DOS OSSOS", "quantas ondas você aguenta?", 104, 50)
cap("a2", "ONDA 1", "", 140, 50, CANDLE)
cap("a3", "ONDA 2", "", 140, 50, (226, 85, 75))
cap("a4", "A PLATEIA PAGA!", "e cai osso novo", 108, 52, CANDLE, BONE)
cap("k1", "102 OSSOS", "quantos você acharia?", 130, 56)
cap("k2", "cada osso deixa você", "mais forte pra sempre", 88, 56, BONE, CANDLE)
cap("v1", "DO ESQUELETO BÁSICO...", "", 96)
cap("v2", "...AO MONSTRO", "", 120, 50, CANDLE)
cap("v3", "cada osso muda", "seu corpo e seus poderes", 96, 52)

# cartela da receita (vídeo 3)
bones = ["bone_skull_wolf", "bone_wings_bat", "bone_tail_scorpion"]
labels = ["Crânio de Lobo", "Asas de Morcego", "Cauda de Escorpião"]
cell, gap, qw = 240, 60, 140
total = 3 * cell + 3 * gap + qw
img = Image.new("RGBA", (W, cell + 200), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
x = (W - total) // 2
fl = font(FREDOKA, 30, True)
plus = font(PIRATA, 110)
for i, (b, lab) in enumerate(zip(bones, labels)):
    box = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, cell - 1, cell - 1), radius=34, fill=(31, 24, 34, 235), outline=(180, 92, 255), width=5)
    art = Image.open(f"{ROOT}/art/bones/{b}.png")
    art.thumbnail((cell - 40, cell - 40), Image.LANCZOS)
    box.alpha_composite(art, ((cell - art.width) // 2, (cell - art.height) // 2))
    img.alpha_composite(box, (x, 20))
    tb = d.textbbox((0, 0), lab, font=fl, stroke_width=4)
    d.text((x + (cell - (tb[2] - tb[0])) // 2, cell + 34), lab, font=fl, fill=BONE, stroke_width=4, stroke_fill=DARK)
    x += cell
    sym = "+" if i < 2 else "="
    sb = d.textbbox((0, 0), sym, font=plus, stroke_width=5)
    d.text((x + (gap - (sb[2] - sb[0])) // 2 - sb[0], 20 + (cell - (sb[3] - sb[1])) // 2 - sb[1]), sym, font=plus, fill=CANDLE, stroke_width=5, stroke_fill=DARK)
    x += gap
q = font(PIRATA, 200)
qb = d.textbbox((0, 0), "?", font=q, stroke_width=6)
d.text((x + (qw - (qb[2] - qb[0])) // 2 - qb[0], 20 + (cell - (qb[3] - qb[1])) // 2 - qb[1]), "?", font=q, fill=(180, 92, 255), stroke_width=6, stroke_fill=DARK)
img.save(f"{OUTD}/combo.png")
print("ok 2-10")
