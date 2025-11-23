import streamlit as st
import numpy as np
from io import BytesIO
from scipy.io.wavfile import write
import base64

# Modules internes
from synth.engine import render_note
from sequencer.stepseq import seq_multi_track
from ui.piano_component import piano_component


###############################################################################
# CONFIGURATION
###############################################################################

st.set_page_config(page_title="Cymatics DAW", layout="wide")

SAMPLE_RATE = 44100

# États persistants pour boucle + wave
if "looping" not in st.session_state:
    st.session_state.looping = False

if "loop_wave" not in st.session_state:
    st.session_state.loop_wave = None


###############################################################################
# AUDIO SYSTEM
###############################################################################

def float_to_int16(wave):
    return (wave * 32767).astype(np.int16)


def play_once(wave, sample_rate=SAMPLE_RATE):
    """Lecture d'un son en one-shot via HTML5 autoplay."""
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


def play_loop_infinite():
    """Lit st.session_state.loop_wave en boucle infinie."""
    wave = st.session_state.loop_wave
    if wave is None:
        return

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


def stop_audio():
    """Stop immédiat."""
    st.session_state.looping = False
    st.session_state.loop_wave = None
    st.markdown("<audio></audio>", unsafe_allow_html=True)
    st.success("Lecture arrêtée.")


###############################################################################
# 432 Hz DIAPASON
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
# SECTION SYNTH
###############################################################################

if section == "Synth":
    st.header("Synthétiseur 432 Hz — Boucle infinie ⟷ Stop")

    midi = st.slider("Note MIDI", 21, 108, 69)
    freq = midi_to_freq(midi)
    st.write(f"Fréquence : **{freq:.2f} Hz**")

    duration = st.slider("Durée (s)", 0.1, 10.0, 1.0)

    params = dict(
        osc="sine",
        attack=0.01,
        decay=0.1,
        sustain=0.8,
        release=0.2,
        volume=1.0,
    )

    # PLAY ONESHOT
    if st.button("▶️ Jouer"):
        st.session_state.looping = False
        wave = render_note(freq, duration, params)
        play_once(wave)

    # TOGGLE BOUCLE / STOP
    toggle = st.button("🔁 Boucle infinie" if not st.session_state.looping else "⏹️ Stop")

    if toggle:
        # ACTIVER BOUCLE
        if not st.session_state.looping:
            st.session_state.looping = True
            wave = render_note(freq, duration, params)
            long = np.tile(wave, 2000)
            st.session_state.loop_wave = long
            play_loop_infinite()

        # STOP
        else:
            stop_audio()


###############################################################################
# SECTION PIANO
###############################################################################

elif section == "Piano":
    st.header("Piano Interactif — Boucle infinie ⟷ Stop — Accordage 432 Hz")

    raw_note = piano_component()

    # Extraction robuste
    note = raw_note
    if isinstance(note, dict):
        note = note.get("value")

    if isinstance(note, str) and len(note) >= 2:

        name = note[:-1]
        octave = int(note[-1])
        names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

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

        # PLAY
        st.session_state.looping = False
        play_once(wave)

        # TOGGLE BOUCLE / STOP
        toggle = st.button("🔁 Boucle infinie (piano)" if not st.session_state.looping else "⏹️ Stop")

        if toggle:
            if not st.session_state.looping:
                st.session_state.looping = True
                long = np.tile(wave, 2000)
                st.session_state.loop_wave = long
                play_loop_infinite()
            else:
                stop_audio()


###############################################################################
# SECTION SEQUENCEUR
###############################################################################

elif section == "Séquenceur":
    st.header("Séquenceur — Boucle infinie ⟷ Stop — Accordage 432 Hz")

    note_list = ["C4","D4","E4","F4","G4","A4","B4"]

    names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
    freq_map = {}

    for n in note_list:
        name = n[:-1]
        octave = int(n[-1])
        midi = names.index(name) + octave * 12
        freq_map[n] = midi_to_freq(midi)

    patterns = {"track1": [note_list[i % 7] for i in range(16)]}

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

    # On génère la séquence ici (une seule fois par run)
    wave = seq_multi_track(patterns, freq_map, bpm, params_tracks)

    # PLAY
    if st.button("▶️ Jouer séquence"):
        st.session_state.looping = False
        play_once(wave)

    # TOGGLE LOOP / STOP
    toggle = st.button("🔁 Boucle infinie (seq)" if not st.session_state.looping else "⏹️ Stop")

    if toggle:
        if not st.session_state.looping:
            st.session_state.looping = True
            long = np.tile(wave, 2000)
            st.session_state.loop_wave = long
            play_loop_infinite()
        else:
            stop_audio()
