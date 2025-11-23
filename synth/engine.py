
import numpy as np

SAMPLE_RATE=44100

def osc_sine(freq, t): return np.sin(2*np.pi*freq*t)
def osc_square(freq, t): return np.sign(np.sin(2*np.pi*freq*t))
def osc_saw(freq, t): return 2*(t*freq - np.floor(0.5 + t*freq))
def osc_triangle(freq, t): return 2*np.abs(osc_saw(freq,t)) - 1

def supersaw(freq, t, n=7, detune=0.01):
    sig=0
    for i in range(n):
        det = (i-n/2)*detune*freq
        sig += osc_saw(freq+det, t)
    return sig/n

def fm(freq, t, mod_freq, mod_index):
    return np.sin(2*np.pi*freq*t + mod_index*np.sin(2*np.pi*mod_freq*t))

def am(freq, t, mod_freq, depth):
    return (1+depth*np.sin(2*np.pi*mod_freq*t))*np.sin(2*np.pi*freq*t)

def adsr(t, a,d,s,r, dur):
    env=np.ones_like(t)*s
    env[t<a]= (t[t<a]/a)
    env[(t>=a)&(t<a+d)] = 1 - (1-s)*((t[(t>=a)&(t<a+d)]-a)/d)
    env[t>dur-r] = s*(1-((t[t>dur-r]-(dur-r))/r))
    env[t>=dur]=0
    return env

def render_note(freq, dur, p, sr=SAMPLE_RATE):
    N=int(dur*sr)
    t=np.linspace(0,dur,N,endpoint=False)
    osc=p.get("osc","sine")
    if osc=="sine": wave=osc_sine(freq,t)
    elif osc=="square": wave=osc_square(freq,t)
    elif osc=="saw": wave=osc_saw(freq,t)
    elif osc=="triangle": wave=osc_triangle(freq,t)
    elif osc=="supersaw": wave=supersaw(freq,t)
    elif osc=="fm": wave=fm(freq,t,p["mod_freq"],p["mod_index"])
    elif osc=="am": wave=am(freq,t,p["mod_freq"],p["mod_depth"])
    else: wave=osc_sine(freq,t)

    env = adsr(t, p["attack"], p["decay"], p["sustain"], p["release"], dur)
    wave = wave*env*p.get("volume",1.0)
    return wave.astype(np.float32)

def render_chord(freqs, dur, p, sr=SAMPLE_RATE):
    waves=[render_note(f,dur,p,sr) for f in freqs]
    mix=np.sum(waves,axis=0)
    mix/=np.max(np.abs(mix))+1e-9
    return mix.astype(np.float32)

def to_int16(w): return (w*32767).astype(np.int16)
