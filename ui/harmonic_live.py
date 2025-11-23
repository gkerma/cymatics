import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from ui.harmonic_analyzer import harmonic_analyzer


def harmonic_analyzer_live(
    get_wave_fn,
    duration=5.0,
    fps=5,
    sample_rate=44100,
    base_freq=None,
    max_harmonics=20
):
    """
    get_wave_fn : fonction → retourne une waveform numpy
    duration    : temps total de monitoring
    fps         : nombre d’analyses/sec
    """

    refresh_interval = 1.0 / fps
    placeholder = st.empty()

    start = time.time()

    while time.time() - start < duration:

        wave = get_wave_fn()
        if wave is None or len(wave) == 0:
            placeholder.warning("Aucun signal reçu.")
            time.sleep(refresh_interval)
            continue

        with placeholder.container():
            harmonic_analyzer(
                wave,
                sample_rate=sample_rate,
                base_freq=base_freq,
                max_harmonics=max_harmonics,
                title="Analyse harmonique — Temps réel"
            )

        time.sleep(refresh_interval)
