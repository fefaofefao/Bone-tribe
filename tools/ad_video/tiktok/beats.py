import sys, numpy as np, scipy.io.wavfile as wf
sr, x = wf.read(sys.argv[1]); x = x.astype(float).mean(axis=1) / 32768
hop = 512; n = len(x)//hop
env = np.array([np.sqrt((x[i*hop:(i+1)*hop]**2).mean()) for i in range(n)])
t = np.arange(n)*hop/sr
# energia por 0,5 s
for s in np.arange(0, len(x)/sr, 0.5):
    m = (t >= s) & (t < s+0.5); print(f"{s:5.1f}s {'#'*int(env[m].mean()*120)}")
# fluxo de início (onsets) e tempo por autocorrelação
fl = np.maximum(0, np.diff(env, prepend=env[0])); fl = fl - fl.mean()
ac = np.correlate(fl, fl, 'full')[len(fl)-1:]
lags = np.arange(len(ac))*hop/sr
ok = (lags > 0.3) & (lags < 1.0)
p = lags[ok][np.argmax(ac[ok])]; print("período ~%.3f s  (%.1f BPM)" % (p, 60/p))
pk = [i for i in range(1, n-1) if fl[i] > fl[i-1] and fl[i] >= fl[i+1] and fl[i] > fl.std()*2.2]
print("ataques fortes:", " ".join(f"{t[i]:.2f}" for i in pk))
