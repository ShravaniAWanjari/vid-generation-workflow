"""
extractor.py – Extract equidistant keyframes from a video file.

Usage:
    python extractor.py <video_path> [output_dir]
"""

import os
import sys
import cv2


def extract_keyframes(video_path: str, output_dir: str) -> list[str]:
    """Extract 5 equidistant keyframes from a video and save them as JPEGs.

    Frames are sampled at 0%, 25%, 50%, 75%, and 100% of the video duration.

    Args:
        video_path: Path to the input video file (.mp4 or .mov).
        output_dir: Directory where extracted frames will be saved.

    Returns:
        A list of absolute file paths for the saved JPEG frames.

    Raises:
        FileNotFoundError: If the video file does not exist.
        ValueError: If the video cannot be opened, has zero duration, or
                     contains no readable frames.
    """
    # --- Validate input -------------------------------------------------------
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file (unsupported format?): {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if total_frames <= 0 or fps <= 0:
        cap.release()
        raise ValueError(
            f"Video has zero duration or unreadable metadata "
            f"(frames={total_frames}, fps={fps})."
        )

    duration_sec = total_frames / fps
    print(f"Video : {video_path}")
    print(f"Frames: {total_frames}  |  FPS: {fps:.2f}  |  Duration: {duration_sec:.2f}s")

    # --- Compute the 5 target frame indices -----------------------------------
    # 0%, 25%, 50%, 75%, 100%  →  indices spread across the full range.
    # Clamp the last index to (total_frames - 1) to stay in bounds.
    num_keyframes = 5
    frame_indices = [
        min(int(i * (total_frames - 1) / (num_keyframes - 1)), total_frames - 1)
        for i in range(num_keyframes)
    ]

    # --- Extract & save -------------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)

    saved_paths: list[str] = []
    jpeg_quality = [cv2.IMWRITE_JPEG_QUALITY, 95]

    for seq, idx in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()

        if not ret:
            print(f"  ⚠  Could not read frame at index {idx}, skipping.")
            continue

        filename = f"frame_{seq}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame, jpeg_quality)
        saved_paths.append(os.path.abspath(filepath))
        print(f"  ✓  Saved {filename}  (frame index {idx})")

    cap.release()

    if not saved_paths:
        raise ValueError("No frames could be read from the video.")

    return saved_paths


# ---------------------------------------------------------------------------
# Quick local test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <video_path> [output_dir]")
        sys.exit(1)

    video = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "keyframes_output"

    try:
        paths = extract_keyframes(video, out)
        print(f"\nDone – {len(paths)} keyframe(s) saved:")
        for p in paths:
            print(f"  {p}")
    except (FileNotFoundError, ValueError) as err:
        print(f"Error: {err}")
        sys.exit(1)
