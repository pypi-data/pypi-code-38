# -*- coding: utf-8 -*-
import sys

from jpype import unicode

import SmiToText.tokenizer.mecab as mecab

from SmiToText.util.util import Util

util = Util()


def find_offsets(string, char):
    """
    Find the start of all (possibly-overlapping) instances of needle in haystack
    """
    offset = -1
    offsets_list = []
    while True:
        offset = string.find(char, offset + 1)
        if offset == -1:
            break
        else:
            offsets_list.append(offset)

    return offsets_list


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def mecabSpacing(sentence, DEBUG=False):
    split_sp_type = [
        "SL"
        # ,"SN"
        # , "SF"
        , "SSO"
        , "SSC"
        # , "SC"
        , "SY"
    ]

    split_not_sp_type = [
        "SF"
        , "SC"
        , "SN"
        , "SE"
        , "NNBC"
        , "NNP"
        , "NNB", "NNB+JKS", "NNB+VCP"
        , "NNG"
        , "NR"
        , "NP"
        , "MM"
        , "MAG"
        , "MAJ"
        , "XPN"
        , "XR"
        , "XSV", "XSV+EC", "XSV+EP", "XSV+EF", "XSV", "XSV+ETM", "XSV+EP+EC", "XSV+EP+EC+VX+EF"
        , "XSN"
        , "XSA+ETM", "XSA", "XSA+EC", "XSA+EP"
        , "EF", "EC", "EP"
        , "EP+EC", "EC+VX+EP", "EP+EP", "EP+EF", "EC+VX+EF", "EC+JX"
        , "ETM"
        , "ETN", "ETN+JKO"
        , "VCP", "VCP+EF", "VCP+ETM", "VCP+EC", "VCP+EP"
        , "VX+EP", "VV+EP+EP"
        , "VX+EF"
        , "VX"
        , "VV", "VV+EP", "VV+EC", "VV+ETM", "VV+EP+EP"
        , "JKB+JX"
    ]

    josa_type = [
        "JKS", "JKC", "JKG", "JKO", "JKB", "JKV", "JKQ", "JX", "JC"
        , "JKB+JX"

    ]

    debug_history = []
    prev_dict_word = ('START', 'START')
    mecabSpacingSentence = ""

    sentence = sentence.replace("\"", "＂")

    mecabAnalizeWord = mecab.mecabAnalize(sentence)
    for dict_word_idx, dict_word in enumerate(mecabAnalizeWord):
        debug_history.append(dict_word)

        mecabSpacingSentence = mecabSpacingSentence + " " + str(dict_word[0])

        if dict_word[1] in split_sp_type:
            mecabSpacingSentence = " " + mecabSpacingSentence + " "

            print(mecabSpacingSentence)

        elif dict_word[1] in josa_type or dict_word[1] in split_not_sp_type:

            if dict_word[1] in josa_type:
                if prev_dict_word[1] not in split_sp_type:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                    mecabSpacingSentence = mecabSpacingSentence + " "
            else:
                if dict_word[1] in ["SF"] and dict_word[0] in [".", "!", "?"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif dict_word[1] in ["SN"] and dict_word[0] in [","]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["SN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif dict_word[1] in ["SC"] and dict_word[0] in [","]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["SC"] and dict_word[1] in ["SN"] and util.is_int(dict_word[1][0]):
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["SY"] and dict_word[1] in ["SN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["VA"] and dict_word[1] in ["EC", "EP", "EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VA"] and dict_word[1] in ["ETM", "ETN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VA+EP"] and dict_word[1] in ["EF", "EC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VA+EC+VX+EP"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["VV"] and dict_word[1] in ["EC", "EC+VX+EP", "EC+JX"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV"] and dict_word[1] in ["EP", "EP+EP", "EP+EF", "EP+ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV"] and dict_word[1] in ["ETN", "ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["VV"] and dict_word[1] in ["ETN+JKO", "ETN+JX"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)



                elif prev_dict_word[1] in ["VV+EP"] and dict_word[1] in ["ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+EP"] and dict_word[1] in ["ETN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+EP"] and dict_word[1] in ["EC", "EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+EP+EP"] and dict_word[1] in ["EF"]:

                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+EC"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+EC"] and dict_word[1] in ["VX", "VX+EP", "VX+EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+EC+VX+EP"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["VV+ETM"] and dict_word[1] in ["MAG"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+ETM"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VV+ETM"] and dict_word[1] in ["NNB+JKS"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["VX+EP"] and dict_word[1] in ["EF", "EC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VX"] and dict_word[1] in ["EP", "EC", "EF", "EP+EF", "EP+EP"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VX"] and dict_word[1] in ["ETM", "ETN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["VCN"] and dict_word[1] in ["ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VCN"] and dict_word[1] in ["EC", "EP", "EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VCN"] and dict_word[1] in ["EC+VX+EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["VCP"] and dict_word[1] in ["EC", "EF", "EP"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VCP"] and dict_word[1] in ["ETN", "ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["VCP+EP"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["EC"] and dict_word[1] in ["!VX+EP", "!VX+EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["EP"] and dict_word[1] in ["EF", "EC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["EC+VX+EP"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["EP"] and dict_word[1] in ["ETM", "ETN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["EP+EP"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["EP+EP"] and dict_word[1] in ["ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)



                elif prev_dict_word[1] in ["ETN"] and dict_word[1] in ["JKB+JX"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["ETM"] and dict_word[1] in ["! NNB+VCP"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["ETM"] and dict_word[1] in ["NNB+JKS"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["NP"] and dict_word[1] in ["XSN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["MAG"] and dict_word[1] in ["MM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["SE"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["MAG"] and dict_word[1] in ["VCP+EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["VCP", "VCP+EF", "VCP+EC", "VCP+EP"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["VV+EP", "VV+ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["XSV", "XSV+EP", "XSV+EF", "XSV+EC", "XSV",
                                                                       "XSV+ETM", "XSV+EP+EC", "XSV+EP+EC+VX+EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["XSA", "XSA+ETM", "XSA+EC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["XSN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["VCP+ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                # elif prev_dict_word[1] in ["NNG"] and dict_word[1] in ["NNP"]:
                #     mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["NNBC"] and dict_word[1] in ["XSN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                # elif prev_dict_word[1] in ["NNBC"] and dict_word[1] in ["NNG"]:
                #     mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNBC"] and dict_word[1] in ["VCP"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNBC+JKO"] and dict_word[1] in ["XSN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["NNB"] and dict_word[1] in ["VCP", "VCP+EF", "VCP+EP", "VCP+EC", "VCP+ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNB"] and dict_word[1] in ["XSA", "XSN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NNB+VCP"] and dict_word[1] in ["EC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["NP"] and dict_word[1] in ["VCP+EF", "VCP+EC", "VCP"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["NR"] and dict_word[1] in ["NR"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["NR"] and dict_word[1] in ["NNBC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)



                elif prev_dict_word[1] in ["NNP"] and dict_word[1] in ["NNB"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["XSA"] and dict_word[1] in ["EC", "EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["XSA+EC+VX+EP"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["XSA+EP"] and dict_word[1] in ["EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                # elif prev_dict_word[1] in ["XSA+ETM"] and dict_word[1] in ["NNB"]:
                #     mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["XSV"] and dict_word[1] in ["EP+EP", "EP+EF"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["XSV+EP"] and dict_word[1] in ["EF", "EC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["XSV+EP"] and dict_word[1] in ["ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["XSV+EC"] and dict_word[1] in ["VX+EP", "VX"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["XSV"] and dict_word[1] in ["ETN", "ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["XSV"] and dict_word[1] in ["EP+EC", "EP", "EC"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                elif prev_dict_word[1] in ["XSN"] and dict_word[1] in ["VCP", "VCP+ETM"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)
                elif prev_dict_word[1] in ["XSN"] and dict_word[1] in ["XSN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["XR"] and dict_word[1] in ["XSA+ETM", "XSA+EC", "XSA+EP", "XSA", "XSN"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)

                elif prev_dict_word[1] in ["XPN"] and dict_word[1] in ["NNG"]:
                    mecabSpacingSentence = rreplace(mecabSpacingSentence, " ", "", 1)


                else:
                    mecabSpacingSentence = " " + mecabSpacingSentence + " "

        prev_dict_word = dict_word

        # Todo 특수 기호를 키보드에 있는 키호로 변화 필요
        mecabSpacingSentence = mecabSpacingSentence.replace("＂", "\"")
        mecabSpacingSentence = mecabSpacingSentence.replace("`", "'")
        mecabSpacingSentence = mecabSpacingSentence.replace("‘`", "'")
        mecabSpacingSentence = mecabSpacingSentence.replace("’", "'")
        mecabSpacingSentence = mecabSpacingSentence.replace("'", "'")
        mecabSpacingSentence = mecabSpacingSentence.replace("`", "'")
        mecabSpacingSentence = mecabSpacingSentence.replace("‘", "'")
        mecabSpacingSentence = mecabSpacingSentence.replace("'", "'")
        mecabSpacingSentence = mecabSpacingSentence.replace("‘", "'")

        mecabSpacingSentence = mecabSpacingSentence.strip()

    mecabSpacingSentence = spectial_char_pair_blank_remove(mecabSpacingSentence, "\"")
    mecabSpacingSentence = spectial_char_pair_blank_remove(mecabSpacingSentence, "'")

    mecabSpacingSentence = mecabSpacingSentence.replace(" 이 같이", " 이같이")
    mecabSpacingSentence = mecabSpacingSentence.replace(" 어 이", " 어이 ")
    mecabSpacingSentence = mecabSpacingSentence.replace("가건 말 건", "가건말건 ")
    mecabSpacingSentence = mecabSpacingSentence.replace("승산 비", "승산비")
    mecabSpacingSentence = mecabSpacingSentence.replace("매달한 번", "매달 한 번")
    mecabSpacingSentence = mecabSpacingSentence.replace("네브 라스카", "네브라스카")
    mecabSpacingSentence = mecabSpacingSentence.replace("여전히그", "여전히 그")
    mecabSpacingSentence = mecabSpacingSentence.replace("기 상통 보관", "기상 통보관")
    mecabSpacingSentence = mecabSpacingSentence.replace("주시 겠습니까", "주시겠습니까")
    mecabSpacingSentence = mecabSpacingSentence.replace(". ..", "...")
    mecabSpacingSentence = mecabSpacingSentence.replace(", .", ",.")
    mecabSpacingSentence = mecabSpacingSentence.replace(", .", ",.")
    mecabSpacingSentence = mecabSpacingSentence.replace(" · ", "·")
    mecabSpacingSentence = mecabSpacingSentence.replace("· ", "·")
    mecabSpacingSentence = mecabSpacingSentence.replace(" …", "…")
    mecabSpacingSentence = mecabSpacingSentence.replace("  ", " ")
    mecabSpacingSentence = mecabSpacingSentence.replace(" / ", "/")
    mecabSpacingSentence = mecabSpacingSentence.replace("[ ", "[")
    mecabSpacingSentence = mecabSpacingSentence.replace(" ]", "]")
    mecabSpacingSentence = mecabSpacingSentence.replace("( ", "(")
    mecabSpacingSentence = mecabSpacingSentence.replace(" )", ")")
    mecabSpacingSentence = mecabSpacingSentence.replace(" ,", ",")

    if DEBUG == True:
        print(debug_history)

    return mecabSpacingSentence


def spectial_char_pair_blank_remove(sentence, char="\""):
    sentence = sentence + "     "
    offsets_list_length = int(len(find_offsets(sentence, char)))

    print("[", sentence, "]")
    for idx in range(offsets_list_length):
        offsets_list = find_offsets(sentence, char)

        if (idx % 2 == 0):

            if (sentence[offsets_list[idx] + 1] == " "):
                sentence = sentence[:offsets_list[idx] + 1] + sentence[(offsets_list[idx] + 2):]
        else:

            # if (sentence[offsets_list[idx] + 1] == "."):
            #     print("3ASdF")
            #     sentence = sentence[:offsets_list[idx]] + sentence[(offsets_list[idx] + 1):]

            if (sentence[offsets_list[idx] - 1] == " "):
                sentence = sentence[:offsets_list[idx] - 1] + sentence[(offsets_list[idx]):]

            if (sentence[offsets_list[idx] - 1] == char):
                sentence = sentence[:offsets_list[idx]] + " " + sentence[(offsets_list[idx]):]

            if (sentence[offsets_list[idx] + 1 ] == "."):
                sentence = sentence[:offsets_list[idx]] + sentence[(offsets_list[idx]+1):]

            if (sentence[offsets_list[idx] + 1 ] == ","):
                sentence = sentence[:offsets_list[idx]] + sentence[(offsets_list[idx]+1):]

        print("idx", idx, sentence)

    return sentence.strip()


if __name__ == '__main__':
    while True:
        try:
            inputText = input("\n\n문장을 입력하세요?: \n")
            inputText = unicode(inputText)
        except UnicodeDecodeError:
            print("다시 입력하세요\n")
            continue

        if inputText == 'exit':
            exit(1)
        print(inputText)
        print(mecab.mecabTokenizer(inputText))
        print(mecabSpacing(inputText, DEBUG=True))

# -------------------------------------------------------------------------------------------------------------------

# readfile = open("/home/jjeaby/Dev/06.rosamia/SmiToText/data/20180717-small_jin/AllInOne_KO_20180627_0_VALID.txt",
#                 mode="r", encoding="utf-8")
# linenum = 0
#
# if len(sys.argv) == 1:
#     break_linenum = 0
# else:
#     break_linenum = int(sys.argv[1])
#
# while True:
#
#     linenum += 1
#     line = readfile.readline()
#
#     if break_linenum != 0:
#         if linenum == break_linenum:
#             break
#     else:
#         if not line:
#             print("NOT LINE : ", '\'' + line + '\'', linenum)
#             break
#
#     text = line.strip()
#
#     # print(linenum, "--------------------------------")
#     # print(mecab.mecabTokenizer(text))
#     mecabOutput = mecabSpacing(text, DEBUG=False)
#     print(text)
#     print(mecabOutput)
#     # print(mecab.mecabTokenizer(mecabOutput.replace(" ", "_")).replace(" _ ", "_").replace(" ", "|") )
#     # print(linenum, "--------------------------------")
