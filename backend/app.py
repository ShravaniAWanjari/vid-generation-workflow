"""
app.py - Naturo AI Engine · Streamlit UI
Horizontal Stepper Track Architecture
"""

import streamlit as st
import os
import time

# Ensure dependencies are available before importing core modules
try:
    from prompt_compiler import compile_spatial_prompt
    from pipeline_engine import execute_video_pipeline
except ImportError as e:
    st.error(f"Failed to import core modules: {e}. Please check requirements.")

# ──────────────────────────────────────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Naturo AI Engine",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS Overrides for Dark Mode & Horizontal Layout
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* 1. Global Dark Mode & Prevent Vertical Scrolling */
html, body, [class*="css"], .stApp {
    background-color: #0a0a0a !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif;
    overflow-y: hidden !important; 
    overflow-x: hidden !important;
}

/* 2. Top Bar Wrapper - Fixed at top */
.top-bar-wrapper {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 5rem;
    background-color: #0a0a0a;
    border-bottom: 1px solid #2a2a2a;
    z-index: 9999;
    display: flex;
    align-items: center;
    padding: 0 3rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.top-bar-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    flex-grow: 1;
}

.demo-toggle-container {
    display: flex;
    align-items: center;
    justify-content: flex-end;
}

/* 3. Main Horizontal Track */
.block-container {
    max-width: 100% !important;
    padding-top: 6.5rem !important; /* Below the fixed top bar */
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 0 !important;
}

div[data-testid="stHorizontalBlock"] {
    display: flex;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    height: calc(100vh - 7rem);
    padding-bottom: 1rem;
    gap: 1.5rem;
}

/* 4. Individual Cards (Columns) */
div[data-testid="column"] {
    flex: 0 0 420px !important; 
    min-width: 420px !important;
    background-color: #111111;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    overflow-y: auto;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05);
}

/* Custom Scrollbar for horizontal container & cards */
::-webkit-scrollbar {
    width: 8px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: #0a0a0a;
}
::-webkit-scrollbar-thumb {
    background-color: #333;
    border-radius: 10px;
}

/* 5. Typography & Widget Styling */
h4 {
    color: #e5e5e5;
    font-weight: 600;
    margin-bottom: 0.2rem;
}

hr {
    border-color: #2a2a2a;
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
}

/* Inputs & File Uploaders */
div[data-baseweb="input"] > div, 
div[data-baseweb="file-uploader"] {
    background-color: #1a1a1a !important;
    border: 1px solid #444 !important;
}

/* 6. Card 2 - Prompt Workspace Box */
.stTextArea textarea {
    background-color: #050505 !important;
    border: 2px solid #555 !important;
    font-family: monospace;
    font-size: 13px;
    color: #a3e635 !important; /* Distinct terminal-like color for emphasis */
}

/* 7. Card 4 - Status Pills */
.status-pill {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 9999px;
    background-color: #1a1a1a;
    border: 1px solid #333;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.8rem;
    width: 100%;
    text-align: center;
}
.status-pill.success { border-color: #10b981; color: #10b981; }
.status-pill.running { border-color: #3b82f6; color: #3b82f6; }
.status-pill.error   { border-color: #ef4444; color: #ef4444; }

/* Hide Streamlit header/footer */
header[data-testid="stHeader"], footer {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Fixed Top Bar
# ──────────────────────────────────────────────────────────────────────────────
# We use a trick to render the toggle inside the normal flow but use CSS to 
# pull a container to the top. However, Streamlit toggles are hard to pull out 
# individually via CSS if we mix them with raw HTML. 
# So we just render a regular column block for the top bar and apply CSS above.
st.markdown('<div class="top-bar-wrapper">', unsafe_allow_html=True)
top_col1, top_col2 = st.columns([1, 1])
with top_col1:
    st.markdown('<p class="top-bar-title">Naturo AI Engine 🎬</p>', unsafe_allow_html=True)
with top_col2:
    st.markdown('<div class="demo-toggle-container">', unsafe_allow_html=True)
    demo_mode = st.toggle("Enable Cost-Free Demo Mode (Bypass Replicate Paywalls)", value=True, key="demo_mode")
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# Initialize Session State
if "compiled_prompt" not in st.session_state:
    st.session_state["compiled_prompt"] = ""


# ──────────────────────────────────────────────────────────────────────────────
# Horizontal Stepper Track (4 Cards)
# ──────────────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

# ══════════════════════════════════════════════════════════════════════════════
# CARD 1: INGRESS INPUT
# ══════════════════════════════════════════════════════════════════════════════
with c1:
    st.markdown("#### Card 1: Ingress Input")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    product_image = st.file_uploader("Product Image (PNG)", type=["png"])
    style_video = st.file_uploader("Style Reference (MP4)", type=["mp4", "mov"])
    raw_intent = st.text_input("Ingredients / Raw Intent", placeholder="e.g. Tamarind pods & Rose flowers")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Extract & Compile Prompt", use_container_width=True):
        if product_image and style_video and raw_intent:
            with st.spinner("Extracting & Compiling..."):
                try:
                    # Save to temp files
                    img_path = "temp_product.png"
                    vid_path = "temp_style.mp4"
                    with open(img_path, "wb") as f: f.write(product_image.getbuffer())
                    with open(vid_path, "wb") as f: f.write(style_video.getbuffer())
                    
                    from extractor import extract_keyframes
                    kf_paths = extract_keyframes(vid_path, "temp_keyframes")
                    
                    prompt = compile_spatial_prompt(img_path, kf_paths, raw_intent)
                    st.session_state["compiled_prompt"] = prompt
                    st.success("Prompt compiled!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please provide both assets and the text intent.")

# ══════════════════════════════════════════════════════════════════════════════
# CARD 2: PROMPT WORKSPACE
# ══════════════════════════════════════════════════════════════════════════════
with c2:
    st.markdown("#### Card 2: Prompt Workspace")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    edited_prompt = st.text_area(
        "Compiled VLM Prompt (Editable)", 
        value=st.session_state["compiled_prompt"], 
        height=450,
        help="This box will hold the spatially-structured prompt generated by GPT-4o-mini."
    )
    
    # Sync edited prompt back to session state if user types
    if edited_prompt != st.session_state["compiled_prompt"]:
        st.session_state["compiled_prompt"] = edited_prompt

# ══════════════════════════════════════════════════════════════════════════════
# CARD 3: VIDEO GENERATION MODEL
# ══════════════════════════════════════════════════════════════════════════════
with c3:
    st.markdown("#### Card 3: Model Selector")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    tier = st.radio("Select Generation Tier", [
        "Tier 1: Decent Videos ($0.03)",
        "Tier 2: Special Product Movements & Hyper-Realism ($0.12)",
        "Tier 3: Precision Cinematic Shots ($0.25)"
    ], index=1)
    
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    execute_btn = st.button("🚀 Execute Pipeline", type="primary", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# CARD 4: OUTPUT & DELIVERY ARCHIVE
# ══════════════════════════════════════════════════════════════════════════════
with c4:
    st.markdown("#### Card 4: Archive & Output")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if execute_btn:
        if not edited_prompt.strip():
            st.error("No prompt available. Please compile or type a prompt first.")
        else:
            payload = {
                "demo_mode": demo_mode,
                "compiled_prompt": edited_prompt,
                "selected_tier": tier
            }
            
            status_placeholder = st.empty()
            status_placeholder.markdown('<div class="status-pill running">⏳ Engine Processing Pipeline...</div>', unsafe_allow_html=True)
            
            # Use placeholder to simulate loading UI
            player_placeholder = st.empty()
            
            try:
                # Consume the generator to simulate step-by-step UI updates
                for update in execute_video_pipeline(payload):
                    if not update.get("done"):
                        status_placeholder.markdown(f'<div class="status-pill running">⏳ {update["status"]}</div>', unsafe_allow_html=True)
                    else:
                        status = update["status"]
                        active_tier = update["tier"]
                        metadata_array = update["metadata"]
                        status_placeholder.markdown(f'<div class="status-pill success">✅ Executed: {status}</div>', unsafe_allow_html=True)
                
                if demo_mode:
                    # Video Player
                    video_path = "static/demo_output.mp4"
                    if not os.path.exists(video_path):
                        video_path = "demo.mp4"
                    if os.path.exists(video_path):
                        player_placeholder.video(video_path)
                    else:
                        player_placeholder.error("Demo video file missing.")
                
                st.markdown("**Storage Links:**")
                for meta in metadata_array:
                    link = meta.get("webViewLink")
                    if link:
                        st.link_button("🔗 Open Asset inside Google Drive Archive", link, use_container_width=True)
                
                st.markdown(f"<small>Model: {active_tier}</small>", unsafe_allow_html=True)
                
            except Exception as e:
                status_placeholder.markdown('<div class="status-pill error">❌ Execution Failed</div>', unsafe_allow_html=True)
                st.error(str(e))
    else:
        st.info("Awaiting execution...")
        st.markdown('<div style="height:250px; border: 1px dashed #333; display:flex; align-items:center; justify-content:center; color:#555;">Video Player Placeholder</div>', unsafe_allow_html=True)
