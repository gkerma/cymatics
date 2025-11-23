import numpy as np
import streamlit as st
import matplotlib.pyplot as plt


###############################################################################
# HARMONIC ANALYZER (SPECTRE PARTIELS)
###############################################################################
def harmonic_analyzer(
    wave,
    sample_rate=44100,
    max_harmonics=20,
    title="Analyse des harmoniques",
    base_freq=None,
    width=800,
    height=350
):
    """
    Analyse les partiels harmoniques d’un signal périodique.
    
    Si base_freq est donnée :
        → les harmoniques seront alignés sur n × base_freq
    Sinon :
        → estimation automatique via autocorr + FFT peak detection
    """

    N = len(wave)
    fft = np.fft.fft(wave)
    freq = np.fft.fftfreq(N, 1/sample_rate)

    # Keep positive frequencies
    mask = freq > 0
    freq = freq[mask]
    mag = np.abs(fft[mask]) 

    # Estimate base frequency if not provided
    if base_freq is None:
        # Find max peak (excluding sub-low noise)
        idx = np.argmax(mag[1:]) + 1
        base_freq = freq[idx]

    # Build harmonic frequency list
    harmonic_freqs = [base_freq * n for n in range(1, max_harmonics + 1)]
    harmonic_amps = []

    for h in harmonic_freqs:
        # Find FFT bin nearest to harmonic
        idx = np.argmin(np.abs(freq - h))
        harmonic_amps.append(mag[idx])

    # Normalize amplitudes
    harmonic_amps = np.array(harmonic_amps)
    harmonic_amps = harmonic_amps / (harmonic_amps.max() + 1e-9)

    # Plot
    fig, ax = plt.subplots(figsize=(width/100, height/100))

    ax.bar(
        harmonic_freqs,
        harmonic_amps,
        width=base_freq * 0.8,
        color=["#ffaa00" if i%2==0 else "#44ccff" for i in range(max_harmonics)],
        edgecolor="black",
        linewidth=0.6
    )

    ax.set_title(title)
    ax.set_xlabel("Fréquence (Hz)")
    ax.set_ylabel("Amplitude (normalisée)")

    # Optional: show grid
    ax.grid(True, which="both", linestyle="--", linewidth=0.4)

    st.pyplot(fig)

    # Display harmonic table
    st.markdown("### Détails des harmoniques")
    for i, (f, a) in enumerate(zip(harmonic_freqs, harmonic_amps), start=1):
        st.write(f"Harmonique {i} : {f:.2f} Hz — amplitude : {a:.3f}")

    return harmonic_freqs, harmonic_amps
