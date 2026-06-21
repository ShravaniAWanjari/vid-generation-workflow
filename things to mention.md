# Deployment & Evaluation Notes: Hugging Face Spaces

To make it incredibly easy for a new user with zero coding knowledge to test and evaluate the video generation system, we can deploy the setup to Hugging Face Spaces.

## Why Hugging Face Spaces?
Hugging Face Spaces provides a managed environment to host Python apps (Streamlit, Gradio, etc.) directly on the web. Anyone with a browser can open the link and start generating videos instantly without installing Docker, Python, CUDA drivers, or downloading any models.

## Deployment Options

### 1. Hosted Local GPU (Dedicated Space)
* **How it works:** Create a Hugging Face Space running Streamlit. Configure the space to use a GPU hardware tier (e.g., Nvidia T4 Small or A10G).
* **Setup:** Hugging Face automatically provisions the GPU and has extremely fast download speeds to load `Wan-AI/Wan2.2-TI2V-5B` (usually takes less than 2 minutes to download within Hugging Face's network).
* **Cost:** Requires a billing method on Hugging Face. Prices start at ~$0.60/hour for a T4 GPU and can be paused when not in use.

### 2. Streamlit + Cloud API (Serverless / Replicate)
* **How it works:** Create a free CPU-only Hugging Face Space hosting the Streamlit UI. Instead of running the model locally on the Space, the Streamlit app makes external API requests to a cloud provider like Replicate or Kling AI.
* **Setup:** Add the `REPLICATE_API_TOKEN` or `KLING_API_KEY` as a secret/environment variable in the Space's settings.
* **Cost:** The Hugging Face Space is 100% free. The only cost is a few cents per video generated, charged to the cloud API provider.

---

*This file can be shown to reviewers/recruiters to demonstrate your understanding of scaling, deployment, and making applications accessible to non-technical users.*
