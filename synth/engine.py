# Synth engine placeholder
import numpy as np
from .oscillators import *
from .envelopes import adsr

def synth(freq, sr, duration, osc, A, D, S, R, lfo_rate=0, lfo_depth=0, lfo_mode=None):

    t = np.linspace(0, duration, int(sr*duration), endpoint=False)

    wave = {
        "sine": osc_sine(freq, t),
        "square": osc_square(freq, t),
        "saw": osc_saw(freq, t),
        "supersaw": osc_supersaw(freq, t)
    }[osc]

    env = adsr(A,D,S,R,sr,duration)
    wave *= env

    if lfo_mode:
        if lfo_mode == "vibrato":
            wave = osc_sine(freq + lfo_depth*np.sin(2*np.pi*lfo_rate*t), t)
        elif lfo_mode == "tremolo":
            wave *= (1 + lfo_depth*np.sin(2*np.pi*lfo_rate*t))

    return wave
