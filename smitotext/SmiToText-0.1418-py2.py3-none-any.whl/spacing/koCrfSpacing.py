from __future__ import unicode_literals, print_function

import codecs
import re

import pycrfsuite

from SmiToText.util.util import Util


class koCrfSpacing(object):

    def __init__(self):
        self.util = Util()

    def raw2corpus(self, raw_path, corpus_path):
        raw = codecs.open(raw_path, encoding='utf-8')
        raw_sentences = raw.read().split('\n')
        corpus = codecs.open(corpus_path, 'w', encoding='utf-8')
        sentences = []
        for raw_sentence in raw_sentences:
            if not raw_sentence:
                continue
            text = re.sub(r'(\ )+', ' ', raw_sentence).strip()
            taggeds = []
            for i in range(len(text)):
                if i == 0:
                    taggeds.append('{}/B'.format(text[i]))
                elif text[i] != ' ':
                    successor = text[i - 1]
                    if successor == ' ':
                        taggeds.append('{}/B'.format(text[i]))
                    else:
                        taggeds.append('{}/I'.format(text[i]))
            sentences.append(' '.join(taggeds))
        corpus.write('\n'.join(sentences))

    def corpus2raw(self, corpus_path, raw_path):
        corpus = codecs.open(corpus_path, encoding='utf-8')
        corpus_sentences = corpus.read().split('\n')
        raw = codecs.open(raw_path, 'w', encoding='utf-8')
        sentences = []
        for corpus_sentence in corpus_sentences:
            taggeds = corpus_sentence.split(' ')
            text = ''
            len_taggeds = len(taggeds)
            for tagged in taggeds:
                try:
                    word, tag = tagged.split('/')
                    if word and tag:
                        if tag == 'B':
                            text += ' ' + word
                        else:
                            text += word
                except:
                    pass
            sentences.append(text.strip())
        raw.write('\n'.join(sentences))

    def corpus2sent(self, path):
        corpus = codecs.open(path, encoding='utf-8').read()
        raws = corpus.split('\n')
        sentences = []
        for raw in raws:
            tokens = raw.split(' ')
            sentence = []
            for token in tokens:
                try:
                    word, tag = token.split('/')
                    if word and tag:
                        sentence.append([word, tag])
                except:
                    pass
            sentences.append(sentence)
        return sentences

    def index2feature(self, sent, i, offset):
        word, tag = sent[i + offset]
        if offset < 0:
            sign = ''
        else:
            sign = '+'
        return '{}{}:word={}'.format(sign, offset, word)

    def word2features(self, sent, i):
        L = len(sent)
        word, tag = sent[i]
        features = ['bias']
        features.append(self.index2feature(sent, i, 0))
        if i > 1:
            features.append(self.index2feature(sent, i, -2))
        if i > 0:
            features.append(self.index2feature(sent, i, -1))
        else:
            features.append('bos')
        if i < L - 2:
            features.append(self.index2feature(sent, i, 2))
        if i < L - 1:
            features.append(self.index2feature(sent, i, 1))
        else:
            features.append('eos')
        return features

    def sent2words(self, sent):
        return [word for word, tag in sent]

    def sent2tags(self, sent):
        return [tag for word, tag in sent]

    def sent2features(self, sent):
        return [self.word2features(sent, i) for i in range(len(sent))]





if __name__ == '__main__':
    util = Util()

    rootDirPath = util.getRootPath('SmiToText.SmiToText')

    koSpaceCheck = koCrfSpacing()

    #### 학습
    koSpaceCheck.raw2corpus(rootDirPath + '/data/koDetokenizerData/ko_law_common_space.txt', rootDirPath + '/data/koDetokenizerData/ko_law_common_space.txt.copus')
    koSpaceCheck.raw2corpus(rootDirPath + '/data/koDetokenizerData/kospacing_Train.txt', rootDirPath + '/data/koDetokenizerData/kospacing_Train.txt.copus')
    # raw_train.txt에 뭔가 긴 글이 있음


    train_sents = koSpaceCheck.corpus2sent(rootDirPath + '/data/koDetokenizerData/ko_law_common_space.txt.copus')
    test_sents = koSpaceCheck.corpus2sent(rootDirPath + '/data/koDetokenizerData/kospacing_Train.txt.copus')
    train_x = [koSpaceCheck.sent2features(sent) for sent in train_sents]

    train_y = [koSpaceCheck.sent2tags(sent) for sent in train_sents]

    test_x = [koSpaceCheck.sent2features(sent) for sent in test_sents]
    test_y = [koSpaceCheck.sent2tags(sent) for sent in test_sents]
    trainer = pycrfsuite.Trainer()
    for x, y in zip(train_x, train_y):  # 파이썬2에서 돌렸다
        trainer.append(x, y)
    trainer.train(rootDirPath + '/kocrf-models/koCrfSpacing.crfsuite')


    ## 모델 로드
    tagger = pycrfsuite.Tagger()
    tagger.open(rootDirPath + '/kocrf-models/koCrfSpacing.crfsuite')

    x = "이것도괜찬고"

    print(tagger.tag(x))

    sentence = ""
    for idx, item in enumerate(tagger.tag(x)):
        if item == "B" :
            sentence += " "

        sentence += x[idx]

    print(sentence)