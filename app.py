import streamlit as st
import numpy as np
from io import BytesIO
from scipy.io.wavfile import write
import base64

# Imports internes
from synth.engine import render_note
from sequencer.stepseq import seq_multi_track
from ui.piano_component import piano_component


###############################################################################
# CONFIG
###############################################################################
SAMPLE_RATE = 44100
BUFFER_LENGTH = 60  # boucle longue stable

st.set_page_config(page_title="Cymatics DAW", layout="wide")


###############################################################################
# AUDIO SYSTEM - VERSION HTML5 (fiable, autoplay)
###############################################################################

def float_to_int16(wave):
    return (wave * 32767).astype(np.int16)


def play_once(wave, sample_rate=SAMPLE_RATE):
    """Lecture d'un son une fois, via lecteur HTML5 (autoplay)."""
    wave16 = float_to_int16(wave)

    buf = BytesIO()
    write(buf, sample_rate, wave16)
    buf.seek(0)

    b64 = base64.b64encode(buf.read()).decode()
    html = f"""
    <audio autoplay>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)


def play_loop(wave, sample_rate=SAMPLE_RATE):
    """Lecture en boucle infinie sans tick (HTML5)."""
    wave16 = float_to_int16(wave)

    buf = BytesIO()
    write(buf, sample_rate, wave16)
    buf.seek(0)

    b64 = base64.b64encode(buf.read()).decode()
    html = f"""
    <audio autoplay loop>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)


###############################################################################
# DIAPASON 432 Hz
###############################################################################

diapason = st.sidebar.number_input(
    "Diapason A4 (Hz)",
    min_value=400.0,
    max_value=500.0,
    value=432.0,
    step=0.1,
)


def midi_to_freq(midi):
    return diapason * (2 ** ((midi - 69) / 12))


###############################################################################
# NAVIGATION
###############################################################################

section = st.sidebar.selectbox("Section", ["Synth", "Piano", "Séquenceur"])


###############################################################################
# SECTION : SYNTH
###############################################################################

if section == "Synth":
    st.header("Synthétiseur 432 Hz — Audio OK")

    midi = st.slider("MIDI Note", 21, 108, 69)
    freq = midi_to_freq(midi)

    st.write(f"Fréquence : **{freq:.2f} Hz**")

    duration = st.slider("Durée", 0.1, 10.0, 1.0)

    params = dict(
        osc="sine",
        attack=0.01,
        decay=0.1,
        sustain=0.8,
        release=0.2,
        volume=1.0,
    )

    if st.button("JOUER"):
        wave = render_note(freq, duration, params)
        play_once(wave)

    if st.button("BOUCLE 60s"):
        wave = render_note(freq, duration, params)
        reps = int(BUFFER_LENGTH / duration) + 1
        long = np.tile(wave, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
        play_loop(long)


###############################################################################
# SECTION : PIANO
###############################################################################

elif section == "Piano":
    st.header("Piano Interactif 432 Hz")

    note = piano_component()

    if note:
        st.success(f"Note : {note}")

        names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        name = note[:-1]
        octave = int(note[-1])

        midi = names.index(name) + octave * 12
        freq = midi_to_freq(midi)

        st.write(f"Fréquence : **{freq:.2f} Hz**")

        params = dict(
            osc="sine",
            attack=0.01,
            decay=0.1,
            sustain=0.8,
            release=0.2,
            volume=1.0,
        )

        wave = render_note(freq, 1.0, params)
        play_once(wave)

        if st.button("BOUCLE 60s (PIANO)"):
            reps = int(BUFFER_LENGTH / 1.0) + 1
            long = np.tile(wave, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
            play_loop(long)


###############################################################################
# SECTION : SÉQUENCEUR
###############################################################################

elif section == "Séquenceur":
    st.header("Séquenceur minimal – 432 Hz")

    note_list = ["C4","D4","E4","F4","G4","A4","B4"]

    # TABLE DE FREQUENCE
    freq_map = {}
    names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

    for n in note_list:
        name = n[:-1]
        octave = int(n[-1])
        midi = names.index(name) + octave * 12
        freq_map[n] = midi_to_freq(midi)

    patterns = {
        "track1": [note_list[i % 7] for i in range(16)]
    }

    params_tracks = {
        "track1": dict(
            osc="sine",
            attack=0.01,
            decay=0.1,
            sustain=0.8,
            release=0.2,
            volume=1.0,
        )
    }

    bpm = st.slider("BPM", 40, 200, 120)

    if st.button("JOUER SÉQUENCE"):
        wave = seq_multi_track(patterns, freq_map, bpm, params_tracks)
        play_once(wave)

    if st.button("BOUCLE 60s (SÉQUENCEUR)"):
        wave = seq_multi_track(patterns, freq_map, bpm, params_tracks)
        reps = int(BUFFER_LENGTH / (len(wave) / SAMPLE_RATE)) + 1
        long = np.tile(wave, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
        play_loop(long)
