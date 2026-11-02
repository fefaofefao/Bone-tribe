#!/usr/bin/env python3
"""Monta os 3 anúncios em inglês (A 10 s, B 15 s, C 20 s), vertical e horizontal."""
import subprocess
import sys

D = sys.argv[1]
SFX = sys.argv[2]
WORLD = (90, 215, 900, 1010)       # área do mundo do jogo (sem HUD, rótulo e painel)
HUB = (0, 100, 1080, 1212)          # tela do Ossuário (mesma proporção)
BOSS = (90, 215, 900, 840)          # lutas com chefe: o painel é mais alto, recorte mais baixo

# trecho: (arquivo, início, duração, recorte)
ADS = {
    "A": {
        "segs": [("demo", 5.7, 1.6, WORLD), ("demo", 12.45, 1.25, WORLD), ("demo", 29.4, 1.25, WORLD),
                 ("demo", 36.5, 2.7, WORLD), ("demo", 50.5, 0.7, WORLD), ("demo", 55.5, 1.15, BOSS)],
        "end": ("demo", 56.65, 1.35, "endA"),
        "caps": [("a1", 0.0, 1.6, "top"), ("a2", 1.6, 4.1, "top"), ("a3", 4.1, 6.8, "top"), ("a4", 6.8, 8.65, "top")],
        "sfx": [],
    },
    "B": {
        "segs": [("demo", 3.3, 2.2, WORLD), ("demo", 5.8, 1.3, WORLD), ("demo", 29.5, 1.3, WORLD), ("demo", 35.6, 1.4, WORLD),
                 ("demo", 37.0, 3.0, WORLD), ("demo", 52.3, 1.6, BOSS), ("demo", 55.4, 1.6, BOSS)],
        "end": ("demo", 57.0, 2.6, "endB"),
        "caps": [("combo", 0.0, 6.2, "top_big"), ("b1", 0.0, 2.2, "low"), ("b2", 7.6, 9.4, "top"), ("b3", 9.4, 12.4, "top")],
        "sfx": [],
    },
    "C": {
        "segs": [("lose", 16.5, 3.0, BOSS), ("ossuary", 0.5, 2.6, HUB), ("demo", 5.7, 1.4, WORLD), ("demo", 12.5, 1.2, WORLD),
                 ("demo", 29.4, 1.2, WORLD), ("demo", 35.7, 1.0, WORLD), ("demo", 37.0, 2.8, WORLD), ("demo", 50.5, 0.8, WORLD),
                 ("demo", 52.3, 1.2, BOSS), ("demo", 55.4, 1.8, BOSS)],
        "end": ("demo", 57.2, 3.0, "endC"),
        "caps": [("c1", 0.0, 3.0, "top"), ("c2", 3.0, 5.6, "top"), ("c3", 5.6, 10.4, "top"), ("c4", 10.4, 13.2, "top"),
                 ("c5", 15.0, 17.0, "top")],
        "sfx": [(3.5, "upgrade"), (4.2, "upgrade"), (4.9, "dust_gain")],
    },
}


def build(ad: str, kind: str) -> str:
    cfg = ADS[ad]
    vertical = kind == "v"
    W, H = (1080, 1920) if vertical else (1920, 1080)
    segs = cfg["segs"] + [(cfg["end"][0], cfg["end"][1], cfg["end"][2], BOSS)]
    end_at = sum(s[2] for s in cfg["segs"])
    total = end_at + cfg["end"][2]
    inputs, fc = [], []
    for src, st, du, _ in segs:
        inputs += ["-ss", str(st), "-t", str(du), "-i", f"{D}/{src}.avi"]
    n = len(segs)
    k = n
    idx = {}
    names = [c[0] for c in cfg["caps"]] + ["strip", cfg["end"][3]] + ([] if vertical else ["bg"])
    for name in names:
        path = f"{D}/ov/{name}.png" if name == "bg" else f"{D}/ov/{name}_{kind}.png"
        if name == "bg":
            path = f"{D}/ov/bg_h.png"
        inputs += ["-loop", "1", "-t", str(total), "-i", path]
        idx[name] = k
        k += 1
    sfx_idx = []
    for t, s in cfg["sfx"] + [(end_at, "tower_clear")]:
        inputs += ["-i", f"{SFX}/{s}.wav"]
        sfx_idx.append((k, t))
        k += 1

    for i, (src, st, du, (cx, cy, cw, ch)) in enumerate(segs):
        if vertical:
            gh = int(ch * W / cw) // 2 * 2
            gy = 400 + max(0, (1240 - gh) // 2)
            fc.append(f"[{i}:v]split[a{i}][b{i}]")
            fc.append(f"[a{i}]crop={cw}:{ch}:{cx}:{cy},scale={W}:{gh},setsar=1[g{i}]")
            fc.append(f"[b{i}]crop={cw}:{ch}:{cx}:{cy},scale={W}:{H},setsar=1,boxblur=28:2,eq=brightness=-0.18[bg{i}]")
            fc.append(f"[bg{i}][g{i}]overlay=0:{gy},format=yuv420p[v{i}]")
        else:
            gw, gh = int(cw * H / ch) // 2 * 2, H
            if gw > 962:
                gw, gh = 962, int(ch * 962 / cw) // 2 * 2
            fc.append(f"[{idx['bg']}:v]trim=duration={du},setpts=PTS-STARTPTS,scale={W}:{H},setsar=1[bgs{i}]")
            fc.append(f"[{i}:v]crop={cw}:{ch}:{cx}:{cy},scale={gw}:{gh},setsar=1[g{i}]")
            fc.append(f"[bgs{i}][g{i}]overlay={70 + (962 - gw) // 2}:{(H - gh) // 2},format=yuv420p[v{i}]")
        f = 0.04
        fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,afade=t=in:d={f},afade=t=out:st={du - f}:d={f},apad=whole_dur={du},atrim=duration={du}[s{i}]")
    fc.append("".join(f"[v{i}][s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    cur = "vc"
    for name, t0, t1, where in cfg["caps"]:
        i = idx[name]
        fc.append(f"[{i}:v]format=rgba,fade=t=in:st={t0}:d=0.15:alpha=1,fade=t=out:st={t1 - 0.12}:d=0.12:alpha=1[c_{name}]")
        if vertical:
            pos = {"top": "x=(W-w)/2:y=70", "top_big": "x=(W-w)/2:y=0", "low": "x=(W-w)/2:y=430"}[where]
        else:
            pos = {"top": "x=1040+(880-w)/2:y=150", "top_big": "x=1040+(880-w)/2:y=110", "low": "x=1040+(880-w)/2:y=560"}[where]
        fc.append(f"[{cur}][c_{name}]overlay={pos}:enable='between(t,{t0},{t1})'[o_{name}]")
        cur = f"o_{name}"
    spos = f"x=0:y={H - 280}" if vertical else f"x=1040+(880-w)/2:y={H - 260}"
    fc.append(f"[{cur}][{idx['strip']}:v]overlay={spos}:enable='lt(t,{end_at})'[o_strip]")
    endn = cfg["end"][3]
    fc.append(f"[{idx[endn]}:v]format=rgba,fade=t=in:st={end_at}:d=0.3:alpha=1[endc]")
    fc.append(f"[o_strip][endc]overlay=0:0:enable='gte(t,{end_at})',format=yuv420p[vout]")
    mixes = ["[ac]"]
    for j, (si, t) in enumerate(sfx_idx):
        ms = int(t * 1000)
        fc.append(f"[{si}:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms},volume=0.85[x{j}]")
        mixes.append(f"[x{j}]")
    fc.append("".join(mixes) + f"amix=inputs={len(mixes)}:duration=first:normalize=0,afade=t=out:st={total - 0.3}:d=0.3,alimiter=limit=0.95[aout]")
    orient = "vertical_9x16" if vertical else "horizontal_16x9"
    secs = int(round(total))
    out = f"{D}/BoneTribe_ad_{ad}_{secs}s_{orient}.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
           "-t", str(total), "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    return out


for ad in (sys.argv[3] if len(sys.argv) > 3 else "ABC"):
    for kind in ("v", "h"):
        print(build(ad, kind))
