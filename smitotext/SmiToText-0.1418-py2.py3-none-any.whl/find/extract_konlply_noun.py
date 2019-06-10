# -*- coding: utf-8 -*-
import re

from jpype import unicode
from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Komoran
from konlpy.tag import Okt

from SmiToText.tokenizer import mecab


''' 
코모란 꼬꼬마, 트위터를 이용한 명사 추출기

'''
class extractNoun(object):

    def __init__(self):
        pass

    def findKoNoun(self, sentence, detail=False ):
        nounSet = set([])

        hannanum = Hannanum()
        # print(hannanum.analyze(sentence))
        hannanumNoun = hannanum.nouns(sentence)
        nounSet.update(hannanumNoun)
        #
        if detail == True :
            kkma = Kkma()
            # print(kkma.analyze(sentence))
            kkmaNoun = kkma.nouns(sentence)
            nounSet.update(kkmaNoun)

            komoran = Komoran()
            # print(komoran.analyze(sentence))
            komaranNoun = komoran.nouns(sentence)
            nounSet.update(komaranNoun)

            twitter = Okt()
            # print(twitter.analyze(sentence))
            twitterNoun = twitter.nouns(sentence)
            nounSet.update(twitterNoun)

        mecabSentence = mecab.nouns(sentence)
        mecabSentence = mecabSentence.split(" ")
        mecabSentence = [n for n in mecabSentence if len(n) > 0]
        nounSet.update(mecabSentence)

        norm_noun = []
        exception_noun = []

        for nounItem in nounSet:
            if len(nounItem) > 1:
                numList = re.findall(r'\d+', nounItem)
                if len(numList) == 0:
                    nounItem = nounItem.replace("]", "\n")
                    nounItem = nounItem.replace("[", "\n")
                    nounItem = nounItem.replace("(", "\n")
                    nounItem = nounItem.replace(")", "\n")
                    nounItem = nounItem.replace("ㆍ", "\n")
                    nounItem = nounItem.replace("·", "\n")
                    nounItem = nounItem.replace("「", "\n")
                    nounItem = nounItem.replace("」", "\n")
                    nounItem = nounItem.replace(",", "\n")
                    nounItem = nounItem.replace(":", "\n")
                    nounItem = nounItem.replace(";", "\n")
                    nounItem = nounItem.replace(".", "\n")
                    nounItem = nounItem.replace("\"", "\n")
                    nounItem = nounItem.replace("”", "\n")
                    nounItem = nounItem.replace("“", "\n")
                    nounItem = nounItem.replace("'", "\n")



                    nounItemList = nounItem.split("\n")

                    for item in nounItemList:
                        if len(item) > 1:
                            removejosa = ["은", "는",
                                          #"이",
                                          #"가",
                                          #"리노",
                                          "을", "를", "의", "또한", "에", "에게", "등", "거나", "하다", "자로",
                                          "이하", "관이", "했", "이다", "렸다","렸", "으로",  "함께", "한다고", "디뎠", "밝혔" ,"에서"]

                            # if not str(item).endswith(tuple(removejosa)):
                            if not str(item).endswith(tuple(removejosa)):
                                norm_noun.append(item)
                            else:
                                exception_noun.append(item)

        return_noun = [norm_noun, exception_noun]
        return return_noun


if __name__ == '__main__':
    extractnoun = extractNoun()


    while True:
        try:
            inputText = input("\n\n문장을 입력하세요?: \n")
            inputText = unicode(inputText)
        except UnicodeDecodeError:
            print("다시 입력하세요\n")
            continue

        if inputText == 'exit':
            exit(1)
        print(extractnoun.findKoNoun(inputText))

