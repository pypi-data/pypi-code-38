from __future__ import print_function

from aitools.core import n_gram as ng
from aitools.utils import constant

# Reading the dummy data
n_gram_data_raw = open('../data/n_gram', encoding="utf8")
n_gram_data = n_gram_data_raw.read()

# Initializing and Building N Gram
n_grams = ng.NGram(n_gram_data, 5, constant.REGEX_ALL_SPECIAL_ALPHA_NUMERIC)
n_grams.build()

# Using N Gram for text generation
y = n_grams.predict(100000)
print_function(y)

# Using N Gram for Next word prediction
words = 'and even face detection an'
y = n_grams.predict(words)
print_function(y)
