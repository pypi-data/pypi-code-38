#---------------------------------
#
# Author: Caio Moraes
# Email: <caiomoraes.cesar@gmail.com>
# GitHub: MoraesCaio
#
# LAViD - Laboratório de Aplicações de Vídeo Digital
#
#---------------------------------


import argparse
import pickle
from pygtrie import CharTrie
from .singleton import Singleton
from unidecode import unidecode
import string
from os import path


class NameChecking(metaclass=Singleton):

    def __init__(cls):
        this_file_path = path.abspath(__file__)
        directory = path.dirname(this_file_path)

        with open(path.join(directory, 'pygtrie_CharTrie_names_pickle_wout_inter_3'), 'rb') as file:
            cls.trie = pickle.load(file)

    def is_name(cls, word):
        return cls.trie.has_key(unidecode(word.upper()))

    def is_tag_name(cls, tag):
        if tag[1][:2] not in ['SR', 'ET', 'HV', 'TR', 'VB']:

            # ESTÁ NO DICIONÁRIO DE NOMES'
            if cls.is_name(tag[0]):

                # salva novos nomes encontrados pelo dicionário de nomes
                #  isso é necessário por causa dos acentos retirados
                with open('possible_new_names.txt', 'a') as new_names:
                    new_names.write(tag[0]+'\n')

                return True

        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phrase', help='Phrase')
    args, _ = parser.parse_known_args()

    name_checking = NameChecking()

    table = str.maketrans(dict.fromkeys("“”«»–’‘º" + string.punctuation))
    phrase = args.phrase.translate(table)

    for word in phrase.split():
        print('Is ', end='')
        if not name_checking.is_name(word):
            print('not ', end='')
        print('a name:', word, '<' * 10 if name_checking.is_name(word) else '')


if __name__ == '__main__':
    main()
