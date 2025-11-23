# Step sequencer placeholder
import numpy as np

def step_sequence(pattern, freq, synth_fn, sr, step_len=0.25):
    audio = []
    for step in pattern:
        if step:
            audio.append(synth_fn(freq, sr, step_len))
        else:
            audio.append(np.zeros(int(sr*step_len)))
    return np.concatenate(audio)
