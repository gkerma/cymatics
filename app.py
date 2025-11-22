import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO
import base64

st.set_page_config(page_title="Générateur de son", page_icon="🎵")

st.title("🎵 Générateur de son – Version avec boucle fiable")

st.subheader("Paramètres du signal")

# Saisie numérique de la fréquence
freq = st.number_input("Fréquence (Hz)", min_value=1.0, max_value=20000.0, value=440.0, step=1.0)

# Slider optionnel pour ajuster rapidement (lié à la même variable si tu veux)
freq_slider = st.slider("Ajustement rapide (50–2000 Hz)", 50, 2000, int(freq), 1)
freq = float(freq_slider)

# Durée jusqu’à 5 minutes (300 s)
duration = st.slider("Durée (secondes)", 0.1, 300.0, 1.0, 0.1)

wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"])
volume = st.slider("Volume (0 à 1)", 0.0, 1.0, 0.5, 0.05)

loop = st.checkbox("Lecture en boucle")

sample_rate = 44100


def generate_wave(freq, duration, wave_type, volume, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    if wave_type == "Sinus":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "Carré":
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "Dent de scie":
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    else:
        wave = np.sin(2 * np.pi * freq * t)

    wave = volume * wave
    return np.int16(wave * 32767)


st.subheader("Génération")

if st.button("Générer le son"):
    audio_data = generate_wave(freq, duration, wave_type, volume, sample_rate)

    # Écriture dans un buffer WAV
    buffer = BytesIO()
    wavfile.write(buffer, sample_rate, audio_data)
    buffer.seek(0)

    if not loop:
        # Mode normal : Streamlit gère le lecteur
        st.audio(buffer, format="audio/wav")
    else:
        # Mode boucle : on encode en base64 et on utilise <audio loop>
        wav_bytes = buffer.read()
        b64 = base64.b64encode(wav_bytes).decode()

        audio_html = f"""
        <audio controls autoplay loop>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            Votre navigateur ne supporte pas l'audio HTML5.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

    st.success(f"Son généré : {freq:.1f} Hz – {duration:.1f} s – forme {wave_type.lower()}.")
