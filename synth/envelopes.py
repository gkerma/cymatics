import numpy as np

###############################################################################
# ADSR – ENVELOPPE STANDARD
###############################################################################
def adsr_envelope(attack, decay, sustain, release, sample_rate, duration):
    """
    Génère une enveloppe ADSR linéaire.

    attack  (s)  : montée 0 → 1
    decay   (s)  : descente 1 → sustain
    sustain (%)  : niveau constant (0–1)
    release (s)  : retour à 0
    duration (s) : durée totale
    sample_rate  : fréquence d’échantillonnage
    """
    total_samples = int(duration * sample_rate)
    env = np.zeros(total_samples, dtype=np.float32)

    # SAFETY: éviter divisions nulles
    attack = max(attack, 0.00001)
    decay = max(decay, 0.00001)
    release = max(release, 0.00001)

    a = int(attack * sample_rate)
    d = int(decay * sample_rate)
    r = int(release * sample_rate)
    sustain_level = sustain

    # Zones
    a_end = a
    d_end = a_end + d
    s_end = total_samples - r

    # Attack
    if a > 0:
        env[:a_end] = np.linspace(0.0, 1.0, a_end, endpoint=False)

    # Decay
    if d > 0 and d_end > a_end:
        env[a_end:d_end] = np.linspace(1.0, sustain_level, d, endpoint=False)

    # Sustain
    if s_end > d_end:
        env[d_end:s_end] = sustain_level

    # Release
    if r > 0 and total_samples > s_end:
        env[s_end:] = np.linspace(sustain_level, 0.0, total_samples - s_end)

    return env


###############################################################################
# ADSR EXPONENTIEL (plus musical)
###############################################################################
def adsr_exponential(attack, decay, sustain, release, sample_rate, duration):
    """
    ADSR exponentiel (sons plus naturels).
    """
    linear_env = adsr_envelope(attack, decay, sustain, release, sample_rate, duration)
    # Exponential shaping
    return np.power(linear_env, 1.5)


###############################################################################
# ADSR SANS RELEASE (utile pour un piano cliquable / key-down)
###############################################################################
def adsr_no_release(attack, decay, sustain, sample_rate, duration):
    """
    Version ADSR où la note reste à sustain jusqu'à la fin.
    """
    total_samples = int(duration * sample_rate)
    env = np.zeros(total_samples, dtype=np.float32)

    attack = max(attack, 0.00001)
    decay = max(decay, 0.00001)

    a = int(attack * sample_rate)
    d = int(decay * sample_rate)
    s_end = total_samples

    a_end = a
    d_end = a_end + d

    # Attack
    env[:a_end] = np.linspace(0.0, 1.0, a_end, endpoint=False)

    # Decay
    env[a_end:d_end] = np.linspace(1.0, sustain, d, endpoint=False)

    # Sustain
    env[d_end:s_end] = sustain

    return env


###############################################################################
# ADSR GÉNÉRIQUE, AVEC MODE
###############################################################################
def adsr(mode, attack, decay, sustain, release, sample_rate, duration):
    """
    mode = "linear", "exp", "no_release"
    """
    if mode == "exp":
        return adsr_exponential(attack, decay, sustain, release, sample_rate, duration)
    elif mode == "no_release":
        return adsr_no_release(attack, decay, sustain, sample_rate, duration)
    return adsr_envelope(attack, decay, sustain, release, sample_rate, duration)
