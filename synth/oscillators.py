import numpy as np

###############################
#  BASE OSCILLATEURS
###############################

def osc_sine(freq, t):
    return np.sin(2 * np.pi * freq * t)

def osc_square(freq, t):
    return np.sign(np.sin(2 * np.pi * freq * t))

def osc_saw(freq, t):
    return 2 * (freq * t - np.floor(0.5 + freq * t))

def osc_triangle(freq, t):
    return 2 * np.abs(osc_saw(freq, t)) - 1

def osc_noise(t):
    return np.random.uniform(-1, 1, len(t))

###############################
#  SUPERSAW (7 VOIX)
###############################
def osc_supersaw(freq, t):
    # Désaccord fin
    detunes = [-0.015, -0.01, -0.005, 0, 0.006, 0.012, 0.018]
    waves = [osc_saw(freq * (1 + d), t) for d in detunes]
    return np.sum(waves, axis=0) / len(waves)

###############################
#  MODULATION
###############################
def osc_fm(freq, t, mod_freq=2.0, index=3.0):
    """
    Frequency Modulation
    """
    return np.sin(2 * np.pi * freq * t + index * np.sin(2 * np.pi * mod_freq * t))

def osc_am(freq, t, mod_freq=2.0, depth=0.5):
    """
    Amplitude Modulation
    """
    mod = (1 + depth * np.sin(2 * np.pi * mod_freq * t))
    return mod * np.sin(2 * np.pi * freq * t)

###############################
#  ADDITIVE SYNTH (HARMONIQUES)
###############################
def osc_additive(freq, t, harmonics=5):
    wave = np.zeros(len(t))
    for h in range(1, harmonics + 1):
        wave += (1 / h) * np.sin(2 * np.pi * freq * h * t)
    return wave
