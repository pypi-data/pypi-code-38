import speech_recognition as sr
import argparse
import os

"""
Speech-To-Text transcription using Google API.
Currently, SpeechRecognition supports the following file formats:

WAV: must be in PCM/LPCM format
AIFF
AIFF-C
FLAC: must be native FLAC format; OGG-FLAC is not supported

Example od usage:
python3 speech_to_text,py --audio_file ./myfile.wav --lang cs-CZ

"""


def process(audio_file_path: str, lang: str):
    rec = sr.Recognizer()
    audio_file = sr.AudioFile(audio_file_path)

    transcriptPath = '.'.join(audio_file_path[:audio_file_path.find(".")], ".txt")

    with audio_file as source:
        print("Processing audio...")
        audio = rec.record(source)
        recognized = rec.recognize_google(audio, language=lang)
        print("Recognized text: {}".format(recognized))

    with open(transcriptPath, "w", encoding="utf-8") as tf:
        tf.writelines(recognized)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio_file", help="Path to input audio file")
    parser.add_argument("--lang", help="en-US/en-UK/cs-CZ")
    args = parser.parse_args()

    rec = sr.Recognizer()
    audio_file = sr.AudioFile(args.audio_file)

    with audio_file as source:
        print("Processing audio...")
        audio = rec.record(source)
        recognized = rec.recognize_google(audio, language=args.lang)
        print("Recognized text: {}".format(recognized))
