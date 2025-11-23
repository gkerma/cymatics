
import streamlit as st
from io import BytesIO
import numpy as np
from scipy.io.wavfile import write

# Import modules
from synth.engine import render_note, render_chord
from sequencer.stepseq import seq_multi_track
from ui.piano_component import piano_component
from ui.visualizer import oscilloscope, spectrum_fft, spectrogram
from ui.harmonic_analyzer import harmonic_analyzer
from ui.harmonic_live import harmonic_analyzer_live
from synth.brainwave_engine import (
    binaural_beats, isochronic_tones, hybrid_brainwave, hemisync,
    solfeggio_tone, SOLFEGGIO, brainwave_sequence
)
from synth.ai_music_gen import ai_music_brainwave
from synth.brainwave_presets import BRAINWAVE_PRESETS_PRO

SAMPLE_RATE = 44100
BUFFER_LENGTH = 60

st.set_page_config(page_title="Cymatics DAW", layout="wide")

sections = [
    "Synth",
    "Piano",
    "Sequencer",
    "Brainwaves Pro",
    "AI Music Brainwaves",
    "Cognitive Presets"
]

section = st.sidebar.selectbox("Section", sections)

# --- Synth ---
if section == "Synth":
    st.header("Synth Standalone")
    freq = st.number_input("Frequency", 20.0, 20000.0, 440.0)
    duration = st.slider("Duration", 0.1, 10.0, 1.0)
    params = {"osc": "sine", "attack": 0.01, "decay": 0.1, "sustain": 0.7,
              "release": 0.1, "env_mode": "linear", "volume": 0.8}
    if st.button("Play"):
        wave = render_note(freq, duration, params)
        wave_int = (wave * 32767).astype(np.int16)
        st.audio(BytesIO(wave_int.tobytes()), format="audio/wav")
        oscilloscope(wave)
        spectrum_fft(wave)
        spectrogram(wave)

# --- Piano ---
elif section == "Piano":
    st.header("Piano")
    note = piano_component()
    if note:
        st.write("Note:", note)

# --- Sequencer ---
elif section == "Sequencer":
    st.header("Sequencer")
    st.info("Setup patterns in sequencer modules.")

# --- Brainwaves Pro ---
elif section == "Brainwaves Pro":
    st.header("Brainwaves Pro")
    mode = st.selectbox("Mode", ["Binaural", "Isochronic", "Hybrid", "Hemisync", "Solfeggio"])
    duration = st.slider("Duration", 5, 600, 60)
    if st.button("Generate"):
        if mode == "Binaural":
            wave = binaural_beats(200, 6, duration)
        elif mode == "Isochronic":
            wave = isochronic_tones(200, 10, duration)
        elif mode == "Hybrid":
            wave = hybrid_brainwave(200, 6, duration)
        elif mode == "Hemisync":
            wave = hemisync(200, 210, 5, 7, duration)
        else:
            wave = solfeggio_tone(432, duration)
        wave_int = (wave * 32767).astype(np.int16)
        st.audio(BytesIO(wave_int.tobytes()), format="audio/wav")

# --- AI Music ---
elif section == "AI Music Brainwaves":
    st.header("AI Music Generator")
    tonic = st.number_input("Tonic Hz", 100.0, 800.0, 432.0)
    brain = st.selectbox("Brainwave", ["delta", "theta", "alpha", "beta", "gamma"])
    if st.button("Generate Music"):
        music = ai_music_brainwave(tonic, brain)
        wav = (music * 32767).astype(np.int16)
        st.audio(BytesIO(wav.tobytes()), format="audio/wav")

# --- Presets ---
elif section == "Cognitive Presets":
    st.header("Cognitive Presets")
    names = [p["name"] for p in BRAINWAVE_PRESETS_PRO]
    chosen = st.selectbox("Preset", names)
    preset = next(p for p in BRAINWAVE_PRESETS_PRO if p["name"] == chosen)
    if st.button("Start Program"):
        mode = preset["mode"]
        if mode == "binaural":
            wave = binaural_beats(preset["carrier"], preset["beat"], preset["duration"])
        elif mode == "isochronic":
            wave = isochronic_tones(preset["carrier"], preset["pulse"], preset["duration"])
        elif mode == "hybrid":
            wave = hybrid_brainwave(preset["carrier"], preset["beat"], preset["duration"])
        elif mode == "solfeggio":
            wave = solfeggio_tone(preset["freq"], preset["duration"])
        wave_int = (wave * 32767).astype(np.int16)
        st.audio(BytesIO(wave_int.tobytes()), format="audio/wav")
