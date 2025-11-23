import streamlit as st
import streamlit.components.v1 as components


def piano_component(height=260, width="100%"):
    """
    Piano interactif : renvoie une note cliquée au format "C4" ou "F#3".
    Compatible Streamlit Components (JS → Python).
    """

    html = """
    <style>
    .piano-container {
        width: 820px;
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
        border-radius: 4px 4px 10px 10px;
        cursor: pointer;
        position: relative;
    }
    .white:hover { background: #e3e3e3; }
    .white.pressed { background: #89b4fa !important; }

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
    .black:hover { background: #222; }
    .black.pressed { background: #89b4fa !important; }
    </style>

    <div class="piano-container">
        <!-- White keys -->
        <div class="white" data-note="C4"  style="left:0px;"></div>
        <div class="white" data-note="D4"  style="left:60px;"></div>
        <div class="white" data-note="E4"  style="left:120px;"></div>
        <div class="white" data-note="F4"  style="left:180px;"></div>
        <div class="white" data-note="G4"  style="left:240px;"></div>
        <div class="white" data-note="A4"  style="left:300px;"></div>
        <div class="white" data-note="B4"  style="left:360px;"></div>
        <div class="white" data-note="C5"  style="left:420px;"></div>

        <!-- Black keys -->
        <div class="black" data-note="C#4" style="left:40px;"></div>
        <div class="black" data-note="D#4" style="left:100px;"></div>
        <div class="black" data-note="F#4" style="left:220px;"></div>
        <div class="black" data-note="G#4" style="left:280px;"></div>
        <div class="black" data-note="A#4" style="left:340px;"></div>
    </div>

    <script>
    const keys = document.querySelectorAll(".white, .black");

    function pressKey(el) {
        el.classList.add("pressed");
        setTimeout(() => el.classList.remove("pressed"), 150);
    }

    keys.forEach(k => {
        k.addEventListener("click", () => {
            const note = k.getAttribute("data-note");
            pressKey(k);

            window.parent.postMessage({
                "isStreamlitMessage": true,
                "type": "streamlit:setComponentValue",
                "value": note
            }, "*");
        });
    });
    </script>
    """

    return components.html(html, height=height, width=width, scrolling=False)
