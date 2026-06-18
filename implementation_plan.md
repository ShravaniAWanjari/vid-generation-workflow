# Fix Hugging Face Image-to-Video Model Support

The current implementation throws an error because `Wan-AI/Wan2.1-I2V-14B-480P` is not directly supported by the `fal-ai` provider through Hugging Face's "Routed" Inference endpoints.

## Open Questions

> [!IMPORTANT]
> The `fal-ai` provider on Hugging Face recently updated their supported models. They now support **Wan2.2** models instead of the specific Wan2.1 I2V 480P variant we requested. 
> 
> Are you okay with switching to `Wan-AI/Wan2.2-I2V-A14B` (the latest supported high-quality model), or do you prefer `Wan-AI/Wan2.2-TI2V-5B` for potentially faster/cheaper generation? 

## Proposed Changes

We will update the model ID in the Hugging Face InferenceClient call to use a supported Image-to-Video model that is mapped to `fal-ai`.

### app.py

Update the `generate_background_video` function:

#### [MODIFY] [app.py](file:///c:/Users/shrav/Desktop/12%20week%20thing/NOCT-task/app.py)

```python
        if image_path and os.path.exists(image_path):
            st.write("🖼️ Using Image-to-Video generation with the product image...")
            video_bytes = client.image_to_video(
                image=image_path,
                prompt=prompt,
                model="Wan-AI/Wan2.2-I2V-A14B", # <-- Updated to a supported model
            )
```

## Verification Plan

### Manual Verification
- Run `streamlit run app.py`
- Upload a product image and provide active ingredients.
- Wait for the pipeline to extract the background and submit the image to the new `Wan2.2-I2V` model.
- Verify that the video generation succeeds without the `400 Bad Request / Not Supported` error and compositing completes successfully.
