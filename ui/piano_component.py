import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
#  Piano clicakble JS + Streamlit  — Version Pro
# ---------------------------------------------------------------------------

def piano_component(height=260, width="100%"):
    """
    Retourne la note cliquée (ex: "C4") ou None.
    """

    component_id = "piano_click_component"

    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">

    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
        }}

        #piano {{
            position: relative;
            width: 820px;
            height: 220px;
            margin: 0;
            display: flex;
            align-items: flex-end;
        }}

        .white {{
            width: 60px;
            height: 220px;
            background: #fafafa;
            border: 1px solid #444;
            box-sizing: border-box;
            border-radius: 4px 4px 10px 10px;
            display: inline-block;
            position: relative;
            margin: 0;
            cursor: pointer;
            transition: background 0.05s;
        }}

        .white:hover {{
            background: #e6e6e6;
        }}

        .black {{
            width: 40px;
            height: 140px;
            background: #111;
            border: 1px solid #333;
            border-radius: 0px 0px 6px 6px;
            position: absolute;
            left: 45px;
            top: 0px;
            z-index: 10;
            cursor: pointer;
            transition: background 0.05s;
        }}

        .black:hover {{
            background: #222;
        }}

        .pressed {{
            background: #89b4fa !important;
        }}

    </style>

    </head>

    <body>

    <div id="piano">

        <!-- Notes de C4 à C5 -->
        <div class="white" data-note="C4"></div>
        <div class="black" data-note="C#4" style="left: 40px;"></div>

        <div class="white" data-note="D4"></div>
        <div class="black" data-note="D#4" style="left: 100px;"></div>

        <div class="white" data-note="E4"></div>

        <div class="white" data-note="F4"></div>
        <div class="black" data-note="F#4" style="left: 220px;"></div>

        <div class="white" data-note="G4"></div>
        <div class="black" data-note="G#4" style="left: 280px;"></div>

        <div class="white" data-note="A4"></div>
        <div class="black" data-note="A#4" style="left: 340px;"></div>

        <div class="white" data-note="B4"></div>

        <div class="white" data-note="C5"></div>

    </div>

    <script>
        const keys = document.querySelectorAll(".white, .black");

        // Animation visuelle lors du clic
        function press(el) {{
            el.classList.add("pressed");
            setTimeout(() => el.classList.remove("pressed"), 120);
        }}

        keys.forEach(key => {{
            key.addEventListener("click", () => {{
                const note = key.getAttribute("data-note");

                press(key);

                window.parent.postMessage({{
                    "isStreamlitMessage": true,
                    "type": "streamlit:setComponentValue",
                    "value": note
                }}, "*");
            }});
        }});
    </script>

    </body>
    </html>
    """

    # Injection du composant
    note = components.html(
        html,
        height=height,
        width=width,
        scrolling=False,
    )

    return note
