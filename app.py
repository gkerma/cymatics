import streamlit as st
import numpy as np
from io import BytesIO
from scipy.io.wavfile import write
import base64

from synth.engine import render_note
from sequencer.stepseq import seq_multi_track
from ui.piano_component import piano_component


###############################################################################
# AUDIO SYSTEM
###############################################################################

SAMPLE_RATE = 44100
BUFFER_LENGTH = 60


def float_to_int16(x):
    return (x * 32767).astype(np.int16)


def play_once(wave):
    """Lecture Streamlit sécurisée"""
    wave16 = float_to_int16(wave)
    st.audio(BytesIO(wave16.tobytes()), format="audio/wav")


def play_loop(wave):
    """Lecteur HTML5 qui boucle SANS tick"""
    wave16 = float_to_int16(wave)

    buf = BytesIO()
    write(buf, SAMPLE_RATE, wave16)
    buf.seek(0)

    b64 = base64.b64encode(buf.read()).decode()
    html = f"""
    <audio autoplay loop>
      <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)


###############################################################################
# GLOBAL 432 Hz
###############################################################################

diapason = st.sidebar.number_input(
    "Diapason A4",
    min_value=400.0,
    max_value=500.0,
    value=432.0,
    step=0.1,
)

def midi_to_freq(m):
    return diapason * (2 ** ((m - 69) / 12))


###############################################################################
# SECTIONS
###############################################################################

section = st.sidebar.selectbox("Section", ["Synth", "Piano", "Séquenceur"])


###############################################################################
# SYNTH
###############################################################################

if section == "Synth":

    st.header("Synthé fonctionnel 432 Hz")

    midi = st.slider("Note MIDI", 21, 108, 69)
    freq = midi_to_freq(midi)
    duration = st.slider("Durée", 0.1, 5.0, 1.0)

    params = dict(
        osc="sine",
        attack=0.01,
        decay=0.1,
        sustain=0.8,
        release=0.2,
        volume=1.0,
    )

    if st.button("Jouer"):
        w = render_note(freq, duration, params)
        play_once(w)

    if st.button("Boucle 60 sec"):
        w = render_note(freq, duration, params)
        reps = int(BUFFER_LENGTH / duration) + 1
        long = np.tile(w, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
        play_loop(long)


###############################################################################
# PIANO
###############################################################################

elif section == "Piano":

    st.header("Piano 432 Hz")

    note = piano_component()

    if note:
        st.success(f"Touche : {note}")

        name = note[:-1]
        octave = int(note[-1])
        names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

        midi = names.index(name) + octave * 12
        freq = midi_to_freq(midi)

        params = dict(
            osc="sine",
            attack=0.01,
            decay=0.1,
            sustain=0.8,
            release=0.2,
            volume=1.0,
        )

        w = render_note(freq, 1.0, params)
        play_once(w)

        if st.button("Boucle 60 sec (piano)"):
            reps = int(BUFFER_LENGTH / 1.0) + 1
            play_loop(np.tile(w, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)])


###############################################################################
# SÉQUENCEUR
###############################################################################

elif section == "Séquenceur":

    st.header("Séquenceur 432 Hz minimal")

    note_list = ["C4","D4","E4","F4","G4","A4","B4"]

    # construction freq_map propre
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

    if st.button("Jouer séquence"):
        w = seq_multi_track(patterns, freq_map, bpm, params_tracks)
        play_once(w)

    if st.button("Boucle 60 sec (séquenceur)"):
        w = seq_multi_track(patterns, freq_map, bpm, params_tracks)
        reps = int(BUFFER_LENGTH / (len(w) / SAMPLE_RATE)) + 1
        long = np.tile(w, reps)[: int(BUFFER_LENGTH * SAMPLE_RATE)]
        play_loop(long)
