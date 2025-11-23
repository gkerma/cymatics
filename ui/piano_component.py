# Piano component placeholder
import streamlit.components.v1 as components

def piano():
    html = """
    <style>
    .key { width: 45px; height: 180px; display:inline-block; margin:1px; border-radius:3px; }
    .white { background:white; border:1px solid #444; }
    .black { background:black; height:120px; margin-left:-20px; z-index:2; position:relative; }
    .white:hover { background:#ddd; }
    .black:hover { background:#222; }
    </style>

    <div id="piano">
        <div class="key white" data-note="C4"></div>
        <div class="key black" data-note="C#4"></div>
        <div class="key white" data-note="D4"></div>
        <div class="key black" data-note="D#4"></div>
        <div class="key white" data-note="E4"></div>
        <div class="key white" data-note="F4"></div>
        <div class="key black" data-note="F#4"></div>
        <div class="key white" data-note="G4"></div>
        <div class="key black" data-note="G#4"></div>
        <div class="key white" data-note="A4"></div>
        <div class="key black" data-note="A#4"></div>
        <div class="key white" data-note="B4"></div>
        <div class="key white" data-note="C5"></div>
    </div>

    <script>
    document.querySelectorAll('.key').forEach(key => {
        key.onclick = () => {
            const note = key.dataset.note;
            window.parent.postMessage({"type":"streamlit:setComponentValue","value":note},"*");
        }
    });
    </script>
    """
    return components.html(html, height=220)
