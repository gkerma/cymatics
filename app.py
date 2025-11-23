
import streamlit as st
import numpy as np
from io import BytesIO
from scipy.io.wavfile import write
import base64

# --- Imports ---
from synth.engine import render_note, render_chord, to_int16
from sequencer.stepseq import seq_multi_track
from ui.piano_component import piano_component

# --- Audio utilities ---
SAMPLE_RATE = 44100
BUFFER_LENGTH = 60

def play_audio_once(audio_float, sample_rate=SAMPLE_RATE):
    audio_int16 = (audio_float * 32767).astype("int16")
    st.audio(BytesIO(audio_int16.tobytes()), format="audio/wav")

def play_audio_loop(audio_float, sample_rate=SAMPLE_RATE):
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

# --- 432 Hz Diapason ---
diapason = st.sidebar.number_input("Diapason A4 (Hz)", 400.0, 500.0, 432.0, 0.1)

def midi_to_freq(midi, a4=diapason):
    return a4 * (2 ** ((midi - 69) / 12))

# --- UI Sections ---
section = st.sidebar.selectbox("Section", ["Synth", "Piano", "Sequencer"])

# --- Synth ---
if section == "Synth":
    st.header("Synth 432 Hz + boucle 60s")
    midi = st.slider("MIDI note", 21, 108, 69)  # A4 default
    freq = midi_to_freq(midi)
    duration = st.slider("Durée (s)", 0.1, 10.0, 1.0)
    params = {"osc": "sine", "attack":0.01,"decay":0.1,"sustain":0.8,"release":0.2,"volume":1}

    if st.button("Jouer note"):
        w = render_note(freq, duration, params)
        if st.checkbox("Boucle longue 60s"):
            reps = int(BUFFER_LENGTH/duration)+1
            w2 = np.tile(w,reps)[:int(BUFFER_LENGTH*SAMPLE_RATE)]
            play_audio_loop(w2)
        else:
            play_audio_once(w)

# --- Piano ---
elif section == "Piano":
    st.header("Piano Interactif 432 Hz")
    note = piano_component()
    if note:
        name = note[:-1]
        octave = int(note[-1])
        names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        midi = names.index(name) + octave*12
        freq = midi_to_freq(midi)
        params = {"osc":"sine","attack":0.01,"decay":0.1,"sustain":0.8,"release":0.2,"volume":1}
        w = render_note(freq,1.0,params)
        if st.checkbox("Boucle piano 60s"):
            reps = int(BUFFER_LENGTH/1.0)+1
            play_audio_loop(np.tile(w,reps)[:int(BUFFER_LENGTH*SAMPLE_RATE)])
        else:
            play_audio_once(w)

# --- Sequencer ---
elif section == "Sequencer":
    st.header("Séquenceur minimal")
    note_list = ["C4","D4","E4","F4","G4","A4","B4"]
    patterns = {
        "track1":[note_list[i%7] for i in range(16)]
    }
    freq_map = {n:midi_to_freq(60+note_list.index(n)) for n in note_list}
    params_tracks={"track1":{"osc":"sine","attack":0.01,"decay":0.1,"sustain":0.8,"release":0.2,"volume":1}}
    bpm=120
    if st.button("Jouer séquence"):
        w = seq_multi_track(patterns,freq_map,bpm,params_tracks)
        if st.checkbox("Boucle séquence 60s"):
            reps = int(BUFFER_LENGTH/(len(w)/SAMPLE_RATE))+1
            play_audio_loop(np.tile(w,reps)[:int(BUFFER_LENGTH*SAMPLE_RATE)])
        else:
            play_audio_once(w)
