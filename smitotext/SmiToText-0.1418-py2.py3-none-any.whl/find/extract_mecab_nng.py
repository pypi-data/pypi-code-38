import argparse
import os
from nltk.tokenize import sent_tokenize

from SmiToText.tokenizer.nltk import nltkSentTokenizer
from SmiToText.util.util import Util
from SmiToText.tokenizer import mecab


''' 
Mecab 을 이용한 명사 추출기 
Pos tagger 이용

'''

util = Util()


def expect_nng_text(text):
    nng_list = []
    vv_list = []

    replace_char_list = ['[', ']', '\'', '\"', ')', '(', '「', '」', '-',
                         '’', ':', '/', '”', '“', '〃',
                         '~', '-', 'ㆍ', '○', '◇', '△', '〈', '〉',
                         '·', '+', '…', '#', '=']

    check_word_end = [',', '.', ':', ';', '!', '?', '\"', '\'']

    check_vv = ['EC', 'VV', 'X', 'ETN', 'ETM', 'EF', ]

    check_skip = ['MAG']

    end_josa_list = [

        '처럼',
        '했고', '고',
        '하게',
        '된',
        '보다',
        '당한', '한',
        '하기',
        '하던',
        '이라는',
        '로부터는', '로부터',
        '에서는', '에서', '에는',
        '은', '하는', '는',
        '하면',
        '이다',
        '이라',
        '이', '가', '께서', '에서', '서',
        '을', '를',
        '이', '가',
        '의',
        '에도',
        '되지만',
        '에게서', '에게', '에', '에서', '한테', '으로', '로', '와', '과',
        '아', '야',
    ]

    exception_list = [
        '무허가',
    ]

    sent_tokenize_list = sent_tokenize(text)

    for sentence in sent_tokenize_list:

        sentence = sentence.strip()

        for item in replace_char_list:
            sentence = sentence.replace(item, ' ')

        for word in sentence.split(' '):
            if word.endswith(tuple(check_word_end)):
                word = word[:len(word) - 1]

            if word in exception_list:
                nng_list.append(word)
            else:
                if len(word) >= 2:
                    if str(word).endswith(tuple(end_josa_list)):
                        for josa in end_josa_list:
                            if str(word).endswith(josa):
                                word = util.rreplace(word, josa, '', 1)
                                break;
                        if len(word) >= 2:
                            if any([vv for vv in check_vv if vv in str(check_vv)]):
                                nng_list.append(word.strip())
                            else:
                                nng_list.append(word.strip())
                            # print(word.strip())
                    else:
                        if len(word) >= 2:
                            if any([vv for vv in check_vv if vv in str(check_vv)]):
                                nng_list.append(word.strip())
                            else:
                                nng_list.append(word.strip())

    print(vv_list)
    return nng_list


def extract_file_noun(input, output):
    input_file = open(input, mode='r', encoding='utf-8')
    open(output, mode='w', encoding='utf-8')
    output_file = open(output, mode='a', encoding='utf-8')
    line_number = 1
    while (True):
        line = input_file.readline()
        if not line:
            break;

        line = line.strip()

        for line_array in line.split("\n"):
            sentences = nltkSentTokenizer(line_array)

            sentence_words = []
            for sent in sentences:

                word_list = expect_nng_text(sent)

                if len(word_list):
                    for word in word_list:
                        if util.check_email(word) or util.is_int(word) or util.is_alpha(word):
                            continue
                        else:
                            output_file.write(word + os.linesep)
                            sentence_words.append(word)
                            # print(line_number, word)
        print(line_number, sentence_words)
        line_number += 1




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract File Noun word")
    parser.add_argument('--input', type=str, required=True, default='', help='Input File')
    parser.add_argument('--output', type=str, required=True, default='', help='Output File')
    args = parser.parse_args()

    if not args.input:
        print("input file is invalid!")
        exit(1)

    if not args.output:
        print("output file is invalid!")
        exit(1)

    input = str(args.input)
    output = str(args.output)

    extract_file_noun(input, output)
