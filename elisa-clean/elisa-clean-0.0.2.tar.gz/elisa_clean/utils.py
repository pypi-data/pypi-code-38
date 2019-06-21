import regex as re
from string import punctuation
import spacy


open_punctuations = re.compile(r'(^.*?[)\]}])|([(\[{].*?$)')
pronouns = re.compile(r' *(?:\b(?:themselves|they|them|their|ourselves|our|us|we|himself|him|he|his|herself|hers|her|she|myself|my|I|me|it|its)\b)(?:/\b(?:themselves|they|them|their|ourselves|our|us|we|himself|him|he|his|herself|hers|her|she|myself|my|I|me|it|its)\b)* *')


def remove_open_punctuations(string: str) -> str:
    return open_punctuations.sub('', string)


def remove_pronouns(string: str) -> str:
    found = pronouns.findall(string)
    if  found and found[0] == string:
        return string
    else:
        return pronouns.sub("", string)


def remove_punctuations(string: str, puncts="".join(set(punctuation) - set(",/;"))) -> str:
    pass

    return ''.join(char for char in string if char not in puncts)


def remove_abbrev(string: str) -> str:

    for x in {'a.m.', 'a.m', 'p.m.', 'p.m', 'etc.', 'etc', 'e.g.', 'e.g', 'i.e.', 'i.e'}:
        if x in string:
            string = string.replace(x, '')
    return string


def filter_pos(string: str, pos, nlp) -> str:
    if nlp is None:
        return string

    tokens = []
    for token in nlp(string):
        if token.pos_ == pos or token.pos_ == "SYM":
            tokens.append(token.text)
    return ' '.join(tokens) if tokens else string


def filter_entity(string: str, nlp) -> str:
    if nlp is None:
        return string
    tokens = []
    for ent in nlp(string).ents:
        tokens.append(ent.text)
    return ' '.join(tokens) if tokens else string


def split(string: str, sep=',/;') -> list:
    return re.split(r'['+sep+']', string)

