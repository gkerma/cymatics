import numpy as np

from .oscillators import (
    osc_sine, osc_square, osc_saw, osc_triangle,
    osc_supersaw, osc_fm, osc_am, osc_noise, osc_additive
)
from .envelopes import adsr
from .lfo import apply_lfo_amplitude, apply_lfo_vibrato, apply_lfo_filter


###############################################################################
# CONFIGURATION GLOBALE
###############################################################################

DEFAULT_SR = 44100

OSC_TYPES = {
    "sine": osc_sine,
    "square": osc_square,
    "saw": osc_saw,
    "triangle": osc_triangle,
    "supersaw": osc_supersaw,
    "noise": lambda freq, t: osc_noise(t),
    "fm": osc_fm,
    "am": osc_am,
    "additive": osc_additive
}


###############################################################################
# RENDU D’UNE SEULE NOTE
###############################################################################

def render_note(
    freq,
    duration,
    params,
    sample_rate=DEFAULT_SR
):
    """
    Génère une note complète avec :
    - oscillateur
    - ADSR
    - LFO (vibrato, tremolo, filter)
    - shaping & normalisation
    """

    osc = params.get("osc", "sine")
    A = params.get("attack", 0.01)
    D = params.get("decay", 0.1)
    S = params.get("sustain", 0.8)
    R = params.get("release", 0.1)
    env_mode = params.get("env_mode", "linear")

    lfo_rate = params.get("lfo_rate", 0.0)
    lfo_depth = params.get("lfo_depth", 0.0)
    lfo_mode = params.get("lfo_mode", None)
    lfo_wave = params.get("lfo_wave", "sine")

    volume = params.get("volume", 1.0)
    harmonics = params.get("harmonics", 5)  # for additive

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    ###########################################################################
    # OSCILLATEUR → signal brut
    ###########################################################################
    if osc not in OSC_TYPES:
        osc = "sine"

    if osc == "fm":
        signal = osc_fm(freq, t, params.get("mod_freq", 2.0), params.get("mod_index", 3.0))
    elif osc == "am":
        signal = osc_am(freq, t, params.get("mod_freq", 2.0), params.get("mod_depth", 0.5))
    elif osc == "additive":
        signal = osc_additive(freq, t, harmonics=harmonics)
    else:
        signal = OSC_TYPES[osc](freq, t)

    ###########################################################################
    # LFO → vibrato (modulation de fréquence)
    ###########################################################################
    if lfo_mode == "vibrato" and lfo_depth > 0:
        inst_freq = apply_lfo_vibrato(freq, t, rate=lfo_rate, depth=lfo_depth, waveform=lfo_wave)
        signal = np.sin(2 * np.pi * inst_freq * t)

    ###########################################################################
    # LFO → tremolo (modulation de volume)
    ###########################################################################
    if lfo_mode == "tremolo" and lfo_depth > 0:
        signal = apply_lfo_amplitude(signal, t, lfo_rate, lfo_depth, waveform=lfo_wave)

    ###########################################################################
    # LFO → filter modulation
    ###########################################################################
    if lfo_mode == "filter" and lfo_depth > 0:
        signal = apply_lfo_filter(signal, t, lfo_rate, lfo_depth, waveform=lfo_wave)

    ###########################################################################
    # ADSR
    ###########################################################################
    env = adsr(
        env_mode,
        A, D, S, R,
        sample_rate,
        duration
    )
    signal *= env

    ###########################################################################
    # Volume
    ###########################################################################
    signal *= volume

    ###########################################################################
    # Normalisation
    ###########################################################################
    peak = np.max(np.abs(signal)) + 1e-9
    signal /= peak

    return signal.astype(np.float32)


###############################################################################
# RENDU D’UN ACCORD (PLUSIEURS NOTES)
###############################################################################

def render_chord(freq_list, duration, params, sample_rate=DEFAULT_SR):
    """
    Génère un accord polyphonique.
    freq_list = [freq1, freq2, freq3...]
    """

    waves = [
        render_note(freq, duration, params, sample_rate)
        for freq in freq_list
    ]

    mix = np.sum(waves, axis=0)

    # Normalisation polyphonique
    peak = np.max(np.abs(mix)) + 1e-9
    mix /= peak

    return mix.astype(np.float32)


###############################################################################
# CONVERSION → int16
###############################################################################

def to_int16(wave):
    return (wave * 32767).astype(np.int16)


###############################################################################
# RENDU + CONVERSION DIRECTE POUR WAV
###############################################################################

def render_note_int16(freq, duration, params, sample_rate=DEFAULT_SR):
    return to_int16(render_note(freq, duration, params, sample_rate))


def render_chord_int16(freq_list, duration, params, sample_rate=DEFAULT_SR):
    return to_int16(render_chord(freq_list, duration, params, sample_rate))
