#!/usr/bin/env python3
"""Textos, faixas e telas finais em inglês para os 3 anúncios (A, B, C)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlays_base import *  # noqa
from PIL import Image, ImageDraw, ImageFilter

OUTD = sys.argv[1]
os.makedirs(OUTD, exist_ok=True)


def cap(name, title, sub, W, big, subsz, title_color=BONE, sub_color=CANDLE):
    lines = [(title, font(PIRATA, big), title_color)]
    if sub:
        lines.append((sub, font(FREDOKA, subsz, True), sub_color))
    text_block(lines, W).save(f"{OUTD}/{name}.png")


def icon_img(size):
    icon = Image.open(ROOT + "/art/ui/ui_app_icon_512.png").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=size // 5, fill=255)
    icon.putalpha(mask)
    return icon


def end_card(W, H, name, vertical, headline, sub):
    bg = Image.new("RGBA", (W, H), (14, 11, 16, 220))
    logo = Image.open(ROOT + "/art/ui/ui_logo.png")
    s = 1.45 if vertical else 1.2
    logo = logo.resize((int(logo.width * s), int(logo.height * s)), Image.LANCZOS)
    isz = 290 if vertical else 250
    icon = icon_img(isz)
    cw = W - 80 if vertical else 1000
    head = text_block([(headline, font(PIRATA, 96 if vertical else 80), CANDLE)], cw, 10)
    tag = text_block([(sub, font(FREDOKA, 46 if vertical else 40, True), BONE)], cw, 10)
    btn = button("PLAY FREE", font(FREDOKA, 76 if vertical else 64, True), 620 if vertical else 560, 140 if vertical else 118)
    store = text_block([("Get it on Google Play", font(FREDOKA, 40 if vertical else 34, True), BONE)], cw, 10)
    if vertical:
        y = 260
        bg.alpha_composite(icon, ((W - isz) // 2, y)); y += isz + 20
        bg.alpha_composite(logo, ((W - logo.width) // 2, y)); y += logo.height
        bg.alpha_composite(head, ((W - head.width) // 2, y)); y += head.height
        bg.alpha_composite(tag, ((W - tag.width) // 2, y)); y += tag.height + 90
        bg.alpha_composite(btn, ((W - btn.width) // 2, y)); y += btn.height + 20
        bg.alpha_composite(store, ((W - store.width) // 2, y))
    else:
        left = 170
        bg.alpha_composite(icon, (left, (H - isz) // 2))
        cx = left + isz + 70
        y = 130
        bg.alpha_composite(logo, (cx + (cw - logo.width) // 2, y)); y += logo.height
        bg.alpha_composite(head, (cx, y)); y += head.height
        bg.alpha_composite(tag, (cx, y)); y += tag.height + 30
        bg.alpha_composite(btn, (cx + (cw - btn.width) // 2, y)); y += btn.height + 6
        bg.alpha_composite(store, (cx, y))
    bg.save(f"{OUTD}/{name}.png")


def strip(W, H, name):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(img)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=(14, 11, 16, int(235 * min(1, y / (H * 0.35)))))
    isz = int(H * 0.62)
    y0 = int(H * 0.28)
    img.alpha_composite(icon_img(isz), (40, y0))
    d = ImageDraw.Draw(img)
    d.text((40 + isz + 24, y0 + 2), "Bone Tribe", font=font(PIRATA, int(H * 0.27)), fill=BONE, stroke_width=3, stroke_fill=DARK)
    d.text((40 + isz + 26, y0 + int(H * 0.33)), "Skeleton RPG · Free", font=font(FREDOKA, int(H * 0.14), True), fill=CANDLE)
    btn = button("PLAY", font(FREDOKA, int(H * 0.17), True), int(W * 0.24), int(H * 0.34))
    img.alpha_composite(btn, (W - btn.width - 20, y0 + (isz - btn.height) // 2))
    img.save(f"{OUTD}/{name}.png")


def combo_card(W, name, vertical):
    """Wolf Skull + Bat Wings + Scorpion Tail = ?"""
    bones = ["bone_skull_wolf", "bone_wings_bat", "bone_tail_scorpion"]
    labels = ["Wolf Skull", "Bat Wings", "Scorpion Tail"]
    cell = 240 if vertical else 200
    gap = 60 if vertical else 50
    qw = 140
    total = 3 * cell + 3 * gap + qw
    H = cell + 200
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = (W - total) // 2
    fl = font(FREDOKA, 34 if vertical else 28, True)
    plus = font(PIRATA, 110 if vertical else 90)
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
    q = font(PIRATA, 200 if vertical else 170)
    qb = d.textbbox((0, 0), "?", font=q, stroke_width=6)
    d.text((x + (qw - (qb[2] - qb[0])) // 2 - qb[0], 20 + (cell - (qb[3] - qb[1])) // 2 - qb[1]), "?", font=q, fill=(180, 92, 255), stroke_width=6, stroke_fill=DARK)
    img.save(f"{OUTD}/{name}.png")


for tag, W in (("v", 1080), ("h", 860)):
    big = 120 if tag == "v" else 92
    sub = 52 if tag == "v" else 42
    # A
    cap(f"a1_{tag}", "STEAL THEIR BONES", "beat a monster, take its bones", W, big, sub)
    cap(f"a2_{tag}", "EVERY BONE CHANGES YOU", "new body, new powers", W, big - 12, sub)
    cap(f"a3_{tag}", "SECRET FORMS!", "match the right bones", W, big + 8, sub, CANDLE, BONE)
    cap(f"a4_{tag}", "BEAT THE BOSSES", "and climb 20 towers", W, big, sub)
    # B
    cap(f"b1_{tag}", "WHAT HAPPENS IF", "you mix these bones?", W, big, sub + 6)
    cap(f"b2_{tag}", "SECRET FORM:", "NIGHT MANTICORE", W, big, sub + 14, CANDLE, (215, 170, 255))
    cap(f"b3_{tag}", "102 BONES", "9 forms to find", W, big, sub + 6)
    combo_card(1080 if tag == "v" else 860, f"combo_{tag}", tag == "v")
    # C
    cap(f"c1_{tag}", "LOST TO A RAT…", "run 1: destroyed", W, big, sub, BONE, (226, 85, 75))
    cap(f"c2_{tag}", "GET STRONGER", "upgrade with bone dust", W, big, sub)
    cap(f"c3_{tag}", "NEW RUN. NEW BODY.", "steal their bones", W, big - 14, sub)
    cap(f"c4_{tag}", "SECRET FORM!", "unlocked", W, big + 8, sub, CANDLE, BONE)
    cap(f"c5_{tag}", "REVENGE!", "", W, big + 40, sub, CANDLE)
    strip(1080 if tag == "v" else 860, 280 if tag == "v" else 220, f"strip_{tag}")
for tag, (W, H) in (("v", (1080, 1920)), ("h", (1920, 1080))):
    end_card(W, H, f"endA_{tag}", tag == "v", "STEAL. BUILD. WIN.", "Build your monster from bones!")
    end_card(W, H, f"endB_{tag}", tag == "v", "CAN YOU FIND THEM ALL?", "9 forms · 102 bones")
    end_card(W, H, f"endC_{tag}", tag == "v", "20 TOWERS. 9 BOSSES.", "Every run makes you stronger")
fg = Image.open(ROOT + "/store/feature_graphic.png").convert("RGB").resize((1920, 938), Image.LANCZOS)
side = Image.new("RGB", (1920, 1080), DARK)
side.paste(fg, (0, 71))
side = side.filter(ImageFilter.GaussianBlur(18))
Image.blend(side, Image.new("RGB", (1920, 1080), DARK), 0.45).save(f"{OUTD}/bg_h.png")
print("ok")
