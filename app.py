import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO
import base64

st.set_page_config(page_title="Audio Tools", layout="wide")

st.title("🎵 Outils Audio : Générateur + Piano")

# -------------------------------------------------------------
# Sélecteur de mode
# -------------------------------------------------------------
mode = st.selectbox("Mode :", ["Générateur de fréquence", "Piano"])

sample_rate = 44100

# -------------------------------------------------------------
# Fonction utilitaire : encoder WAV en HTML audio loop
# -------------------------------------------------------------
def play_audio_loop(audio_data):
    buffer = BytesIO()
    wavfile.write(buffer, sample_rate, audio_data)
    buffer.seek(0)

    wav_bytes = buffer.read()
    b64 = base64.b64encode(wav_bytes).decode()

    audio_html = f"""
        <audio controls autoplay loop>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


# -------------------------------------------------------------
# Générateur de forme d'onde
# -------------------------------------------------------------
def generate_wave(freq, duration, wave_type, volume):
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


# =====================================================================
#   MODE 1 : GENERATEUR DE FREQUENCE AVEC BOUCLE
# =====================================================================
if mode == "Générateur de fréquence":

    st.header("Générateur de fréquence")

    # Entrée de fréquence
    freq = st.number_input("Fréquence (Hz)", min_value=1.0, max_value=20000.0, value=440.0)
    freq_slider = st.slider("Slider : 50–2000 Hz", 50, 2000, int(freq))
    freq = float(freq_slider)

    duration = st.slider("Durée (secondes)", 0.1, 300.0, 1.0, 0.1)
    wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"])
    volume = st.slider("Volume", 0.0, 1.0, 0.5)
    loop = st.checkbox("Lecture en boucle")

    if st.button("Générer le son"):

        audio_data = generate_wave(freq, duration, wave_type, volume)

        if loop:
            play_audio_loop(audio_data)
        else:
            buffer = BytesIO()
            wavfile.write(buffer, sample_rate, audio_data)
            buffer.seek(0)
            st.audio(buffer, format="audio/wav")

        st.success(f"Son généré : {freq} Hz – {duration} s – {wave_type}")


# =====================================================================
#   MODE 2 : PIANO + ACCORDS + BOUCLE
# =====================================================================
else:
    st.header("Piano polyphonique")

    notes_freq = {
        "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13,
        "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00,
        "G#4": 415.30, "A4": 440.00, "A#4": 466.16, "B4": 493.88,
        "C5": 523.25,
    }

    selected_notes = st.multiselect(
        "Sélectionne plusieurs notes pour un accord :",
        list(notes_freq.keys())
    )

    duration = st.slider("Durée (s)", 0.1, 5.0, 1.0)
    volume = st.slider("Volume", 0.0, 1.0, 0.5)
    wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"], key="piano_wave")
    loop = st.checkbox("Lecture en boucle (accord)")

    if st.button("Jouer l’accord"):

        if not selected_notes:
            st.warning("Choisis au moins une touche.")
        else:
            waves = [generate_wave(notes_freq[n], duration, wave_type, volume) for n in selected_notes]
            mix = np.sum(waves, axis=0)
            mix /= np.max(np.abs(mix)) + 1e-9
            audio = np.int16(mix * 32767)

            if loop:
                play_audio_loop(audio)
            else:
                buffer = BytesIO()
                wavfile.write(buffer, sample_rate, audio)
                buffer.seek(0)
                st.audio(buffer, format="audio/wav")

            st.success("Accord : " + ", ".join(selected_notes))
