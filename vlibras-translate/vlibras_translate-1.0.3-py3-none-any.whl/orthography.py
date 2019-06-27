#---------------------------------
#
# Author: Caio Moraes
# Email: <caiomoraes.cesar@gmail.com>
# GitHub: MoraesCaio
#
# LAViD - Laboratório de Aplicações de Vídeo Digital
#
#---------------------------------


import string
import argparse
import hunspell
from .singleton import Singleton
from os import path


class Orthography(metaclass=Singleton):

    def __init__(cls, dic='hunspell/ptbr.dic', aff='hunspell/ptbr.aff'):
        this_file_path = path.abspath(__file__)
        directory = path.dirname(this_file_path)

        cls.hunspell = hunspell.HunSpell(path.join(directory, dic), path.join(directory, aff))

    def check(cls, word):
        '''Return True if the word is correct in Pt-BR'''
        return cls.hunspell.spell(word)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phrase', help='Phrase')
    args, _ = parser.parse_known_args()

    orthography = Orthography()

    table = str.maketrans(dict.fromkeys("“”«»–’‘º" + string.punctuation))
    phrase = args.phrase.translate(table)

    for word in phrase.split():
        print(word)
        if not orthography.check(word):
            print('Error in:', word)


if __name__ == '__main__':
    main()
