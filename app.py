import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO
import base64

st.set_page_config(page_title="Piano Streamlit", layout="wide")

st.title("🎹 Piano – Génération d'accords")

# -------------------------------------------------------------
# Définition des notes (octave 4 ici)
# -------------------------------------------------------------
notes_freq = {
    "C4": 261.63,  # Do
    "C#4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "A4": 440.00,
    "A#4": 466.16,
    "B4": 493.88,
    "C5": 523.25,
}

white_keys = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
black_keys = ["C#4", "D#4", None, "F#4", "G#4", "A#4", None]

# -------------------------------------------------------------
# Style CSS du piano
# -------------------------------------------------------------
piano_css = """
<style>
.piano {
    position: relative;
    width: 700px;
    height: 200px;
    margin: 20px auto;
}

.white-key {
    width: 60px;
    height: 200px;
    background: white;
    border: 1px solid black;
    float: left;
    position: relative;
    z-index: 1;
    text-align: center;
    line-height: 180px;
}

.black-key {
    width: 40px;
    height: 120px;
    background: black;
    position: absolute;
    z-index: 2;
    margin-left: -20px;
    text-align: center;
    line-height: 100px;
    color: white;
}

.key-selected {
    background: #88c0ff !important;
}
</style>
"""

st.markdown(piano_css, unsafe_allow_html=True)

# -------------------------------------------------------------
# Sélection multiple des touches
# -------------------------------------------------------------
st.subheader("Sélection des notes (accord)")

selected_notes = st.multiselect(
    "Choisis plusieurs touches du piano pour générer un accord :",
    list(notes_freq.keys()),
    default=[]
)

# -------------------------------------------------------------
# Dessin du piano interactif
# (les touches cliquées changent l'état du multiselect)
# -------------------------------------------------------------
st.markdown("<div class='piano'>", unsafe_allow_html=True)

# Dessin touches blanches
for i, note in enumerate(white_keys):
    selected_class = " key-selected" if note in selected_notes else ""
    st.markdown(
        f"<div class='white-key{selected_class}'>{note}</div>",
        unsafe_allow_html=True
    )

# Dessin touches noires par-dessus
for i, note in enumerate(black_keys):
    if note is None:
        continue
    x = i * 60 + 45  # positionnement entre touches blanches
    selected_class = " key-selected" if note in selected_notes else ""
    st.markdown(
        f"<div class='black-key{selected_class}' style='left:{x}px'>{note}</div>",
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Paramètres son
# -------------------------------------------------------------
duration = st.slider("Durée (s)", 0.1, 5.0, 1.0, 0.1)
volume = st.slider("Volume", 0.0, 1.0, 0.5, 0.05)
wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"])

sample_rate = 44100

def generate_wave(freq, duration, wave_type, volume, sr):
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    if wave_type == "Sinus":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "Carré":
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "Dent de scie":
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    return volume * wave

# -------------------------------------------------------------
# Bouton pour jouer l'accord
# -------------------------------------------------------------
if st.button("Jouer l'accord"):

    if not selected_notes:
        st.warning("Sélectionne au moins une note.")
    else:
        # Génération de l’accord (somme des signaux)
        waves = [
            generate_wave(notes_freq[n], duration, wave_type, volume, sample_rate)
            for n in selected_notes
        ]
        mix = np.sum(waves, axis=0)
        mix /= np.max(np.abs(mix)) + 1e-9  # normalisation
        audio = np.int16(mix * 32767)

        buffer = BytesIO()
        wavfile.write(buffer, sample_rate, audio)
        buffer.seek(0)

        # Lecture audio
        st.audio(buffer, format="audio/wav")

        st.success(f"Accord joué : {', '.join(selected_notes)}")
