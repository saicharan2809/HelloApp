import ollama
from config import OLLAMA_MODEL
import memory
from audio_engine import speak

session_messages = []

def clear_session():
    global session_messages
    session_messages = []
    print("[Memory] Session context reset.")

def plan_and_execute_goal(prompt):
    global session_messages

    # Check if user wants to reset or start a fresh topic
    if any(w in prompt.lower() for w in ["forget", "reset chat", "clear memory", "new topic"]):
        clear_session()
        speak("Got it, fresh start.")
        return True

    system_prompt = """You are Jay, a smart, witty, and friendly AI companion.
Be conversational, natural, and easygoing. Speak clearly and concisely.
Avoid overly stiff, robotic, or Victorian formal butler phrasing.
Do NOT use markdown bullet points, bold text, or lists since your response is read aloud.
Answer Sir's request directly without repeating previous answers.
"""

    # Build clean messages list (system prompt + active session turns + current user prompt)
    messages = [{"role": "system", "content": system_prompt}]
    
    # Include up to the last 2 turns (4 messages) for smooth immediate follow-ups
    for msg in session_messages[-4:]:
        messages.append(msg)
        
    messages.append({"role": "user", "content": prompt})

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
        )
        answer = response["message"]["content"].strip()
        
        if answer:
            # Track current session turn cleanly
            session_messages.append({"role": "user", "content": prompt})
            session_messages.append({"role": "assistant", "content": answer})
            if len(session_messages) > 10:
                session_messages = session_messages[-10:]

            memory.add_conversation_memory(prompt, answer)
            speak(answer)
            return True
        else:
            speak("I didn't get a response. Could you try asking again?")
            return False
            
    except Exception as e:
        print(f"LLM Planner exception: {e}")
        speak("I encountered an issue accessing my core brain Sir. Please ensure Ollama is running.")
        return False
