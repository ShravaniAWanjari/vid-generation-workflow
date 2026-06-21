# Naturo Animation Generator — Streamlit App Agent Instructions

## What to build

A single-page Streamlit app hosted on Streamlit Cloud.
The app takes a product image + text prompt from the user,
sends both to an external inference endpoint (Kaggle notebook exposed via ngrok),
and returns a downloadable .mp4 video.

---

## File structure

```
naturo-app/
├── app.py
├── requirements.txt
└── .streamlit/
    └── secrets.toml   ← already exists, do not create or overwrite
```

---

## secrets.toml (already set, just read these)

```python
INFERENCE_URL = st.secrets["INFERENCE_URL"]  # e.g. https://abc123.ngrok-free.app
```

This URL changes every time the Kaggle notebook restarts.
The user will paste the new ngrok URL in the sidebar to override it.

---

## app.py

### Imports and config

```python
import io, os, requests, time
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Naturo – Animation Generator",
    page_icon="🌿",
    layout="centered",
)
```

### Inference URL resolution

Read from sidebar input first, fall back to secrets:

```python
with st.sidebar:
    st.header("⚙️ Settings")

    custom_url = st.text_input(
        "Inference URL",
        placeholder="https://abc123.ngrok-free.app",
        help="Paste the ngrok URL printed by the Kaggle notebook"
    )

    inference_url = custom_url.strip().rstrip("/") if custom_url.strip() \
        else st.secrets.get("INFERENCE_URL", "").rstrip("/")

    if inference_url:
        st.caption(f"Using: `{inference_url}`")
    else:
        st.warning("No inference URL set. Paste the ngrok URL above.")

    st.divider()
    st.header("🎬 Video Settings")
    num_frames   = st.slider("Frames", min_value=16, max_value=81, value=49, step=8,
                              help="49 frames ≈ 3s at 16fps")
    size_choice  = st.selectbox("Resolution", ["832x480", "480x832", "624x624"], index=0)
    steps        = st.slider("Inference steps", min_value=15, max_value=40, value=25)
    guidance     = st.slider("Guidance scale", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
    neg_prompt   = st.text_area("Negative prompt (optional)",
                                 placeholder="blurry, distorted, watermark, text overlay",
                                 height=80)
```

### Main layout

Two columns: left = image upload, right = prompt.

```python
st.title("🌿 Naturo Animation Generator")
st.caption("Upload a product image and describe the animation. The model will generate a blooming ingredient video.")
st.divider()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Product image")
    uploaded = st.file_uploader(
        "Upload product photo",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed"
    )
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, use_container_width=True)
        st.caption(f"{img.width} × {img.height}px")

with col2:
    st.subheader("Prompt")
    prompt = st.text_area(
        "Describe the animation",
        height=220,
        placeholder="Rose flowers and tamarind pods slowly bloom and grow from behind the product. "
                    "Camera gently zooms out. Soft bokeh background, warm studio lighting. "
                    "Cinematic macro shot, premium cosmetics advertisement style.",
        label_visibility="collapsed"
    )
    st.caption(f"{len(prompt)} characters")
```

### Generate button and flow

```python
st.divider()

can_generate = bool(uploaded and prompt.strip() and inference_url)
missing = []
if not inference_url: missing.append("inference URL (sidebar)")
if not uploaded:      missing.append("product image")
if not prompt.strip(): missing.append("prompt")
if missing:
    st.info(f"Still needed: {', '.join(missing)}")

generate = st.button(
    "✨ Generate video",
    disabled=not can_generate,
    use_container_width=True,
    type="primary"
)

if generate and can_generate:
    w, h = map(int, size_choice.split("x"))

    # Prepare image bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    status  = st.status("Starting generation…", state="running")
    prog    = st.progress(0)
    start   = time.time()

    try:
        status.update(label="Sending to inference server…")
        prog.progress(10)

        response = requests.post(
            f"{inference_url}/generate",
            files={"image": ("product.png", buf, "image/png")},
            data={
                "prompt":               prompt.strip(),
                "negative_prompt":      neg_prompt.strip(),
                "num_frames":           num_frames,
                "width":                w,
                "height":               h,
                "num_inference_steps":  steps,
                "guidance_scale":       guidance,
            },
            timeout=600,   # generation takes 3-8 min on P100
            stream=True,
        )

        prog.progress(90)

        if response.status_code == 200:
            video_bytes = response.content
            elapsed     = int(time.time() - start)
            prog.progress(100)
            status.update(label=f"Done in {elapsed}s!", state="complete")

            st.success("Your animation is ready.")
            st.video(video_bytes)
            st.download_button(
                label="⬇️ Download .mp4",
                data=video_bytes,
                file_name="naturo_animation.mp4",
                mime="video/mp4",
                use_container_width=True,
            )

            # Session history
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "prompt":  prompt[:80] + ("…" if len(prompt) > 80 else ""),
                "elapsed": elapsed,
            })

        else:
            prog.empty()
            error = response.json().get("error", response.text)
            status.update(label="Generation failed", state="error")
            st.error(f"Error from inference server: {error}")

    except requests.exceptions.Timeout:
        prog.empty()
        status.update(label="Timed out", state="error")
        st.error("Request timed out after 10 minutes. The Kaggle notebook may have disconnected.")
    except requests.exceptions.ConnectionError:
        prog.empty()
        status.update(label="Connection failed", state="error")
        st.error("Could not reach the inference server. Check the ngrok URL is current and the Kaggle notebook is running.")
    except Exception as e:
        prog.empty()
        status.update(label="Error", state="error")
        st.error(f"Unexpected error: {e}")
```

### Session history (bottom of page)

```python
if st.session_state.get("history"):
    st.divider()
    with st.expander(f"Session history — {len(st.session_state.history)} video(s)"):
        for i, item in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"**{i}.** {item['prompt']} — `{item['elapsed']}s`")
```

---

## requirements.txt

```
streamlit>=1.35.0
Pillow>=10.0.0
requests>=2.31.0
```

---

## Deployment

1. Push to GitHub
2. Go to share.streamlit.io → New app → select repo → main file: `app.py`
3. App settings → Secrets → paste:
   ```toml
   INFERENCE_URL = ""
   ```
   (leave blank — users paste the live ngrok URL in the sidebar)
4. Deploy and share the URL

---

## What NOT to do

- Do not auto-generate prompts — user writes the full prompt
- Do not hardcode any ngrok URL
- Do not add any video generation logic — the app only calls the external endpoint
- Do not use deprecated Streamlit APIs (`st.experimental_rerun`, `use_column_width`, etc.)
- Do not add login or auth UI
