
from aitools.utils import util, constant
from aitools.core import naive_bayes_old
from aitools.data import frames


# data_metric = util.prepare_data('./../data/naive_bayes', constant.LABEL_LABEL)
data_metric = frames.NAIVE_BAYES_TEXT_CLASSIFIER
nb = naive_bayes_old.NaiveBayes(data_metric, constant.REGEX_ALL_SPECIAL_ALPHA_NUMERIC)
nb.build()

speech = 'I would like to eat sandwich'
x = nb.predict(speech)
#print(x)
