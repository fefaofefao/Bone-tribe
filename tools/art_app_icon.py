#!/usr/bin/env python3
"""Ícone do app (1.4.2): o Ossinho com crânio, asas e cauda de dragão sobre
um fundo de fogo com raios. O personagem vem de um render do próprio jogo
(tools/icon_src/icon_dragon_render.png: Ossinho.tscn com bone_skull_dragon,
bone_ribs_bear, bone_wings_dragon, bone_tail_dragon, bone_claw_bear,
bone_claw_lizard e bone_legs_wolf, escala 3,6, fundo transparente, 1200x1400).

Gera em art/ui/:
  ui_app_icon_512.png            ícone da Play Store (enviar na Play Console)
  ui_app_icon.png                ícone do celular (192)
  ui_app_icon_background.png     camada de fundo do ícone adaptável (432)
  ui_app_icon_foreground.png     camada da frente do ícone adaptável (432):
                                 o rosto fica dentro da área segura (66%)
Uso: python3 tools/art_app_icon.py
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "icon_src", "icon_dragon_render.png")
OUT = os.path.join(HERE, "..", "art", "ui")
N = 1024


def radial(c_in, c_out, cx=0.5, cy=0.5, power=1.0):
    img = Image.new("RGB", (N, N))
    px = img.load()
    md = math.hypot(max(cx, 1 - cx), max(cy, 1 - cy)) * N
    for y in range(N):
        for x in range(N):
            t = min(1.0, (math.hypot(x - cx * N, y - cy * N) / md)) ** power
            px[x, y] = tuple(int(c_in[i] + (c_out[i] - c_in[i]) * t) for i in range(3))
    return img.convert("RGBA")


def rays(img, color, n=16, alpha=60, cx=0.5, cy=0.5, rot=0.0):
    lay = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(n):
        a0 = rot + i * 2 * math.pi / n
        a1 = a0 + math.pi / n * 0.55
        pts = [(cx * N, cy * N), (cx * N + math.cos(a0) * 2 * N, cy * N + math.sin(a0) * 2 * N),
               (cx * N + math.cos(a1) * 2 * N, cy * N + math.sin(a1) * 2 * N)]
        d.polygon(pts, fill=color + (alpha,))
    img.alpha_composite(lay)


def glow_spot(img, color, cx, cy, r, alpha=200):
    lay = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r * 0.45)))


def sparks(img, color, n=40, seed=1):
    r = random.Random(seed)
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = r.randint(0, N), r.randint(0, N)
        s = r.choice([3, 4, 6, 8])
        d.ellipse([x - s, y - s, x + s, y + s], fill=color + (r.randint(150, 255),))


def vignette(img, strength=120):
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse([-N * 0.15, -N * 0.15, N * 1.15, N * 1.15], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(N * 0.12))
    dark = Image.new("RGBA", (N, N), (10, 4, 14, 0))
    dark.putalpha(ImageChops.invert(m).point(lambda v: int(v * strength / 255)))
    img.alpha_composite(dark)


def character(box, size, pos):
    """Recorta o render, escala e põe contorno escuro + sombra (destaca em tamanho pequeno)."""
    im = Image.open(SRC).convert("RGBA").crop(box)
    h = int(im.height * size / im.width)
    im = im.resize((size, h), Image.LANCZOS)
    pad = 40
    big = Image.new("RGBA", (size + pad * 2, h + pad * 2), (0, 0, 0, 0))
    big.paste(im, (pad, pad), im)
    stroke = big.getchannel("A").filter(ImageFilter.MaxFilter(21))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow.putalpha(stroke.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55)))
    out.alpha_composite(shadow)
    ink = Image.new("RGBA", big.size, (20, 10, 24, 0))
    ink.putalpha(stroke)
    out.alpha_composite(ink)
    out.alpha_composite(big)
    layer = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    layer.alpha_composite(out, (pos[0] - pad, pos[1] - pad)) if pos[0] - pad >= 0 and pos[1] - pad >= 0 else layer.paste(out, (pos[0] - pad, pos[1] - pad), out)
    return layer


def background():
    im = radial((255, 196, 70), (150, 20, 18), 0.58, 0.42, 0.8)
    rays(im, (255, 240, 170), 18, 70, 0.58, 0.42)
    glow_spot(im, (255, 230, 140), 600, 420, 300, 170)
    sparks(im, (255, 214, 90), 45, 3)
    vignette(im, 120)
    return im


def main():
    bg = background()
    fg = character((0, 0, 900, 820), 1100, (-80, 120))
    full = bg.copy()
    full.alpha_composite(fg)
    full.convert("RGB").resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "ui_app_icon_512.png"), optimize=True)
    full.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "ui_app_icon.png"), optimize=True)
    # ícone adaptável (108 dp = 432 px): fundo cheio e personagem por cima; o
    # Android recorta em círculo/squircle mostrando o centro (72 dp = 288 px)
    bg.convert("RGB").resize((432, 432), Image.LANCZOS).save(os.path.join(OUT, "ui_app_icon_background.png"), optimize=True)
    # o launcher mostra só os 66% do centro: o personagem encolhe para a
    # cabeça inteira caber; as bordas cortadas ficam fora da área visível
    k = 0.68
    small = fg.resize((int(N * k), int(N * k)), Image.LANCZOS)
    adapt = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    off = int(N * (1 - k) / 2)
    adapt.alpha_composite(small, (off + 10, off + 20))
    adapt.resize((432, 432), Image.LANCZOS).save(os.path.join(OUT, "ui_app_icon_foreground.png"), optimize=True)
    print("ícone ok")


if __name__ == "__main__":
    main()
