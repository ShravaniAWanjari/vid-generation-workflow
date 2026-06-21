"""
prompt_compiler.py – Vision-driven prompt compiler for video diffusion networks.

Uses Google Gemini (gemini-2.5-flash) to analyze a product image + style-reference keyframes
and produces a spatially-structured video generation prompt that keeps the
product pristine while animating background ingredients in isolated zones.
"""

import os
from pathlib import Path
import PIL.Image

from google import genai
from google.genai import types

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an expert prompt compiler for video diffusion networks. "
    "Your goal is to write a highly detailed chronological animation script describing the scene over a 6-second timeline. "
    "Rules:\n"
    "1. Identify the product type and its visible ingredients from the image.\n"
    "2. Start your response with a standalone sentence explicitly stating that the product container/packaging remains perfectly crisp, static, and unaltered in the center of the frame.\n"
    "3. Next, write three distinct time blocks: 'Time 00:00 to 00:02:', 'Time 00:02 to 00:04:', and 'Time 00:04 to 00:06:'.\n"
    "4. For each time block, heavily emphasize the MOTION of the ingredients. Explicitly state they do NOT just 'spring up' or 'pop in'. Instead, describe them as 'gradually rising, slowly unfurling, and expanding with delicate, organic, time-lapse style growth motion'. Describe smooth camera movements.\n"
    "5. Use the style-reference keyframes ONLY to understand the desired motion style, lighting, and camera work — do NOT copy unrelated content from them.\n"
    "6. Output exactly the static container statement followed by the three timestamped blocks on new lines. Do not output a single paragraph.\n"
    "7. CRITICAL: The entire generated prompt MUST be under 1000 characters in length. Be concise but descriptive."
)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def compile_spatial_prompt(
    product_image_path: str,
    keyframe_paths: list[str],
    raw_intent: str,
) -> str:
    """Compile a spatially-structured video-generation prompt using Gemini.

    Args:
        product_image_path: Path to the product PNG image.
        keyframe_paths:     List of up to 5 keyframe paths extracted from the video.
        raw_intent:         Free-form text describing the desired animation.

    Returns:
        The compiled prompt string ready for a video diffusion model.
    """
    # ── Validate inputs ──────────────────────────────────────────────────
    if not os.path.isfile(product_image_path):
        raise FileNotFoundError(f"Product image not found: {product_image_path}")

    for kf in keyframe_paths:
        if not os.path.isfile(kf):
            raise FileNotFoundError(f"Keyframe not found: {kf}")

    if not raw_intent or not raw_intent.strip():
        raise ValueError("raw_intent must be a non-empty string.")

    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is missing. Please add it to .env")

    # ── Configure Gemini (Using the new SDK) ──────────────────────────────
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # ── Prepare Media ────────────────────────────────────────────────────
    product_img = PIL.Image.open(product_image_path)
    kf_imgs = [PIL.Image.open(kf) for kf in keyframe_paths[:5]]

    content_payload = [
        "Below are the inputs for this compilation job.\n\n"
        f"**Raw Text Intent:** {raw_intent.strip()}\n\n"
        "**Product Image** (first image) — analyze the product type, label, shape, and visible ingredient cues.\n\n"
        "**Style-Reference Keyframes** (subsequent images) — use these ONLY for motion/lighting/camera style. Do NOT extract product identity from them.\n\n"
        "Compile and return the final chronological prompt script now. You MUST use the 'Time 00:00 to 00:02:' format on separate lines as instructed.",
        product_img,
        *kf_imgs
    ]

    # ── Call Gemini API ──────────────────────────────────────────────────
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=content_payload,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.4,
        )
    )

    compiled_prompt = response.text.strip()

    # Strip any accidental wrapping quotes the model might add
    if compiled_prompt.startswith(("'", '"')) and compiled_prompt.endswith(("'", '"')):
        compiled_prompt = compiled_prompt[1:-1].strip()

    return compiled_prompt

# ──────────────────────────────────────────────────────────────────────────────
# Quick local test
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python prompt_compiler.py <product.png> <keyframes_dir> <raw_intent>")
        sys.exit(1)

    img_path = sys.argv[1]
    kf_dir = sys.argv[2]
    intent = sys.argv[3]

    kf_files = sorted(str(p) for p in Path(kf_dir).glob("frame_*.jpg"))

    if not kf_files:
        print(f"No frame_*.jpg files found in {kf_dir}")
        sys.exit(1)

    result = compile_spatial_prompt(img_path, kf_files, intent)
    print("\n✅ Compiled Prompt:\n")
    print(result)
