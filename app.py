import streamlit as st
import numpy as np
from io import BytesIO
from scipy.io.wavfile import write
import base64
import os
import re

# Synth modules
from synth.engine import (
    render_note, render_chord,
    render_note_int16, render_chord_int16
)
from sequencer.stepseq import (
    seq_one_track, seq_multi_track, seq_to_int16
)

from ui.piano_component import piano_component


###############################################################################
# THEME STYLE ABLETON / FL STUDIO
###############################################################################

theme_path = "ui/theme.css"
if os.path.exists(theme_path):
    with open(theme_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


###############################################################################
# CONFIG GLOBALE
###############################################################################

SAMPLE_RATE = 44100
BUFFER_LENGTH = 60.0  # buffer long pour boucles sans ticks

def play_audio_loop(audio_int16):
    """Affiche un lecteur HTML5 qui boucle sans tick."""
    buffer = BytesIO()
    write(buffer, SAMPLE_RATE, audio_int16)
    buffer.seek(0)

    b64 = base64.b64encode(buffer.read()).decode()

    html = f"""
    <audio controls autoplay loop>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """

    st.markdown(html, unsafe_allow_html=True)

st.set_page_config(
    page_title="CYMATICS DAW",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎛️ CYMATICS DAW — Streamlit Ableton/FL Studio Hybrid")
###############################################################################
# BLOC 2 — SYNTHÉ STANDALONE (Ableton Instrument View)
###############################################################################

st.header("🎹 Synthé Standalone – Oscillateurs, ADSR, LFO")

colL, colR = st.columns([2, 1])

with colL:
    st.subheader("Paramètres du synthétiseur")

    # Diapason global
    diapason = st.number_input(
        "Diapason A4 (Hz)",
        min_value=400.0,
        max_value=500.0,
        value=432.0,
        step=0.1
    )

    # NOTE
    midi_note = st.slider("Note MIDI", 21, 108, 69)
    freq = diapason * (2 ** ((midi_note - 69) / 12))
    st.write(f"Fréquence : **{freq:.2f} Hz**")

    # OSCILLATEUR
    osc = st.selectbox(
        "Oscillateur",
        ["sine", "square", "saw", "triangle", "supersaw", "noise", "fm", "am", "additive"]
    )

    harmonics = 1
    mod_freq = 2.0
    mod_depth = 0.5
    mod_index = 3.0

    if osc == "additive":
        harmonics = st.slider("Nombre d'harmoniques", 1, 20, 5)

    if osc == "fm":
        mod_freq = st.slider("Mod Frequency (Hz)", 0.1, 60.0, 2.0)
        mod_index = st.slider("FM Index", 0.1, 20.0, 3.0)

    if osc == "am":
        mod_freq = st.slider("Mod Frequency (Hz)", 0.1, 60.0, 2.0)
        mod_depth = st.slider("AM Depth", 0.0, 1.0, 0.5)

    # ADSR
    st.subheader("ADSR")

    atk = st.slider("Attack (s)", 0.0, 2.0, 0.01)
    dec = st.slider("Decay (s)", 0.0, 2.0, 0.1)
    sus = st.slider("Sustain (0–1)", 0.0, 1.0, 0.8)
    rel = st.slider("Release (s)", 0.0, 3.0, 0.1)
    env_mode = st.selectbox("Mode ADSR", ["linear", "exp", "no_release"])

    # LFO
    st.subheader("LFO")

    lfo_rate = st.slider("LFO Rate (Hz)", 0.0, 20.0, 0.0)
    lfo_depth = st.slider("LFO Depth", 0.0, 1.0, 0.0)
    lfo_mode = st.selectbox("LFO Mode", ["none", "vibrato", "tremolo", "filter"])
    lfo_wave = st.selectbox("LFO Wave", ["sine", "triangle", "square", "saw"])

    # Durée et volume
    duration = st.slider("Durée (s)", 0.1, 10.0, 1.0)
    volume = st.slider("Volume", 0.0, 1.0, 0.8)


with colR:
    st.subheader("Options de lecture")

    play_mode = st.radio("Mode de jeu", ["Note unique", "Accord"])

    # Accord
    chord = []
    if play_mode == "Accord":
        chord_notes = st.multiselect(
            "Notes de l’accord :",
            ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        )

        chord_octave = st.slider("Octave", 1, 7, 4)

        for n in chord_notes:
            # conversion en MIDI
            idx = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"].index(n)
            midi = chord_octave * 12 + idx
            chord.append(diapason * (2 ** ((midi - 69) / 12)))

    loop_enabled = st.checkbox("🔁 Boucle longue (60s sans tick)")
    play_button = st.button("▶️ Jouer")


# Rendu audio
if play_button:

    params = {
        "osc": osc,
        "attack": atk,
        "decay": dec,
        "sustain": sus,
        "release": rel,
        "harmonics": harmonics,
        "mod_freq": mod_freq,
        "mod_index": mod_index,
        "mod_depth": mod_depth,
        "env_mode": env_mode,
        "lfo_rate": lfo_rate,
        "lfo_depth": lfo_depth,
        "lfo_mode": lfo_mode if lfo_mode != "none" else None,
        "lfo_wave": lfo_wave,
        "volume": volume
    }

    if play_mode == "Note unique":
        audio = render_note(freq, duration, params)
    else:
        audio = render_chord(chord, duration, params)

    # Long buffer (remplissage x fois)
    repeat = int(BUFFER_LENGTH // duration) + 1
    audio_long = np.tile(audio, repeat)
    audio_long = audio_long[:int(BUFFER_LENGTH * SAMPLE_RATE)]

    audio_int16 = (audio_long * 32767).astype(np.int16)

    if loop_enabled:
        play_audio_loop(audio_int16)
    else:
        st.audio(BytesIO(audio_int16.tobytes()), format="audio/wav")
###############################################################################
# BLOC 3 — Piano Interactif / Jeu temps réel / Générateur 432 Hz
###############################################################################

st.header("🎼 Piano Interactif & Générateur 432 Hz")

piano_col, synth_col = st.columns([2, 2])


###############################################################################
# COLONNE GAUCHE : PIANO CLIQUABLE
###############################################################################
with piano_col:
    st.subheader("Clavier interactif")

    clicked_note = piano_component()

    if clicked_note:
        st.success(f"Touche pressée : {clicked_note}")

        # Conversion note → MIDI
        note_names = ["C","C#","D","D#","E","F",
                      "F#","G","G#","A","A#","B"]
        
        regex = r"^([A-G]#?)([0-9])$"
        
        if clicked_note and isinstance(clicked_note, str):
            match = re.match(regex, clicked_note)
            if match:
                name = match.group(1)
                octave = int(match.group(2))
            else:
                st.warning("Format de note invalide : " + str(clicked_note))
                st.stop()
        else:
            st.stop()  # aucune note → on arrête proprement

        midi = note_names.index(name) + octave * 12
        freq_clicked = diapason * (2 ** ((midi - 69) / 12))

        params = {
            "osc": osc,
            "attack": atk,
            "decay": dec,
            "sustain": sus,
            "release": rel,
            "harmonics": harmonics,
            "mod_freq": mod_freq,
            "mod_index": mod_index,
            "mod_depth": mod_depth,
            "env_mode": env_mode,
            "lfo_rate": lfo_rate,
            "lfo_depth": lfo_depth,
            "lfo_mode": lfo_mode if lfo_mode != "none" else None,
            "lfo_wave": lfo_wave,
            "volume": volume
        }

        # une note instantanée (pas de long buffer ici)
        audio = render_note(freq_clicked, 1.0, params)
        audio_int16 = (audio * 32767).astype(np.int16)
        st.audio(BytesIO(audio_int16.tobytes()), format="audio/wav")


###############################################################################
# COLONNE DROITE : GÉNÉRATEUR 432 Hz / 440 Hz / FREQUENCY OSCILLATOR
###############################################################################
with synth_col:
    st.subheader("Générateur de fréquence (432Hz / 440Hz / custom)")

    gen_freq = st.number_input(
        "Fréquence (Hz) :",
        min_value=10.0,
        max_value=20000.0,
        value=float(diapason),   # synchronisé sur le diapason
        step=0.1
    )

    gen_duration = st.slider("Durée du signal (s)", 0.1, 20.0, 2.0)
    gen_wave = st.selectbox("Forme d’onde", ["sine", "square", "saw", "triangle", "supersaw"])
    gen_volume = st.slider("Volume", 0.0, 1.0, 0.7)
    gen_loop = st.checkbox("🔁 Boucle longue (60s)", key="genloop")

    play_gen = st.button("🎧 Jouer fréquence")

    if play_gen:

        gen_params = {
            "osc": gen_wave,
            "attack": 0.01,
            "decay": 0.01,
            "sustain": 1.0,
            "release": 0.01,
            "harmonics": 5,
            "mod_freq": 2.0,
            "mod_index": 3.0,
            "mod_depth": 0.5,
            "env_mode": "linear",
            "lfo_rate": 0.0,
            "lfo_depth": 0.0,
            "lfo_mode": None,
            "lfo_wave": "sine",
            "volume": gen_volume
        }

        wave = render_note(gen_freq, gen_duration, gen_params)

        # buffer long
        reps = int(BUFFER_LENGTH // gen_duration) + 1
        wave_long = np.tile(wave, reps)
        wave_long = wave_long[:int(BUFFER_LENGTH * SAMPLE_RATE)]
        wave_int16 = (wave_long * 32767).astype(np.int16)

        if gen_loop:
            play_audio_loop(wave_int16)
        else:
            st.audio(BytesIO(wave_int16.tobytes()), format="audio/wav")
###############################################################################
# BLOC 4 — SEQUENCEUR MULTIPISTES + EXPORT WAV & MIDI
###############################################################################

st.header("🧩 Séquenceur Multipistes (style FL Studio / Ableton Rack)")

seq_cols = st.columns([2, 1])

###############################################################################
# COLONNE 1 : CONFIGURATION DU SEQUENCEUR
###############################################################################

with seq_cols[0]:

    st.subheader("Configuration générale")

    bpm = st.slider("BPM", 40, 200, 120)
    subdivision = st.selectbox("Subdivision rythmique", ["4", "8", "16", "32"], index=2)
    subdivision = int(subdivision)
    swing = st.slider("Swing (groove)", -0.5, 0.5, 0.0)
    gate = st.slider("Gate (%)", 0.1, 1.0, 0.9)

    num_steps = st.selectbox("Nombre de pas", [16, 32, 64], index=0)

    st.markdown("---")

    st.subheader("Pistes")

    # Définition des pistes
    track_names = st.multiselect(
        "Ajouter des pistes :",
        ["kick", "snare", "hihat", "bass", "lead", "pad"],
        default=["kick", "snare", "hihat"]
    )

    # Note dictionary
    note_names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

    # stockage patterns
    patterns = {}
    params_per_track = {}

    for tname in track_names:
        st.markdown(f"#### Piste : {tname}")

        # valeurs par défaut par instrument
        default_note = "C3" if tname == "bass" else "C4"

        with st.expander(f"Pattern : {tname}", expanded=True):

            steps = []
            for i in range(num_steps):
                col = st.columns(num_steps // 8 + 1)[i % 8]  # 8 steps per row
                with col:
                    active = st.checkbox(f"{i+1}", key=f"{tname}_step_{i}")
                    if active:
                        steps.append(default_note)
                    else:
                        steps.append(0)

            patterns[tname] = steps

        # paramètres synthé par piste
        st.markdown(f"##### Synthé ({tname})")

        osc_t = st.selectbox(
            f"Oscillateur ({tname})",
            ["sine", "square", "saw", "triangle", "supersaw", "fm", "am", "additive"],
            key=f"{tname}_osc"
        )

        atk_t = st.slider(f"Attack ({tname})", 0.0, 1.0, 0.01, key=f"{tname}_atk")
        dec_t = st.slider(f"Decay ({tname})", 0.0, 1.0, 0.1, key=f"{tname}_dec")
        sus_t = st.slider(f"Sustain ({tname})", 0.0, 1.0, 0.8, key=f"{tname}_sus")
        rel_t = st.slider(f"Release ({tname})", 0.0, 2.0, 0.1, key=f"{tname}_rel")

        params_per_track[tname] = {
            "osc": osc_t,
            "attack": atk_t,
            "decay": dec_t,
            "sustain": sus_t,
            "release": rel_t,
            "env_mode": "linear",
            "mod_freq": 2.0,
            "mod_index": 3.0,
            "mod_depth": 0.5,
            "harmonics": 5,
            "lfo_rate": 0.0,
            "lfo_depth": 0.0,
            "lfo_mode": None,
            "lfo_wave": "sine",
            "volume": 1.0
        }

with seq_cols[1]:
    st.subheader("Playback & Export")

    play_seq = st.button("▶️ Lire le séquenceur")
    export_wav = st.button("💾 Export WAV")
    export_midi = st.button("🎼 Export MIDI")


###############################################################################
# RENDU AUDIO DU SEQUENCEUR
###############################################################################

if play_seq:

    # map notes -> freq
    notes_freq = {}
    for octave in range(0, 9):
        for i, note in enumerate(note_names):
            midi = octave * 12 + i
            freq = diapason * (2 ** ((midi - 69) / 12))
            notes_freq[f"{note}{octave}"] = freq

    wave = seq_multi_track(
        patterns,
        notes_freq,
        bpm,
        params_per_track,
        subdivision=subdivision,
        sample_rate=SAMPLE_RATE,
        gate=gate,
        swing=swing
    )

    wave_int16 = (wave * 32767).astype(np.int16)
    st.audio(BytesIO(wave_int16.tobytes()), format="audio/wav")
    st.success("Séquence jouée.")


###############################################################################
# EXPORT WAV
###############################################################################

if export_wav:

    # map notes -> freq
    notes_freq = {}
    for octave in range(0, 9):
        for i, note in enumerate(note_names):
            midi = octave * 12 + i
            freq = diapason * (2 ** ((midi - 69) / 12))
            notes_freq[f"{note}{octave}"] = freq

    wave = seq_multi_track(
        patterns,
        notes_freq,
        bpm,
        params_per_track,
        subdivision=subdivision,
        sample_rate=SAMPLE_RATE,
        gate=gate,
        swing=swing
    )

    wave_int16 = (wave * 32767).astype(np.int16)

    out = BytesIO()
    write(out, SAMPLE_RATE, wave_int16)
    st.download_button(
        label="Télécharger WAV",
        data=out,
        file_name="sequence.wav",
        mime="audio/wav"
    )
    st.success("Fichier WAV exporté.")


###############################################################################
# EXPORT MIDI
###############################################################################

if export_midi:
    # On génère un MIDI simplifié (1 note par step par piste)
    from mido import MidiFile, MidiTrack, Message

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    ticks_per_beat = 480
    mid.ticks_per_beat = ticks_per_beat

    for tname, patt in patterns.items():
        for i, step in enumerate(patt):
            if step != 0:
                # extraire la note
                note = step[:-1]
                octave = int(step[-1])
                midi = note_names.index(note) + octave * 12

                track.append(Message("note_on", note=midi, velocity=90, time=0))
                track.append(Message("note_off", note=midi, velocity=90, time=int(ticks_per_beat / 4)))

    out = BytesIO()
    mid.save(out)
    st.download_button(
        label="Télécharger MIDI",
        data=out,
        file_name="sequence.mid",
        mime="audio/midi"
    )
    st.success("Fichier MIDI exporté.")
