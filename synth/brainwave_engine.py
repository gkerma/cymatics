import numpy as np

SAMPLE_RATE = 44100


###############################################################################
# 1. BINAURAL BEATS
###############################################################################
def binaural_beats(carrier, beat, duration, volume=0.8, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    left  = np.sin(2*np.pi*carrier * t)
    right = np.sin(2*np.pi*(carrier + beat) * t)

    stereo = np.vstack([left, right]).T
    return (stereo * volume).astype(np.float32)


###############################################################################
# 2. ISOCHRONIC TONES
###############################################################################
def isochronic_tones(carrier, pulse_freq, duration, volume=0.8, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    wave = np.sin(2*np.pi*carrier * t)
    pulse = 0.5 * (1 + np.sign(np.sin(2*np.pi*pulse_freq * t)))  # Carré 0/1

    mono = wave * pulse * volume
    stereo = np.vstack([mono, mono]).T
    return stereo.astype(np.float32)


###############################################################################
# 3. HEMISYNC (CROSS-BRAIN ENTRAINMENT)
###############################################################################
def hemisync(carrier_l, carrier_r, beat_l, beat_r, duration, volume=0.8, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    left  = np.sin(2*np.pi*(carrier_l + beat_l) * t)
    right = np.sin(2*np.pi*(carrier_r + beat_r) * t)

    # Crossfade léger entre L/R pour effet spatial
    pan = (np.sin(2*np.pi*0.2*t) + 1) / 2   # LFO lent 0.2 Hz
    left_final  = left  * (1-pan) + right * pan
    right_final = right * pan  + left  * (1-pan)

    stereo = np.vstack([left_final, right_final]).T
    return (stereo * volume).astype(np.float32)


###############################################################################
# 4. HYBRID (BINAURAL + ISOCHRONIC)
###############################################################################
def hybrid_brainwave(carrier, beat, duration, volume=0.8, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # binaural
    left  = np.sin(2*np.pi*carrier * t)
    right = np.sin(2*np.pi*(carrier + beat) * t)

    # isochronic overlay
    pulse = 0.5 * (1 + np.sign(np.sin(2*np.pi*beat * t)))

    left  = left  * pulse
    right = right * pulse

    stereo = np.vstack([left, right]).T

    return (stereo * volume).astype(np.float32)


###############################################################################
# 5. SOLFEGGIO 432 / SACRED FREQUENCIES
###############################################################################
SOLFEGGIO = {
    "396 Hz – Libération de la peur": 396,
    "417 Hz – Transformation": 417,
    "432 Hz – Harmonie universelle": 432,
    "528 Hz – ADN / Guérison": 528,
    "639 Hz – Relations": 639,
    "741 Hz – Intuition": 741,
    "852 Hz – Retour à la source": 852
}

def solfeggio_tone(freq, duration, volume=0.8, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2*np.pi*freq * t) * volume
    stereo = np.vstack([wave, wave]).T
    return stereo.astype(np.float32)


###############################################################################
# 6. BRAINWAVE SEQUENCER (Theta → Alpha → Delta → Gamma...)
###############################################################################
def brainwave_sequence(sequence, volume=0.8, sample_rate=SAMPLE_RATE):
    """
    sequence = [
        {"mode": "binaural", "carrier": 200, "beat": 6, "duration": 60},
        {"mode": "solfeggio", "freq": 528, "duration": 30},
        {"mode": "isochronic", "carrier": 150, "pulse": 10, "duration": 120},
    ]
    """

    output = []

    for item in sequence:
        mode = item["mode"]

        if mode == "binaural":
            wave = binaural_beats(
                item["carrier"],
                item["beat"],
                item["duration"],
                volume
            )

        elif mode == "isochronic":
            wave = isochronic_tones(
                item["carrier"],
                item["pulse"],
                item["duration"],
                volume
            )

        elif mode == "hemisync":
            wave = hemisync(
                item["carrier_l"],
                item["carrier_r"],
                item["beat_l"],
                item["beat_r"],
                item["duration"],
                volume
            )

        elif mode == "hybrid":
            wave = hybrid_brainwave(
                item["carrier"],
                item["beat"],
                item["duration"],
                volume
            )

        elif mode == "solfeggio":
            wave = solfeggio_tone(
                item["freq"],
                item["duration"],
                volume
            )

        else:
            raise ValueError("Unknown brainwave mode:", mode)

        output.append(wave)

    combined = np.vstack([seg for seg in output])
    return combined.astype(np.float32)
