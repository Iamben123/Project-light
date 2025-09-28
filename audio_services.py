import tensorflow as tf
import numpy as np
from scipy.signal import resample

# --- TensorFlow YAMNet Initialization ---
try:
    yamnet_model = tf.saved_model.load('yamnet-tensorflow2-yamnet-v1')
    with open('yamnet-tensorflow2-yamnet-v1/assets/yamnet_class_map.csv', 'r') as f:
        class_names = [line.strip().split(',', 2)[2].strip('"') for line in f.readlines()[1:]]
except Exception as e:
    print(f"Error loading TensorFlow model: {e}")
    yamnet_model = None
    class_names = []

def process_audio_chunk(waveform, sample_rate):
    if not yamnet_model:
        return "MODEL NOT LOADED"

    if sample_rate != 16000:
        num_samples = int(len(waveform) * 16000 / sample_rate)
        waveform = resample(waveform, num_samples)

    waveform = waveform.astype(np.float32) / 32768.0
    scores, embeddings, spectrogram = yamnet_model(waveform)
    
    prediction = np.mean(scores, axis=0)
    predicted_index = np.argmax(prediction)
    predicted_class_name = class_names[predicted_index]

    # --- EXPANDED TARGET LIST for greater environmental awareness ---
    target_sounds = [
        # Critical Alerts
        'Siren', 'Civil defense siren', 'Police car (siren)', 'Emergency vehicle',
        'Alarm', 'Alarm clock', 'Fire alarm', 'Smoke detector, smoke alarm',
        'Car horn', 'Vehicle horn, honking',
        'Screaming', 'Shout', 'Yell',
        
        # General Awareness Sounds
        'Dog', 'Bark',
        'Knock', 'Doorbell',
        'Speech', 'Conversation',
        'Water', 'Stream', 'Waterfall', 'Gurgling',
        'Typing',
        'Vehicle', 'Motor vehicle (road)', 'Car'
    ]

    # Check if the clean prediction is in our target list
    if predicted_class_name in target_sounds:
        return predicted_class_name
    
    return None

