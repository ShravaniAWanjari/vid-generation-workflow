"""
pipeline_engine.py - Simulates backend n8n engine logic for video generation.
"""

import time
import os
from drive_storage import upload_production_render

def upload_to_drive(video_stream: bytes, filename: str) -> dict:
    """
    Uploads the video to Google Drive via the drive_storage module.
    """
    # Assuming the client is Naturo and project is Demo for now.
    client_name = "Naturo"
    project_name = filename.split('.')[0]
    
    return upload_production_render(video_stream, client_name, project_name)

def execute_video_pipeline(payload: dict):
    """
    Simulates the backend engine logic.
    Yields status updates as dictionaries.
    
    Args:
        payload: A dictionary containing 'demo_mode' (bool), 
                 'compiled_prompt' (str), and 'selected_tier' (str).
                 
    Yields:
        Dictionaries containing either {"status": "Update Message"} 
        or {"done": True, "status": "SUCCESS", "tier": "...", "metadata": [...]}.
    """
    demo_mode = payload.get("demo_mode", False)
    compiled_prompt = payload.get("compiled_prompt", "")
    selected_tier = payload.get("selected_tier", "Tier 1: Decent Videos")
    product_image_name = payload.get("product_image_name", "demo_generated.png")
    base_name = os.path.splitext(product_image_name)[0]
    
    # Determine the requested tier
    tier_num = 1
    if "Tier 2" in selected_tier:
        tier_num = 2
    elif "Tier 3" in selected_tier:
        tier_num = 3
    
    if demo_mode:
        yield {"status": "Extracting Keyframes..."}
        time.sleep(1.5)
        
        yield {"status": "Compiling Spatial VLM Prompt..."}
        time.sleep(1.5)
        
        yield {"status": "Archiving to Studio Drive..."}
        time.sleep(2.0)
        
        # Determine video with fallback: Requested Tier -> Higher Tiers -> No Tier -> Default
        candidates = []
        base_name_us = base_name.replace(" ", "_")
        for t in range(tier_num, 4):
            candidates.append(f"{base_name}_tier{t}.mp4")
            if base_name_us != base_name:
                candidates.append(f"{base_name_us}_tier{t}.mp4")
        candidates.append(f"{base_name}.mp4")
        if base_name_us != base_name:
            candidates.append(f"{base_name_us}.mp4")
        candidates.append("demo_generated.mp4")
        candidates.append("demo.mp4")
        
        video_path = None
        for cand in candidates:
            cand_path = os.path.join("data", cand)
            if os.path.exists(cand_path):
                video_path = cand_path
                break
                
        if not video_path:
            raise FileNotFoundError(f"Generated video not found for {base_name}")
            
        # Bypass Google Drive API and use a direct local download link
        upload_metadata = {
            'file_id': 'local',
            'webViewLink': f'https://noct-creative-dispatch.onrender.com/api/download-video?video_name={os.path.basename(video_path)}'
        }
        
        final_storage_metadata_array = [upload_metadata]
        
        yield {
            "done": True,
            "status": "SUCCESS", 
            "tier": selected_tier, 
            "metadata": final_storage_metadata_array
        }
        
    else:
        raise NotImplementedError("Paid API integration bypassed in development mode.")

# Quick test if run directly
if __name__ == "__main__":
    test_payload = {
        "demo_mode": True,
        "compiled_prompt": "Cinematic macro photography...",
        "selected_tier": "Tier 2: Special Product Movements & Hyper-Realism"
    }
    
    try:
        for update in execute_video_pipeline(test_payload):
            if update.get("done"):
                print(f"Status: {update['status']}")
                print(f"Tier: {update['tier']}")
                print(f"Metadata: {update['metadata']}")
            else:
                print(update['status'])
    except Exception as e:
        print(f"Error: {e}")
