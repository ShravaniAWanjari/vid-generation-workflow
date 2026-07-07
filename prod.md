# Production TODO List

A simple list of what exists now versus what needs to change to make this tool fully live.

---

### 1. File Storage
*   **What's there:** Uploaded images and video files are currently saved in a temporary folder that deletes itself immediately.
*   **What to change:** Save files in a permanent folder (like Google Drive or AWS S3) using a unique ID so we don't lose the product image.

### 2. Frontend API Connection
*   **What's there:** The frontend UI currently uses a simulated progress timer.
*   **What to change:** Connect the frontend to the backend's `/api/stream-generation` Server-Sent Events (SSE) endpoint to fetch live progress status directly from the server.

### 3. Video Generation Models
*   **What's there:** The backend is bypassed and does not connect to a live model generator.
*   **What to change:** Connect the backend to a cloud video model API (like Replicate) using the prompt and the stored product image.

###   4. Demo Mode Toggle
*   **What's there:** The toggle switch at the top of the app is locked to "Demo Mode".
*   **What to change:** Unlock the toggle switch so users can switch the app from "Demo Mode" to "Production Mode".

### 5. API Keys
*   **What to change:** Add the API credentials to the server settings:
    *   `REPLICATE_API_TOKEN` (for the video generator)
    *   `GOOGLE_CREDENTIALS` (for Drive uploads)
