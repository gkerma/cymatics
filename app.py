import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO
import base64

st.set_page_config(page_title="Audio Tools 432Hz", layout="wide")

st.title("🎵 Synthèse Audio 432 Hz – Multi-Octaves + Gammes + Piano visuel")

# -------------------------------------------------------------
# CONFIGURATION GLOBALE
# -------------------------------------------------------------
SAMPLE_RATE = 44100
BUFFER_LENGTH = 60.0  # secondes de son pour boucles sans ticks


# -------------------------------------------------------------
# MIDI -> fréquence (avec diapason variable)
# -------------------------------------------------------------
def midi_to_freq(midi, a4=432.0):
    return a4 * (2 ** ((midi - 69) / 12))   # 69 = A4 MIDI


# -------------------------------------------------------------
# Génération onde simple
# -------------------------------------------------------------
def generate_wave(freq, duration, wave_type, volume, buffer_length=BUFFER_LENGTH):

    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    if wave_type == "Sinus":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "Carré":
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "Dent de scie":
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    else:
        wave = np.sin(2 * np.pi * freq * t)

    wave = volume * wave

    # Buffer long
    repeat_count = int(buffer_length // duration) + 1
    long_wave = np.tile(wave, repeat_count)
    long_wave = long_wave[:int(buffer_length * SAMPLE_RATE)]

    return np.int16(long_wave * 32767)


# -------------------------------------------------------------
# HTML Loop Audio
# -------------------------------------------------------------
def play_audio_loop(audio):
    buffer = BytesIO()
    wavfile.write(buffer, SAMPLE_RATE, audio)
    buffer.seek(0)

    b64 = base64.b64encode(buffer.read()).decode()
    html = f"""
    <audio controls autoplay loop>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)


# -------------------------------------------------------------
# Sélecteur de mode
# -------------------------------------------------------------
mode = st.sidebar.selectbox(
    "Mode :",
    ["Générateur simple", "Piano multi-octaves", "Gammes & Chakras"]
)


# ============================================================
# MODE 1 — GENERATEUR SIMPLE (lié au diapason)
# ============================================================
if mode == "Générateur simple":

    st.header("Générateur simple lié au diapason")

    diapason = st.number_input(
        "Diapason A4 (Hz)",
        min_value=400.0,
        max_value=500.0,
        value=432.0,
        step=0.1
    )

    midi_note = st.slider("Note MIDI", 0, 127, 69)  # 69 = A4

    freq = midi_to_freq(midi_note, diapason)

    st.write(f"Fréquence = **{freq:.3f} Hz**")

    duration = st.slider("Durée cycle (s)", 0.1, 10.0, 1.0)
    volume = st.slider("Volume", 0.0, 1.0, 0.5)
    wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"])
    loop = st.checkbox("Boucle")

    if st.button("Jouer"):
        audio = generate_wave(freq, duration, wave_type, volume)

        if loop:
            play_audio_loop(audio)
        else:
            st.audio(BytesIO(audio.tobytes()), format="audio/wav")



# ============================================================
# MODE 2 — PIANO MULTI-OCTAVES + VISUEL
# ============================================================
elif mode == "Piano multi-octaves":

    st.header("Piano multi-octaves 432 Hz")

    diapason = st.number_input(
        "Diapason A4 (Hz)",
        min_value=400.0,
        max_value=500.0,
        value=432.0,
        step=0.1
    )

    # Choix des octaves
    octaves = st.slider("Octaves", 3, 6, (3, 5))   # affiche C3 → C6

    # Génération liste des notes
    notes = []
    for midi in range(octaves[0] * 12, octaves[1] * 12 + 12):
        name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][midi % 12]
        octave = midi // 12 - 1
        notes.append((f"{name}{octave}", midi))

    notes_freq = {name: midi_to_freq(midi, diapason) for name, midi in notes}

    # Sélection multi-notes
    selected = st.multiselect("Sélection des notes pour accord :", list(notes_freq.keys()))

    # Visuel du clavier
    st.subheader("Clavier visuel (non cliquable)")

    piano_css = """
    <style>
    .piano { display: flex; }
    .white { width: 40px; height: 200px; background: white; border: 1px solid black; position: relative; }
    .black { width: 25px; height: 120px; background: black; position: absolute; left: 28px; top: 0; z-index: 2; }
    .sel { background: #88c0ff !important; }
    </style>
    """
    st.markdown(piano_css, unsafe_allow_html=True)

    html = "<div class='piano'>"
    for name, midi in notes:
        is_selected = " sel" if name in selected else ""
        if "#" in name:
            html += f"<div class='white'></div><div class='black{is_selected}'></div>"
        else:
            html += f"<div class='white{is_selected}'></div>"
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    # Audio
    duration = st.slider("Durée cycle (s)", 0.1, 5.0, 1.0)
    volume = st.slider("Volume", 0.0, 1.0, 0.5)
    wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"], key="pianowave")
    loop = st.checkbox("Boucle", key="pianoloop")

    if st.button("Jouer accord"):
        if not selected:
            st.warning("Sélectionne au moins une note.")
        else:
            waves = [
                generate_wave(notes_freq[n], duration, wave_type, volume, duration)
                for n in selected
            ]

            mix = np.sum(waves, axis=0).astype(np.float64)
            mix /= np.max(np.abs(mix)) + 1e-9

            repeat = int(BUFFER_LENGTH // duration) + 1
            long_mix = np.tile(mix, repeat)
            long_mix = long_mix[:int(BUFFER_LENGTH * SAMPLE_RATE)]

            audio = np.int16(long_mix * 32767)

            if loop:
                play_audio_loop(audio)
            else:
                buffer = BytesIO()
                wavfile.write(buffer, SAMPLE_RATE, audio)
                buffer.seek(0)
                st.audio(buffer, format="audio/wav")

            st.success("Accord joué.")



# ============================================================
# MODE 3 — GAMMES 432 Hz & CHAKRAS
# ============================================================
else:

    st.header("Gammes spéciales 432 Hz – Chakras & Modes")

    diapason = st.number_input(
        "Diapason A4 (Hz)",
        min_value=400.0,
        max_value=500.0,
        value=432.0,
        step=0.1
    )

    modes = {
        "Gammes 432 Hz – Naturelle (C majeur 432)": [0,2,4,5,7,9,11,12],
        "Mode Dorien": [0,2,3,5,7,9,10,12],
        "Mode Phrygien": [0,1,3,5,7,8,10,12],
        "Mode Lydien": [0,2,4,6,7,9,11,12],
        "Mode Mixolydien": [0,2,4,5,7,9,10,12],
        "Mode Aeolien (mineur naturel)": [0,2,3,5,7,8,10,12],
        "Mode Locrien": [0,1,3,5,6,8,10,12],

        "Chakra Racine (C)": [0],
        "Chakra Sacré (D)": [2],
        "Chakra Plexus solaire (E)": [4],
        "Chakra Cœur (F)": [5],
        "Chakra Gorge (G)": [7],
        "Chakra 3e œil (A 432)": [9],
        "Chakra Coronal (B)": [11],
    }

    mode_name = st.selectbox("Choisir un mode / chakra :", list(modes.keys()))

    base_midi = 60   # C4
    midi_notes = [base_midi + i for i in modes[mode_name]]
    freqs = [midi_to_freq(midi, diapason) for midi in midi_notes]

    st.write("Fréquences :", freqs)

    duration = st.slider("Durée note (s)", 0.1, 5.0, 1.0)
    wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"], key="modewave")
    volume = st.slider("Volume", 0.0, 1.0, 0.5)

    if st.button("Jouer gamme / chakra"):

        waves = [generate_wave(f, duration, wave_type, volume, duration) for f in freqs]

        total = np.concatenate(waves)
        repeat = int(BUFFER_LENGTH // duration) + 1
        long_total = np.tile(total, repeat)
        long_total = long_total[:int(BUFFER_LENGTH * SAMPLE_RATE)]

        audio = np.int16(long_total * 32767)
        play_audio_loop(audio)

        st.success("Lecture.")
