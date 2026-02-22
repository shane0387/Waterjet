import streamlit as st
import ezdxf
import json
import os
import math
from groq import Groq
import matplotlib.pyplot as plt

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Waterjet Pro CAD", layout="wide")
st.title(" Waterjet Pro: AI-CAD Generator")

# Sidebar for Settings
st.sidebar.header("Settings")
GROQ_API_KEY = st.sidebar.text_input("Groq API Key", type="password")
model_choice = st.sidebar.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile"])

# --- 2. CORE LOGIC ---
SYSTEM_PROMPT = """
You are a CAD Engineer for Waterjet Cutting. Return ONLY a JSON list of commands.
Available commands: circle, rect, line, hole, polygon.
- TEXT: Use stencil style (no loose islands).
- BRIDGING: Leave 0.125" gaps for long cuts.
- Units: Inches. Start at [0,0].
"""

def get_cad_instructions(prompt, api_key):
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model_choice,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    data = json.loads(completion.choices[0].message.content)
    if isinstance(data, dict):
        for key in data:
            if isinstance(data[key], list): return data[key]
    return data if isinstance(data, list) else []

def build_dxf_in_memory(commands, thickness):
    doc = ezdxf.new('R2010')
    doc.layers.add(name="OUTER_CUT", color=7)
    doc.layers.add(name="HOLES", color=1)
    doc.layers.add(name="LEADS", color=3)
    msp = doc.modelspace()
    
    lead_len = max(0.15, (thickness * 0.5) + 0.1)

    for cmd in commands:
        t = cmd.get("type")
        layer = 'HOLES' if t == "hole" else 'OUTER_CUT'
        try:
            if t in ["circle", "hole"]:
                r, c = cmd["radius"], cmd["center"]
                msp.add_circle(c, r, dxfattribs={'layer': layer})
                dir = -1 if t == "hole" else 1
                msp.add_line((c[0]+r+(lead_len*dir), c[1]), (c[0]+r, c[1]), dxfattribs={'layer': 'LEADS'})
            elif t == "rect":
                x, y, w, h = cmd["start"][0], cmd["start"][1], cmd["width"], cmd["height"]
                p = [(x,y), (x+w,y), (x+w,y+h), (x,y+h)]
                for i in range(4): msp.add_line(p[i], p[(i+1)%4], dxfattribs={'layer': layer})
                msp.add_line((x-lead_len, y-lead_len), p[0], dxfattribs={'layer': 'LEADS'})
            elif t == "line":
                msp.add_line(cmd["points"][0], cmd["points"][1], dxfattribs={'layer': layer})
            elif t == "polygon":
                pts = cmd["points"]
                for i in range(len(pts)-1): msp.add_line(pts[i], pts[i+1], dxfattribs={'layer': layer})
                if pts[0] != pts[-1]: msp.add_line(pts[-1], pts[0], dxfattribs={'layer': layer})
        except: continue
    
    doc.saveas("temp.dxf")
    return "temp.dxf"

# --- 3. UI LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Design Parameters")
    user_prompt = st.text_area("Describe your part (e.g., 'A 5-inch star with the word BOSS in the middle')", height=150)
    thickness = st.slider("Material Thickness (Inches)", 0.05, 2.0, 0.25)
    
    if st.button("Generate CAD"):
        if not GROQ_API_KEY:
            st.error("Please enter your Groq API Key in the sidebar!")
        else:
            with st.spinner("AI is drafting your part..."):
                st.session_state.instructions = get_cad_instructions(user_prompt, GROQ_API_KEY)
                st.success("CAD Geometry Generated!")

with col2:
    st.subheader("Preview")
    if 'instructions' in st.session_state:
        fig, ax = plt.subplots()
        for cmd in st.session_state.instructions:
            t = cmd.get("type")
            c = 'red' if t == 'hole' else 'blue'
            if t in ["circle", "hole"]:
                ax.add_patch(plt.Circle(cmd["center"], cmd["radius"], color=c, fill=False))
            elif t == "rect":
                ax.add_patch(plt.Rectangle(cmd["start"], cmd["width"], cmd["height"], edgecolor=c, fill=False))
            elif t in ["polygon", "line"]:
                pts = list(cmd["points"]); xs, ys = zip(*pts)
                plt.plot(xs, ys, color=c)
        plt.axis('equal')
        st.pyplot(fig)
        
        # Download Button
        dxf_file = build_dxf_in_memory(st.session_state.instructions, thickness)
        with open(dxf_file, "rb") as file:
            st.download_button(label=" Download DXF for Waterjet", data=file, file_name="part_output.dxf", mime="application/dxf")
