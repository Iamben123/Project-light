import easyocr

# --- EasyOCR Initialization ---
# The reader object will be created by the initialize_reader function
# to prevent blocking the main application at startup.
reader = None

def initialize_reader():
    """
    Initializes the EasyOCR reader. This is a slow, one-time operation.
    Returns True on success, False on failure.
    """
    global reader
    print("INFO: Initializing EasyOCR model... (This may take several minutes on first run)")
    try:
        # We force CPU mode (gpu=False) because it is more stable and less error-prone
        # for this type of application, especially on devices without a dedicated NVIDIA GPU.
        reader = easyocr.Reader(['en'], gpu=False)
        print("INFO: EasyOCR model loaded successfully.")
        return True
    except Exception as e:
        print(f"FATAL ERROR: Could not initialize EasyOCR: {e}")
        return False

def process_image_with_ocr(frame):
    """
    Performs OCR. This function is now only called by the vision loop
    when the targeting service provides a clear and stable image.
    """
    # If the reader object hasn't been created yet, do nothing.
    if reader is None:
        return ""

    # The 'paragraph=True' setting tells EasyOCR to group nearby text together,
    # which is better for reading sentences or blocks of text.
    result = reader.readtext(frame, detail=0, paragraph=True)
    
    # If any text was found, join it into a single string.
    if result:
        return " ".join(result)
    
    return ""

