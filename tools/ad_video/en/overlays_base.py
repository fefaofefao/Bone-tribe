#!/usr/bin/env python3
"""Textos e tela final dos anúncios (PNG transparentes), com as fontes e cores do jogo."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = "/home/user/Bone-tribe"
OUT = "."
PIRATA = ROOT + "/art/fonts/PirataOne-Regular.ttf"
FREDOKA = ROOT + "/art/fonts/Fredoka-Variable.ttf"
BONE = (234, 223, 198)
CANDLE = (255, 179, 71)
INK = (42, 29, 26)
DARK = (14, 11, 16)


def font(path, size, bold=False):
    f = ImageFont.truetype(path, size)
    if bold and path == FREDOKA:
        try:
            f.set_variation_by_axes([650])
        except Exception:
            pass
    return f


def text_block(lines, width, pad=30):
    """lines: [(texto, fonte, cor)] -> imagem com contorno escuro e sombra."""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    sizes = [tmp.textbbox((0, 0), t, font=f, stroke_width=max(4, f.size // 12)) for t, f, c in lines]
    h = sum(b[3] - b[1] for b in sizes) + pad * (len(lines) + 1)
    img = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(shadow)
    y = pad
    for (t, f, c), b in zip(lines, sizes):
        w = b[2] - b[0]
        x = (width - w) // 2 - b[0]
        sw = max(4, f.size // 12)
        ds.text((x + 6, y - b[1] + 8), t, font=f, fill=(0, 0, 0, 200), stroke_width=sw, stroke_fill=(0, 0, 0, 200))
        d.text((x, y - b[1]), t, font=f, fill=c, stroke_width=sw, stroke_fill=DARK)
        y += b[3] - b[1] + pad
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    shadow.alpha_composite(img)
    return shadow


def save_caption(name, lines, width):
    text_block(lines, width).save(f"{OUT}/{name}.png")


def button(text, f, w, h):
    img = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((10, 10, w + 30, h + 30), radius=h // 2, fill=(255, 179, 71, 170))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((20, 26, w + 20, h + 26), radius=h // 2, fill=(170, 95, 20))
    d.rounded_rectangle((20, 20, w + 20, h + 20), radius=h // 2, fill=CANDLE, outline=(255, 226, 170), width=4)
    b = d.textbbox((0, 0), text, font=f)
    d.text((20 + (w - (b[2] - b[0])) // 2 - b[0], 20 + (h - (b[3] - b[1])) // 2 - b[1] - 2), text, font=f, fill=INK)
    glow.alpha_composite(img)
    return glow


def end_card(W, H, name, vertical):
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    # véu escuro com vinheta (o jogo continua visível atrás)
    veil = Image.new("RGBA", (W, H), (14, 11, 16, 215))
    bg.alpha_composite(veil)
    logo = Image.open(ROOT + "/art/ui/ui_logo.png")
    icon = Image.open(ROOT + "/art/ui/ui_app_icon_512.png")
    s = 1.45 if vertical else 1.25
    logo = logo.resize((int(logo.width * s), int(logo.height * s)), Image.LANCZOS)
    isz = 300 if vertical else 260
    icon = icon.resize((isz, isz), Image.LANCZOS)
    mask = Image.new("L", (isz, isz), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, isz - 1, isz - 1), radius=isz // 5, fill=255)
    icon.putalpha(mask)
    tag = text_block([("Monte seu monstro com ossos!", font(FREDOKA, 58 if vertical else 50, True), BONE)], W - 80, 10)
    feats = text_block([("100+ ossos  ·  20 torres  ·  formas secretas", font(FREDOKA, 40 if vertical else 36, True), CANDLE)], W - 80, 10)
    btn = button("JOGUE GRÁTIS", font(FREDOKA, 74 if vertical else 64, True), 640 if vertical else 600, 140 if vertical else 120)
    store = text_block([("Disponível no Google Play", font(FREDOKA, 40 if vertical else 34, True), BONE)], W - 80, 10)
    if vertical:
        y = 300
        bg.alpha_composite(icon, ((W - isz) // 2, y)); y += isz + 30
        bg.alpha_composite(logo, ((W - logo.width) // 2, y)); y += logo.height + 10
        bg.alpha_composite(tag, ((W - tag.width) // 2, y)); y += tag.height + 10
        bg.alpha_composite(feats, ((W - feats.width) // 2, y)); y += feats.height + 120
        bg.alpha_composite(btn, ((W - btn.width) // 2, y)); y += btn.height + 30
        bg.alpha_composite(store, ((W - store.width) // 2, y))
    else:
        left = 160
        bg.alpha_composite(icon, (left, (H - isz) // 2))
        cx = left + isz + 80
        cw = W - cx - 80
        y = 170
        bg.alpha_composite(logo, (cx + (cw - logo.width) // 2, y)); y += logo.height
        tag2 = text_block([("Monte seu monstro com ossos!", font(FREDOKA, 50, True), BONE)], cw, 10)
        feats2 = text_block([("100+ ossos  ·  20 torres  ·  formas secretas", font(FREDOKA, 34, True), CANDLE)], cw, 10)
        store2 = text_block([("Disponível no Google Play", font(FREDOKA, 34, True), BONE)], cw, 10)
        bg.alpha_composite(tag2, (cx, y)); y += tag2.height
        bg.alpha_composite(feats2, (cx, y)); y += feats2.height + 40
        bg.alpha_composite(btn, (cx + (cw - btn.width) // 2, y)); y += btn.height + 10
        bg.alpha_composite(store2, (cx, y))
    bg.save(f"{OUT}/{name}.png")


