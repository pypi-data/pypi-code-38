""" """
import json
from cryptanalysis.frequency_analysis import get_frequencies


def calculate_index_of_coincidence(sample_text, language='english'):
    """ """
    sample_text = sample_text.upper()
    frequencies = get_frequencies(sample_text)
    summation = 0
    for letter in sample_text:
        summation += (frequencies[letter]*(frequencies[letter]-1))
    # if language == 'english':
    #    normalising_coefficient = 26
    print((((len(sample_text))*(len(sample_text) - 1)) / 26))
    index_of_coincidence = summation / (((len(sample_text)) *
                                        (len(sample_text) - 1)) / 26)
    return index_of_coincidence


# def predict_language(index_of_coincidence):
#     """ """
#     with open('indicies_of_coincidence.json') as f:
#         indicies_dict = json.load(f)
#     language, index = min(indicies_dict.items(),
#                           key=lambda (k, v): abs(v - index_of_coincidence))
#     return language


def index_of_coincidence_analysis(ciphertext):
    """ """
    with open('indicies_of_coincidence.json', 'r') as data_file:
        actual_ioc = json.load(data_file)
    indicies_of_coincidence = {}
    for size in range(2, int((len(ciphertext)/3))):
        y = 0
        text = []
        tmp_ioc = []
        while len(text) < len(ciphertext):
            try:
                tmp_text = ''
                for x in range(0, len(ciphertext), size):
                    tmp_text += ciphertext[x+y]
            except ValueError:
                pass
            y += 1
            text.append(tmp_text)
        for sample in text:
            try:
                tmp_ioc.append(calculate_index_of_coincidence(sample))
            except ValueError:
                pass
        indicies_of_coincidence[size] = sum(tmp_ioc)/len(tmp_ioc)
    print(indicies_of_coincidence)
    print(actual_ioc)
