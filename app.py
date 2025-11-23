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
# CONFIG
###############################################################################

st.set_page_config(page_title="Cymatics DAW", layout="wide")

SAMPLE_RATE = 44100

# États persistants
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
    """Lecture one-shot via HTML5 autoplay."""
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
    """Lit la wave dans session_state en boucle infinie."""
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
    st.session_state.looping = False
    st.session_state.loop_wave = None
    st.markdown("<audio></audio>", unsafe_allow_html=True)
    st.success("Lecture stoppée.")


###############################################################################
# DIAPASON 432 HZ
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
# SYNTH
###############################################################################

if section == "Synth":
    st.header("Synthétiseur 432 Hz — Boucle infinie & STOP")

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

    # --- PLAY ---
    if st.button("▶️ Jouer"):
        st.session_state.looping = False
        wave = render_note(freq, duration, params)
        play_once(wave)

    col1, col2 = st.columns(2)

    # --- BOUTON TOGGLE BOUCLE INFINIE / STOP ---
    toggle = st.button("🔁 Boucle infinie" if not st.session_state.looping else "⏹️ Stop")
    
    if toggle:
        # Si on clique alors que la boucle n'est pas active → activer
        if not st.session_state.looping:
            st.session_state.looping = True
            wave = render_note(freq, duration, params)
            long = np.tile(wave, 2000)
            st.session_state.loop_wave = long
            play_loop_infinite()
    
        # Si on clique alors que la boucle est active → STOP
        else:
            stop_audio()

###############################################################################
# PIANO
###############################################################################

elif section == "Piano":
    st.header("Piano Interactif 432 Hz — Boucle infinie & STOP")

    note = piano_component()

    # Extraction robuste d'une note string
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

        col1, col2 = st.columns(2)

        # BOUCLE
        if not st.session_state.looping:
            if col1.button("🔁 Boucle infinie (piano)"):
                st.session_state.looping = True
                long = np.tile(wave, 3000)
                st.session_state.loop_wave = long
                play_loop_infinite()
        else:
            if col2.button("⏹️ Stop"):
                stop_audio()


###############################################################################
# SEQUENCEUR
###############################################################################

elif section == "Séquenceur":
    st.header("Séquenceur 432 Hz — Boucle infinie & STOP")

    note_list = ["C4","D4","E4","F4","G4","A4","B4"]

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

    # Génération séquence
    wave = seq_multi_track(patterns, freq_map, bpm, params_tracks)

    # PLAY
    if st.button("▶️ Jouer séquence"):
        st.session_state.looping = False
        play_once(wave)

    col1, col2 = st.columns(2)

    # BOUCLE INFINIE
    if not st.session_state.looping:
        if col1.button("🔁 Boucle infinie (séquenceur)"):
            st.session_state.looping = True
            long = np.tile(wave, 3000)
            st.session_state.loop_wave = long
            play_loop_infinite()
    else:
        if col2.button("⏹️ Stop"):
            stop_audio()
