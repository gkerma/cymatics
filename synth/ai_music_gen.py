import numpy as np
from synth.engine import render_note
import random

SAMPLE_RATE = 44100


###############################################################################
# SCALE GENERATOR
###############################################################################
SCALES = {
    "minor":  [0, 2, 3, 5, 7, 8, 10],
    "major":  [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phryg":  [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixol":  [0, 2, 4, 5, 7, 9, 10],
    "locrian":[0, 1, 3, 5, 6, 8, 10]
}


###############################################################################
# BRAINWAVE → TEMPO MAPPING
###############################################################################
BRAINWAVE_BPM = {
    "delta":  40,
    "theta":  60,
    "alpha":  80,
    "beta":   110,
    "gamma":  140,
}


###############################################################################
# AI MUSIC GENERATOR
###############################################################################

def ai_music_brainwave(
    tonic_freq,
    brainwave,
    scale="minor",
    bars=8,
    volume=0.7
):

    bpm = BRAINWAVE_BPM[brainwave]
    spb = 60.0 / bpm  # seconds per beat

    # compute fundamental MIDI
    midi_base = 69 + 12 * np.log2(tonic_freq / 440)

    pattern = []
    wave_segments = []

    params = {
        "osc": "sine",
        "attack": 0.01,
        "decay": 0.2,
        "sustain": 0.7,
        "release": 0.2,
        "env_mode": "exp",
        "lfo_rate": 0.1,
        "lfo_depth": 0.1,
        "lfo_mode": "tremolo",
        "lfo_wave": "sine",
        "volume": volume
    }

    # convert scale to MIDI offsets
    scale_offsets = SCALES.get(scale, SCALES["minor"])

    # create bars
    for bar in range(bars):
        for beat in range(4):

            # probability of playing a note
            if random.random() < 0.85:
                # choose note
                interval = random.choice(scale_offsets)
                midi = midi_base + interval + 12*random.choice([0,0,1,-1])  # slight octave variations
                freq = 440 * (2 ** ((midi - 69) / 12))

                duration = spb * random.choice([0.25, 0.5, 1])

                wave = render_note(freq, duration, params)
                wave_segments.append(wave)

            else:
                # silence
                wave_segments.append(np.zeros(int(spb * SAMPLE_RATE)))

    # join segments
    out = np.concatenate(wave_segments)

    # normalize
    out = out / (np.max(np.abs(out)) + 1e-9)
    return out.astype(np.float32)
