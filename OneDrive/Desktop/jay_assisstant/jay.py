import time
import random
import datetime
import threading
from config import state, state_lock
import audio_engine
import wake_word
import analyzer
import planner

idle_phrases = [
    "Hey, let me know if you need anything.",
    "Standing by whenever you need me.",
    "Ready when you are.",
    "Let me know if I can help with something.",
]

greeting_phrases = [
    "Hey! What's on your mind?",
    "Hey there! How can I help today?",
    "Ready to go. What are we working on?",
]

def idle_talker():
    while True:
        time.sleep(45)
        with state_lock:
            is_awake = state["awake"]
            last_spk = state["last_spoken"]
        
        if is_awake and (time.time() - last_spk > 90):
            audio_engine.speak(random.choice(idle_phrases))

def run_jay():
    audio_engine.calibrate_microphone()
    
    # Background threads
    threading.Thread(target=idle_talker, daemon=True).start()

    audio_engine.speak("Jay is online and ready. Say Hey Jay whenever you need me.")

    # 1. Wake Word Loop
    while True:
        if wake_word.listen_for_wake_word():
            with state_lock:
                state["awake"] = True
            planner.clear_session()
            audio_engine.speak(random.choice(greeting_phrases))
            break
        time.sleep(0.1)

    # Time-based greeting
    hour = datetime.datetime.now().hour
    if hour < 12:
        audio_engine.speak("Good morning! How can I help you start your day?")
    elif hour < 17:
        audio_engine.speak("Good afternoon! What can I help you with?")
    else:
        audio_engine.speak("Good evening! How can I assist you tonight?")

    # Main Orchestrator Loop
    while True:
        try:
            # 2. Speech-to-Text
            command = audio_engine.listen(duration=8)
            if not command:
                continue

            # 3. Request Analyzer & 4. Tool Router
            is_simple, status = analyzer.analyze_and_route_request(command)

            if is_simple:
                if status == "SLEEP":
                    audio_engine.speak("Very well Sir. I shall retire for now. Say Hey Jay whenever you need me.")
                    with state_lock:
                        state["awake"] = False
                    
                    # Sleep loop waiting for wake word
                    while True:
                        print("Sleeping... say Hey Jay to wake me up!")
                        if wake_word.listen_for_wake_word():
                            with state_lock:
                                state["awake"] = True
                            planner.clear_session()
                            audio_engine.speak(random.choice(greeting_phrases))
                            break
                        time.sleep(0.1)

                elif status == "EXIT":
                    audio_engine.speak("Goodbye Sir. It was a pleasure serving you. Shutting down completely.")
                    break
            else:
                # 5. LLM Planner ➔ 6. Execution Manager ➔ 7. System Verifier ➔ 8. Memory ➔ 9. TTS
                planner.plan_and_execute_goal(command)

        except Exception as e:
            print(f"Error in main orchestrator loop: {e}")
            audio_engine.speak("I apologize Sir, I encountered an unexpected issue. Standing by.")
            time.sleep(1)

if __name__ == "__main__":
    run_jay()