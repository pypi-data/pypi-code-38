import numpy
import numpy as np
import os
import pycrfsuite
from hmmlearn import hmm

numpy.random.seed(1007)






def hmm_smoothing(predictY_prob):
    np.random.seed(1007)
    model = hmm.GMMHMM(n_components=2, n_iter=40, n_mix=45)
    model.fit(predictY_prob, )
    predictY = model.predict(predictY_prob)  # 0.871955719557 #0.841328413284
    return predictY


def crf_smoothing(preValidY=None, validY=None,
                  preTestY=None, retrain=1):
    '''
    preValidY=[['no', 'yes'], ['no', 'no', 'yes']], validY=[['yes', 'yes'], ['no', 'no', 'yes']],
                  preTestY=[['no', 'yes'], ['no', 'no', 'yes']], retrain=1
    :param preValidY:
    :param validY:
    :param preTestY:
    :param retrain:
    :return:
    '''
    if preTestY is None:
        preTestY = [['no', 'yes'], ['no', 'no', 'yes']]
    if validY is None:
        validY = [['yes', 'yes'], ['no', 'no', 'yes']]
    if preValidY is None:
        preValidY = [['no', 'yes'], ['no', 'no', 'yes']]
    crf_model = 'crf.modle'
    if retrain == 1 or not os.path.isfile(crf_model):
        trainer = pycrfsuite.Trainer(verbose=False)
        for pr, va in zip(preValidY, validY):
            trainer.append(pr, va)
        trainer.set_params({'c1': 0.1, 'c2': 0.01, 'max_iterations': 2000, 'feature.possible_transitions': True})
        trainer.train(crf_model)
    tagger = pycrfsuite.Tagger()
    tagger.open('crf.model')
    crf_pre = []
    for preYseq in preTestY:
        yseq = tagger.tag(preYseq)
        crf_pre.extend(yseq)
    final = [int(item) for item in crf_pre]
    return final
