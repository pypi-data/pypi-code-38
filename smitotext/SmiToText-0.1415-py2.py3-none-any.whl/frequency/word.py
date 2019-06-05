from collections import Counter

from jpype import unicode
from langdetect import detect

from SmiToText.tokenizer import mecab
from SmiToText.tokenizer import nltk


def nltk_word_tags(text):
    nltkSentence = nltk.nltkTokenizer(text)
    nltkSentence = nltkSentence.split(" ")
    nltkSentence = [n for n in nltkSentence if len(n) > 0]
    count = Counter(nltkSentence)
    return count


def mecab_word_tags(text):
    mecabSentence = mecab.mecabTokenizer(text)
    mecabSentence = mecabSentence.split(" ")
    mecabSentence = [n for n in mecabSentence if len(n) > 0]
    count = Counter(mecabSentence)
    return count


def word_rank_list(countText):

    return_list = []  # 명사 빈도수 저장할 변수
    for n, c in countText.most_common():
        temp = {'tag': n, 'count': c}
        return_list.append(temp)
    # most_common 메소드는 정수를 입력받아 객체 안의 명사중 빈도수
    # 큰 명사부터 순서대로 입력받은 정수 갯수만큼 저장되어있는 객체 반환
    # 명사와 사용된 갯수를 return_list에 저장합니다.
    return return_list


def word_tag_count(text, auto_lang_check=True):
    if auto_lang_check == True:
        try:
            lang = detect(text)

            if lang == "en" or lang == "no":
                word_count = nltk_word_tags(text)
            elif lang == "ko":
                word_count = mecab_word_tags(text)
            else:
                word_count = nltk_word_tags(text)
        except:
            word_count = nltk_word_tags(text)
    else:
        word_count = nltk_word_tags(text)

    return word_count


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

        countText = mecab_word_tags(inputText)
        print(countText)
        print(word_rank_list(countText))