# Original background track for the ad: 120 BPM, A minor, Am-F-C-G loop.
# Quiet filtered intro + riser until the hook "drop", full beat after, fade at the end.
import sys
import numpy as np
import soundfile as sf

SR = 44100
BPM = 120
BEAT = 60 / BPM
TOTAL = float(sys.argv[2]) if len(sys.argv) > 2 else 43.0
DROP = float(sys.argv[3]) if len(sys.argv) > 3 else 2.4
END_FADE = float(sys.argv[4]) if len(sys.argv) > 4 else 40.3
N = int(TOTAL * SR)
rng = np.random.default_rng(7)

def t_arr(d):
    return np.arange(int(d * SR)) / SR

def add(buf, sig, start):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]

def lowpass(x, cutoff):
    # one-pole low-pass, good enough for soft synth tones
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k in range(len(x)):
        acc = (1 - a) * x[k] + a * acc
        y[k] = acc
    return y

def highpass(x, cutoff):
    return x - lowpass(x, cutoff)

def saw(freq, d, detune=0.0):
    t = t_arr(d)
    f = freq * (1 + detune)
    return 2 * ((t * f) % 1.0) - 1

def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

# --- instruments -----------------------------------------------------------
def kick():
    t = t_arr(0.35)
    f = 50 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.95

def clap():
    t = t_arr(0.22)
    n = highpass(rng.standard_normal(len(t)), 900)
    env = np.exp(-t * 22) + 0.5 * np.exp(-((t - 0.012) ** 2) / 1e-5)
    return n * env * 0.24

def hat(open_=False):
    d = 0.16 if open_ else 0.05
    t = t_arr(d)
    n = highpass(rng.standard_normal(len(t)), 6500)
    return n * np.exp(-t * (18 if open_ else 70)) * (0.08 if open_ else 0.055)

def bass(freq, d):
    t = t_arr(d)
    s = 0.6 * np.sin(2 * np.pi * freq * t) + 0.4 * lowpass(saw(freq, d), 380)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 3.2)
    return s * env * 0.42

def pluck(freqs, d):
    t = t_arr(d)
    s = sum(saw(f, d, 0.004) + saw(f, d, -0.004) for f in freqs) / (2 * len(freqs))
    s = lowpass(s, 2200)
    env = np.minimum(1, t / 0.005) * np.exp(-t * 7)
    return s * env * 0.30

def pad(freqs, d):
    t = t_arr(d)
    s = sum(saw(f, d, 0.006) + saw(f, d, -0.006) for f in freqs) / (2 * len(freqs))
    s = lowpass(s, 900)
    env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.3)
    return s * env * 0.22

# --- arrangement -----------------------------------------------------------
# Am, F, C, G (one bar = 4 beats = 2 s each)
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
roots = [45, 41, 48, 43]

drums = np.zeros(N)
bassb = np.zeros(N)
keys = np.zeros(N)
padb = np.zeros(N)
fx = np.zeros(N)

# intro: soft pad + riser into the drop
padb_intro = pad([note(n + 12) for n in chords[0]], DROP + 0.2)
add(padb, padb_intro * 0.9, 0)
rt = t_arr(DROP)
riser = highpass(rng.standard_normal(len(rt)), 2500) * (rt / DROP) ** 3 * 0.35
add(fx, riser, 0)
# downlifter boom on the drop
bt = t_arr(1.2)
add(fx, np.sin(2 * np.pi * (45 + 30 * np.exp(-bt * 6)) * bt) * np.exp(-bt * 3) * 0.8, DROP)

beat_i = 0
t = DROP
while t < END_FADE + 2.0:
    bar = beat_i // 4
    pos = beat_i % 4
    ci = bar % 4
    add(drums, kick(), t)
    if pos in (1, 3):
        add(drums, clap(), t)
    add(drums, hat(), t)
    add(drums, hat(open_=(pos == 3)), t + BEAT / 2)
    # bass: 8th-note pulse on the root, octave jump on the last 8th
    add(bassb, bass(note(roots[ci]), BEAT / 2 * 0.95), t)
    add(bassb, bass(note(roots[ci] + (12 if pos == 3 else 0)), BEAT / 2 * 0.95), t + BEAT / 2)
    # plucked chord stabs, syncopated
    if pos in (0, 2):
        add(keys, pluck([note(n + 12) for n in chords[ci]], BEAT * 0.9), t + BEAT / 2)
    if pos == 3:
        add(keys, pluck([note(n + 12) for n in chords[ci]], BEAT * 0.6), t + BEAT * 0.75)
    if pos == 0:
        add(padb, pad([note(n) for n in chords[ci]], BEAT * 4), t)
    beat_i += 1
    t += BEAT

# sidechain: duck bass/keys/pad under every kick
side = np.ones(N)
st = t_arr(0.3)
duck = 1 - 0.55 * np.exp(-st * 14)
k = DROP
while k < TOTAL:
    i = int(k * SR)
    j = min(N, i + len(duck))
    side[i:j] = np.minimum(side[i:j], duck[: j - i])
    k += BEAT

mix = drums + (bassb + keys + padb) * side + fx

# fade out at the end
tt = np.arange(N) / SR
fade = np.clip((TOTAL - tt) / (TOTAL - END_FADE), 0, 1)
mix *= fade
mix = np.tanh(mix * 1.2)  # gentle saturation / limiting
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89  # ~ -1 dBFS peak

stereo = np.stack([mix, mix], axis=1)
sf.write(sys.argv[1], stereo.astype(np.float32), SR, subtype='PCM_16')
print('wrote', sys.argv[1], f'{TOTAL:.1f}s')
