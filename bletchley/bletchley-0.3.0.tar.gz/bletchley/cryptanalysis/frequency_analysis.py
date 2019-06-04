import json
import string


def frequency_analysis(text, language="english"):
    with open('frequencies.json') as file:
        frequencies = json.load(file)
    text_frequencies = get_frequencies(text)
    freqs_sorted = sorted(frequencies[language].items(), key=lambda kv: kv[1])
    language_alphabet = []
    for key in freqs_sorted:
        language_alphabet.append(str(key[0]))

    text_freqs_sorted = sorted(text_frequencies.items(), key=lambda kv: kv[1])
    text_alphabet = []
    for key in text_freqs_sorted:
        text_alphabet.append(str(key[0]))

    # Should use more than just the first letter in
    # future (won't work for small cipher texts)
    shifts = {}
    for i in range(len(text_alphabet)):
        # org_letter = string.ascii_uppercase.index(language_alphabet[i])
        # text_letter = string.ascii_uppercase.index(text_alphabet[i])
        # shift = text_letter % 26 + 1
        error = 0
        for letter in frequencies[language]:
            error = error + (frequencies[language][letter] -
                             text_frequencies[letter])
        shifts[str(i)] = error
    predicted_shift = min(shifts, key=shifts.get)
    return int(predicted_shift)


def get_frequencies(text):
    alphabet = string.ascii_uppercase
    frequencies = {}
    for letter in alphabet:
        frequencies[letter] = 0
    text = text.upper()
    for letter in text:
        if letter in alphabet:
            frequencies[letter] += 1
    total_letters = len(text)
    for letter in frequencies:
        frequencies[letter] = frequencies[letter] / total_letters
    return frequencies


if __name__ == "__main__":
    x = frequency_analysis("bob")
    print(x)
