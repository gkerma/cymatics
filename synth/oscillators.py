# Oscillators placeholder
import numpy as np

def osc_sine(freq, t):
    return np.sin(2*np.pi*freq*t)

def osc_square(freq, t):
    return np.sign(np.sin(2*np.pi*freq*t))

def osc_saw(freq, t):
    return 2*(t*freq - np.floor(t*freq + 0.5))

def osc_supersaw(freq, t):
    detunes = [-0.02,-0.01,-0.005,0,0.006,0.012,0.02]
    waves = [osc_saw(freq*(1+d), t) for d in detunes]
    return np.sum(waves, axis=0)/len(detunes)

def osc_fm(freq, t, mod_freq, index):
    return np.sin(2*np.pi*(freq*t + index*np.sin(2*np.pi*mod_freq*t)))

def osc_am(freq, t, mod_freq, depth):
    return (1 + depth*np.sin(2*np.pi*mod_freq*t)) * np.sin(2*np.pi*freq*t)
