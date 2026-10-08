#!/usr/bin/env python3
"""Compõe o Ossinho com os ossos dados (usa data/skeleton.json) para conferir os encaixes.
Uso: python3 tools/preview_body.py saida.png slot=bone_id ..."""
import json, os, sys, math
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sk = json.load(open(os.path.join(ROOT, "data", "skeleton.json")))
bones = {b["id"]: b for b in json.load(open(os.path.join(ROOT, "data", "bones.json")))}
eq = dict(sk["starting_bones"])
for a in sys.argv[2:]:
    k, v = a.split("=")
    eq[k] = v
S = 2  # pixels de preview por pixel de jogo
W, H = 360 * S, 420 * S
img = Image.new("RGBA", (W, H), (40, 32, 44, 255))
ox, oy = W // 2, H - 30 * S
parts = []
for p in sk["base_parts"]:
    parts.append((p["z"], p, p["id"], 0))
for s in sk["slots"]:
    if s["id"] in eq:
        parts.append((s["z"], s, eq[s["id"]], s.get("rest_rot", 0)))
lift = 0 if "slot_legs" in eq else 100
for z, s, art, rot in sorted(parts, key=lambda t: t[0]):
    path = os.path.join(ROOT, "art", "bones", art + ".png")
    if not os.path.exists(path):
        continue
    t = Image.open(path).convert("RGBA")
    r = bones.get(art, {}).get("rarity", "basic")
    sc = sk["rarity_scale"].get(r, 1.0) * sk["texture_scale"] * S
    t = t.resize((int(t.width * sc), int(t.height * sc)), Image.LANCZOS)
    px, py = s["pivot"][0] * sc, s["pivot"][1] * sc
    # rotação em torno do pivot (graus, horário como no Godot)
    if rot:
        big = Image.new("RGBA", (t.width * 3, t.height * 3))
        big.paste(t, (int(t.width * 1.5 - px), int(t.height * 1.5 - py)))
        big = big.rotate(-rot, center=(t.width * 1.5, t.height * 1.5), resample=Image.BICUBIC)
        t, px, py = big, t.width * 1.5, t.height * 1.5
    ax = ox + s["attach"][0] * S - px
    ay = oy + (s["attach"][1] + (lift if s["id"] != "slot_legs" else 0)) * S - py
    img.alpha_composite(t, (int(ax), int(ay)))
img.save(sys.argv[1])
