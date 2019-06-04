import os
import re
import sys
from collections import Counter
from operator import itemgetter

import numpy
from langdetect import detect

from SmiToText.frequency import word as word_freq
from SmiToText.tokenizer import mecab
from SmiToText.tokenizer import nltk


def extract_enko(filename):
    global enko_smi_raw
    sync_start_flag = False;
    read_smi = open(filename, mode='rb')
    enko_smi_raw = []
    pair_smi_list = []

    temp_line = ""
    while (True):
        line = read_smi.readline()
        if not line: break
        if len(line) > 0:
            line = read_by_encod_type(line)

        line = remove_unused_word(line)

        sync_tag = ["<SYNC"]
        if line.strip().upper().startswith(tuple(sync_tag)):
            sync_start_flag = True;
        elif sync_start_flag == False:
            continue

        if (line.upper().startswith("<SYNC START=")):
            temp_line = extract_synctime_text(temp_line)

            if temp_line != None:
                if len(temp_line[2]) > 0:
                    pair_smi_list.append(temp_line)
            temp_line = line

        else:
            temp_line = temp_line + " " + line

    read_smi.close()

    # pair_smi_list = pair_smi_list[20:-20]
    # utf8_smi_text = utf8_smi_text[20:-20]
    # euckr_smi_text = euckr_smi_text[20:-20]
    # eucjp_smi_text = eucjp_smi_text[20:-20]

    # print((pair_smi_list))
    # print(type(pair_smi_list))

    pair_smi_list.sort(key=itemgetter(1))
    pair_smi_list.sort(key=itemgetter(0))

    return pair_smi_list


def read_by_encod_type(line):
    try:
        line = line.decode('utf-8')
        # print("utf-8", line)
    except:
        try:
            line = line.decode('EUC-KR')
            # print("euc-kr", line)
        except:
            try:
                line = line.decode('cp949')
                # print("cp949", line)
            except:
                try:
                    line = line.decode('euc-jp')
                    # print("euc-jp", line)
                except:
                    line = line
                    # print("")
    return line


def remove_unused_word(line):
    line = str(line)
    line = line.strip()
    line = line.replace(r' .', '.')
    line = line.replace(r' ,', '.')
    line = line.replace(r'\n', '')
    line = line.replace(r'\r', '')
    line = line.replace('&nbsp;', ' ')
    line = re.sub(r"<[B|b][R|r]*>", " ", line)
    line = re.sub(r"<[I|i]*>", "", line)
    line = re.sub(r"<!--[^>]*>", "", line)
    line = re.sub(r"<\/[f|F][o|O][n|N][t|T]>", "", line)
    line = re.sub(r"<[f|F][o|O][n|N][t|T][^<][^>]*>", "", line)
    line = re.sub(r"<\/[h|H][e|E][a|A][d|D]*>", "", line)
    line = re.sub(r"<[h|H][e|E][a|A][d|D]*>", "", line)
    line = re.sub(r"<\/[b|B][o|O][d|D][y|Y]*>", "", line)
    line = re.sub(r"<[b|B][o|O][d|D][y|Y]*>", "", line)
    line = re.sub(r"-", " ", line)
    line = re.sub(r"[ ]{2,}", " ", line)
    line = re.sub(r"[!]{2,}", "!", line)
    line = re.sub(r"[?]{2,}", "?", line)
    line = re.sub(r"[,]{2,}", ",", line)
    line = re.sub(r"[.]{2,}", ".", line)
    line = re.sub(r"\n", "", line)
    line = line.strip()
    return line


def extract_synctime_text(line):
    sync_time_regexpress = r"<[S|s][Y|y][N|n][C|c][ ]{1,}[S|s][T|t][A|a][R|r][T|t][=]\d*"
    smi_sync_number = re.findall(sync_time_regexpress, line)
    if len(smi_sync_number) > 0:
        smi_sync_number = smi_sync_number[0]
        smi_sync_number = int(smi_sync_number.split("=")[1])

        # print(smi_sync_number, re.sub(r"<[S|s][Y|y][N|n][C|c][ ]{1,}[S|s][T|t][A|a][R|r][T|t][=]\d*>", "", smi))

        smi_text = re.sub(r"<[S|s][Y|y][N|n][C|c][ ]{1,}[S|s][T|t][A|a][R|r][T|t][=]\d*>", "", line).strip()
        smi_text = re.sub(r"<[P|p][^>]*>", "", smi_text)
        smi_lang_code = re.findall(r"<[P|p][ ]{1,}[C|c][L|l][A|a][S|s][S|s][=][^>]*", line)[0]
        smi_lang_code = smi_lang_code.split("=")[1]
        if len(smi_text) > 0:
            return [int(smi_sync_number), smi_lang_code, smi_text.strip()]
        else:
            return [int(smi_sync_number), smi_lang_code, ""]
    else:
        return None


def convert_dict_smi(smi_list):
    pair_smi_dict = {}
    smi_list.sort(key=itemgetter(1))
    pair_smi_numpy_array = numpy.array(pair_smi_list)
    pair_smi_numpy_array = pair_smi_numpy_array[..., 1]
    pair_smi_lang_array = numpy.unique(pair_smi_numpy_array)

    for idx, item in enumerate(pair_smi_lang_array):
        pair_smi_dict[item] = {}

    for idx, item in enumerate(smi_list):
        pair_smi_dict[smi_list[idx][1]].update({smi_list[idx][0]: smi_list[idx][2]})

    return (pair_smi_dict)


def check_special_character(text1, text2):
    special_character_list = ["\"", "`", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "~", "<", ">", "?",
                              ":", "{", "}", "|", ",", ".", "/", ";", "'", "[", "]", "\\"]

    for sp in special_character_list:
        if text1.count(sp) != text2.count(sp):
            return False

    return True


# def write_enko(enko_smi_text, filename, output_path='output', stict_mode=True):
# filename = os.path.basename(filename)
# fullpath_filename = os.path.abspath(output_path) + os.path.sep + filename
#
# en_file = open(fullpath_filename + "_en.txt", mode="w", encoding="utf-8")
# ko_file = open(fullpath_filename + "_ko.txt", mode="w", encoding="utf-8")
# exclude_file = open(fullpath_filename + "_time-ok_sp-fail.txt", mode="w", encoding="utf-8")
# #
# # print(len(enko_smi_text))
# # print((enko_smi_text))
# en_smi_sync_time = 0
# en_smi_text = ""
# for idx in range(int(len(enko_smi_text)-1)):
#     ko_smi_sync_time = enko_smi_text[idx][0]
#     ko_smi_text = enko_smi_text[idx][1]
#
#     if en_smi_sync_time == ko_smi_sync_time:
#         # print(idx, filename)
#
#         if en_smi_text.endswith("!") and not ko_smi_text.endswith("!"):
#             ko_smi_text = ko_smi_text + "!"
#         if ko_smi_text.endswith("!") and not en_smi_text.endswith("!"):
#             en_smi_text = en_smi_text + "!"
#
#         if en_smi_text.endswith("?") and not ko_smi_text.endswith("?"):
#             ko_smi_text = ko_smi_text + "?"
#         if ko_smi_text.endswith("?") and not en_smi_text.endswith("?"):
#             en_smi_text = en_smi_text + "?"
#
#         if not en_smi_text.endswith("."):
#             en_smi_text = en_smi_text + "."
#         if not ko_smi_text.endswith("."):
#             ko_smi_text = ko_smi_text + "."
#
#         if check_special_character(en_smi_text, ko_smi_text):
#
#             # print(en_smi_text)
#             # print(ko_smi_text)
#
#             en_file.writelines(en_smi_text.strip() + os.linesep)
#             ko_file.writelines(ko_smi_text.strip() + os.linesep)
#         else:
#             exclude_file.writelines(en_smi_text.strip() + "\t\t" + ko_smi_text + os.linesep)
#
#     en_smi_sync_time = enko_smi_text[idx][0]
#     en_smi_text = enko_smi_text[idx][1]
#
# exclude_file.close()
# en_file.close()
# ko_file.close()
#
# enko_smi_text.sort()


def sync_pair_smi_text(pair_smi_dict, sync_time_option=1000, special_character_check=True):
    global count
    sync_pair_smi_text_list = []
    dictList = [[], []]
    for lang_idx, lang_code in enumerate(pair_smi_dict.keys()):
        for item_idx, item in enumerate(pair_smi_dict[lang_code]):
            dictList[lang_idx].append([item, pair_smi_dict[lang_code][item], lang_code])
    # write_enko(enko_smi_text, abs_smiPath + os.path.sep + smiItem, "./output")

    for idx, item1 in enumerate(dictList[0]):
        for idx2, item2 in enumerate(dictList[1]):
            if abs(item1[0] - item2[0]) < sync_time_option:

                if item1[1].endswith("!") and not item2[1].endswith("!"):
                    item2[1] = item2[1] + "!"
                if item2[1].endswith("!") and not item1[1].endswith("!"):
                    item1[1] = item1[1] + "!"

                if item1[1].endswith("?") and not item2[1].endswith("?"):
                    item2[1] = item2[1] + "?"
                if item2[1].endswith("?") and not item1[1].endswith("?"):
                    item1[1] = item1[1] + "?"

                if not item1[1].endswith("."):
                    item1[1] = item1[1] + "."
                if not item2[1].endswith("."):
                    item2[1] = item2[1] + "."

                if special_character_check:
                    if check_special_character(item1[1], item2[1]):
                        count = count + 1
                        sync_pair_smi_text_list.append([item1, item2])
                else:
                    count = count + 1
                    sync_pair_smi_text_list.append([item1, item2])
    return sync_pair_smi_text_list





def smi_word_tag_count(sync_pair_smi_text_list):
    count1 = Counter()
    count2 = Counter()

    for idx, item in enumerate(sync_pair_smi_text_list):
        # auto lang check True 면 Mecab Tokenizer 실행
        # auto lang check False 면 Nltk Toeknizer 실행
        word1_tag_count = word_freq.word_tag_count(item[0][1], auto_lang_check=True)
        word2_tag_count = word_freq.word_tag_count(item[1][1], auto_lang_check=True)

        count1 = count1 + word1_tag_count
        count2 = count2 + word2_tag_count

    word1_freq_list = word_freq.word_rank_list(count1)
    word2_freq_list = word_freq.word_rank_list(count2)

    return [word1_freq_list, word2_freq_list]



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("파일을 합칠 폴더를 지정하세요!")
        exit(1)

    smiPath = sys.argv[1] + os.path.sep
    abs_smiPath = os.path.abspath(smiPath)
    smiPath_list = os.listdir(smiPath)
    count = 0

    smi_text1_list = {}
    smi_text2_list = {}

    word1_counter = Counter()
    word2_counter = Counter()

    for smiItem in smiPath_list:
        if smiItem.endswith('.smi'):
            # print(abs_smiPath)
            pair_smi_list = extract_enko(abs_smiPath + os.path.sep + smiItem)
            pair_smi_dict = convert_dict_smi(pair_smi_list)
            sync_pair_smi_text_list = sync_pair_smi_text(pair_smi_dict, sync_time_option=300)

            for idx, item in enumerate(sync_pair_smi_text_list):
                count = count + 1
                print(count, idx, item)
