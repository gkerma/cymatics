import streamlit as st
import numpy as np
from scipy.io import wavfile
from io import BytesIO
import base64

st.set_page_config(page_title="Audio Tools", layout="wide")

st.title("🎵 Outils Audio : Générateur + Piano")

# Durée interne très longue pour éliminer le tick du restart HTML
BUFFER_LENGTH = 60.0      # en secondes (tu peux mettre 120.0, 300.0, etc.)
sample_rate = 44100


# -------------------------------------------------------------
# Fonction utilitaire : lecture HTML en boucle longue
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
def generate_wave(freq, duration, wave_type, volume, buffer_length=BUFFER_LENGTH):
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

    # Répétition pour fabriquer un fichier très long
    repeat_count = int(buffer_length // duration) + 1
    long_wave = np.tile(wave, repeat_count)
    long_wave = long_wave[:int(buffer_length * sample_rate)]

    return np.int16(long_wave * 32767)


# -------------------------------------------------------------
# Sélecteur de mode
# -------------------------------------------------------------
mode = st.selectbox("Mode :", ["Générateur de fréquence", "Piano polyphonique"])


# =====================================================================
#   MODE 1 : GENERATEUR DE FREQUENCE
# =====================================================================
if mode == "Générateur de fréquence":

    st.header("Générateur de fréquence simple (boucle longue)")

    freq = st.number_input("Fréquence (Hz)", min_value=1.0, max_value=20000.0, value=440.0)
    freq_slider = st.slider("Ajustement rapide (50–2000 Hz)", 50, 2000, int(freq))
    freq = float(freq_slider)

    duration = st.slider("Durée du cycle (s)", 0.1, 300.0, 1.0)
    wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"])
    volume = st.slider("Volume", 0.0, 1.0, 0.5)

    loop = st.checkbox("Lecture en boucle (60 secondes de buffer)")

    if st.button("Générer le son"):

        audio_data = generate_wave(freq, duration, wave_type, volume, BUFFER_LENGTH)

        if loop:
            play_audio_loop(audio_data)
        else:
            buffer = BytesIO()
            wavfile.write(buffer, sample_rate, audio_data)
            buffer.seek(0)
            st.audio(buffer, format="audio/wav")

        st.success(f"Signal généré : {freq} Hz – {duration}s – {wave_type}")


# =====================================================================
#   MODE 2 : PIANO POLYPHONIQUE
# =====================================================================
else:
    st.header("Piano polyphonique (accords)")

    notes_freq = {
        "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13,
        "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00,
        "G#4": 415.30, "A4": 440.00, "A#4": 466.16, "B4": 493.88,
        "C5": 523.25,
    }

    selected_notes = st.multiselect(
        "Sélectionne plusieurs touches pour un accord :",
        list(notes_freq.keys())
    )

    duration = st.slider("Durée du cycle (s)", 0.1, 5.0, 1.0)
    wave_type = st.selectbox("Forme d’onde", ["Sinus", "Carré", "Dent de scie"], key="piano_wave")
    volume = st.slider("Volume", 0.0, 1.0, 0.5)

    loop = st.checkbox("Lecture en boucle (buffer 60s)")

    if st.button("Jouer l’accord"):

        if not selected_notes:
            st.warning("Choisis au moins une note.")
        else:
            # Génération des voix
            waves = [
                generate_wave(notes_freq[n], duration, wave_type, volume, duration)   # note courte
                for n in selected_notes
            ]

            # Somme polyphonique
            mix = np.sum(waves, axis=0).astype(np.float64)
            norm = np.max(np.abs(mix)) + 1e-9
            mix = mix / norm

            # Répétition pour produire un long buffer de 60s
            repeat_count = int(BUFFER_LENGTH // duration) + 1
            long_mix = np.tile(mix, repeat_count)
            long_mix = long_mix[:int(BUFFER_LENGTH * sample_rate)]

            audio = np.int16(long_mix * 32767)

            if loop:
                play_audio_loop(audio)
            else:
                buffer = BytesIO()
                wavfile.write(buffer, sample_rate, audio)
                buffer.seek(0)
                st.audio(buffer, format="audio/wav")

            st.success("Accord joué : " + ", ".join(selected_notes))
