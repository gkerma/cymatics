# Cymatics DAW main file placeholder
import streamlit as st
from ui.piano_component import piano
from synth.engine import synth
from sequencer.stepseq import step_sequence
import numpy as np
from scipy.io.wavfile import write
import base64
from io import BytesIO

st.sidebar.title("CYMATICS DAW – Style Ableton")

section = st.sidebar.selectbox("Section :", [
    "Synthé",
    "Piano Roll",
    "Séquenceur",
    "Export"
])

# ... (chaque module appelle son interface)
