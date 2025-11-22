import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO
import time

st.set_page_config(page_title="Générateur de son", page_icon="🎵")

st.title("🎵 Générateur de son – Version avancée")

# --- INPUTS ---
st.subheader("Paramètres du signal")

# Saisie numérique + slider synchronisé
freq_input = st.text_input("Fréquence (Hz)", value="440")
try:
    freq = float(freq_input)
    if freq <= 0:
        st.warning("La fréquence doit être positive.")
        freq = 440
except:
    st.warning("Valeur de fréquence invalide. Utilisation de 440 Hz.")
    freq = 440

freq_slider = st.slider("Ajustement fin via slider", 50, 2000, int(freq), 1)
# Si l’utilisateur bouge le slider, mettre freq à jour
freq = freq_slider

duration = st.slider("Durée (secondes)", 0.1, 3.0, 1.0, 0.1)
wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"])
volume = st.slider("Volume (0 à 1)", 0.0, 1.0, 0.5, 0.05)

loop = st.checkbox("Lecture en boucle continue")

sample_rate = 44100


# --- GENERATION ---
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


# --- ACTIONS ---
st.subheader("Génération")

generate_btn = st.button("Générer et jouer le son")

if generate_btn or loop:
    audio_data = generate_wave(freq, duration, wave_type, volume, sample_rate)

    buffer = BytesIO()
    wavfile.write(buffer, sample_rate, audio_data)
    buffer.seek(0)

    st.audio(buffer, format="audio/wav")
    st.success(f"{'Boucle' if loop else 'Son'} : {freq} Hz – {duration:.1f} s – {wave_type}")

    # Boucle simple : refresher Streamlit toutes les X secondes
    if loop:
        time.sleep(duration)
        st.rerun()
