import cv2
import numpy as np

# This variable will store the previous frame to check for motion
previous_frame_gray = None

def analyze_frame_for_targeting(frame, viewfinder_rect):
    """
    Analyzes the portion of the frame inside the viewfinder.
    Returns a status: "SEARCHING", "HOLD STEADY", or "READY_TO_READ".
    """
    global previous_frame_gray

    # 1. Get the region of interest (the part of the image inside the viewfinder)
    x, y, w, h = viewfinder_rect
    roi = frame[y:y+h, x:x+w]
    
    # 2. Convert to grayscale for analysis
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 3. Clarity Check (Noise Gate) - Is there anything interesting in the box?
    clarity_score = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
    CLARITY_THRESHOLD = 50 # Tune this: higher means it needs very clear text
    
    if clarity_score < CLARITY_THRESHOLD:
        previous_frame_gray = gray_roi
        return "SEARCHING" # Not enough detail, probably no text

    # 4. Stability Check - Is the camera being held steady?
    if previous_frame_gray is not None:
        # Resize for faster comparison, in case of minor frame size changes
        prev_frame_resized = cv2.resize(previous_frame_gray, (gray_roi.shape[1], gray_roi.shape[0]))
        diff = cv2.absdiff(gray_roi, prev_frame_resized)
        motion_score = np.mean(diff)
        STABILITY_THRESHOLD = 5.0 # Tune this: lower means you have to be very still

        if motion_score > STABILITY_THRESHOLD:
            previous_frame_gray = gray_roi
            return "HOLD STEADY" # There's text, but it's moving

    # 5. If it's clear AND stable, it's ready for OCR
    previous_frame_gray = gray_roi
    return "READY_TO_READ"

