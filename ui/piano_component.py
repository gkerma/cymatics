import streamlit as st
import streamlit.components.v1 as components

def piano_component():
    """
    Piano interactif – version PATCHÉE
    Retourne toujours une String ("C4") ou None.
    """

    html = """
    <style>
        .piano-container {
            width: 800px;
            height: 220px;
            position: relative;
            user-select: none;
        }
        .white {
            width: 60px;
            height: 220px;
            background: #fafafa;
            border: 1px solid #555;
            display: inline-block;
            position: relative;
            cursor: pointer;
            border-radius: 4px 4px 10px 10px;
        }
        .white:active {
            background: #90caf9;
        }
        .black {
            width: 40px;
            height: 140px;
            background: #111;
            border: 1px solid #444;
            position: absolute;
            top: 0;
            z-index: 10;
            border-radius: 4px 4px 6px 6px;
            cursor: pointer;
        }
        .black:active {
            background: #42a5f5;
        }
    </style>

    <div class="piano-container">

        <!-- White Keys -->
        <div class="white" data-note="C4"  style="left:0px;"></div>
        <div class="white" data-note="D4"  style="left:60px;"></div>
        <div class="white" data-note="E4"  style="left:120px;"></div>
        <div class="white" data-note="F4"  style="left:180px;"></div>
        <div class="white" data-note="G4"  style="left:240px;"></div>
        <div class="white" data-note="A4"  style="left:300px;"></div>
        <div class="white" data-note="B4"  style="left:360px;"></div>
        <div class="white" data-note="C5"  style="left:420px;"></div>

        <!-- Black Keys -->
        <div class="black" data-note="C#4" style="left:40px;"></div>
        <div class="black" data-note="D#4" style="left:100px;"></div>
        <div class="black" data-note="F#4" style="left:220px;"></div>
        <div class="black" data-note="G#4" style="left:280px;"></div>
        <div class="black" data-note="A#4" style="left:340px;"></div>

    </div>

    <script>
        const keys = document.querySelectorAll('.white, .black');

        keys.forEach(key => {
            key.addEventListener('click', () => {
                const note = key.getAttribute('data-note');

                window.parent.postMessage({
                    isStreamlitMessage: true,
                    type: "streamlit:setComponentValue",
                    value: note
                }, "*");
            });
        });
    </script>
    """

    # Renvoie la valeur, Streamlit gère les messages JS → Python
    selected = components.html(html, height=260)

    # Normalisation : TOUJOURS renvoyer une string ou None
    if isinstance(selected, dict):
        selected = selected.get("value")

    if isinstance(selected, str):
        if len(selected) >= 2:
            return selected  # "C4", "D#3", etc.

    return None
