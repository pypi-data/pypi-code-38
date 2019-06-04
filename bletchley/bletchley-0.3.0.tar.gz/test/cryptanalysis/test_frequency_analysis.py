""" File containing unit tests for frequency_analysis """
import pytest
import json
from cryptanalysis.frequency_analysis import get_frequencies

@pytest.fixture
def english_freqs():
    with open('frequencies.json') as file:
        frequencies = json.load(file)
    text_frequencies = get_frequencies(text)
    freqs = frequencies["english"].items()
    return freqs

@pytest.fixture
def text():
    with open('text_sample.txt') as file:
        sample_text = str(file.readlines())
        print(type(text))
    return sample_text

def test_get_frequencies(text, english_freqs):
    freqs = get_frequencies(text)
    assert freqs == english_freqs