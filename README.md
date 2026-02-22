# Waterjet
Waterjet is an intelligent web application that convts natural language descriptions into production-ready .dxf files. Designed specifically for waterjet and CNC operators, it handles the complex geometry and manufacturing physics that standard AI models usually miss.

KEY FUNCTONS
AI Design Engine: Uses Llama 3.3 via Groq to translate prompts (e.g. "A 4 inch great with a 1 inch keyed shaft") into precise coordinates
Stencil Text: Automatically generates text using stencil logic, ensuring that "island" centers (like in the letters O,A,B) stay attached to the material.
Auto-Bridging Logic: Automatically insterts 0.125 tabs (bridges) on long cuts to prevent part vibration or pieces falling into the tank.
Dynamic Lead-Ins: Generates sacrificial "start paths" (Green Layer) that scale automatically based on your material thickness to pretect the part edge from pierce-point blemishes.
Grid Nesting: Efficiently clones parts across a specified sheet size to minimize scrap material.
Production Layers: Exports DXF files with industry-standard layering:
  Layer 0/white: Outer perimeters
  Layer1/Red: Internal Holes and text
  Layer3/Green: Lead-In Paths

  Prerequisites
    To run this app locally or deploy it to the cloud, you need the following:
    1. GROQ API Key: you must have a free API key from the Groq Console. Thos powers he "intelligence" behind the CAD Generation.
    2. Software & Libraries:This app is built using Python 3.9+. You will need to install these dependencies- streamlit, ezdxf, matplotib

    How to Use
      1. Launch the App: Run streamlit run app.py in your terminal
      2. Configure: Enter your Groq API Key in the Sidebar
      3. Prompt: Describe your part in the text area (e.g. "A 10 inch circular flange with 8 bolt holes")
      4. Adjust physics: use te slder to set your material thickness. This determines the length of your lead ins
      5. Review: Check the visual preview to ensure the "red" internal cuts and "blue" outer cuts are correct
      6. Download" Click Dowload DXF and load the file directly into your CAM software.

      Deployment
      This app is ready to be deployed for free on Streamlit Community Cloud. simply Connect your GitHub repository, add your requirements.txt, and your shop will have a ewb-based CAD generator accessible from many device.
