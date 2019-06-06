# -*- coding: utf-8 -*-
import re
from SmiToText.util.util import Util
from SmiToText.wordcheck.koLastCharCheck import koLastCharCheck
import os


class mecabDictGenerate(object):

    def __init__(self):
        self.util = Util()
        self.kolastChar = koLastCharCheck();

        self.rootDirPath = self.util.getRootPath("SmiToText.SmiToText")

    def dictGenerate(self, word, posTag="NNG", kind=''):
        isLastChar = self.kolastChar.lastKoTextCheck(word)
        if kind:
            kind = kind + '-'

        # 포커스 인,,,,NNG,*,T,포커스 인,*,*,*,*
        if isLastChar == 1:
            # print(line + ",,,,NNG,*,T,추가-" + line + ",*,*,*,*")
            # write_file.writelines(word + ",,,,NNG,*,T,추가-" + word + ",*,*,*,*" + "\n")
            mecabDictLine = word + ",,,," + posTag + ",*,T," + kind + word + ",*,*,*,*"
        else:
            # print(line + ",,,,NNG,*,F,추가-" + line + ",*,*,*,*")
            # write_file.writelines(word + ",,,,NNG,*,F,추가-" + word + ",*,*,*,*" + "\n")
            mecabDictLine = word + ",,,," + posTag + ",*,F," + kind + word + ",*,*,*,*"
        return mecabDictLine

    def mecab_dict_gen_from_file(self, input_filename, output_filename, posTag='NNG', kind=''):

        read_file = open(input_filename, mode='r', encoding='utf-8')
        write_file = open(output_filename, mode='w', encoding='utf-8')

        linenum = 0
        while True:
            word = read_file.readline()
            word = word.strip()
            linenum += 1
            if not word:
                break

            mecabDictLine = self.dictGenerate(word, posTag=posTag, kind=kind)
            print(mecabDictLine)
            write_file.writelines(mecabDictLine + "\n")

        print("LINE NUMBER END : ", linenum)

        write_file.close()
        read_file.close()


if __name__ == '__main__':
    util = Util()
    mecabDictGen = mecabDictGenerate()

    rootDirPath = util.getRootPath("SmiToText.SmiToText")
    data_path = rootDirPath + os.path.sep + "data" + os.path.sep + "koDetokenizerData"

    # input_filename = data_path + os.path.sep + "국어_명사_초성포함단어제거.txt"
    # output_filename = data_path + os.path.sep + "./국어_명사_초성포함단어제거_mecabUserDict.csv"

    # input_filename = data_path + os.path.sep + "ttaDict_KO_sort.txt"
    # output_filename = data_path + os.path.sep + "./ttaDict_KO_sort_mecabUserDict.csv"

    input_filename = data_path + os.path.sep + "나라.txt"
    output_filename = data_path + os.path.sep + "./나라_mecabUserDict.csv"

    mecabDictGen.mecab_dict_gen_from_file(input_filename, "/home/jjeaby/Dev/06.rosamia/SmiToText/a.txt")

    # read_file = open(input_filename, mode='r', encoding='utf-8')
    # write_file = open(output_filename, mode='w', encoding='utf-8')
    #
    # linenum = 0
    # while True:
    #     word = read_file.readline()
    #     word = word.strip()
    #     isLastChar = 0
    #     linenum += 1
    #     if not word:
    #         break
    #
    #     mecabDictLine = mecabDictGen.dictGenerate(word)
    #     print(mecabDictLine)
    #     write_file.writelines(mecabDictLine + "\n")
    #
    # print("LINE NUMBER END : ", linenum)
    #
    # write_file.close()
    # read_file.close()
