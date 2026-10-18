#!/usr/bin/env python3
"""Gera os sons e as músicas do Bone Tribe (placeholders sintetizados).

Cada arquivo leva o ID usado em data/audio.json. Para trocar pela versão final,
basta substituir o arquivo mantendo o nome (efeitos em WAV, músicas em OGG).

Uso: python3 tools/gen_audio.py [sfx|music|all]   (precisa de numpy, scipy e ffmpeg)
"""
import os
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR = 44100
RNG = np.random.default_rng(7)


# ------------------------------------------------------------ primitivas

def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def env(n, a=0.005, d=0.1, s=0.0, r=0.05, hold=0.0):
    """ADSR em segundos; o total é n amostras."""
    out = np.zeros(n)
    ia, id_, ih = int(a * SR), int(d * SR), int(hold * SR)
    ir = int(r * SR)
    i = 0
    seg = min(ia, n - i)
    out[i:i + seg] = np.linspace(0, 1, seg, endpoint=False) if seg > 0 else 0
    i += seg
    seg = min(id_, n - i)
    if seg > 0:
        out[i:i + seg] = np.linspace(1, s, seg, endpoint=False)
        i += seg
    seg = min(ih, n - i)
    if seg > 0:
        out[i:i + seg] = s
        i += seg
    seg = min(ir, n - i)
    if seg > 0:
        out[i:i + seg] = np.linspace(s, 0, seg)
        i += seg
    return out


def exp_env(n, tau):
    return np.exp(-np.arange(n) / (SR * tau))


def noise(n):
    return RNG.uniform(-1, 1, n)


def lp(x, f, order=2):
    b, a = butter(order, min(f / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = butter(order, max(f / (SR / 2), 0.0005), "high")
    return lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = butter(order, [max(lo / (SR / 2), 0.0005), min(hi / (SR / 2), 0.99)], "band")
    return lfilter(b, a, x)


def sweep_phase(f0, f1, n, curve=1.0):
    k = np.linspace(0, 1, n) ** curve
    f = f0 + (f1 - f0) * k
    return 2 * np.pi * np.cumsum(f) / SR


def sine(f, dur):
    return np.sin(2 * np.pi * f * t_axis(dur))


def tri(phase):
    return 2 / np.pi * np.arcsin(np.sin(phase))


def saw(f, n, detune=0.0):
    ph = (np.arange(n) * f * (1 + detune) / SR) % 1.0
    return 2 * ph - 1


def square(f, n, duty=0.5):
    ph = (np.arange(n) * f / SR) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def pluck(f, dur, damp=0.996, bright=0.5):
    """Karplus-Strong (corda/caixinha de música)."""
    n = int(SR * dur)
    p = max(2, int(SR / f))
    buf = lp(noise(p), 2000 + 6000 * bright, 1)
    out = np.zeros(n)
    for i in range(n):
        v = buf[i % p]
        out[i] = v
        buf[i % p] = damp * 0.5 * (v + buf[(i + 1) % p])
    return out


def bell(f, dur, ratios=(1, 2.76, 5.4, 8.93), decay=1.2):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for i, r in enumerate(ratios):
        out += np.sin(2 * np.pi * f * r * t) * np.exp(-t * (1.5 + i * 2.2) / decay) / (i + 1)
    return out


def click(n_len=0.02, f=3000, tau=0.004):
    n = int(SR * n_len)
    return bp(noise(n), f * 0.6, f * 1.6) * exp_env(n, tau)


def bone_clack(f=1400, tau=0.018, dur=0.12):
    """Batida seca de osso: clique ressonante + corpo amadeirado."""
    n = int(SR * dur)
    x = np.zeros(n)
    c = click(0.03, f * 2.2, 0.003)
    x[:len(c)] += c * 0.8
    t = np.arange(n) / SR
    x += np.sin(2 * np.pi * f * t) * exp_env(n, tau) * 0.6
    x += np.sin(2 * np.pi * f * 1.51 * t) * exp_env(n, tau * 0.6) * 0.35
    return x


def reverb(x, size=0.6, wet=0.25, damp=3500):
    n = int(SR * size)
    ir = noise(n) * np.exp(-np.arange(n) / (SR * size / 5))
    ir = lp(ir, damp, 1)
    ir[0] = 0
    y = np.convolve(x, ir) * (wet / np.sqrt(np.sum(ir ** 2)) * 0.6)
    out = np.zeros(len(y))
    out[: len(x)] += x
    return out + y


def mix(*parts, offsets=None):
    offsets = offsets or [0] * len(parts)
    n = max(int(o * SR) + len(p) for p, o in zip(parts, offsets))
    out = np.zeros(n)
    for p, o in zip(parts, offsets):
        i = int(o * SR)
        out[i:i + len(p)] += p
    return out


def norm(x, peak=0.89):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def fade(x, fin=0.002, fout=0.01):
    a, b = int(fin * SR), int(fout * SR)
    x = x.copy()
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def trim(x, thr=0.0015):
    idx = np.where(np.abs(x) > thr)[0]
    return x[: idx[-1] + 1] if len(idx) else x


def note(name):
    """'A4' -> Hz."""
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[pitch] + 12 * (octave - 4)) / 12)


def save_wav(name, x, peak=0.89):
    path = os.path.join(ROOT, "audio", "sfx", name + ".wav")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    y = fade(trim(norm(x, peak)))
    wavfile.write(path, SR, (y * 32767).astype(np.int16))


def save_ogg(name, x, peak=0.8):
    tmp = os.path.join(ROOT, "audio", "music", name + "_tmp.wav")
    out = os.path.join(ROOT, "audio", "music", name + ".ogg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    y = norm(x, peak)
    wavfile.write(tmp, SR, (y * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libvorbis", "-q:a", "3", "-ac", "1", out], check=True)
    os.remove(tmp)


# ------------------------------------------------------------- efeitos

def whoosh(dur=0.22, lo=500, hi=3500, up=True):
    n = int(SR * dur)
    x = noise(n)
    out = np.zeros(n)
    # filtro passa-banda que varre: soma de faixas com envelopes deslocados
    steps = 8
    for i in range(steps):
        f = lo + (hi - lo) * (i / (steps - 1) if up else 1 - i / (steps - 1))
        band = bp(x, f * 0.7, f * 1.3)
        w = np.exp(-((np.linspace(0, 1, n) - i / (steps - 1)) ** 2) / 0.03)
        out += band * w
    return out * env(n, 0.03, dur * 0.6, 0.0, dur * 0.3)


def sfx_all():
    # interface
    save_wav("ui_tap", mix(click(0.03, 2600, 0.004) * 0.6, bone_clack(1900, 0.008, 0.06) * 0.5), 0.6)
    save_wav("ui_open", mix(whoosh(0.18, 600, 2400) * 0.6, bone_clack(1200, 0.012, 0.1) * 0.4, offsets=[0, 0.08]), 0.6)
    save_wav("ui_close", mix(whoosh(0.15, 2400, 600, up=False) * 0.6), 0.5)
    save_wav("ui_error", mix(np.sin(sweep_phase(330, 220, int(SR * 0.18))) * env(int(SR * 0.18), 0.005, 0.15, 0, 0.02)), 0.55)
    save_wav("ui_buy", mix(bell(note("E6"), 0.5) * 0.5, bell(note("B6"), 0.6) * 0.5, offsets=[0, 0.07]), 0.7)
    save_wav("ui_claim", reverb(mix(*[bell(note(n), 0.7) * 0.45 for n in ["C6", "E6", "G6", "C7"]], offsets=[0, 0.06, 0.12, 0.18]), 0.5, 0.25), 0.75)
    # moedas
    save_wav("dust_gain", mix(*[bell(f, 0.35, (1, 3.1), 0.5) * 0.3 for f in (1900, 2400, 2100)], noise(int(SR * 0.25)) * 0.05 * exp_env(int(SR * 0.25), 0.05), offsets=[0, 0.04, 0.08, 0]), 0.55)
    save_wav("diamond_gain", reverb(mix(bell(note("A6"), 0.6) * 0.5, bell(note("E7"), 0.7) * 0.4, offsets=[0, 0.05]), 0.4, 0.3), 0.6)
    # combate
    for i, (lo, hi) in enumerate([(500, 3000), (400, 2600), (600, 3400)]):
        save_wav("swing_%d" % (i + 1), whoosh(0.16, lo, hi) * 0.8, 0.45)
    for i, f in enumerate([1250, 1080, 1420]):
        thud = np.sin(sweep_phase(160, 70, int(SR * 0.12))) * exp_env(int(SR * 0.12), 0.03)
        save_wav("hit_%d" % (i + 1), mix(bone_clack(f, 0.02, 0.14), thud * 0.7, lp(noise(int(SR * 0.08)), 2500) * exp_env(int(SR * 0.08), 0.012) * 0.6), 0.85)
    crit_ring = bell(2600, 0.5, (1, 2.4, 4.1), 0.6) * 0.35
    boom = np.sin(sweep_phase(220, 55, int(SR * 0.25))) * exp_env(int(SR * 0.25), 0.07)
    save_wav("hit_crit", mix(bone_clack(1000, 0.03, 0.2), boom * 0.9, crit_ring, lp(noise(int(SR * 0.15)), 4000) * exp_env(int(SR * 0.15), 0.02) * 0.7), 0.95)
    save_wav("hit_hero", mix(bone_clack(800, 0.03, 0.16), np.sin(sweep_phase(130, 60, int(SR * 0.16))) * exp_env(int(SR * 0.16), 0.04) * 0.9), 0.85)
    save_wav("miss", whoosh(0.24, 1500, 5000) * 0.7, 0.45)
    clank = bell(820, 0.5, (1, 2.71, 4.32, 6.1), 0.45)
    save_wav("block", mix(clank * 0.6, click(0.03, 3500, 0.004)), 0.7)
    n = int(SR * 0.22)
    bub = sum(np.sin(sweep_phase(f, f * 1.8, n // 3, 0.5)) * env(n // 3, 0.002, 0.07, 0, 0.0) for f in (300, 380))
    save_wav("poison_tick", mix(bub * 0.5, bub * 0.35, offsets=[0, 0.08]), 0.5)
    save_wav("bleed_tick", mix(lp(noise(int(SR * 0.12)), 1500) * exp_env(int(SR * 0.12), 0.03), np.sin(sweep_phase(300, 140, int(SR * 0.1))) * exp_env(int(SR * 0.1), 0.03) * 0.5), 0.5)
    save_wav("stun", mix(*[np.sin(sweep_phase(f, f * 1.25, int(SR * 0.09))) * env(int(SR * 0.09), 0.003, 0.08, 0, 0.0) for f in (1600, 1900, 1700, 2100)], offsets=[0, 0.08, 0.16, 0.24]), 0.5)
    save_wav("heal", reverb(mix(*[bell(note(n), 0.5, (1, 2.0), 0.5) * 0.4 for n in ["G5", "B5", "D6", "G6"]], offsets=[0, 0.05, 0.1, 0.15]), 0.4, 0.25), 0.55)
    n = int(SR * 0.7)
    eerie = (np.sin(sweep_phase(200, 420, n)) + 0.5 * np.sin(sweep_phase(203, 415, n))) * env(n, 0.15, 0.3, 0.4, 0.25)
    save_wav("summon", reverb(mix(eerie * 0.6, whoosh(0.5, 300, 1500) * 0.5), 0.7, 0.4), 0.65)
    save_wav("guard_up", mix(clank * 0.5, whoosh(0.2, 400, 1600) * 0.3), 0.6)
    shards = mix(*[bell(f, 0.35, (1, 2.9), 0.35) * 0.3 for f in (2200, 2900, 3500, 2500)], offsets=[0, 0.03, 0.06, 0.1])
    save_wav("guard_break", mix(shards, lp(noise(int(SR * 0.3)), 6000) * exp_env(int(SR * 0.3), 0.06) * 0.6, np.sin(sweep_phase(150, 60, int(SR * 0.2))) * exp_env(int(SR * 0.2), 0.05) * 0.6), 0.85)
    # mortes
    rattle = mix(*[bone_clack(RNG.uniform(900, 1800), 0.012, 0.08) * RNG.uniform(0.35, 0.7) for _ in range(9)],
                 offsets=list(np.cumsum(RNG.uniform(0.025, 0.06, 9)) - 0.03))
    save_wav("monster_die", mix(rattle, np.sin(sweep_phase(180, 70, int(SR * 0.3))) * exp_env(int(SR * 0.3), 0.08) * 0.5), 0.8)
    big = np.sin(sweep_phase(110, 35, int(SR * 1.2))) * exp_env(int(SR * 1.2), 0.35)
    save_wav("boss_die", reverb(mix(big * 1.0, rattle * 0.8, lp(noise(int(SR * 0.8)), 900) * exp_env(int(SR * 0.8), 0.2) * 0.8, rattle * 0.6, offsets=[0, 0.05, 0, 0.35]), 1.0, 0.35), 0.95)
    sad = mix(*[pluck(note(n), 0.8, 0.995, 0.3) * 0.5 for n in ["E4", "C4", "A3"]], offsets=[0.3, 0.55, 0.8])
    save_wav("hero_die", reverb(mix(rattle * 0.9, sad), 0.8, 0.3), 0.8)
    n = int(SR * 0.9)
    save_wav("revive", reverb(mix(np.sin(sweep_phase(220, 880, n, 0.7)) * env(n, 0.05, 0.6, 0.3, 0.25) * 0.5, whoosh(0.8, 300, 3000) * 0.5), 0.6, 0.3), 0.7)
    # especiais
    n = int(SR * 0.45)
    zap = (square(0, n) * 0 + np.sin(sweep_phase(1800, 500, n))) * env(n, 0.005, 0.35, 0.2, 0.1)
    save_wav("special_beam", mix(zap * 0.6, bp(noise(n), 2000, 6000) * env(n, 0.01, 0.4, 0.1, 0.05) * 0.4), 0.7)
    n = int(SR * 0.8)
    roar = lp(noise(n), 1200) * env(n, 0.06, 0.4, 0.5, 0.3)
    save_wav("special_fire", mix(roar, lp(noise(n), 300) * env(n, 0.05, 0.5, 0.3, 0.2) * 0.8, np.sin(sweep_phase(90, 60, n)) * env(n, 0.05, 0.5, 0.3, 0.2) * 0.4), 0.85)
    save_wav("special_punch", mix(np.sin(sweep_phase(120, 40, int(SR * 0.35))) * exp_env(int(SR * 0.35), 0.1), bone_clack(700, 0.04, 0.2) * 0.8, lp(noise(int(SR * 0.2)), 1800) * exp_env(int(SR * 0.2), 0.04) * 0.6), 0.95)
    save_wav("special_wave", reverb(mix(whoosh(0.7, 200, 1400) * 0.8, np.sin(sweep_phase(80, 50, int(SR * 0.6))) * env(int(SR * 0.6), 0.1, 0.4, 0.2, 0.1) * 0.6), 0.6, 0.3), 0.8)
    save_wav("special_extra", mix(*[bell(note(n), 0.3, (1, 2.0), 0.3) * 0.4 for n in ["A5", "E6"]], whoosh(0.2, 800, 3000) * 0.4, offsets=[0, 0.05, 0]), 0.6)
    # ossos
    save_wav("bone_drop", mix(bone_clack(1700, 0.015, 0.1), bone_clack(1500, 0.012, 0.08) * 0.6, bone_clack(1650, 0.01, 0.06) * 0.35, offsets=[0, 0.09, 0.15]), 0.6)
    save_wav("bone_fly", whoosh(0.45, 400, 2800) * 0.6, 0.4)
    sparkle = mix(*[bell(f, 0.4, (1, 2.6), 0.4) * 0.25 for f in (2800, 3500, 4200)], offsets=[0, 0.04, 0.08])
    save_wav("attach", reverb(mix(bone_clack(950, 0.04, 0.25), np.sin(sweep_phase(200, 90, int(SR * 0.18))) * exp_env(int(SR * 0.18), 0.05) * 0.8, sparkle, offsets=[0, 0, 0.03]), 0.4, 0.2), 0.9)
    n = int(SR * 0.45)
    grind = bp(noise(n), 300, 2400) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 38 * np.arange(n) / SR))) * env(n, 0.01, 0.3, 0.3, 0.1)
    save_wav("crush", mix(grind, rattle * 0.5, bone_clack(800, 0.02, 0.1) * 0.6), 0.75)
    save_wav("upgrade", reverb(mix(bell(note("C6"), 0.6) * 0.4, bell(note("G6"), 0.7) * 0.4, bell(note("C7"), 0.9) * 0.35, offsets=[0, 0.08, 0.16]), 0.5, 0.25), 0.7)
    anvil = bell(1250, 0.9, (1, 2.47, 3.93, 5.6), 0.8)
    save_wav("forge", mix(anvil * 0.7, click(0.03, 4000, 0.003), anvil * 0.4, offsets=[0, 0, 0.35]), 0.8)
    # progressão
    arp = mix(*[pluck(note(n), 0.6, 0.997, 0.7) * 0.5 for n in ["C5", "E5", "G5", "C6", "E6"]], offsets=[0, 0.07, 0.14, 0.21, 0.28])
    save_wav("levelup", reverb(mix(arp, bell(note("C7"), 0.8) * 0.3, offsets=[0, 0.3]), 0.6, 0.3), 0.8)
    n = int(SR * 2.2)
    chord = sum(saw(note(x), n, d) for x in ["A3", "E4", "A4", "C#5"] for d in (-0.004, 0.004)) / 8
    swell = lp(chord, 2500) * env(n, 0.8, 0.6, 0.6, 0.8)
    save_wav("form", reverb(mix(swell, whoosh(1.0, 200, 3000) * 0.5, bell(note("A6"), 1.2) * 0.3, offsets=[0, 0, 0.9]), 1.0, 0.35), 0.9)
    drum = lambda f: mix(np.sin(sweep_phase(f, f * 0.5, int(SR * 0.5))) * exp_env(int(SR * 0.5), 0.15), lp(noise(int(SR * 0.1)), 400) * exp_env(int(SR * 0.1), 0.02) * 0.5)
    n = int(SR * 1.1)
    growl = lp(saw(55, n) * (1 + 0.3 * np.sin(2 * np.pi * 9 * np.arange(n) / SR)), 700) * env(n, 0.2, 0.5, 0.5, 0.4)
    save_wav("boss_intro", reverb(mix(drum(90), drum(80), drum(70), growl * 0.7, offsets=[0, 0.35, 0.7, 0.6]), 1.2, 0.35), 0.95)
    save_wav("step", mix(lp(noise(int(SR * 0.06)), 900) * exp_env(int(SR * 0.06), 0.015), bone_clack(600, 0.01, 0.05) * 0.3), 0.35)
    save_wav("door", reverb(mix(lp(noise(int(SR * 0.5)), 600) * env(int(SR * 0.5), 0.05, 0.3, 0.2, 0.15) * 0.6, np.sin(sweep_phase(70, 50, int(SR * 0.4))) * exp_env(int(SR * 0.4), 0.12) * 0.6), 0.8, 0.3), 0.6)
    save_wav("event", mix(whoosh(0.25, 1200, 4000) * 0.5, bell(note("E6"), 0.4, (1, 2.0), 0.4) * 0.25, offsets=[0, 0.12]), 0.5)
    creak = bp(saw(70, int(SR * 0.45)) * (1 + 0.5 * np.sin(2 * np.pi * 23 * np.arange(int(SR * 0.45)) / SR)), 400, 1800) * env(int(SR * 0.45), 0.05, 0.3, 0.3, 0.1)
    save_wav("chest", reverb(mix(creak * 0.6, sparkle * 1.2, bell(note("G6"), 0.6) * 0.3, offsets=[0, 0.35, 0.4]), 0.5, 0.25), 0.75)
    save_wav("trap", mix(bell(500, 0.4, (1, 2.3, 3.7), 0.3) * 0.6, click(0.04, 3000, 0.006), lp(noise(int(SR * 0.15)), 2000) * exp_env(int(SR * 0.15), 0.03) * 0.5), 0.75)
    jingle = mix(*[pluck(note(n), 0.7, 0.997, 0.6) * 0.5 for n in ["G4", "C5", "E5", "G5", "E5", "G5", "C6"]], offsets=[0, 0.12, 0.24, 0.36, 0.52, 0.62, 0.78])
    save_wav("victory", reverb(mix(jingle, bell(note("C7"), 1.0) * 0.3, offsets=[0, 0.78]), 0.7, 0.3), 0.8)
    save_wav("defeat", reverb(mix(*[pluck(note(n), 0.9, 0.996, 0.35) * 0.5 for n in ["E4", "D4", "C4", "A3"]], offsets=[0, 0.25, 0.5, 0.8]), 0.8, 0.35), 0.7)
    big_arp = mix(*[pluck(note(n), 0.9, 0.998, 0.8) * 0.45 for n in ["C4", "G4", "C5", "E5", "G5", "C6", "E6", "G6"]], offsets=[i * 0.09 for i in range(8)])
    save_wav("tower_clear", reverb(mix(big_arp, swell * 0.5, bell(note("C7"), 1.4) * 0.35, offsets=[0, 0.1, 0.7]), 1.0, 0.35), 0.9)
    save_wav("mission", reverb(mix(bell(note("D6"), 0.5) * 0.4, bell(note("A6"), 0.7) * 0.4, offsets=[0, 0.1]), 0.5, 0.25), 0.65)
    save_wav("offline", reverb(mix(*[bell(f, 0.5, (1, 3.0), 0.5) * 0.3 for f in (1500, 1900, 2300, 2800, 3300)], offsets=[0, 0.07, 0.14, 0.21, 0.28]), 0.5, 0.3), 0.65)
    save_wav("hunter", reverb(mix(growl * 0.6, *[bell(f, 0.6, (1, 1.5), 0.5) * 0.25 for f in (300, 320)], offsets=[0, 0.1, 0.25]), 0.9, 0.35), 0.8)
    save_wav("tutorial", mix(bell(note("E6"), 0.4, (1, 2.0), 0.4) * 0.35, bell(note("B6"), 0.5, (1, 2.0), 0.4) * 0.3, offsets=[0, 0.08]), 0.5)
    print("sfx ok")


# ------------------------------------------------------------- músicas

def chord_notes(root, kind):
    iv = {"m": [0, 3, 7], "M": [0, 4, 7], "dim": [0, 3, 6], "sus": [0, 5, 7]}[kind]
    return [root * 2 ** (i / 12) for i in iv]


def pad(freqs, dur, cutoff=1400):
    n = int(SR * dur)
    x = sum(saw(f, n, d) for f in freqs for d in (-0.003, 0.003))
    return lp(x / (2 * len(freqs)), cutoff) * env(n, dur * 0.25, dur * 0.2, 0.8, dur * 0.3)


def kick(n_len=0.3):
    n = int(SR * n_len)
    return np.sin(sweep_phase(120, 45, n, 0.4)) * exp_env(n, 0.08)


def hat(n_len=0.05):
    n = int(SR * n_len)
    return hp(noise(n), 7000) * exp_env(n, 0.012)


def snare(n_len=0.18):
    n = int(SR * n_len)
    return bp(noise(n), 1200, 6000) * exp_env(n, 0.04) * 0.8 + np.sin(sweep_phase(220, 160, n)) * exp_env(n, 0.03) * 0.4


def render_loop(total, parts, tail=1.5):
    """parts: lista de (tempo, sinal). Faz o loop sem emenda somando a cauda no começo."""
    n = int(SR * total)
    out = np.zeros(n + int(SR * tail) + SR * 4)
    for t0, sig in parts:
        i = int(t0 * SR)
        out[i:i + len(sig)] += sig[: len(out) - i]
    loop = out[:n].copy()
    rest = out[n:]
    loop[: len(rest)] += rest[: n]
    return loop


def music_hub():
    # caixinha de música calma em Ré menor, 72 bpm, 16 compassos
    bpm, bars = 72, 16
    beat = 60 / bpm
    prog = [("D3", "m"), ("A#2", "M"), ("F3", "M"), ("A2", "M")] * 4
    mel = ["A4", "D5", "F5", "E5", "D5", "C5", "A4", "C5", "D5", "F5", "A5", "G5", "F5", "E5", "D5", "E5"]
    parts = []
    for b, (r, k) in enumerate(prog):
        t = b * 4 * beat
        notes = chord_notes(note(r), k)
        parts.append((t, pad([f for f in notes], 4 * beat + 0.5, 900) * 0.35))
        for i in range(8):
            f = notes[i % 3] * (2 if i >= 4 else 1) * 2
            parts.append((t + i * beat / 2, pluck(f, 1.2, 0.996, 0.45) * 0.16))
        m = note(mel[b % len(mel)])
        parts.append((t, bell(m, 2.5, (1, 2.0, 3.0), 2.0) * 0.18))
        parts.append((t, lp(np.sin(2 * np.pi * note(r) / 2 * t_axis(4 * beat)) * env(int(SR * 4 * beat), 0.05, 1.0, 0.6, 0.5), 400) * 0.3))
    x = render_loop(bars * 4 * beat, parts)
    return reverb(x, 1.8, 0.35)[: len(x)]


def music_crypt():
    # exploração misteriosa em Lá menor, 88 bpm, 16 compassos
    bpm, bars = 88, 16
    beat = 60 / bpm
    prog = [("A2", "m"), ("F2", "M"), ("D3", "m"), ("E2", "M")] * 4
    parts = []
    arp_pat = [0, 1, 2, 1, 0, 2, 1, 2]
    for b, (r, k) in enumerate(prog):
        t = b * 4 * beat
        notes = chord_notes(note(r), k)
        parts.append((t, pad([f * 2 for f in notes], 4 * beat + 0.4, 1100) * 0.3))
        for i, p in enumerate(arp_pat):
            parts.append((t + i * beat / 2, pluck(notes[p] * 4, 0.8, 0.995, 0.5) * 0.14))
        parts.append((t, lp(saw(note(r), int(SR * 4 * beat)) * env(int(SR * 4 * beat), 0.02, 0.5, 0.5, 0.3), 300) * 0.35))
        parts.append((t, kick(0.4) * 0.35))
        parts.append((t + 2 * beat, kick(0.4) * 0.25))
        for i in range(4):
            parts.append((t + i * beat + beat / 2, hat() * 0.05))
    x = render_loop(bars * 4 * beat, parts)
    return reverb(x, 1.4, 0.3)[: len(x)]


def music_combat():
    # combate em Mi menor, 124 bpm, 16 compassos, baixo marcado e bateria
    bpm, bars = 124, 16
    beat = 60 / bpm
    prog = [("E2", "m"), ("C2", "M"), ("G2", "M"), ("D2", "M")] * 4
    lead = ["E5", "G5", "B5", "A5", "G5", "F#5", "E5", "D5"]
    parts = []
    for b, (r, k) in enumerate(prog):
        t = b * 4 * beat
        root = note(r)
        notes = chord_notes(root, k)
        for i in range(8):
            f = root * (2 if i % 2 else 1)
            parts.append((t + i * beat / 2, lp(saw(f, int(SR * beat / 2)) * env(int(SR * beat / 2), 0.003, 0.15, 0.3, 0.05), 900) * 0.32))
        parts.append((t, pad([f * 2 for f in notes], 4 * beat, 1600) * 0.18))
        for i in range(4):
            parts.append((t + i * beat, kick() * (0.55 if i % 2 == 0 else 0.4)))
            if i % 2 == 1:
                parts.append((t + i * beat, snare() * 0.35))
            for j in range(2):
                parts.append((t + i * beat + j * beat / 2, hat() * 0.07))
        if b % 2 == 1:
            for i, n_ in enumerate(lead[(b // 2) % 2 * 4:(b // 2) % 2 * 4 + 4]):
                parts.append((t + i * beat, pluck(note(n_), 0.5, 0.993, 0.7) * 0.2))
    x = render_loop(bars * 4 * beat, parts)
    return reverb(x, 1.0, 0.22)[: len(x)]


def music_boss():
    # chefe em Dó menor, 136 bpm, timbales, órgão e baixo pesado
    bpm, bars = 136, 16
    beat = 60 / bpm
    prog = [("C2", "m"), ("C2", "m"), ("G#1", "M"), ("G1", "M")] * 4
    parts = []
    for b, (r, k) in enumerate(prog):
        t = b * 4 * beat
        root = note(r)
        notes = chord_notes(root, k)
        organ = sum(np.sin(2 * np.pi * f * h * t_axis(4 * beat)) / h for f in notes for h in (2, 4, 8))
        parts.append((t, lp(organ, 2500) * env(int(SR * 4 * beat), 0.05, 0.3, 0.7, 0.2) * 0.12))
        for i in range(16):
            if i % 4 != 3:
                parts.append((t + i * beat / 4, lp(saw(root, int(SR * beat / 4)) * env(int(SR * beat / 4), 0.002, 0.08, 0.2, 0.03), 700) * 0.3))
        for i in range(4):
            parts.append((t + i * beat, kick(0.35) * 0.6))
            parts.append((t + i * beat + beat / 2, hat() * 0.08))
            if i in (1, 3):
                parts.append((t + i * beat, snare(0.22) * 0.45))
        if b % 4 == 3:
            for i in range(4):
                parts.append((t + 3 * beat + i * beat / 4, np.sin(sweep_phase(140 - i * 15, 60, int(SR * 0.3))) * exp_env(int(SR * 0.3), 0.08) * 0.5))
        stab = chord_notes(root * 4, k)
        parts.append((t, sum(pluck(f, 0.4, 0.99, 0.9) for f in stab) * 0.08))
    x = render_loop(bars * 4 * beat, parts)
    return reverb(x, 1.2, 0.25)[: len(x)]


def music_all():
    save_ogg("music_hub", music_hub(), 0.7)
    save_ogg("music_crypt", music_crypt(), 0.7)
    save_ogg("music_combat", music_combat(), 0.75)
    save_ogg("music_boss", music_boss(), 0.78)
    print("music ok")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("sfx", "all"):
        sfx_all()
    if what in ("music", "all"):
        music_all()
