class TextProcessor:

    def __init__(self, lemmatizer = 'nltk', stopwords = 'default', punctuation = 'default', contractions = 'default', substitutions = 'default'):
        '''
        :param corpus:  list of sentences to process
        :param lemmatizer:  Function to lemmatize words.  If None, no lemmatizer used.  If 'nltk', uses nltk WordNetLemmatizer.
            if 'spaCy en', uses the spaCy English lemmatizer.  If anything else, treats as function mapping a word to it's
            lemmatized form.
        :param stopwords: a simple set of words to remove
        :param punctuation: a set of punctuation to remove
        :param contractions: a dictionary of contractions to make.  Example is {"can't": "can not", "n't": not, ...}
        :param substitution:   similar to contractions but for grouping words together.  Example {'i': 'me', 'my': 'me', etc.}
        '''

        if lemmatizer == 'nltk':
            from nltk import WordNetLemmatizer
            self.lemmatizer = WordNetLemmatizer()
            self.default_lem = 'nltk'
            from nltk.corpus import wordnet
            self.wordnet = wordnet
        elif lemmatizer == 'spaCy en':
            import spacy
            self.spacy = spacy.load('en', disable=['parser', 'ner'])
            self.lemmatizer = self.identity
            self.default_lem = 'spaCy'
        elif not lemmatizer:
            self.default_lem = False
            self.lemmatizer = self.identity
        else:
            self.default_lem = False
            self.lemmatizer = lemmatizer

        if substitutions == 'default':
            self.substitutions = {}
        else:
            self.substitutions = substitutions

        if stopwords == 'default':
            self.stopwords = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about',
              'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be',
              'some', 'for', 'do', 'its', 'your', 'such', 'into', 'of', 'most', 'itself',
              'other', 'off', 'is', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the',
              'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through',
              'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our',
              'their', 'while', 'above', 'both', 'up', 'to', 'had', 'she',
              'when', 'at', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will',
              'on', 'does', 'yourselve', 'then', 'that', 'because', 'what', 'over', 'why', 'so',
              'can', 'did', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where',
              'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 'being',
              'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was',
              'here', 'than', 'pron'}
        elif stopwords == 'none':
            self.stopwords = {}
        else:
            self.stopwords = stopwords

        if contractions == 'default':
            self.contractions = {"can't": "can not", "won't": "will not", "n't": " not",
             "'ve": " have", "'m": " am", "'s": "", "'d": " had", '-': ' '}
        elif contractions == 'none':
            self.contracts = {}
        else:
            self.contractions = contractions

        if punctuation == 'default':
            self.punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        elif punctuation == 'none':
            self.punctuation = ''
        else:
            self.punctuation = punctuation

    def identity(self, word):
        return word

    def lemmatize(self, word):
        '''
        Lemmatizes a word based on the given lemmatizer
        :param word: Word to lemmatize
        :return: Lemmatized word
        '''
        if self.default_lem == 'nltk':
            POS = [self.wordnet.ADJ, self.wordnet.VERB, self.wordnet.NOUN, self.wordnet.ADV]
            im_just_guessing_here = [self.lemmatizer.lemmatize(word, x) for x in POS]

            lemmatized_word = max(set(im_just_guessing_here),
                                  key=im_just_guessing_here.count)
        else:
            lemmatized_word = self.lemmatizer(word)

        return lemmatized_word

    def transform(self, corpus, combined_strings=False, return_length=False, verbose=False):
        '''
        Processes entire corpus in accordance with defined when instantiating object
        :param corpus: DataFrame, list, or array of strings (docs)
        :param combined_strings: If False, return sentences split into words in a list.  If true, returns complete
            sentences as strings
        :param return_length: True to return length of largest doc with processed text
        :param verbose: True to get updated on progress of transformation
        :return:
        '''
        try:
            corpus = corpus.tolist()
        except:
            corpus = corpus

        if verbose:
            import tqdm
            if not combined_strings:
                max_length = 0
                combined = []
                for x in tqdm.tqdm(corpus):
                    if len(self.filter(x))>max_length:
                        max_length=len(self.filter(x))
                    combined.append(self.filter(x))
                if return_length:
                    return combined, max_length
                else:
                    return combined
            else:
                max_length = 0
                combined = []
                for x in tqdm.tqdm(corpus):
                    if len(self.filter(x)) > max_length:
                        max_length = len(self.filter(x))
                    combined.append(' '.join(self.filter(x)))
                if return_length:
                    return combined, max_length
                else:
                    return combined
        elif not combined_strings:
            max_length = 0
            combined = []
            for x in corpus:
                if len(self.filter(x)) > max_length:
                    max_length = len(self.filter(x))
                combined.append(self.filter(x))
            if return_length:
                return combined, max_length
            else:
                return combined
        else:
            max_length = 0
            combined = []
            for x in corpus:
                if len(self.filter(x)) > max_length:
                    max_length = len(self.filter(x))
                combined.append(' '.join(self.filter(x)))
            if return_length:
                return combined, max_length
            else:
                return combined

    def filter(self, input_string, return_list = True):
        '''
        Applies all defined rules to a given sentence
        :param input_string: Sentence to process
        :param return_list: If True, return as list of words.  If false, return as string
        :return: Processed string
        '''
        from re import sub
        new_list = []

        if self.default_lem == 'spaCy':
            spacy_string = self.spacy(input_string)
            input_string = [x.lemma_ for x in spacy_string]

        if type(input_string) == str:
            input_string = input_string.lower()
            for key in self.contractions:
                input_string = input_string.replace(key, self.contractions[key])
            for key in self.substitutions:
                input_string = input_string.replace(key, self.substitutions[key])
            input_string = sub('[' + self.punctuation + ']', '', input_string)
            pro_text = input_string.split()

        elif type(input_string) == list:
            pro_text = []
            for s in input_string:
                s = s.lower()
                if '-' in self.punctuation:
                    s = s.replace('-', ' ')
                elif '/' in self.punctuation:
                    s = s.replace('/', ' ')
                for key in self.contractions:
                    s = s.replace(key, self.contractions[key])
                for key in self.substitutions:
                    s = s.replace(key, self.substitutions[key])
                s = sub('[' + self.punctuation + ']', '', s)
                for i in s.split():
                    i=i.replace(' ', '')
                    if i:
                        pro_text.append(i)

        for u in pro_text:
            if (not (u in self.stopwords)) and (not self.lemmatize(u).isspace()) and (self.lemmatize(u)):
                new_list.append(self.lemmatize(u))

        if return_list:
            return new_list
        else:
            return ' '.join(new_list)

    def save(self, corpus, name, labels=None, file_dir="./", encoding="utf-8", verbose=False):
        try:
            labels=labels.tolist()
        except:
            labels=labels
        save_file = file_dir+name+'.wvt'
        corpus, max_length = self.transform(corpus, combined_strings=True, return_length=True, verbose=verbose)
        corpus_size = len(corpus)
        file = open(save_file, 'w', encoding=encoding)
        if type(labels) is not None:
            file.write(name+' Y '+str(max_length)+" "+str(corpus_size)+"\n")
        else:
            file.write(name+' N '+str(max_length)+" "+str(corpus_size)+"\n")
        for index in range(len(corpus)):
            if type(labels) is not None:
                file.write((str(labels[index])+' '+corpus[index]+"\n"))
            else:
                file.write(corpus[index]+"\n")
        file.close()

class FastVectokenizer:

    def __init__(self, corpus, max_words=None, max_sentence_length=None, tokenize_unknown=False):
        '''
        :param corpus: The text input to be processed.  Can be either a TextProcessor object, list of sentences as lists,
            or np array of sentences as lists.
        :param test_corpus:  The test data.  Can be either a TextProcessor object, list of sentences as lists, or np array
            of sentences as lists.
        :param max_words:   The maximum number of words to use for embedding.  All words are ranked by how commmon they are
            and the top max_words words will be used.  If None, use all words.
        :param max_sentence_length:  The maximum sentence length.  Cut off sentences longer than this length.  If None
            use the length of the largest 'sentence' in the corpus
        :param tokenize_unknown:  If False, make all out of dictionary (ie out of range of maximum word count) words
            equal to empty space.  If True, will substitute 'UNKNOWN' for any out-of-dictionary words.  Vector representation
            in the word vector dictionary will be the mean of all out-of-dictionary words in the corpus.
        :param verbose:  True or False.  If True, show progress of various load and generation processes.  If False, show
            nothing.

        ******************

        :var ranked_word_list:  List of words ranked from most used to least used, cut off so that size of list equals
            max_words
        :var max_sentence_length:  Length of the longest 'sentence' in corpus if no max_sentence_length is forced when
            creating object
        :var oov_vector:  The mean of the vectors for all out-of-dictionary words (ie, words transformed to 'UNKNOWN' if
            tokenize_unknown == True.
        '''
        try:
            from keras.preprocessing.text import Tokenizer
            from keras.preprocessing.sequence import pad_sequences
        except:
            raise ValueError('FastVectokenizer requires Keras.  Please utilize the normal Vectokenizer class if Keras not installed.')

        import numpy as np
        self.np = np
        self.fast_type = True
        self.pad_sequences = pad_sequences
        self.tokenize_unknown = tokenize_unknown

        self.corpus = self.__format(corpus)

        if max_sentence_length:
            self.max_sentence_length = max_sentence_length
        else:
            self.max_sentence_length = np.max([len(x) for x in corpus])

        self.corpus_size = len(self.corpus)

        if self.tokenize_unknown:
            self.toke = Tokenizer(num_words = max_words, oov_token='__UNKNOWN__')
        else:
            self.toke = Tokenizer(num_words = max_words)

        self.toke.fit_on_texts(self.corpus)

        self.ranked_word_list = np.concatenate([[' '], (sorted(self.toke.word_index.keys(), key=self.toke.word_index.__getitem__, reverse=False))])

        if max_words:
            self.max_words = max_words
            if not self.tokenize_unknown:
                self.ranked_word_list = self.ranked_word_list[:self.max_words]
            else:
                self.ranked_word_list = self.ranked_word_list[:self.max_words+1]
        else:
            if self.tokenize_unknown == True:
                self.max_words = len(self.toke.word_index)-1
            else:
                self.max_words = len(self.toke.word_index)

        if self.tokenize_unknown:
            self.lost_words = set()
            for key in self.toke.word_index:
                if key not in self.ranked_word_list:
                    self.lost_words.add(key)
            self.oov_vec = np.average([self.query(word) for word in self.lost_words], axis=0)

    def __format(self, corpus):
        try:
            data = [doc.split() for doc in corpus]
        except:
            try:
                data = corpus.tolist()
            except:
                try:
                    data = corpus.pull(include_labels=False)
                except:
                    data = corpus
        return data

    def tokenized_word_index(self):
        '''
        :return: word vector dictionary for the corpus
        '''
        return self.toke.word_index

    def fit_integer_embedding(self):
        '''
        Fits all 'sentences' in corpus to their integer representation
        :return: all padded 'sentences' of corpus in integer embedded form
        '''
        seqs = self.toke.texts_to_sequences(self.corpus)
        return self.pad_sequences(seqs, maxlen = self.max_sentence_length)

    def transform_to_integer_embedding(self, test_corpus):
        '''
        Same as fit_integer_embedding, but converts the test corpus to integer representation.  Test corpus is only
            converted for words in the corpus integer embedding dictionary
        :return: all padded 'sentences' of test corpus in integer embedded form
        '''
        test_corpus = self.__format(test_corpus)
        seqs = self.toke.texts_to_sequences(test_corpus)
        return self.pad_sequences(seqs, maxlen = self.max_sentence_length)

    def fit_vector_dict(self, vectors):
        '''
        Generate word vector dictionary for all words on ranked word list and for out-of-dictionary word if
            tokenize_unknown == True.
        :return: dictionary mapping all words in ranked word list to it's vector representation
        '''
        dict_size = len(self.ranked_word_list[1:self.max_words])
        vect_dict = self.np.zeros((dict_size+1, vectors.dim))
        vect_dict[1:dict_size+1]=vectors.query(self.ranked_word_list[1:self.max_words])
        return vect_dict

    def to_keras(self, vectors, test_corpus=None):
        '''
        Output integer embedding and linked word vector dictionary in format suitable to use in a Keras mode.  The
            model will be trained on the integer embedding of the corpus and the word vector dictionary will be imported as
            weights of the Keras embedding layer
        :return: if text corpus input, returns a 3-tuple of (corpus integer embeddings, test corpus integer embeddings,
            word vector dictionary).  If no test corpus, returns a 2-tuple of (corpus integer embeddings, word vector dictionary)
        '''
        test_corpus = self.__format(test_corpus)
        if test_corpus:
            return self.fit_integer_embedding(), self.transform_to_integer_embedding(test_corpus), self.fit_vector_dict(vectors)
        else:
            return self.fit_integer_embedding(), self.fit_vector_dict(vectors)

    def __query(self, word, vectors, restrict_search = False):
        '''
        Look up word vector representation of a word
        :param word: word to return vector representation of
        :param restrict_search: if True, only return for words in ranked word list.  Default to False as one of the major
            benefits of using pretrained words is that you can reference them for words in the test set that are not in the
            training set
        :return: word vector representation of 'word'
        '''
        if self.tokenize_unknown and (word == 'UNKNOWN'):
            return self.oov_vec
        elif restrict_search and (word in self.ranked_word_list[1:]):
            return vectors.query(word)
        elif not restrict_search:
            return vectors.query(word)
        else:
            return self.np.zeros(vectors.dim)

class VectorDictionary:
    '''
    Creates searchable dictionary of all word/vector pairs in given .txt file.  Designed to allow GLoVe embeddings
    without using pymagnitude library
    '''
    def __init__(self, file_dir, encoding="utf-8", verbose = False):
        '''
        :param file_dir: file directory of embedding dictionary
        :param encoding: file encoding
        :param verbose: True to see updates on loading dictionary

        :var vector_dict:  dictionary of all word/vector pairs in input .txt file
        :var vector_dim:  size of vector representations
        :var size:  number of words total in dictionary
        '''
        self.vector_dict, self.size, self.dim, self.oov_vector = self.__load_dict(file_dir, encoding=encoding, verbose=verbose)

    def __load_dict(self, file_dir, oov_vector=None, encoding="utf-8", verbose=False):
        '''
        Loads in all word/vector pairs from .txt file
        :param file_dir: directory of .txt file
        :param encoding: encoding of .txt file
        :param verbose: if True, reports progress of loading dictionary
        :return: Nothing.  Update internal variables
        '''
        if verbose:
            import tqdm

        file = open(file_dir, 'r+', encoding=encoding)
        lines = file.readlines()
        file.close()
        vector_dict={}
        if verbose:
            for line in tqdm.tqdm(lines):
                components = line.split(' ')
                vector_dict[components[0]] = [float(x) for x in components[1:]]
        else:
            for line in lines:
                components = line.split(' ')
                vector_dict[components[0]] = [float(x) for x in components[1:]]

        size = len(vector_dict)
        dim = len(vector_dict['test'])
        if not oov_vector:
            oov_vector=[0.00]*dim
        return vector_dict, size, dim, oov_vector

    def __query(self, word):
        '''
        Search word/vector pairs for vector representation of specific word
        :param word: word to find vector representation of
        :param return_empty: vector to return if word not found in dictionary.  If None, returns the 0-vector
        :return: vector representation of input word
        '''
        try:
            return self.vector_dict[word]
        except:
            return self.oov_vector

    def query(self, word_list):
        if type(word_list) == str:
            return self.__query(word_list)
        else:
            size = len(word_list)
            import numpy as np
            embedding = np.zeros((size, self.dim))
            for index in range(size):
                embedding[index] = self.__query(word_list[index])
            return embedding

class VectorEmbedder:

    def __init__(self):
        """
        Converts a corpus (dataframe or list of docs--which are themselves lists of words) into vector embedded form
        """

    def __format(self, corpus):
        import numpy as np
        try:
            data = [doc.split() for doc in corpus]
        except:
            try:
                data = corpus.tolist()
            except:
                try:
                    data = corpus.pull(include_labels=False)
                except:
                    data = corpus
        try:
            max_sentence_length = data.max_length
        except:
            max_sentence_length = np.max([len(x) for x in data])
        return data, max_sentence_length

    def __embed_doc(self, doc, vectors, max_length, pad_first=False):
        """
        Converts a single document to a matrix embedding

        :param doc: doc to embed
        :param vectors: vectors to use as embeddings.  Can be either a pymagnitude.Magnitude object or VectorDictionary object
        :param max_length:  Maximum number of words allowed per doc
        :return: array of size (max_length, vector_dims)
        """
        import numpy as np
        doc_size = len(doc)
        embedding = np.zeros((max_length, vectors.dim), dtype=float)
        if not pad_first:
            embedding[:doc_size] = vectors.query(doc[:max_length])
        else:
            embedding[-doc_size:] = vectors.query(doc[:max_length])
        return embedding


    def fit(self, corpus, vectors, max_length=None, pad_first=False, save_file=None, verbose=False):
        """

        :param corpus: dataframe or list of docs
        :param max_length: integer length setting the maximum allowable doc length
        :param vectors:  vectors to use for embedding.  Can be a pymagnitude.Magnitude object or a wordvecpy.VectorDictionary object
        :param pad_first: True to put empty space at top of embedding or False to put it at end of embedding
        :param save_file: String, file directory and name to save embeddeding array as .npy
        :param verbose: True to update on progress

        :return: vectorized embedding for entire corpus, array of size (number of docs, max_length, vector_dims).
        """
        import numpy as np

        corpus, max_size = self.__format(corpus)
        if not max_length:
            max_length=max_size
        corpus_size = len(corpus)
        embedding = np.zeros((corpus_size, max_length, vectors.dim), dtype=float)

        if verbose:
            import tqdm
            for doc_index in tqdm.tqdm(range(corpus_size)):
                embedding[doc_index] = self.__embed_doc(corpus[doc_index], vectors, max_length, pad_first)
        else:
            for doc_index in range(corpus_size):
                embedding[doc_index] = self.__embed_doc(corpus[doc_index], vectors, max_length, pad_first)

        if save_file:
            np.save(save_file+'.wve', embedding)

        return embedding

    def load(self, file_dir):
        import numpy as np
        if file_dir[-4:]!='.wve':
            file_dir+='.wve'
        return np.load(file_dir+'.npy')

class ImportCorpus:

    def __init__(self, input_file, encoding="utf-8"):
        self.input_file = input_file
        if self.input_file[-4:]!='.wvt':
            self.input_file+='.wvt'
        self.encoding = encoding
        self.name, self.has_labels, self.max_length, self.corpus_size = self.__read_header()

    def __read_header(self):
        file = open(self.input_file, 'r', encoding=self.encoding)
        header = file.readline().split()
        file.close()
        if header[1]=='Y':
            has_labels=True
        else:
            has_labels=False
        return header[0], has_labels, int(header[2]), int(header[3])

    def pull(self, min_row=None, max_row=None, include_labels=True, convert_labels=True):
        if not max_row and not min_row:
            min_row=0
            max_row=self.corpus_size
        elif (not min_row) and max_row:
            min_row=0
        elif (not max_row) and min_row:
            max_row = min_row
        if max_row > self.corpus_size:
            max_row = self.corpus_size
        if include_labels:
            include_labels=self.has_labels
        corpus_chunk = []
        label_chunk = []
        file = open(self.input_file, 'r', encoding=self.encoding)
        file.readline()
        for index in range(max_row):
            doc, label = self.__quick_read(file.readline(), include_labels, convert_labels=convert_labels)
            if min_row <= index:
                corpus_chunk.append(doc)
                label_chunk.append(label)
        file.close()
        if include_labels:
            return corpus_chunk, label_chunk
        else:
            return corpus_chunk

    def __quick_read(self, line, labels=False, convert_labels=True):
        line=line.split()
        if labels:
            if convert_labels:
                try:
                    label=float(line[0])
                    if int(label)==label:
                        label=int(label)
                except:
                    label=line[0]
            else:
                label=line[0]
            return line[1:], label
        else:
            if not self.has_labels:
                return line, None
            else:
                return line[1:], None

class Chunkifier:

    def __init__(self, cycle=True, preprocess_directory=None, pad_first=False):
        '''
        Class which splits a text corpus into chunks and generates embeddings for each chunk.  Mainly to get around memory issues,
        since vector embeddings for a single document can be very large, and vector embeddings for a corpus of documents
        may not fit into memory at once.

        :param cycle: If True, indices greater than the total number of chunks will be wrapped around modulo the number of chunks.
            If False, trying to use an index greater than total number of chunks will return None.
        :param preprocess_directory: Directory to save preprocessed embeddings to.  Needed if you plan on preprocessing embeddings.
            If generating embeddings in real-time, no directory needed
        :param pad_first: True to pad zeros at front of embeddings, False to pad them at end.
        '''
        self.cycle=cycle
        self.file_dir = preprocess_directory
        if (self.file_dir) and (self.file_dir[-1] != '/'):
            self.file_dir += '/'
        self.pad_first = pad_first

    def __initialize_variables(self):
        self.chunk_size = 1
        self.corpus_size = 0
        self.precomputed = False
        self.num_chunks = 1
        self.max_length = 1
        self.local = True
        self.corpus = None
        self.vectors = None
        self.dim = 0
        self.name = None
        self.current_chunk = None
        self.current_index = 0
        self.chunk_labels = None
        self.labels = None
        self.has_labels=False

    def __index_wrap(self, chunk_index):
        if self.cycle:
            return chunk_index%self.num_chunks
        elif chunk_index<self.num_chunks:
            return chunk_index
        else:
            return None

    def __chunk_range(self, chunk_index):
        min = chunk_index*self.chunk_size
        max = (chunk_index+1)*self.chunk_size
        if chunk_index == self.num_chunks:
            return min, self.corpus_size
        elif chunk_index > self.num_chunks:
            if self.cycle == True:
                return self.__chunk_range(chunk_index%self.num_chunks)
            else:
                return None, None
        else:
            return min, max

    def __format(self, corpus):
        local = True
        try:
            data = [doc.split() for doc in corpus]
        except:
            try:
                data = corpus.tolist()
            except:
                data = corpus
        if type(data)!=list:
            local = False
        return data, local

    def __format_labels(self, labels):
        try:
            data = labels.tolist()
        except:
            data = labels
        return data

    def load(self, corpus, vectors, chunk_size, labels=None, name=None, convert_labels=True, max_length=None, preload=False):
        '''
        Used to load raw corpus into class.

        :param corpus: Text data to process
        :param vectors: vectors to use for embeddings
        :param chunk_size: How many documents to include in a single chunk
        :param labels: Labels for each document.  If loading with LoadCorpus object, labels are automatically detected and loaded
            if they exist
        :param name: the name of the corpus.  This is important for preprocessing and saving preprocessed embeddings
        :param convert_labels: If True, convert string labels of integers into integers
        :param max_length: max allowable size of documents.  If None, selects size of largest document.
        :param preload: Only works with LoadCorpus corpus documents.  If True, loads entire corpus into memory.  If false, only
            loads chunks as they are used
        '''
        import numpy as np
        self.__initialize_variables()
        self.vectors = vectors
        self.dim = vectors.dim
        corpus, local = self.__format(corpus)
        labels = self.__format_labels(labels)
        if local:
            corpus, corpus_size, max_possible_length = self.__load_local(corpus)
            if labels:
                self.has_labels=True
            if not name:
                name = 'temp'
        else:
            corpus, corpus_size, max_possible_length, labels, old_name = self.__load_wvp(corpus, preload=preload, convert_labels=convert_labels)
            if labels:
                self.has_labels=True
        if not max_length:
            self.max_length = max_possible_length
        else:
            self.max_length = max_length
        self.corpus = corpus
        self.corpus_size = corpus_size
        self.labels = labels
        self.local = local
        self.chunk_size = chunk_size
        self.precomputed = False
        self.num_chunks = int(np.ceil(self.corpus_size/self.chunk_size))
        if (not local) and (not name):
            self.name = old_name
        else:
            self.name = name

    def load_precomputed(self, name, return_available=False, matching_labels=True):
        self.__initialize_variables()
        self.name = name
        self.local = False
        self.precomputed = True
        chunky, labely = self.precomputed_available(name)
        self.num_chunks = len([x[0] for x in chunky if x[0]==name])
        if return_available:
            if matching_labels:
                matching = self.matching_precomputed_available(chunky, labely)
                return matching
            else:
                return chunky, labely

    def __load_local(self, corpus):
        import numpy as np
        max_possible_length = np.max([len(doc) for doc in corpus])
        corpus_size = len(corpus)
        return corpus, corpus_size, max_possible_length

    def __load_wvp(self, corpus, preload, convert_labels=True):
        if preload:
            self.local = True
            if corpus.has_labels:
                corpus, labels = corpus.pull(convert_labels=convert_labels)
            else:
                labels = None
                corpus = corpus.pull()
        else:
            self.local = False
            if corpus.has_labels:
                corpus_dummy, labels = corpus.pull(convert_labels=convert_labels)
            else:
                labels = None
        return corpus, corpus.corpus_size, corpus.max_length, labels, corpus.name

    def pull_chunk(self, chunk_index, return_labels=True):
        if self.precomputed:
            return self.load_embedding(self.name, chunk_index, return_labels=return_labels)
        min, max = self.__chunk_range(chunk_index)
        if self.local:
            if return_labels:
                return self.corpus[min:max], self.labels[min:max]
            else:
                return self.corpus[min:max]
        else:
            if return_labels:
                return self.corpus.pull(min, max, True)
            else:
                return self.corpus.pull(min, max, False)

    def fit_chunk(self, chunk_index, return_labels=True, save=False, verbose=False):
        import numpy as np
        chunk_index = self.__index_wrap(chunk_index)
        if self.precomputed:
            return self.load_embedding(self.name, chunk_index, return_labels=return_labels)
        if return_labels:
            chunk, label = self.pull_chunk(chunk_index, True)
        else:
            chunk = self.pull_chunk(chunk_index, False)
        if save:
            save_dir = self.file_dir+self.name+'___'+str(chunk_index)
            if return_labels:
                np.save(save_dir+'.wvl', label)
        else:
            save_dir = None
        embedder = VectorEmbedder()
        if return_labels and self.labels:
            return embedder.fit(chunk, self.vectors, max_length=self.max_length, pad_first=self.pad_first, save_file=save_dir, verbose=verbose), label
        else:
            return embedder.fit(chunk, self.vectors, max_length=self.max_length, pad_first=self.pad_first, save_file=save_dir, verbose=verbose)

    def preprocess_all(self, return_labels=True, verbose=False):
        self.set_current_chunk(0)
        for index in range(self.num_chunks):
            self.fit_chunk(index, return_labels=return_labels, save=True, verbose=verbose)

    def precomputed_available(self, name=None):
        '''

        :return: preprocessed embeddings available, label chunks available
        '''
        from os import listdir
        all_files = [f for f in listdir(self.file_dir)]
        wvl_files = list(filter(lambda x: x[-8:] == '.wve.npy', all_files))
        wvl_files = [x[:-8] for x in wvl_files]
        wvl_files = list(filter(lambda x: len(x.split('___'))!=len(x.split(' ')), wvl_files))
        wve_files = list(filter(lambda x: x[-8:] == '.wvl.npy', all_files))
        wve_files = [x[:-8] for x in wve_files]
        wve_files = list(filter(lambda x: len(x.split('___'))!=len(x.split(' ')), wve_files))
        wve_files = [(x.split('___')[0], int(x.split('___')[1])) for x in wve_files]
        wvl_files = [(x.split('___')[0], int(x.split('___')[1])) for x in wvl_files]
        if name:
            wve_files = list(filter(lambda x: x[0]==name, wve_files))
            wvl_files = list(filter(lambda x: x[0]==name, wvl_files))
        return wve_files, wvl_files

    def matching_precomputed_available(self, wve_files, wvl_files):
        matching = []
        for key, index in wve_files:
            if (key, index) in wvl_files:
                matching.append((key, index))
        return matching

    def load_embedding(self, name, chunk_index, return_labels=True):
        import numpy as np
        chunk_index = self.__index_wrap(chunk_index)
        wve_dir, wvl_dir = self.precomputed_available(name=name)
        if return_labels:
            matching = self.matching_precomputed_available(wve_dir, wvl_dir)
        try:
            embedding_file = self.file_dir+name+'___'+str(chunk_index)+'.wve.npy'
            embedding = np.load(embedding_file)
            if (name, chunk_index) in matching:
                try:
                    label_file = self.file_dir+name+'___'+str(chunk_index)+'.wvl.npy'
                    labels = np.load(label_file)
                except:
                    labels = None
        except:
            raise ValueError('Error with embedding name or chunk index')
        if return_labels:
            return embedding, labels
        else:
            return embedding

    def fit_iterate(self, return_labels=True, verbose=False):
        if type(self.current_index)==int:
            embedding = self.fit_chunk(self.current_index, return_labels=return_labels, verbose=verbose)
            self.current_index = self.__index_wrap(self.current_index+1)
            return embedding
        else:
            return None, None

    def set_current_chunk(self, chunk_index):
        self.current_index = self.__index_wrap(chunk_index)
        return self.current_index

class Vectokenizer:

    def __init__(self, corpus, vector_dict, test_corpus = None, max_words = None, max_sentence_length = None, tokenize_unknown = False, name  = None, verbose = False):
        '''
        :param corpus: The text input to be processed.  Can be either a TextProcessor object, list of sentences as lists,
            or np array of sentences as lists.
        :param vector_dict:  The vector dictionary to query the pretrained embeddings.  Can be a VectorDictionary object
            or a pymagnitude object
        :param test_corpus:  The test data.  Can be either a TextProcessor object, list of sentences as lists, or np array
            of sentences as lists.
        :param max_words:   The maximum number of words to use for embedding.  All words are ranked by how commmon they are
            and the top max_words words will be used.  If None, use all words.
        :param max_sentence_length:  The maximum sentence length.  Cut off sentences longer than this length.  If None
            use the length of the largest 'sentence' in the corpus
        :param tokenize_unknown:  If False, make all out of dictionary (ie out of range of maximum word count) words
            equal to empty space.  If True, will substitute 'UNKNOWN' for any out-of-dictionary words.  Vector representation
            in the word vector dictionary will be the mean of all out-of-dictionary words in the corpus.
        :param name:   String name of this vectokenizer.  Used with the VectorEmbeddedDoc class for saving slices of complete
            word vector embeddings that are too large to store in memory at one time.
        :param verbose:  True or False.  If True, show progress of various load and generation processes.  If False, show
            nothing.

        ******************

        :var vector_dim:  The size of each word vector
        :var ranked_word_list:  List of words ranked from most used to least used, cut off so that size of list equals
            max_words
        :var max_sentence_length:  Length of the longest 'sentence' in corpus if no max_sentence_length is forced when
            creating object
        :var oov_vector:  The mean of the vectors for all out-of-dictionary words (ie, words transformed to 'UNKNOWN' if
            tokenize_unknown == True.
        '''

        import numpy as np
        self.np = np

        import sys

        import tqdm
        self.tqdm = tqdm

        if not name:
            self.name = name
        else:
            self.name = 'unnamed'

        self.fast_type = False
        self.bar = ('tqdm' in sys.modules)
        self.verbose = verbose
        self.vectors = vector_dict
        self.vector_dim = len(self.vectors.query('test'))
        self.tokenize_unknown = tokenize_unknown

        if test_corpus != None:
            try:
                self.test_corpus = self.test_corpus.transform()
            except:
                self.test_corpus = test_corpus
        else:
            self.test_corpus = None

        try:
            self.corpus = corpus.transform()
        except:
            self.corpus = corpus

        if not max_sentence_length:
            self.longest_sentence = np.max([len(x) for x in self.corpus])
        else:
            self.longest_sentence = max_sentence_length

        self.total_list = [x for sentence in self.corpus for x in sentence]

        self.freq_dict = None

        if not self.freq_dict:
            self.freq_dict = {}
            if self.verbose:
                print('Generating frequency dictionary (.freq_dict)...')
                for word in self.tqdm.tqdm(self.total_list):
                    self.freq_dict[word] = self.freq_dict.get(word, 0) + 1
            else:
                for word in self.total_list:
                    self.freq_dict[word] = self.freq_dict.get(word, 0) + 1

        if self.freq_dict:
            self.total_list = None

        self.ranked_word_list = np.concatenate([[' '], (sorted(self.freq_dict.keys(), key = self.freq_dict.__getitem__, reverse = True))])

        if not max_words:
            self.max_words = len(self.ranked_word_list)-1
        else:
            self.max_words = max_words

        self.lost_words = self.ranked_word_list[self.max_words+1:]
        self.ranked_word_list = self.ranked_word_list[:self.max_words+1]

        self.avg_missing_vector = np.zeros(self.vector_dim)

        if self.tokenize_unknown and len(self.lost_words) > 0:
            self.ranked_word_list = np.concatenate([self.ranked_word_list, ['UNKNOWN']])
            if verbose == True:
                print('Calculating vector average of discarded words...')
            self.avg_missing_vector = np.average(self.query(self.lost_words, verbose = verbose), axis = 0)

        for key in list(self.freq_dict):
            if key not in self.ranked_word_list: del self.freq_dict[key]

    def tokenized_word_index(self):
        '''
        :return: word vector dictionary for the corpus
        '''
        return {word:self.integer_token_lookup(word) for word in self.ranked_word_list}

    def fit_vector_dict(self, verbose = None):
        '''
        Generate word vector dictionary for all words on ranked word list and for out-of-dictionary word if
            tokenize_unknown == True.
        :return: dictionary mapping all words in ranked word list to it's vector representation
        '''
        if type(verbose)!= bool:
            verbose = self.verbose
        if verbose == True:
            print('Generating integer token to word vector dictionary...')
        vector_dict = self.query(self.ranked_word_list[1:], initial_zero = True, verbose = verbose)
        return vector_dict

    def fit_integer_embedding(self, verbose = None, pad_first = True):
        '''
        Fits all 'sentences' in corpus to their integer representation
        :return: all padded 'sentences' of corpus in integer embedded form
        '''
        if verbose == None:
            verbose = self.verbose
        integer_embedding = self.np.zeros((len(self.corpus), self.longest_sentence), dtype=int)
        if verbose:
            print('Generating integer embedding (.integer_embedding)...')
            for index in self.tqdm.trange(len(self.corpus)):
                integer_embedding[index] = self.str_to_int_tokens(self.corpus[index], max_length=self.longest_sentence, pad_first = pad_first)
        else:
            for index in range(len(self.corpus)):
                integer_embedding[index] = self.str_to_int_tokens(self.corpus[index], max_length=self.longest_sentence, pad_first = pad_first)
        return integer_embedding

    def __query_str(self, word):
        '''
        Internal function to query and individual word
        :param word:
        :return:
        '''
        if word == 'UNKNOWN':
            return self.avg_missing_vector
        else:
            return self.vectors.query(str(word))

    def query(self, word_list, restrict_search = False, initial_zero = False, verbose = False):
        '''
        Generalization of _query_str.  If string is given, return __query_str.  If list is given, return list of
            __query_str for each word in list.
        :param word_list: Word or list of words to search
        :param restrict_search: If True, only return words in ranked word list
        :param initial_zero: set to True only if generating entire vector dictionary from ranked word list
        :param verbose: show progress
        :return: return vector representation or list of vector representations for word or words
        '''
        if type(word_list)==str:
            if restrict_search and word_list in self.ranked_word_list:
                return __query_str(word_list)
            elif restrict_search:
                return np.zeros(self.vector_dim)
            else:
                return __query_str(word_list)
        if initial_zero == False:
            query_embedding = self.np.zeros((len(word_list), self.vector_dim))
            i_z = 0
        else:
            query_embedding = self.np.zeros((len(word_list)+1, self.vector_dim))
            i_z = 1
        if verbose == True and self.bar == True:
            for i in self.tqdm.trange(i_z, len(word_list)+i_z):
                if (restrict_search == True) and (word_list[i] in self.ranked_word_list):
                    query_embedding[i] = self.__query_str(word_list[i-i_z])
                elif (restrict_search == False):
                    query_embedding[i] = self.__query_str(word_list[i-i_z])
            return query_embedding
        else:
            for i in range(i_z, len(word_list)):
                if restrict_search and (word_list[i] in self.ranked_word_list):
                    query_embedding[i] = self.__query_str(word_list[i-i_z])
                elif not restrict_search:
                    query_embedding[i] = self.__query_str(word_list[i-i_z])
            return query_embedding

    def str_to_int_tokens(self, word_list, max_length = None, pad_first = True):
        '''
        Converts a list of words into it's integer embedding form
        :param word_list: words to convert
        :param max_length: maximum number of words to convert
        :param pad_first: if True, pad sentences from the beginning of embedding.  If false, add zeros after sentence embedding
        :return: return list of integer representations of the input list of words
        '''
        if not max_length:
            max_length = len(word_list)
        if not pad_first:
            return self.np.concatenate([[self.integer_token_lookup(x) for x in word_list], self.np.zeros(max_length - (len(word_list)), dtype = int)])
        else:
            return self.np.concatenate([self.np.zeros(max_length - len(word_list), dtype = int), [self.integer_token_lookup(x) for x in word_list]])

    def integer_token_lookup(self, str_token):
        '''
        Look up integer representation of word
        :param str_token: word to look up
        :return: integer representation of word
        '''
        try:
            return self.ranked_word_list.tolist().index(str_token)
        except:
            if not self.tokenize_unknown:
                return 0
            else:
                return self.max_words + 2

    def to_keras(self, pad_first = True):
        '''
        Output integer embedding and linked word vector dictionary in format suitable to use in a Keras mode.  The
            model will be trained on the integer embedding of the corpus and the word vector dictionary will be imported as
            weights of the Keras embedding layer
        :return: if text corpus input, returns a 3-tuple of (corpus integer embeddings, test corpus integer embeddings,
            word vector dictionary).  If no test corpus, returns a 2-tuple of (corpus integer embeddings, word vector dictionary)
        '''
        if not self.test_corpus:
            return self.fit_integer_embedding(pad_first = pad_first), self.fit_vector_dict()
        else:
            return self.fit_integer_embedding(pad_first = pad_first), self.test_to_integer_embedding(pad_first = pad_first), self.fit_vector_dict()

    def test_to_integer_embedding(self, pad_first = True):
        '''
        Same as fit_integer_embedding, but converts the test corpus to integer representation.  Test corpus is only
            converted for words in the corpus integer embedding dictionary
        :return: all padded 'sentences' of test corpus in integer embedded form
        '''
        if not self.test_corpus:
            raise ValueError('Vectokenizer has no test corpus input.')
        transformed_corpus = self.np.zeros((len(self.test_corpus), self.longest_sentence), dtype = int)
        for line in range(transformed_corpus.shape[0]):
            transformed_corpus[line] = self.str_to_int_tokens(self.test_corpus[line], self.longest_sentence, pad_first = pad_first)

        return transformed_corpus

class MultiVectors:

    def __init__(self, vector_list):
        
        self.vector_list = vector_list