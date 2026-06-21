# Naturo Animation Generator

AI-powered cosmetics animation tool. Upload a product image, write a prompt, get a blooming ingredient video.

---

## Requirements

- **Docker** + **Docker Compose**
- **Nvidia GPU** with 8GB+ VRAM & [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (required for local model execution only)

---

## Quick Start (Two Modes)

### Mode 1: Instant Mock Mode (Recommended for quick testing / No GPU required)
This runs the entire container orchestration (FastAPI + Streamlit) instantly on **any computer** without downloading the 10GB model or needing a GPU. It uses the pre-generated sample `demo.mp4` to simulate generation.

1. Start the services with `MOCK_INFERENCE=true`:
   ```bash
   $env:MOCK_INFERENCE="true"; docker compose up --build
   ```
   *(Or on Linux/macOS)*:
   ```bash
   MOCK_INFERENCE=true docker compose up --build
   ```
2. Open **http://localhost:8501** in your browser.
3. Upload any product image, write a prompt, click **Generate**, and preview/download the video instantly!

---

### Mode 2: Full Local GPU Execution (Wan2.2-TI2V-5B Model)
Runs the model locally on your Nvidia GPU. Downloads ~10GB of weights from Hugging Face on first run.

1. (Optional) Provide your Hugging Face Token for faster rates:
   ```bash
   $env:HF_TOKEN="your_token_here"; docker compose up --build
   ```
2. Start the services:
   ```bash
   docker compose up --build
   ```
3. Open **http://localhost:8501** in your browser.
   * *Note: The system status card in the UI will display **System Initializing** while the model downloads. Once ready, it automatically updates to **System Online & Ready**.*
4. Generate cosmetic animations on your local GPU.

---

## Technical Architecture

* **`inference` container (Port 8000)**: Serves a FastAPI backend. In GPU mode, loads the `WanImageToVideoPipeline` using PyTorch & Hugging Face Diffusers. Slices and tiles video frame computations to run efficiently on an 8GB GPU.
* **`app` container (Port 8501)**: Serves a highly polished Streamlit UI using a custom responsive typography grid, status ping loops, and visual assets.