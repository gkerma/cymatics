import numpy as np
from synth.engine import render_note, render_chord, to_int16


###############################################################################
# UTILITAIRES
###############################################################################

def bpm_to_seconds(bpm, subdivision):
    """
    subdivision:
        4 = noire
        8 = croche
        16 = double croche
        32 = triple croche
    """
    beat_duration = 60.0 / bpm          # 1 temps
    return beat_duration * (4.0 / subdivision)


###############################################################################
# SÉQUENCEUR UNE PISTE (MONO VOICE OU POLY VOICE)
###############################################################################

def seq_one_track(
    track_pattern,
    notes,
    bpm,
    params,
    subdivision=16,
    sample_rate=44100,
    gate=0.9,        # proportion de la durée du pas
    swing=0.0        # feeling groove (-0.5 → +0.5)
):
    """
    track_pattern : liste de booléens ou de listes de notes
        - ex1: [1,0,1,0,...]
        - ex2: [['C4'], [], ['E4','G4'], ...]
    notes : dict note->freq
    subdivision : 4, 8, 16, 32 etc.
    swing : ajoute un décalage rythmique sur les pas pairs
    """

    step_dur = bpm_to_seconds(bpm, subdivision)
    audio = []

    for i, step in enumerate(track_pattern):

        # Swing : décalage des pas pairs (feeling humain)
        local_step_dur = step_dur
        if (i % 2 == 1) and swing != 0:
            local_step_dur *= (1 + swing)

        # pas vide
        if step in [0, False, None, [], ()]:
            audio.append(np.zeros(int(local_step_dur * sample_rate)))
            continue

        # Si le pas contient une seule note
        if isinstance(step, str):
            freq = notes[step]
            note_audio = render_note(freq, local_step_dur * gate, params, sample_rate)

        # Si le pas contient un accord
        elif isinstance(step, (list, tuple)):
            freqs = [notes[n] for n in step]
            note_audio = render_chord(freqs, local_step_dur * gate, params, sample_rate)

        else:  # fallback
            audio.append(np.zeros(int(local_step_dur * sample_rate)))
            continue

        # Compléter le pas avec du silence si gate < 1
        sustain_len = int((local_step_dur * (1 - gate)) * sample_rate)
        if sustain_len > 0:
            silence = np.zeros(sustain_len)
            note_audio = np.concatenate([note_audio, silence])

        audio.append(note_audio)

    return np.concatenate(audio)


###############################################################################
# SÉQUENCEUR MULTI-PISTES (STYLE DRUM RACK / ABLETON)
###############################################################################

def seq_multi_track(
    patterns,
    notes,
    bpm,
    params_per_track,
    subdivision=16,
    sample_rate=44100,
    gate=0.9,
    swing=0.0
):
    """
    patterns : dict { "kick": [...], "snare":[...], ... }
    params_per_track : dict paramètres du synthé par piste
    """

    final_tracks = []

    for track_name, pattern in patterns.items():
        params = params_per_track.get(track_name, params_per_track.get("default"))

        rendered = seq_one_track(
            pattern,
            notes,
            bpm,
            params,
            subdivision=subdivision,
            sample_rate=sample_rate,
            gate=gate,
            swing=swing
        )

        final_tracks.append(rendered)

    # Mixage multi-pistes
    mix = np.sum(final_tracks, axis=0)

    # Normalisation
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak

    return mix.astype(np.float32)


###############################################################################
# EXPORT INT16
###############################################################################

def seq_to_int16(wave):
    return to_int16(wave)
