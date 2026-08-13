import os
import pickle
import time
import numpy as np
import sounddevice as sd
import librosa
from config import WAKE_WORD_MODEL_PATH, SAMPLE_RATE

wake_model = None
wake_scaler = None

if os.path.exists(WAKE_WORD_MODEL_PATH):
    try:
        with open(WAKE_WORD_MODEL_PATH, "rb") as f:
            wake_model, wake_scaler = pickle.load(f)
        print("Wake word detector model loaded successfully.")
    except Exception as e:
        print(f"Error loading wake word model: {e}")

def record_audio_chunk(duration=3):
    try:
        recording = sd.rec(int(SAMPLE_RATE * duration), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        return recording.flatten(), SAMPLE_RATE
    except Exception as e:
        print(f"Audio chunk recording error: {e}")
        return np.zeros(int(SAMPLE_RATE * duration), dtype='float32'), SAMPLE_RATE

def is_wake_word(audio, sr):
    if wake_model is None or wake_scaler is None:
        return False
    try:
        audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        features = np.mean(mfcc.T, axis=0).reshape(1, -1)
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        features_scaled = wake_scaler.transform(features)
        prob = wake_model.predict_proba(features_scaled)[0][1]
        print(f"Wake word probability: {prob:.2f}")
        return prob > 0.85
    except Exception as e:
        print(f"Wake word prediction exception: {e}")
        return False

def listen_for_wake_word():
    print("Waiting for wake word...")
    audio, sr = record_audio_chunk(duration=3)
    if is_wake_word(audio, sr):
        time.sleep(0.2)
        audio2, sr2 = record_audio_chunk(duration=2)
        if is_wake_word(audio2, sr2):
            return True
    return False
