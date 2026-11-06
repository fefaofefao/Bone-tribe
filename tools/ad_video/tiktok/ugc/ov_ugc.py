import os, sys
sys.path.insert(0, "/home/user/Bone-tribe/tools/ad_video/en")
from overlays_base import *  # noqa
from PIL import Image, ImageDraw, ImageFilter
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920

def ugc(name, text, size=70, color=(255, 255, 255)):
    # legenda estilo TikTok: branca, contorno preto grosso
    f = font(FREDOKA, size, True)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = text.split("\n")
    boxes = [tmp.textbbox((0, 0), l, font=f, stroke_width=9) for l in lines]
    h = sum(b[3] - b[1] for b in boxes) + 18 * (len(lines) + 1)
    img = Image.new("RGBA", (W, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img); y = 18
    for l, b in zip(lines, boxes):
        d.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1]), l, font=f, fill=color, stroke_width=9, stroke_fill=(0, 0, 0))
        y += b[3] - b[1] + 18
    img.save(f"{OUT}/{name}.png")

ugc("u1", "estou adorando jogar\nesse jogo...", 74)
ugc("u2", "você conhece? 👀".replace(" 👀", ""), 84, (255, 214, 90))
ugc("u3", "você monta seu corpo com\nos ossos dos monstros", 64)
ugc("u4", "tem forma SECRETA!", 76, (215, 170, 255))
ugc("u5", "monstro dourado = osso raro", 64, (255, 214, 90))
ugc("u6", "40 torres pra subir", 70)
ugc("u7", "e os chefes...", 76)
# etiqueta de transparência (avatar de IA) para a abertura
f = font(FREDOKA, 30, True)
tag = Image.new("RGBA", (260, 56), (0, 0, 0, 0)); d = ImageDraw.Draw(tag)
d.rounded_rectangle((0, 0, 259, 55), radius=16, fill=(0, 0, 0, 140))
tb = d.textbbox((0, 0), "avatar de IA", font=f)
d.text(((260 - (tb[2] - tb[0])) // 2 - tb[0], (56 - (tb[3] - tb[1])) // 2 - tb[1]), "avatar de IA", font=f, fill=(255, 255, 255, 230))
tag.save(f"{OUT}/aitag.png")
# moldura do celular com a tela vazada (cantos arredondados)
PW, PH, SX, SY, SW, SH = 900, 1640, 36, 40, 828, 1472   # tela 828x1472 (9:16)
ph = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
d.rounded_rectangle((0, 0, PW - 1, PH - 1), radius=110, fill=(18, 16, 22, 255), outline=(70, 66, 80, 255), width=6)
hole = Image.new("L", (PW, PH), 0)
ImageDraw.Draw(hole).rounded_rectangle((SX, SY, SX + SW, SY + SH), radius=70, fill=255)
ph.putalpha(Image.fromarray(__import__("numpy").minimum(__import__("numpy").array(ph.getchannel("A")), 255 - __import__("numpy").array(hole))))
d = ImageDraw.Draw(ph)
d.rounded_rectangle((PW // 2 - 70, SY + 16, PW // 2 + 70, SY + 46), radius=15, fill=(8, 8, 10, 255))  # câmera
d.rounded_rectangle((PW // 2 - 110, PH - 70, PW // 2 + 110, PH - 58), radius=6, fill=(60, 58, 70, 255))
sh = Image.new("RGBA", (PW + 80, PH + 80), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((40, 50, PW + 40, PH + 50), radius=120, fill=(0, 0, 0, 160))
sh = sh.filter(ImageFilter.GaussianBlur(22)); sh.alpha_composite(ph, (40, 40))
sh.save(f"{OUT}/phone.png")
print("ok")
