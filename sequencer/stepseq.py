import numpy as np
from synth.engine import render_note, render_chord, to_int16


###############################################################################
# Utility
###############################################################################
def bpm_to_seconds(bpm, subdivision):
    beat = 60.0 / bpm
    return beat * (4.0 / subdivision)


###############################################################################
# One Track
###############################################################################
def seq_one_track(
    pattern,
    freq_map,
    bpm,
    synth_params,
    subdivision=16,
    sample_rate=44100,
    gate=0.9,
    swing=0.0
):
    """
    pattern : [0, "C4", ["C4","E4"], ...]
    freq_map : dict note → frequency
    """

    step_duration = bpm_to_seconds(bpm, subdivision)
    audio = []

    for i, step in enumerate(pattern):

        local_duration = step_duration

        # swing sur les pas pairs
        if (i % 2 == 1) and swing != 0.0:
            local_duration *= (1.0 + swing)

        if step == 0 or step is None:
            audio.append(np.zeros(int(local_duration * sample_rate)))
            continue

        # MONO note
        if isinstance(step, str):
            freq = freq_map.get(step, None)
            if freq is None:
                continue
            wave = render_note(freq, local_duration * gate, synth_params, sample_rate)

        # ACCORD
        elif isinstance(step, (list, tuple)):
            freqs = [freq_map[n] for n in step if n in freq_map]
            wave = render_chord(freqs, local_duration * gate, synth_params, sample_rate)

        else:
            audio.append(np.zeros(int(local_duration * sample_rate)))
            continue

        # silence si gate < 1.0
        silence_len = int(local_duration * (1 - gate) * sample_rate)
        if silence_len > 0:
            wave = np.concatenate([wave, np.zeros(silence_len)])

        audio.append(wave)

    out = np.concatenate(audio)
    out = out / (np.max(np.abs(out)) + 1e-9)
    return out.astype(np.float32)


###############################################################################
# Multi Track
###############################################################################
def seq_multi_track(
    patterns,
    freq_map,
    bpm,
    params_per_track,
    subdivision=16,
    sample_rate=44100,
    gate=0.9,
    swing=0.0
):

    tracks = []

    for tname, pattern in patterns.items():
        synth_params = params_per_track.get(tname, params_per_track.get("default"))

        wave = seq_one_track(
            pattern,
            freq_map,
            bpm,
            synth_params,
            subdivision,
            sample_rate,
            gate,
            swing
        )

        tracks.append(wave)

    mix = np.sum(tracks, axis=0)
    mix = mix / (np.max(np.abs(mix)) + 1e-9)

    return mix.astype(np.float32)


###############################################################################
# Output conversion
###############################################################################
def seq_to_int16(wave):
    return to_int16(wave)
