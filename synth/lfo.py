import numpy as np

###############################################################################
# WAVEFORMS LFO
###############################################################################

def lfo_sine(t, rate):
    return np.sin(2 * np.pi * rate * t)

def lfo_triangle(t, rate):
    return 2 * np.abs(2 * ((t * rate) % 1) - 1) - 1

def lfo_square(t, rate):
    return np.sign(np.sin(2 * np.pi * rate * t))

def lfo_saw(t, rate):
    return 2 * ((t * rate) % 1) - 1


LFO_WAVES = {
    "sine":   lfo_sine,
    "triangle": lfo_triangle,
    "square": lfo_square,
    "saw":    lfo_saw
}


###############################################################################
# LFO GENERAL
###############################################################################

def lfo(
    t,
    rate=5.0,
    depth=0.5,
    waveform="sine",
    bipolar=True,
    tempo_sync=None,
    bpm=120
):
    """
    Génère une forme LFO selon tous les paramètres classiques.

    t           : timeline en secondes
    rate        : fréquence du LFO (Hz) si pas de tempo sync
    depth       : intensité de modulation (0–1)
    waveform    : sine, triangle, square, saw
    bipolar     : True → [-1,1], False → [0,1]
    tempo_sync  : None ou valeur du type "1/4", "1/8", "1/16"
    bpm         : tempo pour sync
    """

    # Tempo sync
    if tempo_sync is not None:
        # durée d’une note
        note_div = eval(tempo_sync)   # "1/4" → 0.25
        seconds_per_beat = 60.0 / bpm
        period = note_div * seconds_per_beat
        rate = 1.0 / period

    # Calcul waveform
    if waveform not in LFO_WAVES:
        waveform = "sine"

    wave = LFO_WAVES[waveform](t, rate)

    # Bipolaire : [-1,1], unipolaire : [0,1]
    if not bipolar:
        wave = (wave + 1) / 2

    # Application profondeur
    return wave * depth


###############################################################################
# LFO APPLIQUÉ A UN SIGNAL
###############################################################################

def apply_lfo_amplitude(signal, t, rate, depth, waveform="sine"):
    """
    Tremolo : modulation d’amplitude
    """
    mod = lfo(t, rate, depth, waveform, bipolar=False)
    return signal * (1 + mod)


def apply_lfo_vibrato(freq, t, rate, depth, waveform="sine"):
    """
    Vibrato : modulation de fréquence
    Retourne une nouvelle fréquence instantanée.
    """
    mod = lfo(t, rate, depth, waveform, bipolar=True)
    return freq + freq * mod


def apply_lfo_filter(signal, t, rate, depth, waveform="sine"):
    """
    LFO type "filtre" simple : modulation multiplicative.
    Approche douce style auto-filter Ableton.
    """
    mod = lfo(t, rate, depth, waveform, bipolar=False)
    return signal * (0.5 + mod)
