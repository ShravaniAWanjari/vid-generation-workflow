Prompt 2: The Foreground Extraction Module
Goal: Integrate the exact programmatic logic to strip the background without distorting the product.

Copy and paste this into your coding agent:

Now we will implement the actual logic for Step 1: Background Isolation.

Add rembg to our requirements.txt.

Update the main application script. Inside the first step of our st.status block, take the uploaded_file and open it using PIL.Image.

Pass the image through rembg.remove() to isolate the foreground.

Save the resulting transparent image to the local disk as temp_product.png.

Below the file uploader (before the generate button is clicked), add a feature that automatically displays the transparent temp_product.png preview as soon as the user uploads an image, so they can verify the extraction worked before initiating the full video pipeline.

Handle potential PIL image format errors gracefully using a try/except block and use st.error if the extraction fails.

Prompt 3: The Video API & Prompt Engine
Goal: Connect to the external video generator (Fal.ai is recommended here for developer stability, but you can swap it for Runway if you have the API key) and handle the API polling.

Copy and paste this into your coding agent:

Phase 3: Implement the prompt expansion and Video API integration.

Create a function generate_background_video(ingredients_text, api_key).

Inside this function, construct the following prompt structure: "Cinematic macro time-lapse photography of {ingredients_text} blooming and unfurling, highly detailed organic textures, soft studio lighting, clean defocus bokeh background, shallow depth of field, high-end commercial cosmetics advertisement style, 8k resolution."

Write the exact Python requests logic to send this prompt to the Fal.ai Text-to-Video API endpoint (or a generic placeholder endpoint if I specify later).

Implement a polling mechanism using a while loop that checks the API status every 5 seconds until the video URL is returned or it times out after 120 seconds.

Download the returned .mp4 and save it locally as bg_video.mp4.

Integrate this function into Step 2 and Step 3 of our Streamlit st.status block. Read the API key securely from st.secrets["VIDEO_API_KEY"]. If the key is missing, halt execution and throw an st.error.

Prompt 4: Programmatic Compositing (The Core IP)
Goal: Stitch the transparent product over the blooming background using code to guarantee absolute visual consistency.

Copy and paste this into your coding agent:

Phase 4: Implement the final programmatic compositing using moviepy.

Add moviepy to requirements.txt.

Create a compositing block in Step 4 of our Streamlit pipeline.

Load the downloaded bg_video.mp4 using VideoFileClip.

Load the temp_product.png using ImageClip.

Set the duration of the ImageClip to match the VideoFileClip.

Resize the ImageClip so its height is exactly 75% of the background video's height.

Position the ImageClip exactly in the bottom-center of the frame (('center', 'bottom')).

Composite the two clips together using CompositeVideoClip.

Write the final output to naturo_final_delivery.mp4 using the libx264 video codec and aac audio codec.

Once the video is rendered, display it in the Streamlit app using st.video().

Add an st.download_button so the user can download the final MP4.

Checkpoints for You
As the agent writes this code, watch out for these common failure points:

MoviePy Audio Bug: moviepy sometimes throws errors if the generated background video lacks an audio track. If the agent's code fails on the .write_videofile() step, instruct the agent to add audio=False to the render command.

Image Modes: rembg outputs an RGBA image. If the agent tries to save it as a .jpg, it will crash. Ensure it strictly saves the extracted product as a .png to preserve the alpha channel.
