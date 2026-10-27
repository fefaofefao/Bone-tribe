#!/usr/bin/env python3
"""Textos e tela final dos anúncios (PNG transparentes), com as fontes e cores do jogo."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = sys.argv[1]
OUT = sys.argv[2]
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


for tag, W in (("v", 1080), ("h", 860)):
    big = 128 if tag == "v" else 100
    sub = 54 if tag == "v" else 44
    save_caption(f"cap1_{tag}", [("MONTE SEU MONSTRO", font(PIRATA, big), BONE), ("com os ossos de quem você derrota", font(FREDOKA, sub, True), CANDLE)], W)
    save_caption(f"cap2_{tag}", [("CADA OSSO MUDA", font(PIRATA, big), BONE), ("seu corpo e seus poderes", font(FREDOKA, sub, True), CANDLE)], W)
    save_caption(f"cap3_{tag}", [("FORMA SECRETA!", font(PIRATA, big + 10), CANDLE), ("junte 4 ossos da mesma família", font(FREDOKA, sub, True), BONE)], W)
    save_caption(f"cap4_{tag}", [("VENÇA OS CHEFES", font(PIRATA, big), BONE), ("e suba 20 torres", font(FREDOKA, sub, True), CANDLE)], W)
end_card(1080, 1920, "end_v", True)
end_card(1920, 1080, "end_h", False)
# lado do anúncio horizontal: fundo com a arte da loja desfocada
fg = Image.open(ROOT + "/store/feature_graphic.png").convert("RGB").resize((1920, 938), Image.LANCZOS)
side = Image.new("RGB", (1920, 1080), DARK)
side.paste(fg, (0, 71))
side = side.filter(ImageFilter.GaussianBlur(18))
side = Image.blend(side, Image.new("RGB", (1920, 1080), DARK), 0.45)
side.save(f"{OUT}/bg_h.png")
print("ok")


def strip(W, H, name):
    """Faixa fixa com ícone, nome e botão (aparece o vídeo todo)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=(14, 11, 16, int(235 * min(1, y / (H * 0.35)))))
    img.alpha_composite(grad)
    isz = int(H * 0.62)
    icon = Image.open(ROOT + "/art/ui/ui_app_icon_512.png").resize((isz, isz), Image.LANCZOS)
    mask = Image.new("L", (isz, isz), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, isz - 1, isz - 1), radius=isz // 5, fill=255)
    icon.putalpha(mask)
    y0 = int(H * 0.28)
    img.alpha_composite(icon, (40, y0))
    d = ImageDraw.Draw(img)
    d.text((40 + isz + 24, y0 + 2), "Bone Tribe", font=font(PIRATA, int(H * 0.27)), fill=BONE, stroke_width=3, stroke_fill=DARK)
    d.text((40 + isz + 26, y0 + int(H * 0.33)), "RPG de esqueleto · Grátis", font=font(FREDOKA, int(H * 0.14), True), fill=CANDLE)
    btn = button("JOGAR", font(FREDOKA, int(H * 0.17), True), int(W * 0.26), int(H * 0.34))
    img.alpha_composite(btn, (W - btn.width - 20, y0 + (isz - btn.height) // 2))
    img.save(f"{OUT}/{name}.png")


strip(1080, 280, "strip_v")
strip(860, 220, "strip_h")
