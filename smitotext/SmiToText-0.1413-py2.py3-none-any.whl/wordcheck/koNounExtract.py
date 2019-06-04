# -*- coding: utf-8 -*-
import re
from SmiToText.util.util import Util
from SmiToText.wordcheck.koLastCharCheck import koLastCharCheck
import os


class koNounExtract(object):

    def __init__(self):
        self.util = Util()
        self.kolastChar = koLastCharCheck();

        self.rootDirPath = self.util.getRootPath("SmiToText.SmiToText")

    def dictGenerate(self, sentence):


        return mecabDictLine

if __name__ == '__main__':

    util = Util()
    mecabDictGen = koNounExtract()

    rootDirPath = util.getRootPath("SmiToText.SmiToText")
    data_path = rootDirPath + os.path.sep + "data" + os.path.sep + "koDetokenizerData"

    input_filename = data_path + os.path.sep + "국어_명사_초성포함단어제거.txt"
    output_filename = data_path + os.path.sep + "./국어_명사_초성포함단어제거_mecabUserDict.csv"

    read_file = open(input_filename, mode='r', encoding='utf-8')
    write_file = open(output_filename, mode='w', encoding='utf-8')

    linenum = 0
    while True:
        word = read_file.readline()
        word = word.strip()
        isLastChar = 0
        linenum += 1
        if not word:
            break

        mecabDictLine = mecabDictGen.dictGenerate(word)
        print(mecabDictLine)
        # write_file.writelines(mecabDictLine + "\n")

    print("LINE NUMBER END : ", linenum)

    write_file.close()
    read_file.close()
