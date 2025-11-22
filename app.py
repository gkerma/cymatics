import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO

st.set_page_config(page_title="Générateur de son", page_icon="🎵")

st.title("🎵 Générateur de son – Demo Streamlit")

st.write(
    "Utilise les sliders pour choisir une fréquence et une durée, "
    "puis clique sur **Générer le son** pour l’écouter."
)

# Paramètres
freq = st.slider("Fréquence (Hz)", min_value=50, max_value=2000, value=440, step=10)
duration = st.slider("Durée (secondes)", min_value=0.1, max_value=3.0, value=1.0, step=0.1)
wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"])
volume = st.slider("Volume (0 à 1)", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

st.caption("Astuce : bouge la fréquence et régénère pour entendre la différence.")

sample_rate = 44100  # 44.1 kHz standard audio

def generate_wave(freq, duration, wave_type, volume, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    if wave_type == "Sinus":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "Carré":
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "Dent de scie":
        # Signal en dent de scie simple
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    else:
        wave = np.sin(2 * np.pi * freq * t)

    # Application du volume et conversion en int16 pour WAV
    wave = volume * wave
    audio = np.int16(wave * 32767)
    return audio

if st.button("Générer le son"):
    audio_data = generate_wave(freq, duration, wave_type, volume, sample_rate)

    # Écrire dans un buffer mémoire au format WAV
    buffer = BytesIO()
    wavfile.write(buffer, sample_rate, audio_data)
    buffer.seek(0)

    st.audio(buffer, format="audio/wav")
    st.success(f"Son généré : {freq} Hz, {duration:.1f} s, forme {wave_type.lower()}.")
