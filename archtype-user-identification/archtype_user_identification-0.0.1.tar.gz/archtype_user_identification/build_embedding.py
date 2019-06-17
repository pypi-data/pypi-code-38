import wget
import gzip
from gensim.models.keyedvectors import KeyedVectors

url = 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.vec.gz'
filename = wget.download(url)

f = gzip.open(wget.download(url), 'rb')
model = KeyedVectors.load_word2vec_format(f.read(), binary=False)
model.save_word2vec_format('wiki.el.txt', binary=False)
f.close()