#!/usr/bin/env python3
"""Monta o vídeo do TikTok (1080x1920) com a música do usuário, cortes no ritmo."""
import json, subprocess, sys

D = sys.argv[1]            # pasta com rec/, ov/ e song.wav
SEGS = json.load(open(sys.argv[2]))   # lista de trechos e legendas
OUT = sys.argv[3]
W, H = 1080, 1920
WORLD = (60, 292, 960, 935)
BOSS = (60, 292, 960, 760)
crops = {"world": WORLD, "boss": BOSS, "panel": (0, 600, 1080, 1290), "ui": (0, 90, 1080, 1250)}

segs = SEGS["segs"]
end = SEGS["end"]
caps = SEGS["caps"]
song_len = float(SEGS["song_len"])
end_at = sum(s["dur"] for s in segs)
end_dur = song_len - end_at
allsegs = segs + [{"src": end["src"], "start": end["start"], "dur": end_dur, "crop": "world"}]

inputs, fc = [], []
for s in allsegs:
    # freeze: congela o quadro do início do trecho (perguntas para o público)
    inputs += ["-ss", str(s["start"]), "-t", str(0.1 if s.get("freeze") else s["dur"]), "-i", f"{D}/rec/{s['src']}.avi"]
n = len(allsegs)
k = n
idx = {}
for c in caps:
    inputs += ["-loop", "1", "-t", str(song_len), "-i", f"{D}/ov/{c['img']}.png"]
    idx[c["img"] + str(c["t0"])] = k
    k += 1
inputs += ["-loop", "1", "-t", str(song_len), "-i", f"{D}/ov/end.png"]
end_i = k; k += 1
inputs += ["-i", f"{D}/song.wav"]
song_i = k; k += 1

for i, s in enumerate(allsegs):
    fz = f",tpad=stop_mode=clone:stop_duration={s['dur']}" if s.get("freeze") else ""
    if s.get("crop") == "full":
        fc.append(f"[{i}:v]scale={W}:{H},setsar=1{fz},format=yuv420p,trim=duration={s['dur']},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={s['dur']},atrim=duration={s['dur']},asetpts=PTS-STARTPTS[s{i}]")
        continue
    cx, cy, cw, ch = crops[s.get("crop", "world")]
    # cabe na faixa de 430 a 1520 (acima da interface do TikTok embaixo)
    f = min(W / cw, 1090 / ch)
    gw = int(cw * f) // 2 * 2
    gh = int(ch * f) // 2 * 2
    gy = 430 + max(0, (1090 - gh) // 2)
    gx = (W - gw) // 2
    fc.append(f"[{i}:v]split[a{i}][b{i}]".replace("split", "split") if not fz else f"[{i}:v]tpad=stop_mode=clone:stop_duration={s['dur']},split[a{i}][b{i}]")
    # zoom leve no começo de cada corte (sensação de batida)
    fc.append(f"[a{i}]crop={cw}:{ch}:{cx}:{cy},scale={gw}:{gh},setsar=1[g{i}]")
    fc.append(f"[b{i}]crop={cw}:{ch}:{cx}:{cy},scale={W}:{H},setsar=1,boxblur=30:2,eq=brightness=-0.2[bg{i}]")
    fc.append(f"[bg{i}][g{i}]overlay={gx}:{gy},format=yuv420p,trim=duration={s['dur']},setpts=PTS-STARTPTS[v{i}]")
    fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={s['dur']},atrim=duration={s['dur']},asetpts=PTS-STARTPTS[s{i}]")
fc.append("".join(f"[v{i}][s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
# flash branco curto em cada corte (no ritmo)
cuts = []
t = 0.0
for s in segs:
    t += s["dur"]
    cuts.append(round(t, 3))
flash = "+".join(f"between(t,{c},{c + 0.06})" for c in cuts)
fc.append(f"[vc]eq=brightness=0:eval=frame,drawbox=x=0:y=0:w={W}:h={H}:color=white@0.22:t=fill:enable='{flash}'[vf]")
cur = "vf"
for c in caps:
    i = idx[c["img"] + str(c["t0"])]
    nm = f"c{i}"
    fc.append(f"[{i}:v]format=rgba,fade=t=in:st={c['t0']}:d=0.12:alpha=1,fade=t=out:st={c['t1'] - 0.1}:d=0.1:alpha=1[{nm}]")
    fc.append(f"[{cur}][{nm}]overlay=x=(W-w)/2:y={c.get('y', 250)}:enable='between(t,{c['t0']},{c['t1']})'[o{nm}]")
    cur = f"o{nm}"
fc.append(f"[{end_i}:v]format=rgba,fade=t=in:st={end_at}:d=0.25:alpha=1[endc]")
fc.append(f"[{cur}][endc]overlay=0:0:enable='gte(t,{end_at})',format=yuv420p[vout]")
# áudio: a música manda; o som do jogo fica bem baixo por baixo
fc.append(f"[{song_i}:a]loudnorm=I=-14:TP=-1.5:LRA=11,aformat=sample_rates=44100:channel_layouts=stereo[mus]")
fc.append(f"[ac]volume=0.16[gam]")
fc.append(f"[mus][gam]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={song_len - 0.35}:d=0.35,alimiter=limit=0.95[aout]")
cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
       "-t", str(song_len), "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print(OUT)
