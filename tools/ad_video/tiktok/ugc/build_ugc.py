#!/usr/bin/env python3
"""Vídeo UGC: abertura com o avatar (vídeo do usuário, marca da PixVerse mantida), zoom no
celular e gameplay dentro de um celular desenhado, cortes no ritmo da música."""
import subprocess, sys
W, H = 1080, 1920
U, T, OUT = sys.argv[1], sys.argv[2], sys.argv[3]   # pasta ugc, pasta tiktok (gravações, música, cartão final)
SONG = 16.1
AV_DUR = 2.04
INTRO = 2.25                     # avatar + zoom no celular (até a batida)
PX, PY = 50, 110                 # posição da imagem do celular
SX, SY, SW, SH = PX + 76, PY + 80, 828, 1472
segs = [("demo", 5.6, 0.91), ("demo", 12.6, 0.91), ("demo", 29.1, 0.9), ("demo", 36.0, 1.82), ("demo", 37.9, 0.9),
        ("elite", 3.9, 1.81), ("elite", 11.85, 0.91), ("cursed", 1.4, 0.9), ("demo", 56.6, 1.82)]
end_at = INTRO + sum(s[2] for s in segs)
caps = [("u1", 0.3, 1.25, 1380), ("u2", 1.25, INTRO, 1380), ("u3", 2.25, 4.97, 560), ("u4", 4.97, 7.69, 560),
        ("u5", 7.69, 10.41, 560), ("u6", 10.41, 11.31, 560), ("u7", 11.31, end_at, 560)]
inp, fc = [], []
inp += ["-i", f"{U}/in/avatar.mp4"]                       # 0
for src, st, du in segs:
    inp += ["-ss", str(st), "-t", str(du), "-i", f"{T}/rec/{src}.avi"]
n = len(segs)
k = 1 + n
inp += ["-ss", "65.0", "-t", str(SONG - end_at), "-i", f"{T}/rec/demo.avi"]; endsrc = k; k += 1
idx = {}
for name in ["phone", "aitag"] + [c[0] for c in caps]:
    inp += ["-loop", "1", "-t", str(SONG), "-i", f"{U}/ov/{name}.png"]; idx[name] = k; k += 1
inp += ["-loop", "1", "-t", str(SONG), "-i", f"{T}/ov/end.png"]; endc = k; k += 1
inp += ["-i", f"{T}/song.wav"]; song = k; k += 1

# abertura: vídeo inteiro (870x1920, marca d'água visível) sobre fundo desfocado; depois congela e aproxima o celular
z = 0.21
fc.append(f"[0:v]fps=30,scale=870:1920,setsar=1,tpad=stop_mode=clone:stop_duration={z},split[av][avb]")
fc.append(f"[avb]scale={W}:{H},boxblur=30:2,eq=brightness=-0.15[avbg]")
fc.append(f"[avbg][av]overlay=(W-w)/2:0[avc]")
# aproximação no celular que ela segura (~72% x, 49% y do quadro) nos últimos {z}s
fc.append(f"[avc]scale=w='{W}*(1+3*max(0,t-{AV_DUR})/{z})':h='{H}*(1+3*max(0,t-{AV_DUR})/{z})':eval=frame,crop={W}:{H}:x='(iw-{W})*0.70':y='(ih-{H})*0.47',setsar=1,trim=duration={INTRO},setpts=PTS-STARTPTS,format=yuv420p[v0]")
fc.append(f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={INTRO},atrim=duration={INTRO},asetpts=PTS-STARTPTS[voz]")
fc.append(f"anullsrc=r=44100:cl=stereo,atrim=duration={INTRO}[a0]")
# trechos de gameplay dentro do celular, com zoom lento para a ação
for i, (src, st, du) in enumerate(segs, start=1):
    label = ",delogo=x=330:y=182:w=420:h=46" if src == "demo" else ""
    fc.append(f"[{i}:v]setsar=1{label},split[g{i}][b{i}]")
    fc.append(f"[b{i}]scale={W}:{H},boxblur=34:2,eq=brightness=-0.28[bg{i}]")
    fc.append(f"[g{i}]scale={SW}:{SH},scale=w='{SW}*(1+0.12*t/{du})':h='{SH}*(1+0.12*t/{du})':eval=frame,crop={SW}:{SH}:x='(iw-{SW})/2':y='(ih-{SH})*0.42',setsar=1[s{i}]")
    fc.append(f"[bg{i}][s{i}]overlay={SX}:{SY}[c{i}]")
    fc.append(f"[c{i}][{idx['phone']}:v]overlay={PX}:{PY}:shortest=1,trim=duration={du},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
    fc.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={du},atrim=duration={du},asetpts=PTS-STARTPTS[a{i}]")
e = n + 1
fc.append(f"[{endsrc}:v]setsar=1,delogo=x=330:y=182:w=420:h=46,scale={W}:{H},trim=duration={SONG - end_at},setpts=PTS-STARTPTS,format=yuv420p[v{e}]")
fc.append(f"[{endsrc}:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={SONG - end_at},atrim=duration={SONG - end_at},asetpts=PTS-STARTPTS[a{e}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(e + 1)) + f"concat=n={e + 1}:v=1:a=1[vc][ac]")
cuts, t = [INTRO], INTRO
for s in segs:
    t += s[2]; cuts.append(round(t, 3))
flash = "+".join(f"between(t,{c},{c + 0.06})" for c in cuts)
fc.append(f"[vc]drawbox=x=0:y=0:w={W}:h={H}:color=white@0.25:t=fill:enable='{flash}'[vf]")
cur = "vf"
fc.append(f"[{idx['aitag']}:v]format=rgba[tag]")
fc.append(f"[{cur}][tag]overlay=24:60:enable='lt(t,{AV_DUR})'[vt]"); cur = "vt"
for name, t0, t1, y in caps:
    fc.append(f"[{idx[name]}:v]format=rgba,fade=t=in:st={t0}:d=0.1:alpha=1,fade=t=out:st={t1 - 0.08}:d=0.08:alpha=1[k{name}]")
    fc.append(f"[{cur}][k{name}]overlay=x=(W-w)/2:y={y}:enable='between(t,{t0},{t1})'[o{name}]"); cur = f"o{name}"
fc.append(f"[{endc}:v]format=rgba,fade=t=in:st={end_at}:d=0.25:alpha=1[endc]")
fc.append(f"[{cur}][endc]overlay=0:0:enable='gte(t,{end_at})',format=yuv420p[vout]")
# áudio: voz dela na abertura; música baixa por baixo da fala e cheia depois
fc.append(f"[{song}:a]loudnorm=I=-14:TP=-1.5:LRA=11,aformat=sample_rates=44100:channel_layouts=stereo,volume='if(lt(t,{AV_DUR}),0.35,1)':eval=frame[mus]")
fc.append(f"[voz]loudnorm=I=-14:TP=-1.5,apad=whole_dur={SONG}[vz]")
fc.append(f"[ac]volume=0.14[gam]")
fc.append(f"[mus][vz][gam]amix=inputs=3:duration=first:normalize=0,afade=t=out:st={SONG - 0.35}:d=0.35,alimiter=limit=0.95[aout]")
cmd = ["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-t", str(SONG),
       "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print(OUT, "fim do gameplay em", round(end_at, 2))
