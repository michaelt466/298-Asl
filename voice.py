import pyttsx3

# ════════════════════════════════════════════════════════════════════════════
#  VOICE ENGINE
# ════════════════════════════════════════════════════════════════════════════

def build_engine():
    """Initialize and configure the TTS engine."""
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    male_voice = next(
        (v for v in (voices or []) if 'male' in v.name.lower() or 'david' in v.name.lower()), # type: ignore
        None
    )
    if male_voice:
        engine.setProperty('voice', male_voice.id)

    engine.setProperty('rate', 165)
    engine.setProperty('volume', 0.95)

    return engine


def speak(text: str):
    """Speak text in a blocking call (run in thread)."""
    try:
        engine = build_engine()
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print(f"Voice error: {e}")