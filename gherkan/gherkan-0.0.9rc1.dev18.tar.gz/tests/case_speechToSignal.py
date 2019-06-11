import os
import gherkan.utils.constants as c
from gherkan.speech_recognition.paid_speech_to_text import transcribe

from gherkan.flask_api.raw_text_to_signal import nl_to_signal

audio_path = os.path.join(c.DATA_DIR, "audio", "montrac.wav")
language_code = 'cs-CZ'

text_raw = transcribe(audio_path, language_code)

print(f"Transcribed text: {text_raw}")

request = {
    "feature" : "Montrac",
    "feature_desc" : "Test audia",
    "background" : "Jakmile linka je zapnutá",
    "text_raw" : text_raw,
    "language" : c.LANG_CZ
}

base_path = os.path.join(c.DATA_DIR, "output", "raw_out")

nl_to_signal(base_path, request)

nl_file_path = base_path + ".feature"
signal_file_path = base_path + "_signals.feature"

print("\n\n--- NL FILE ---")
with open(nl_file_path, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)

print("\n\n--- SIGNAL FILE ---")
with open(signal_file_path, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)