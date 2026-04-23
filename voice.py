import pyttsx3

# ════════════════════════════════════════════════════════════════════════════
#  VOICE ENGINE
# ════════════════════════════════════════════════════════════════════════════
engine = None

def init_tts():
    global engine
    if pyttsx3 is not None:
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')  # type: ignore
    
            for v in voices:  # type: ignore
                    if 'male' in v.name.lower() or 'david' in v.name.lower():  # type: ignore
                        engine.setProperty('voice', v.id)  # type: ignore
                        break

            engine.setProperty('rate', 165)   # Slightly slower = more robotic gravitas
            engine.setProperty('volume', 0.95)
            print("✅ pyttsx3 voice engine ready")
        except Exception as e:
            print(f" TTS init failed: {e}")
    else:
        print(" pyttsx3 not available, TTS disabled")

def speak(text: str):
    """Speak text in a blocking call (run in thread)."""
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")

# Initialize on import
init_tts()

