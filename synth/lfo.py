# LFO placeholder
import numpy as np

def lfo(t, rate, depth, mode, base_wave):
    mod = depth*np.sin(2*np.pi*rate*t)

    if mode == "vibrato":
        return np.sin(2*np.pi*(base_wave + mod)*t)
    elif mode == "tremolo":
        return base_wave * (1 + mod)
    return base_wave
