import os
import time
import tempfile
import asyncio
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
import edge_tts
import pygame
import threading
import re

from config import DEEPGRAM_API_KEY, SAMPLE_RATE, CHUNK_SIZE, state, state_lock

# Initialize Pygame Mixer for low-latency audio playback
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Pygame mixer init warning: {e}")

# Initialize Faster-Whisper (Local Offline STT Engine)
whisper_model = None
try:
    from faster_whisper import WhisperModel
    print("Loading local Faster-Whisper STT model (base.en)...")
    whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
    print("Faster-Whisper STT engine ready!")
except Exception as e:
    print(f"Faster-Whisper not active: {e}. Will fallback to Deepgram if API key is set.")

# Deepgram Client Initialization (Fallback)
deepgram_client = None
if DEEPGRAM_API_KEY and whisper_model is None:
    try:
        from deepgram import DeepgramClient
        deepgram_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)
    except Exception as e:
        print(f"Deepgram init warning: {e}")

def calibrate_microphone():
    print("Calibrating microphone sensitivity...")
    try:
        recording = sd.rec(int(SAMPLE_RATE * 2), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sd.wait()
        level = float(np.abs(recording).mean())
        with state_lock:
            state["ambient_threshold"] = min(max(level * 1.3, 150.0), 400.0)
            thresh = state["ambient_threshold"]
        print(f"Microphone calibrated. Threshold: {thresh:.1f}")
    except Exception as e:
        print(f"Calibration failed: {e}")

async def _generate_speech(text, file_path):
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save(file_path)

def _listen_for_interrupt():
    with state_lock:
        threshold = state["ambient_threshold"] * 1.5
        
    while pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        try:
            chunk = sd.rec(CHUNK_SIZE, samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            sd.wait()
            level = float(np.abs(chunk).mean())
            if level > threshold:
                print("\n[!] Interrupt detected! Stopping speech...")
                with state_lock:
                    state["stop_speaking"] = True
                pygame.mixer.music.stop()
                break
        except Exception:
            break

def _speak_single_chunk(text_chunk):
    with state_lock:
        if state["stop_speaking"]:
            return False

    temp_speech_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    try:
        asyncio.run(_generate_speech(text_chunk, temp_speech_file))
        
        if pygame.mixer.get_init():
            pygame.mixer.music.load(temp_speech_file)
            pygame.mixer.music.play()
            
            interrupt_thread = threading.Thread(target=_listen_for_interrupt, daemon=True)
            interrupt_thread.start()
            
            while pygame.mixer.music.get_busy():
                with state_lock:
                    if state["stop_speaking"]:
                        pygame.mixer.music.stop()
                        return False
                time.sleep(0.05)
            pygame.mixer.music.unload()
            return True
    except Exception as e:
        print(f"TTS Speech error: {e}")
        return False
    finally:
        try:
            if os.path.exists(temp_speech_file):
                os.remove(temp_speech_file)
        except Exception:
            pass

def speak(text):
    print(f"Jay: {text}")
    with state_lock:
        state["stop_speaking"] = False

    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if s.strip()]
    if not sentences:
        sentences = [text]

    for sentence in sentences:
        with state_lock:
            if state["stop_speaking"]:
                break
        success = _speak_single_chunk(sentence)
        if not success:
            break

    with state_lock:
        state["last_spoken"] = time.time()

def listen(duration=8):
    print("Listening...")
    with state_lock:
        threshold = state["ambient_threshold"]
        
    pre_buffer = []
    start_time = time.time()
    
    # Wait for voice activity (Max 6s timeout)
    while True:
        if time.time() - start_time > 6.0:
            print("Listening timed out (no speech detected).")
            return ""
            
        try:
            chunk = sd.rec(CHUNK_SIZE, samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            sd.wait()
            pre_buffer.append(chunk.copy())
            if len(pre_buffer) > 18:
                pre_buffer.pop(0)
            level = float(np.abs(chunk).mean())
            if level > threshold * 0.4:
                print("Recording speech...")
                break
        except Exception as e:
            print(f"Audio read error: {e}")
            return ""

    chunks = list(pre_buffer)
    silence_count = 0
    max_silence = 14

    while True:
        try:
            chunk = sd.rec(CHUNK_SIZE, samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            sd.wait()
            chunks.append(chunk.copy())
            level = float(np.abs(chunk).mean())
            if level < threshold:
                silence_count += 1
            else:
                silence_count = 0
            if silence_count > max_silence:
                break
            if len(chunks) > int(SAMPLE_RATE / CHUNK_SIZE * duration):
                break
        except Exception:
            break

    full_recording = np.concatenate(chunks, axis=0)
    
    # Volume normalization
    max_val = float(np.max(np.abs(full_recording)))
    if max_val > 100.0:
        scaling_factor = min(26000.0 / max_val, 10.0)
        full_recording = (full_recording.astype(np.float32) * scaling_factor).astype(np.int16)

    duration_sec = len(full_recording) / SAMPLE_RATE
    print(f"Captured {duration_sec:.1f}s of audio.")

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    wavfile.write(temp_file, SAMPLE_RATE, full_recording)

    command = ""
    try:
        # Primary: Local Faster-Whisper with VAD Noise Filtering
        if whisper_model:
            segments, info = whisper_model.transcribe(
                temp_file,
                beam_size=5,
                language="en",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )
            command = " ".join([segment.text for segment in segments]).strip().lower()
            if command:
                print(f"Recognized (Local Whisper): {command}")
        
        # Fallback: Deepgram Cloud API
        elif deepgram_client:
            with open(temp_file, "rb") as audio_file:
                buffer_data = audio_file.read()
            
            for model_choice in ["nova-3", "nova-2-general"]:
                try:
                    response = deepgram_client.listen.v1.media.transcribe_file(
                        request=buffer_data,
                        model=model_choice,
                        language="en",
                        smart_format=True,
                        punctuate=True,
                        numerals=True,
                    )
                    command = response.results.channels[0].alternatives[0].transcript.lower().strip()
                    if command:
                        print(f"Recognized (Deepgram {model_choice}): {command}")
                        break
                except Exception as err:
                    print(f"STT Model {model_choice} failed: {err}")
    except Exception as e:
        print(f"STT Error: {e}")
    finally:
        try:
            os.remove(temp_file)
        except Exception:
            pass

    return command
