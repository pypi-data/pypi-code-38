import argparse
import time

import os
from khaiii import KhaiiiApi

from SmiToText.tokenizer.nltk import nltkSentTokenizer
from SmiToText.util.util import Util

'''
카카오 한글 형태소 분석기를 이용한 명사 추출기

'''

util = Util()


def kakao_postagger_nn_finder(summay_text):
    api = KhaiiiApi()
    api.open()
    nn_word_list = []
    for word in api.analyze(summay_text):
        morphs_str = ' + '.join([(m.lex + '/' + m.tag) for m in word.morphs])
        # print(f'{word.lex}\t{morphs_str}')

        morphs_str_list = morphs_str.split(" + ")

        complex_morphs = ""
        for mophs_item in morphs_str_list:
            if mophs_item.split("/")[1].startswith("N") or mophs_item.split("/")[1].startswith("MM") or \
                    mophs_item.split("/")[1].startswith("SN") or mophs_item.split("/")[1].startswith("SL"):
                complex_morphs = complex_morphs + mophs_item.split("/")[0]

        if len(complex_morphs) > 1:
            # print("->", complex_morphs)
            nn_word_list.append(complex_morphs)

    return nn_word_list


def extract_file_noun(input, output, time_interval=0):
    input_file = open(input, mode='r', encoding='utf-8')
    open(output, mode='w', encoding='utf-8')
    output_file = open(output, mode='a', encoding='utf-8')
    line_number = 1
    while (True):
        line = input_file.readline()
        if not line:
            break;

        line = line.strip()
        line = util.remove_naver_news(line)
        line = util.normalize(line)

        for line_array in line.split("\n"):
            sentences = nltkSentTokenizer(line_array)

            sentence_words = []
            for sent in sentences:

                word_list = kakao_postagger_nn_finder(sent)

                if len(word_list):
                    for word in word_list:
                        if util.check_email(word) or util.is_int(word) or util.is_alpha(word):
                            continue
                        else:
                            output_file.write(word + os.linesep)
                            sentence_words.append(word)
                            # print(line_number, word)
        time.sleep(time_interval)
        print(line_number, sentence_words)
        line_number += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Extract File Noun word")
    parser.add_argument('--input', type=str, required=True, default='', help='Input File')
    parser.add_argument('--output', type=str, required=True, default='', help='Output File')
    parser.add_argument('--interval', type=str, required=False, default='0', help='Time Interval')
    args = parser.parse_args()

    if not args.input:
        print("input file is invalid!")
        exit(1)

    if not args.output:
        print("output file is invalid!")
        exit(1)

    input = str(args.input)
    output = str(args.output)
    time_interval = float(args.interval)

    extract_file_noun(input, output, time_interval)
