import io
import re


def read_text(text_path):
    """Reads a text file and converts it to a unicode string.

    Arguments:
        text_path {str} -- A path of text file.

    Returns:
        [unicode] -- A text file's text as a unicode.
    """
    text = io.open(text_path, encoding='utf-8').read()
    return text


def parse_sentences_and_next_characters(
        whole_text, max_sentence_size, interval_between_each_sentence):
    """Extracts sentences from whole_text according to max sentence size and
    interval between each sentence.

    Arguments:
        whole_text {str} -- A text to be parsed.
        max_sentence_size {int} -- A max length of each sentence.
        interval_between_each_sentence {int} --
            An extraction distance between each sentence.
            For example,
            if whole_text is 'hello world' and max_sentence_size is 5
            and interval_between_each_sentence is 1,
            then sentences will be
            ['hello', 'ello ', 'llo w', 'lo wo', 'o wor', ' worl', 'world'].
            or interval_between_each_sentence is 2,
            then sentences will be ['hello', 'llo w', 'o wor', 'world'].

    Returns:
        [list, list] -- A list of sentences and a list of next characters will
        be returned.
    """
    sentences = []
    next_characters = []
    for i in range(0, len(whole_text) - max_sentence_size,
                   interval_between_each_sentence):
        sentence = whole_text[i: i + max_sentence_size]
        sentences.append(sentence)
        next_character_of_sentence = whole_text[i + max_sentence_size]
        next_characters.append(next_character_of_sentence)
    return sentences, next_characters


def get_unique_characters(text):
    """Extracts unique characters from string.

    Arguments:
        text {str} -- A string from which to extract unique characters.

    Returns:
        [list] -- A list of unique characters.
    """
    unique_character_set = set(text)
    unique_characters = list(unique_character_set)
    sorted_unique_characters = sorted(unique_characters)
    return sorted_unique_characters


def get_words_from_text(text):
    word_list = re.sub(r"[^\w]", " ", text).split()  # we will lower all words
    return word_list
