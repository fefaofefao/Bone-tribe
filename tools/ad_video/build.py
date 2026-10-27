#!/usr/bin/env python3
"""Monta os anúncios de 10 s (vertical 1080x1920 e horizontal 1920x1080) a partir da gravação do jogo."""
import subprocess
import sys

D = sys.argv[1]
SFX = sys.argv[2]  # pasta audio/sfx do jogo
RAW = f"{D}/raw.avi"
# (início na gravação, duração) — ordem do anúncio
SEGS = [(5.7, 1.6), (12.45, 1.25), (29.4, 1.25), (36.2, 2.6), (53.35, 0.65), (58.55, 1.15)]
END_SRC, END_DUR = (59.7, 1.5)
# legendas no tempo do anúncio
CAPS = [("cap1", 0.0, 1.6), ("cap2", 1.6, 4.1), ("cap3", 4.1, 6.7), ("cap4", 6.7, 8.5)]
END_AT = sum(d for _, d in SEGS)  # 8.5
TOTAL = END_AT + END_DUR  # 10.0
# área do mundo do jogo na gravação (sem HUD, sem o rótulo de demonstração e sem o painel)
WX, WY, WW, WH = 90, 215, 900, 1010


def build(kind: str) -> None:
    vertical = kind == "v"
    W, H = (1080, 1920) if vertical else (1920, 1080)
    inputs = []
    fc = []
    segs = SEGS + [(END_SRC, END_DUR)]
    for i, (st, du) in enumerate(segs):
        inputs += ["-ss", str(st), "-t", str(du), "-i", RAW]
    n = len(segs)
    ov = {}
    for name in ["cap1", "cap2", "cap3", "cap4", "end", "strip"]:
        ov[name] = len(inputs) // 6 if False else None
    extra = []
    for name in ["cap1", "cap2", "cap3", "cap4"]:
        extra.append((name, f"{D}/ov/{name}_{kind}.png"))
    extra.append(("end", f"{D}/ov/end_{kind}.png"))
    extra.append(("strip", f"{D}/ov/strip_{kind}.png"))
    if not vertical:
        extra.append(("bg", f"{D}/ov/bg_h.png"))
    idx = {}
    k = n
    for name, path in extra:
        inputs += ["-loop", "1", "-t", str(TOTAL), "-i", path]
        idx[name] = k
        k += 1
    inputs += ["-i", f"{SFX}/tower_clear.wav"]
    jingle = k

    # cada trecho: jogo recortado e ampliado sobre um fundo
    for i in range(n):
        if vertical:
            gw = W
            gh = int(WH * W / WW)  # 1218
            fc.append(f"[{i}:v]split[a{i}][b{i}]")
            fc.append(f"[a{i}]crop={WW}:{WH}:{WX}:{WY},scale={gw}:{gh},setsar=1[g{i}]")
            fc.append(f"[b{i}]crop=1080:{WH}:0:{WY},scale={W}:{H},boxblur=28:2,eq=brightness=-0.18[bg{i}]")
            fc.append(f"[bg{i}][g{i}]overlay=0:400,format=yuv420p[v{i}]")
        else:
            gh = H
            gw = int(WW * H / WH)  # 958
            fc.append(f"[{idx['bg']}:v]trim=duration={segs[i][1]},setpts=PTS-STARTPTS,scale={W}:{H}[bgs{i}]")
            fc.append(f"[{i}:v]crop={WW}:{WH}:{WX}:{WY},scale={gw}:{gh},setsar=1[g{i}]")
            fc.append(f"[bgs{i}][g{i}]overlay=70:0,format=yuv420p[v{i}]")
        fade = 0.04
        du = segs[i][1]
        fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,afade=t=in:d={fade},afade=t=out:st={du - fade}:d={fade},apad=whole_dur={du},atrim=duration={du}[s{i}]")
    fc.append("".join(f"[v{i}][s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    cur = "vc"
    # legendas (entram com um leve "pop" de opacidade)
    for name, t0, t1 in CAPS:
        i = idx[name]
        fc.append(f"[{i}:v]format=rgba,fade=t=in:st={t0}:d=0.15:alpha=1,fade=t=out:st={t1 - 0.12}:d=0.12:alpha=1[{name}]")
        if vertical:
            pos = "x=(W-w)/2:y=70"
        else:
            pos = f"x=1040+(880-w)/2:y=150"
        fc.append(f"[{cur}][{name}]overlay={pos}:enable='between(t,{t0},{t1})'[o_{name}]")
        cur = f"o_{name}"
    # faixa fixa com ícone e "Jogar"
    i = idx["strip"]
    spos = f"x=0:y={H - 280}" if vertical else "x=1040+(880-w)/2:y=" + str(H - 260)
    fc.append(f"[{cur}][{i}:v]overlay={spos}:enable='lt(t,{END_AT})'[o_strip]")
    cur = "o_strip"
    # tela final
    i = idx["end"]
    fc.append(f"[{i}:v]format=rgba,fade=t=in:st={END_AT}:d=0.3:alpha=1[endc]")
    fc.append(f"[{cur}][endc]overlay=0:0:enable='gte(t,{END_AT})',format=yuv420p[vout]")
    # áudio: jogo + vinheta de vitória na tela final
    fc.append(f"[{jingle}:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay={int(END_AT * 1000)}|{int(END_AT * 1000)},volume=0.9[jg]")
    fc.append(f"[ac][jg]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={TOTAL - 0.3}:d=0.3,alimiter=limit=0.95[aout]")
    out = f"{D}/BoneTribe_anuncio_{'vertical_9x16' if vertical else 'horizontal_16x9'}.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
           "-t", str(TOTAL), "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(out)


for k in sys.argv[3:] or ["v", "h"]:
    build(k)
