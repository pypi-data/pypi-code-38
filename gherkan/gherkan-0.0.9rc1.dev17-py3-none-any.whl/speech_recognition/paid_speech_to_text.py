import io
import os

from gherkan.utils import logging_types
import logging

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

#if the credentials are inside gherkan package in speech_recognition folder
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(os.path.dirname(os.path.realpath(__file__)),
#                                                          "google_credentials.json")
#if the credentials for google api are in the home folder
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(os.path.expanduser("~/"),"google_credentials.json")                                                          

def transcribe(filename, language_code):
    # Instantiates a client
    try:
        client = speech.SpeechClient()
    except:
        err = "Could not instantiate Google Speech API. Check the path to credentials.",
        logging.error(err, extra={
            "type": logging_types.W_GENERAL_ERROR,
            "phrase": os.environ["GOOGLE_APPLICATION_CREDENTIALS"]})

        raise ConnectionRefusedError(err)

    # Loads the audio into memory
    with io.open(filename, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code)

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])

    return transcript