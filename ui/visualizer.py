import numpy as np
import streamlit as st
import matplotlib.pyplot as plt


###############################################################################
# OSCILLOSCOPE
###############################################################################
def oscilloscope(wave, sample_rate=44100, title="Oscilloscope", width=800, height=200):
    t = np.linspace(0, len(wave)/sample_rate, len(wave))

    fig, ax = plt.subplots(figsize=(width/100, height/100))
    ax.plot(t, wave, linewidth=1.0, color="#00ccff")
    ax.set_title(title)
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True, color="#333")

    st.pyplot(fig)


###############################################################################
# FFT / SPECTRE
###############################################################################
def spectrum_fft(wave, sample_rate=44100, title="Spectrum FFT", width=800, height=200):

    N = len(wave)
    fft = np.fft.fft(wave)
    freq = np.fft.fftfreq(N, d=1/sample_rate)

    # On ne garde que les positives
    pos_mask = freq >= 0
    freq = freq[pos_mask]
    fft = np.abs(fft[pos_mask])

    fig, ax = plt.subplots(figsize=(width/100, height/100))
    ax.plot(freq, fft, color="#ff8800", linewidth=1.2)
    ax.set_title(title)
    ax.set_xlabel("Fréquence (Hz)")
    ax.set_ylabel("Amplitude")
    ax.set_xlim(0, sample_rate/2)
    ax.grid(True, color="#333")

    st.pyplot(fig)


###############################################################################
# SPECTROGRAMME
###############################################################################
def spectrogram(wave, sample_rate=44100, title="Spectrogram", width=800, height=300):

    fig, ax = plt.subplots(figsize=(width/100, height/100))
    ax.specgram(
        wave,
        Fs=sample_rate,
        NFFT=2048,
        noverlap=1024,
        cmap="inferno"
    )
    ax.set_title(title)
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Fréquence (Hz)")

    st.pyplot(fig)
