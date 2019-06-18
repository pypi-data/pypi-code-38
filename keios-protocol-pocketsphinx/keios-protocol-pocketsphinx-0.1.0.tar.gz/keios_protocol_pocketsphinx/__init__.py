from typing import List
from dataclasses import dataclass
import numpy as np
import flatbuffers
from keios_protocol_common import FlatbufferObject
from .flatbuffers import PocketsphinxRequest as PocketsphinxRequestClass
from .flatbuffers import PocketsphinxResponse as PocketsphinxResponseClass
from .flatbuffers import Guess as GuessClass

@dataclass
class PocketsphinxRequestData:
    speech: bytearray

class PocketsphinxRequestEntity(FlatbufferObject):
    def __init__(self):
        super().__init__(PocketsphinxRequestData, PocketsphinxRequestClass)

    # serialize
    def dataclass_to_flatbuffer(self, dataclass):
        speech_vector = self.build_vector('Speech', dataclass.speech)
        self.start()
        self['Speech'] = speech_vector
        return self.end()
        
    def flatbuffer_to_dataclass(self, flatbuffer):
        return self.dataclass(speech=self['Speech'].tobytes())

@dataclass
class GuessData():
    phrase: str = ''
    confidence: float = 0

class GuessEntity(FlatbufferObject):
    def __init__(self, builder):
        super().__init__(GuessData, GuessClass, builder)

    def dataclass_to_flatbuffer(self, dataclass):
        phrase = self.build_string(dataclass.phrase)
        self.start()
        self['Confidence'] = dataclass.confidence
        self['Phrase'] = phrase
        return self.end()
        
    def flatbuffer_to_dataclass(self, flatbuffer):
        return self.dataclass(
            confidence=self['Confidence'],
            phrase=self['Phrase'].decode("utf-8")
        )

@dataclass
class PocketsphinxResponseData:
    guesses: List[GuessData]

class PocketsphinxResponseEntity(FlatbufferObject):
    def __init__(self):
        super().__init__(PocketsphinxResponseData, PocketsphinxResponseClass)

    def dataclass_to_flatbuffer(self, dataclass):
        guess_vector = self.build_vector('Guesses', dataclass.guesses, GuessEntity)
        self.start()
        self['Guesses'] = guess_vector
        return self.end()
        
    def flatbuffer_to_dataclass(self, flatbuffer):
        guess = GuessEntity(self.builder)
        guesses = [guess.build(g) for g in self['Guesses']]
        return self.dataclass(guesses=guesses)