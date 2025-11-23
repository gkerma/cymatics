import streamlit as st
import numpy as np
from io import BytesIO
from scipy.io.wavfile import write
import base64

# Modules internes
from synth.engine import render_note, render_chord
from sequencer.stepseq import seq_multi_track
from ui.piano_component import piano_component


###############################################################################
# CONFIG
###############################################################################

SAMPLE_RATE = 44100
BUFFER_LENGTH = 60  # boucle longue 60 secondes

st.set_page_config(page_title="Cymatics DAW", layout="wide")


###############################################################################
# AUDIO
###############################################################################

def play_audio_once(audio_float, sample_rate=SAMPLE_RATE):
    """Joue un son une fois via st.audio."""
    audio_int16 = (audio_float * 32767).astype("int16")
    st.audio(BytesIO(audio_int16.tobytes()), format="audio/wav")


def play_audio_loop(audio_float, sample_rate=SAMPLE_RATE):
    """Joue un son en boucle HTML5 sans ticks."""
    audio_int16 = (audio_float * 32767).astype("int16")

    buf = BytesIO()
    write(buf, sample_rate, audio_int16)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()

    html = f"""
    <audio controls autoplay loop>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)


###############################################################################
# DIAPASON 432 / 440 Hz
###############################################################################

diapason = st.sidebar.number_input(
    "Diapason A4 (Hz)",
    min_value=400.0,
    max_value=500.0,
    value=432.0,
    step=0.1
)

def midi_to_freq(midi, a4=diapason):
    return a4 * (2 ** ((midi - 69) / 12))


###############################################################################
# SECTIONS
###############################################################################

section = st.sidebar.selectbox("Section", ["Synth", "Piano", "Séquenceur"])


###############################################################################
# SYNTH 432 Hz
###############################################################################

if section == "Synth":
    st.header("Synthétiseur 432 Hz (avec boucle longue)")

    midi = st.slider("Note MIDI", 21, 108, 69)  # A4
    freq = midi_to_freq(midi)

    st.write(f"Fréquence : {freq:.2f} Hz")

    duration = st.slider("Durée", 0.1, 10.0, 1.0)

    params = {
        "osc": "sine",
        "attack": 0.01,
        "decay": 0.1,
        "sustain": 0.8,
        "release": 0.2,
        "volume": 1.0
    }

    if st.button("Jouer la note"):
        w = render_note(freq, duration, params)

        if st.checkbox("Boucle 60 secondes"):
            reps = int(BUFFER_LENGTH / duration) + 1
            long = np.tile(w, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
            play_audio_loop(long)
        else:
            play_audio_once(w)


###############################################################################
# PIANO 432 Hz
###############################################################################

elif section == "Piano":
    st.header("Piano Interactif (accordé 432 Hz)")

    note = piano_component()

    if note:
        st.success(f"Touche : {note}")

        name = note[:-1]
        octave = int(note[-1])

        names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        midi = names.index(name) + octave * 12
        freq = midi_to_freq(midi)

        st.write(f"Fréquence : {freq:.2f} Hz")

        params = {
            "osc": "sine",
            "attack": 0.01,
            "decay": 0.1,
            "sustain": 0.8,
            "release": 0.2,
            "volume": 1.0
        }

        w = render_note(freq, 1.0, params)

        if st.checkbox("Boucle 60s", key="loop_piano"):
            reps = int(BUFFER_LENGTH / 1.0) + 1
            long = np.tile(w, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
            play_audio_loop(long)
        else:
            play_audio_once(w)


###############################################################################
# SÉQUENCEUR MINIMAL
###############################################################################

elif section == "Séquenceur":
    st.header("Séquenceur 432 Hz")

    note_list = ["C4","D4","E4","F4","G4","A4","B4"]
    patterns = {
        "track1": [note_list[i % 7] for i in range(16)]
    }

    # Construction de la table de fréquences
    freq_map = {}

    names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
    for n in note_list:
        name = n[:-1]
        octave = int(n[-1])
        midi = names.index(name) + octave * 12
        freq_map[n] = midi_to_freq(midi)

    params_tracks = {
        "track1": {
            "osc": "sine",
            "attack": 0.01,
            "decay": 0.1,
            "sustain": 0.8,
            "release": 0.2,
            "volume": 1.0
        }
    }

    bpm = st.slider("BPM", 40, 200, 120)

    if st.button("Jouer la séquence"):
        w = seq_multi_track(patterns, freq_map, bpm, params_tracks)

        if st.checkbox("Boucle 60s", key="loop_seq"):
            reps = int(BUFFER_LENGTH / (len(w) / SAMPLE_RATE)) + 1
            long = np.tile(w, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
            play_audio_loop(long)
        else:
            play_audio_once(w)
