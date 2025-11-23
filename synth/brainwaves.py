import numpy as np

def binaural_beat(base_freq, beat_freq, duration, sample_rate=44100, volume=0.8):
    """
    base_freq : fréquence porteuse (ex : 200 Hz)
    beat_freq : différence entre L et R (ex : 4 Hz pour Theta)
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    left = np.sin(2*np.pi*base_freq * t)
    right = np.sin(2*np.pi*(base_freq + beat_freq) * t)

    stereo = np.vstack([left, right]).T
    stereo *= volume

    return stereo


def isochronic_tone(base_freq, pulse_freq, duration, sample_rate=44100, volume=0.8):
    """
    Pulsations On/Off à fréquence fixe → isochronique
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    carrier = np.sin(2*np.pi*base_freq*t)
    pulse = 0.5 * (1 + np.sign(np.sin(2*np.pi*pulse_freq*t)))  # carré 0/1

    result = carrier * pulse * volume
    return result


BRAINWAVE_PRESETS = {
    "Deep Delta Sleep":     {"beat": 1.5, "carrier": 120},
    "Theta Meditation":     {"beat": 5.0, "carrier": 150},
    "Alpha Relaxation":     {"beat": 10.0, "carrier": 200},
    "Focus Beta":           {"beat": 18.0, "carrier": 220},
    "High Gamma":           {"beat": 40.0, "carrier": 250},
}
