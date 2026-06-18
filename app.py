import streamlit as st
import time
import io
import os
import requests
from typing import Optional
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Naturo AI Engine",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Custom Minimal Styles (Markdown-based for stability)
# ---------------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; margin-top: 1rem; margin-bottom: 2.5rem;">
        <h1 style="
            background: linear-gradient(135deg, #059669, #10B981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Outfit', 'Inter', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -0.05em;
            margin-bottom: 0.5rem;
        ">
            Naturo AI Animation Engine
        </h1>
        <p style="
            color: #4B5563;
            font-size: 1.15rem;
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            max-width: 600px;
            margin: 0 auto;
        ">
            Generate high-end, ingredient-inspired product animations in seconds using state-of-the-art AI generation.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Caching Background Removal
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def remove_background_cached(image_bytes: bytes) -> bytes:
    """
    Removes the background from the uploaded image and returns the bytes of the PNG.
    
    Args:
        image_bytes (bytes): The raw bytes of the uploaded image.
        
    Returns:
        bytes: The bytes of the transparent foreground PNG.
    """
    from rembg import remove
    print("\n[Naturo Engine] New image uploaded. Caching & extracting foreground via rembg...")
    input_image = Image.open(io.BytesIO(image_bytes))
    output_image = remove(input_image)
    buffer = io.BytesIO()
    output_image.save(buffer, format="PNG")
    return buffer.getvalue()

# ---------------------------------------------------------
# Video API & Prompt Engine
# ---------------------------------------------------------
def generate_background_video(ingredients_text: str, api_key: str, image_path: Optional[str] = None) -> str:
    """
    Generates a background video using Hugging Face Inference Providers.
    Uses the fal-ai provider with Wan2.1-I2V-14B-480P model, billed against
    your free monthly HF credits.
    
    Args:
        ingredients_text (str): Ingredients to build the video prompt from.
        api_key (str): Hugging Face Access Token (starts with hf_).
        image_path (str, optional): Path to the product image for image-to-video.
    
    Returns:
        str: Path to the saved background video file.
    """
    from huggingface_hub import InferenceClient

    # 1. Construct the prompt
    prompt = (
        f"Cinematic macro time-lapse photography of {ingredients_text} blooming and unfurling around the product, "
        f"highly detailed organic textures, soft studio lighting, clean defocus bokeh background, "
        f"shallow depth of field, high-end commercial cosmetics advertisement style, 8k resolution."
    )
    print(f"\n[Naturo Engine] Formatted Video Generation Prompt:\n{prompt}\n")
    st.write(f"📝 **Formatted API Prompt:** `{prompt}`")

    # 2. Submit the generation request via HF Inference Providers
    st.write("📤 Submitting request to HF Inference Provider (fal-ai / Wan2.2-I2V-A14B)...")
    print("[Naturo Engine] Submitting API Request via HF Inference Providers...")

    try:
        client = InferenceClient(
            provider="fal-ai",
            api_key=api_key,
        )
        st.write("⏳ Job queued successfully. Generating video (this may take 1-3 minutes)...")

        if image_path and os.path.exists(image_path):
            st.write("🖼️ Using Image-to-Video generation with the product image...")
            video_bytes = client.image_to_video(
                image=image_path,
                prompt=prompt,
                model="Wan-AI/Wan2.2-I2V-A14B",
            )
        else:
            st.write("📝 Using Text-to-Video generation...")
            video_bytes = client.text_to_video(
                prompt=prompt,
                model="Wan-AI/Wan2.1-T2V-14B",
            )

        output_filename = "bg_video.mp4"
        with open(output_filename, "wb") as f:
            f.write(video_bytes)
        
        print(f"[Naturo Engine] Video saved: {output_filename} ({len(video_bytes)} bytes)")
        return output_filename
    except Exception as e:
        raise Exception(f"HF Inference Provider video generation failed: {e}")

# ---------------------------------------------------------
# Session State & Pipeline Control
# ---------------------------------------------------------
def run_animation_pipeline(image: UploadedFile, ingredients_list: str) -> None:
    """
    Runs the multi-step animation generation pipeline.
    
    Args:
        image (UploadedFile): The uploaded product image file.
        ingredients_list (str): Text representing ingredients.
    """
    # 1. Securely check for the API key in Streamlit secrets
    api_key: Optional[str] = st.secrets.get("HF_TOKEN", st.secrets.get("VIDEO_API_KEY"))
    if not api_key:
        st.error("❌ Configuration Error: `HF_TOKEN` was not found in `.streamlit/secrets.toml`. Please add your Hugging Face Access Token.")
        return

    # Create the st.status container with expanded=True to show detailed progress
    with st.status("Initializing Naturo AI engine...", expanded=True) as status:
        # Step 1: Background Isolation
        st.write("🔍 Extracting product silhouette & background elements...")
        status.update(label="Extracting product...", state="running")
        try:
            from rembg import remove
            from PIL import Image
            import io
            pil_img = Image.open(image)
            extracted_img = remove(pil_img)
            extracted_img.save("temp_product.png", format="PNG")
            st.write("✅ Product background removed successfully. Saved as `temp_product.png`.")
        except Exception as e:
            st.error(f"❌ Foreground extraction failed: {e}")
            status.update(label="Extraction failed", state="error")
            return
        time.sleep(2)
        
        # Step 2: Optimizing Prompt
        st.write("✍️ Crafting optimized generation prompt from active ingredients...")
        status.update(label="Optimizing prompt...", state="running")
        time.sleep(2)
        
        # Step 3: Generating Video
        st.write("🎬 Requesting and polling video generation API...")
        status.update(label="Generating background video...", state="running")
        try:
            bg_video_path = generate_background_video(ingredients_list, api_key=api_key, image_path="temp_product.png")
            st.write(f"✅ Background video successfully generated!")
        except Exception as e:
            st.error(f"❌ Video generation API failed: {e}")
            status.update(label="Video generation failed", state="error")
            return
            
        # Step 4: Compositing Layers
        st.write("✨ Applying realistic lighting, post-processing & composting...")
        status.update(label="Compositing layers...", state="running")
        try:
            import PIL.Image
            if not hasattr(PIL.Image, 'ANTIALIAS'):
                PIL.Image.ANTIALIAS = getattr(PIL.Image, 'LANCZOS', getattr(PIL.Image.Resampling, 'LANCZOS', None))
                
            from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
            bg_clip = VideoFileClip(bg_video_path)
            
            # Load temp_product.png
            product_clip = ImageClip("temp_product.png")
            
            # Set duration
            product_clip = product_clip.set_duration(bg_clip.duration)
            
            # Resize height to 75% of bg_clip.h
            target_height = int(bg_clip.h * 0.75)
            product_clip = product_clip.resize(height=target_height)
            
            # Position at bottom-center
            product_clip = product_clip.set_position(('center', 'bottom'))
            
            # Composite
            final_clip = CompositeVideoClip([bg_clip, product_clip])
            
            # Write to file
            output_file = "naturo_final_delivery.mp4"
            print("\n[Naturo Engine] Rendering final composited video using MoviePy... (this may take a moment)")
            st.write("⚙️ Rendering final composited video (this may take a moment)...")
            final_clip.write_videofile(
                output_file, 
                codec="libx264", 
                audio_codec="aac", 
                audio=False
            )
            
            # Close clips to free resources
            bg_clip.close()
            product_clip.close()
            final_clip.close()
            
            st.write("✅ Compositing complete!")
        except Exception as e:
            st.error(f"❌ Compositing failed: {e}")
            status.update(label="Compositing failed", state="error")
            return
            
        # Mark the status box as complete
        status.update(label="Pipeline processing complete!", state="complete", expanded=False)
        
    st.success("🎉 Animation generated successfully! Ready to preview.")
    
    st.video("naturo_final_delivery.mp4")
    
    with open("naturo_final_delivery.mp4", "rb") as f:
        st.download_button(
            label="Download Final Video",
            data=f,
            file_name="naturo_final_delivery.mp4",
            mime="video/mp4"
        )

# ---------------------------------------------------------
# UI Layout & Input Section
# ---------------------------------------------------------
st.markdown("### 🛠️ Input Configuration")

# Create a clean layout container for the inputs
with st.container():
    # File uploader for the product image
    uploaded_file: Optional[UploadedFile] = st.file_uploader(
        label="Upload Product Image",
        type=["png", "jpg", "jpeg"],
        help="Provide a high-quality product image against a clean background."
    )

    # Automatically process and display preview when image is uploaded
    if uploaded_file is not None:
        try:
            preview_image: Image.Image = Image.open(uploaded_file)
            st.image(
                preview_image, 
                caption=f"Uploaded Original Image: {uploaded_file.name}", 
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"⚠️ Failed to display image: {e}")

    # Text input for active ingredients
    ingredients: str = st.text_input(
        label="Active Ingredients",
        placeholder="e.g., Aloe Vera, Green Tea, Avocado, Rosewater",
        help="List the main ingredients that will shape the style and environment of the animation."
    )

# ---------------------------------------------------------
# Execution Trigger
# ---------------------------------------------------------
st.markdown("---")

if st.button("Generate Animation", type="primary", use_container_width=True):
    # Validate inputs
    if uploaded_file is None:
        st.warning("⚠️ Please upload a product image before generating the animation.")
    elif not ingredients.strip():
        st.warning("⚠️ Please provide at least one active ingredient to guide the styling.")
    else:
        # Proceed with pipeline execution
        run_animation_pipeline(uploaded_file, ingredients)
