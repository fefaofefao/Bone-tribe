"""Biblioteca de desenho dos placeholders do Bone Tribe.

Desenha em supersampling (SS x) e reduz no fim, para bordas suaves.
Estilo: ossos marfim com contorno escuro, sombreado pintado e detalhes de família.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

SS = 4

IVORY = (236, 226, 200)
IVORY_SHADOW = (170, 150, 120)
IVORY_LIGHT = (255, 250, 236)
OUTLINE = (38, 24, 22)

FAMILY = {
    "family_beast": {"aura": (255, 170, 60), "detail": (150, 92, 48)},
    "family_insect": {"aura": (150, 235, 60), "detail": (70, 140, 40)},
    "family_marine": {"aura": (60, 220, 210), "detail": (40, 120, 130)},
    "family_dragon": {"aura": (255, 80, 50), "detail": (150, 40, 30)},
    "family_construct": {"aura": (90, 160, 255), "detail": (80, 95, 120)},
    "family_shadow": {"aura": (170, 90, 255), "detail": (70, 40, 110)},
    "": {"aura": (236, 226, 200), "detail": (120, 110, 100)},
}


class Layer:
    """Uma máscara em alta resolução (modo L)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("L", (w * SS, h * SS), 0)
        self.d = ImageDraw.Draw(self.img)

    def s(self, v):
        return v * SS

    def pts(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def ellipse(self, cx, cy, rx, ry, fill=255):
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=fill)

    def circle(self, cx, cy, r, fill=255):
        self.ellipse(cx, cy, r, r, fill)

    def poly(self, pts, fill=255):
        self.d.polygon(self.pts(pts), fill=fill)

    def line(self, pts, width, fill=255):
        self.d.line(self.pts(pts), fill=fill, width=int(width * SS), joint="curve")
        for p in (pts[0], pts[-1]):
            self.circle(p[0], p[1], width / 2, fill)

    def rrect(self, x0, y0, x1, y1, r, fill=255):
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=fill)

    def capsule(self, a, b, r, fill=255):
        """Segmento grosso com pontas arredondadas."""
        self.line([a, b], r * 2, fill)

    def bone(self, a, b, r, knob=1.55, fill=255):
        """Osso clássico: haste com duas cabeças duplas nas pontas."""
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        ux, uy = dx / ln, dy / ln
        self.capsule(a, b, r, fill)
        kr = r * knob * 0.62
        for (px, py), sgn in ((a, 1), (b, -1)):
            for side in (-1, 1):
                cx = px + nx * side * r * 0.75 - ux * sgn * kr * 0.25
                cy = py + ny * side * r * 0.75 - uy * sgn * kr * 0.25
                self.circle(cx, cy, kr, fill)

    def curve(self, pts, width, fill=255, steps=24):
        self.line(bezier(pts, steps), width, fill)

    def tapered(self, pts, w0, w1, fill=255, steps=28):
        """Traço que afina de w0 até w1 seguindo uma curva."""
        path = bezier(pts, steps)
        n = len(path)
        for i in range(n - 1):
            t = i / (n - 1)
            w = w0 + (w1 - w0) * t
            self.line([path[i], path[i + 1]], w, fill)

    def cut(self, other):
        self.img = ImageChops.subtract(self.img, other.img)
        self.d = ImageDraw.Draw(self.img)

    def add(self, other):
        self.img = ImageChops.lighter(self.img, other.img)
        self.d = ImageDraw.Draw(self.img)

    def copy(self):
        c = Layer(self.w, self.h)
        c.img = self.img.copy()
        c.d = ImageDraw.Draw(c.img)
        return c


def bezier(pts, steps=24):
    if len(pts) == 2:
        return pts
    out = []
    for i in range(steps + 1):
        t = i / steps
        p = list(pts)
        while len(p) > 1:
            p = [(p[j][0] + (p[j + 1][0] - p[j][0]) * t, p[j][1] + (p[j + 1][1] - p[j][1]) * t) for j in range(len(p) - 1)]
        out.append(p[0])
    return out


def _solid(size, color, alpha=255):
    return Image.new("RGBA", size, color + (alpha,))


def _shift(mask, dx, dy):
    return ImageChops.offset(mask, int(dx), int(dy))


def paint(canvas, mask, base=IVORY, shadow=IVORY_SHADOW, light=IVORY_LIGHT, outline=OUTLINE,
          outline_w=3.0, shade=True, grain=True, light_dir=(-1, -1), alpha=255):
    """Pinta uma máscara no canvas RGBA (alta resolução) com contorno e sombreado."""
    m = mask.img
    size = m.size
    ow = max(1, int(outline_w * SS))
    if outline_w > 0:
        dil = m.filter(ImageFilter.MaxFilter(ow * 2 + 1)) if ow < 12 else m.filter(ImageFilter.GaussianBlur(ow * 0.5)).point(lambda v: 255 if v > 20 else 0)
        canvas.alpha_composite(Image.composite(_solid(size, outline, alpha), Image.new("RGBA", size, (0, 0, 0, 0)), dil))
    body = _solid(size, base, alpha)
    if shade:
        # Sombra interna oposta à luz.
        r = int(9 * SS)
        sh = _shift(m, light_dir[0] * r, light_dir[1] * r)
        inner_shadow = ImageChops.subtract(m, sh).filter(ImageFilter.GaussianBlur(5 * SS))
        body = Image.composite(_solid(size, shadow, alpha), body, inner_shadow)
        r2 = int(5 * SS)
        hl = _shift(m, -light_dir[0] * r2, -light_dir[1] * r2)
        rim = ImageChops.subtract(m, hl).filter(ImageFilter.GaussianBlur(3 * SS))
        rim = rim.point(lambda v: int(v * 0.8))
        body = Image.composite(_solid(size, light, alpha), body, rim)
    if grain:
        noise = Image.effect_noise(size, 22).point(lambda v: 255 if v > 150 else 0).filter(ImageFilter.GaussianBlur(SS))
        noise = noise.point(lambda v: int(v * 0.18))
        body = Image.composite(_solid(size, shadow, alpha), body, noise)
    canvas.alpha_composite(Image.composite(body, Image.new("RGBA", size, (0, 0, 0, 0)), m))


def fill(canvas, mask, color, alpha=255, blur=0):
    m = mask.img
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur * SS))
    if alpha < 255:
        m = m.point(lambda v: int(v * alpha / 255))
    canvas.alpha_composite(Image.composite(_solid(m.size, color), Image.new("RGBA", m.size, (0, 0, 0, 0)), m))


def glow(canvas, mask, color, radius=8, strength=1.0):
    m = mask.img.filter(ImageFilter.GaussianBlur(radius * SS))
    m = m.point(lambda v: min(255, int(v * strength)))
    canvas.alpha_composite(Image.composite(_solid(m.size, color), Image.new("RGBA", m.size, (0, 0, 0, 0)), m))


def new_canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def finish(canvas, w, h, path):
    img = canvas.resize((w, h), Image.LANCZOS)
    img.save(path, optimize=True)
    return img


def rng(seed):
    return random.Random(seed)
