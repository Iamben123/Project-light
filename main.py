import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading
import time
import numpy as np
import pyaudio
from vision_services import process_image_with_ocr, initialize_reader
from audio_services import process_audio_chunk
from targeting_service import analyze_frame_for_targeting

# --- Camera Configuration ---
# Set this to True to use your phone's camera (via DroidCam URL).
USE_PHONE_CAMERA = False 

# Replace this with the IP address shown in the DroidCam app on your phone.
PHONE_CAMERA_URL = "http://192.168.1.12:4747/video" # Example IP

# Set to 0 for your laptop's webcam.
WEBCAM_INDEX = 0

# --- UI Design Constants ---
BG_COLOR = "#000000"
PANE_BG_COLOR = "#1c1c1c"
TEXT_COLOR = "#FFFFFF"
ALERT_COLOR = "#FF0000" 
FONT_FACE = "Segoe UI"
FONT_SIZE_TEXT = 18
FONT_SIZE_ALERT = 24
FONT_SIZE_GUIDE = 22
CV_VIEWFINDER_SEARCHING = (255, 255, 255) # White (BGR for OpenCV)
CV_VIEWFINDER_STEADY = (0, 255, 0)     # Green (BGR for OpenCV)
INDICATOR_COLOR_ACTIVE = "#00FF00"      # Green (Hex for Tkinter)
INDICATOR_COLOR_IDLE = "#444444"        # Gray (Hex for Tkinter)

# --- Shared Variables & Threading Events ---
latest_frame_from_thread = None
detected_text = ""
detected_alert = ""
is_running = True
system_status = "SEARCHING"
SAMPLE_RATE = 16000
ocr_ready_event = threading.Event()

# --- Functions ---

def ocr_initialization_thread():
    """ Loads the heavy OCR model and then sets an event to notify other threads. """
    if initialize_reader():
        ocr_ready_event.set()

def vision_thread_loop():
    """ This thread waits for the OCR model to be ready, then runs the targeting and OCR loop. """
    global detected_text, system_status
    
    print("INFO: Vision thread started, waiting for OCR model...")
    ocr_ready_event.wait()
    print("INFO: Vision processing loop has now started.")
    
    while is_running:
        if latest_frame_from_thread is not None:
            frame_for_analysis = latest_frame_from_thread.copy()
            h, w, _ = frame_for_analysis.shape
            viewfinder_w = int(w * 0.8); viewfinder_h = int(h * 0.5)
            viewfinder_x = (w - viewfinder_w) // 2; viewfinder_y = (h - viewfinder_h) // 2
            viewfinder_rect = (viewfinder_x, viewfinder_y, viewfinder_w, viewfinder_h)

            status = analyze_frame_for_targeting(frame_for_analysis, viewfinder_rect)
            system_status = status
            
            if status == "READY_TO_READ":
                roi_for_ocr = frame_for_analysis[viewfinder_y:viewfinder_y+viewfinder_h, viewfinder_x:viewfinder_x+viewfinder_w]
                text_from_frame = process_image_with_ocr(roi_for_ocr)
                if text_from_frame: detected_text = text_from_frame
            elif status == "SEARCHING":
                detected_text = ""
        time.sleep(0.1)

def audio_thread_loop():
    """ This thread also waits for OCR model to be ready before starting to listen. """
    global detected_alert
    
    print("INFO: Audio thread started, waiting for OCR model...")
    ocr_ready_event.wait()
    print("INFO: Audio processing loop has now started.")
    
    CHUNK_SIZE = 1024; p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True,
                        input_device_index=1, frames_per_buffer=CHUNK_SIZE)
        while is_running:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            waveform = np.frombuffer(data, dtype=np.int16)
            alert = process_audio_chunk(waveform, sample_rate=SAMPLE_RATE)
            detected_alert = alert.upper() if alert else ""
    except Exception as e: print(f"PyAudio Error: {e}"); detected_alert = "AUDIO ERROR"
    finally:
        if 'stream' in locals() and stream.is_active(): stream.stop_stream(); stream.close()
        p.terminate()

def camera_thread_loop():
    """ A dedicated thread to read frames from the camera to prevent UI freezes. """
    global latest_frame_from_thread
    while is_running:
        ret, frame = cap.read()
        if ret: latest_frame_from_thread = frame
        else: time.sleep(0.1)

def update_gui():
    """ This function repeatedly updates all UI elements. """
    # --- THIS IS THE FIX ---
    # Set default values for guide_text and viewfinder_color BEFORE the if-statement.
    # This guarantees they always exist, even if the camera frame fails for a moment.
    guide_text = "Find Text"
    viewfinder_color = CV_VIEWFINDER_SEARCHING

    if latest_frame_from_thread is not None:
        frame_for_display = latest_frame_from_thread.copy()
        h, w, _ = frame_for_display.shape
        viewfinder_w = int(w * 0.8); viewfinder_h = int(h * 0.5)
        viewfinder_x = (w - viewfinder_w) // 2; viewfinder_y = (h - viewfinder_h) // 2
        
        # These lines will now just update the default values if the system status changes.
        if system_status == "HOLD STEADY": guide_text = "Hold Steady..."
        elif system_status == "READY_TO_READ":
            viewfinder_color = CV_VIEWFINDER_STEADY
            guide_text = "Reading..."

        cv2.rectangle(frame_for_display, (viewfinder_x, viewfinder_y), (viewfinder_x + viewfinder_w, viewfinder_y + viewfinder_h), viewfinder_color, 2)
        rgb_frame = cv2.cvtColor(frame_for_display, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))
        
        live_view_label.config(image=photo); live_view_label.image = photo
        app_view_label.config(image=photo); app_view_label.image = photo

    guide_text_label.config(text=guide_text)

    if ocr_ready_event.is_set():
        if detected_text:
            ocr_text_label.config(text=detected_text)
            status_indicator.itemconfig(indicator_circle, fill=INDICATOR_COLOR_ACTIVE)
        else:
            ocr_text_label.config(text="")
            status_indicator.itemconfig(indicator_circle, fill=INDICATOR_COLOR_IDLE)
    else:
        ocr_text_label.config(text="Loading OCR model...")

    alert_text_label.config(text=f"🚨 {detected_alert} 🚨" if detected_alert else "")
    window.after(30, update_gui)

def on_closing(event=None):
    global is_running; is_running = False; time.sleep(0.5); window.destroy()

# --- Main Application Setup ---
camera_source = PHONE_CAMERA_URL if USE_PHONE_CAMERA else WEBCAM_INDEX
cap = cv2.VideoCapture(camera_source)
if not cap.isOpened(): print(f"FATAL ERROR: Could not open camera: {camera_source}"); exit()

window = tk.Tk(); window.title("Presenter Mode"); window.config(bg=BG_COLOR); window.attributes('-fullscreen', True)
left_pane = tk.Frame(window, bg=PANE_BG_COLOR); left_pane.pack(side="left", fill="both", expand=True, padx=10, pady=10)
right_pane = tk.Frame(window, bg=PANE_BG_COLOR); right_pane.pack(side="right", fill="both", expand=True, padx=10, pady=10)
tk.Label(left_pane, text="INPUT (Live Camera View)", font=(FONT_FACE, 16, "bold"), fg=TEXT_COLOR, bg=PANE_BG_COLOR).pack(pady=10)
tk.Label(right_pane, text="OUTPUT (Smart Glass UI)", font=(FONT_FACE, 16, "bold"), fg=TEXT_COLOR, bg=PANE_BG_COLOR).pack(pady=10)
live_view_label = tk.Label(left_pane, bg=BG_COLOR); live_view_label.pack(padx=10, pady=10, expand=True)
app_view_container = tk.Frame(right_pane, bg=BG_COLOR); app_view_container.pack(fill="both", expand=True, padx=10, pady=10)
app_view_label = tk.Label(app_view_container, bg=BG_COLOR); app_view_label.pack(fill="both", expand=True)
alert_text_label = tk.Label(app_view_container, text="", font=(FONT_FACE, FONT_SIZE_ALERT, "bold"), fg=ALERT_COLOR, bg=BG_COLOR)
alert_text_label.place(relx=0.5, y=30, anchor="center")
guide_text_label = tk.Label(app_view_container, text="Find Text", font=(FONT_FACE, FONT_SIZE_GUIDE, "italic"), fg=TEXT_COLOR, bg=BG_COLOR)
guide_text_label.place(relx=0.5, y=80, anchor="center")
status_indicator = tk.Canvas(app_view_container, width=30, height=30, bg=BG_COLOR, highlightthickness=0)
indicator_circle = status_indicator.create_oval(5, 5, 25, 25, fill=INDICATOR_COLOR_IDLE)
status_indicator.place(x=20, rely=1.0, y=-50, anchor="sw")
ocr_text_label = tk.Label(app_view_container, text="", font=(FONT_FACE, FONT_SIZE_TEXT), wraplength=500, justify="left", anchor="nw", fg=TEXT_COLOR, bg=BG_COLOR)
ocr_text_label.place(x=60, rely=1.0, y=-52, anchor="sw")

# --- Start Threads in the Correct Order ---
threading.Thread(target=camera_thread_loop, daemon=True).start()
threading.Thread(target=ocr_initialization_thread, daemon=True).start()
threading.Thread(target=vision_thread_loop, daemon=True).start()
threading.Thread(target=audio_thread_loop, daemon=True).start()
window.bind('<Escape>', on_closing); window.protocol("WM_DELETE_WINDOW", on_closing)
update_gui(); window.mainloop(); cap.release()

