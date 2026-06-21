import os
from dotenv import load_dotenv
load_dotenv()

import tempfile
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, UploadFile, Form, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

# Import our core logic
from extractor import extract_keyframes
from prompt_compiler import compile_spatial_prompt
from pipeline_engine import execute_video_pipeline

app = FastAPI(title="Naturo AI Engine API")

# Configure CORS for Vercel integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load global envs explicitly if needed (though os.environ works dynamically)
# os.getenv("GOOGLE_CREDENTIALS") and os.getenv("GOOGLE_PARENT_FOLDER_ID")
# are accessed inside drive_storage.py and pipeline_engine.py

# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────────────────────────────────────
class StreamGenerationRequest(BaseModel):
    demo_mode: bool = True
    compiled_prompt: str
    selected_tier: str = "Tier 1: Decent Videos ($0.03)"

# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root_health_check():
    return {"status": "online"}

@app.get("/api/download-video")
async def download_video(video_name: str = Query("demo_generated.mp4")):
    video_path = os.path.join("data", video_name)
    if not os.path.exists(video_path):
        video_path = "demo.mp4"
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found.")
    return FileResponse(video_path, media_type="video/mp4", filename=f"Render_{video_name}")

@app.post("/api/compile-prompt")
async def compile_prompt(
    product_image: UploadFile = File(...),
    style_video: Optional[UploadFile] = File(None),
    raw_intent: str = Form(...)
):
    """
    Receives product image and optional style video, saves them temporarily, 
    runs keyframe extraction (if video provided) and spatial prompt compilation, and returns the result.
    """
    try:
        # Create a secure temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            img_path = os.path.join(temp_dir, product_image.filename)
            kf_dir = os.path.join(temp_dir, "keyframes")
            os.makedirs(kf_dir, exist_ok=True)
            
            # Save uploaded image
            with open(img_path, "wb") as f:
                f.write(await product_image.read())

            kf_paths = []
            if style_video:
                vid_path = os.path.join(temp_dir, style_video.filename)
                with open(vid_path, "wb") as f:
                    f.write(await style_video.read())
                kf_paths = extract_keyframes(vid_path, kf_dir)
                
            # Execute Python modules
            compilation_result = compile_spatial_prompt(img_path, kf_paths, raw_intent)
            
            # compilation_result is now a dict containing 'product_name' and 'compiled_prompt', or 'error'
            if "error" in compilation_result:
                raise HTTPException(status_code=400, detail=compilation_result["error"])

            return compilation_result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream-generation")
async def stream_generation(
    demo_mode: bool = Query(True),
    compiled_prompt: str = Query(...),
    selected_tier: str = Query("Tier 1: Decent Videos ($0.03)"),
    product_image_name: str = Query("demo_generated.png")
):
    """
    Streams Server-Sent Events (SSE) back to the React frontend.
    Simulates sending the job to the video diffusion backend.
    """
    
    pipeline_payload = {
        "demo_mode": demo_mode,
        "compiled_prompt": compiled_prompt,
        "selected_tier": selected_tier,
        "product_image_name": product_image_name
    }

    async def event_generator():
        try:
            # We must iterate over our synchronous generator
            # In a true high-throughput FastAPI app, you might wrap this in asyncio.to_thread,
            # but for this deployment, normal iteration is fine since demo sleeps simulate work.
            for update in execute_video_pipeline(pipeline_payload):
                # Format as Server-Sent Event (SSE)
                sse_data = json.dumps(update)
                yield f"data: {sse_data}\n\n"
                
                # Yield control to event loop to actually flush data to the client
                await asyncio.sleep(0)
                
        except Exception as e:
            error_data = json.dumps({"done": True, "error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ──────────────────────────────────────────────────────────────────────────────
# Server Entry Point for Render
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    # Render assigns a dynamic port via the $PORT environment variable.
    # Fallback to 8000 for local development.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
