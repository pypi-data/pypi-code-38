import os
import pprint

import pycrfsuite

from SmiToText.spacing.koPyCrfsuitSpacingUtil import CharacterFeatureTransformer
from SmiToText.spacing.koPyCrfsuitSpacingUtil import Sentence
from SmiToText.spacing.koPyCrfsuitSpacingUtil import TemplateGenerator
from SmiToText.util.util import Util


class koPyCrfsuitSpacing(object):
    def __init__(self, to_feature, tagger=None, verbose=False,
                 feature_vocabulary=None,
                 feature_minfreq=0, max_iterations=100, l1_cost=0, l2_cost=1.0):
        self.sentence = Sentence()
        self.tagger = tagger
        self.to_feature = to_feature
        self.verbose = verbose
        self.feature_vocabulary = feature_vocabulary
        self.params = {'feature.minfreq': max(0, feature_minfreq),
                       'max_iterations': max(1, max_iterations),
                       'c1': max(0, l1_cost),
                       'c2': max(0, l2_cost)
                       }


        if type(tagger) == 'str':
            try:
                self.load_tagger(tagger)
            except Exception as e:
                print(e)
                self.tagger = None

    def __call__(self, sent):
        return self.correct(sent)

    def train_file_load(self, file_name):
        train_dataset = []

        with open(file_name, encoding='utf-8') as f:
            for num_doc, doc in enumerate(f):

                doc = doc.replace('\n', '')
                doc = doc.replace('  ', ' ')
                train_dataset.append(doc)
                if num_doc % 100 == 9 :
                    print("Train File's",num_doc,"line Read.")
                if not doc:
                    continue


        return train_dataset

    def train(self, setences, model_fname):
        if not self.feature_vocabulary:
            self.feature_vocabulary = self._scan_features(setences)
        trainer = pycrfsuite.Trainer(verbose=self.verbose)
        if self.verbose:
            print('begin appending data to trainer')
        for sent in setences:
            x, y = self.sentence.sent_to_xy(sent, self.to_feature)
            x = [[xij for xij in xi if xij in self.feature_vocabulary] for xi in x]
            trainer.append(x, y)
        if self.verbose:
            print('all data are appended to trainer. begin training')
        trainer.set_params(self.params)
        trainer.train(model_fname)
        self.load_tagger(model_fname)

    def _scan_features(self, docs):
        from collections import defaultdict
        min_count = self.params['feature.minfreq']

        feature_vocabulary = defaultdict(int)
        if self.verbose:
            print('feature scanning: begin with min_count={}'.format(min_count))

        for sent in docs:
            x, _ = sentence.sent_to_xy(sent, self.to_feature)
            for xi in x:
                for xij in xi:
                    feature_vocabulary[xij] += 1
        if self.verbose:
            print('feature scanning ... {} -> '.format(len(feature_vocabulary)), end='')

        feature_vocabulary = {feature for feature, count in feature_vocabulary.items() if count >= min_count}
        if self.verbose:
            print('{} with min_count={}'.format(len(feature_vocabulary), min_count))

        return feature_vocabulary

    def load_tagger(self, model_fname):
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(model_fname)

    def correct(self, sent):
        x, y0 = self.sentence.sent_to_xy(sent, self.to_feature)
        y1 = []

        b = 0
        for i in range(len(x)):
            if y0[i] == '1':
                y1 += self.tagger.tag(x[b:i + 1])[:-1] + ['1']
                b = i + 1
        return ''.join([ci if yi == '0' else ci + ' ' for ci, yi in zip(sent.replace(' ', ''), y1)]).strip()



if __name__ == '__main__':
    util = Util()

    rootDirPath = util.getRootPath('SmiToText.SmiToText')

    print(rootDirPath)

    to_feature = CharacterFeatureTransformer(TemplateGenerator(begin=-2,
                                                               end=2,
                                                               min_range_length=3,
                                                               max_range_length=3))

    sentence = Sentence()
    x, y = sentence.sent_to_xy('이것도 너프해 보시지', to_feature)
    pprint.pprint(x)
    print(y)

    train_dataset_fname = rootDirPath + os.path.sep + 'data'+ os.path.sep + 'koDetokenizerData'+ os.path.sep + 'ko_law_common_space.txt'
    # train_dataset_fname = rootDirPath + os.path.sep + 'data'+ os.path.sep + 'koDetokenizerData'+ os.path.sep + '일본어교재+FTA.txt'
    model_fname = rootDirPath + os.path.sep + "koPyCrfsuit-models" + os.path.sep + "koPyCrfsuit_model.model"

    correct = koPyCrfsuitSpacing(to_feature)

    sentences = correct.train_file_load(train_dataset_fname)
    correct.train(sentences, model_fname)

    correct.load_tagger(model_fname)
    sent = 'DAB는, 결정과 관련한 각 위원들의 모든 일당 수수료와 경비에 대한 청구금액이 완전하게 지급될 때 까지는, 결정문을 발급할 의무를 갖지 아니한다.'
    sent_input = sent.replace(" ", "")

    sent_output = correct(sent_input)

    print(sent)
    print(sent_output)


    sent = '이것도 너프해 보시지'
    sent_input = sent.replace(" ", "")

    sent_output = correct(sent_input)

    print(sent)
    print(sent_output)