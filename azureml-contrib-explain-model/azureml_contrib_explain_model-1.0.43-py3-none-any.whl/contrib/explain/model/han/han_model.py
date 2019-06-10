# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defined the HAN model for training, tuning, testing and retrieving the feature importances.

The han_model is a modified version of the implementation in this repository:
https://github.com/ematvey/hierarchical-attention-networks
Which is originally based on the paper:
`Hierarchical Attention Networks for Document Classification (Yang et al., 2016)`
    (https://www.cs.cmu.edu/~diyiy/docs/naacl16.pdf)
"""

import numpy as np
# Soft dependency for spacy
try:
    import spacy
except ImportError:
    print("Could not import spacy, required for HAN model")
import os
from collections import defaultdict
import pickle
import json
from tqdm import tqdm
import random
import pandas as pd
from collections import Counter
import time
import uuid
import re
from abc import ABCMeta, abstractmethod

from azureml._logging import ChainedIdentity
from azureml.explain.model._internal.common import module_logger
from azureml.explain.model._internal.constants import Tensorflow, SKLearn, Spacy

# Ensure we only have a soft dependency on tensorflow
try:
    import tensorflow as tf
    import tensorflow.contrib.layers as layers
    try:
        from tensorflow.contrib.rnn import LSTMStateTuple
    except ImportError:
        LSTMStateTuple = tf.nn.rnn_cell.LSTMStateTuple
except ImportError:
    print("Could not import tensorflow, required for HAN model")

# Ensure we only have a soft dependency on gensim
try:
    import gensim
except ImportError:
    print("Could not import gensim, required for HAN model if word embeddings file not specified")

# Load spacy English language model with NER and tagger only
en = spacy.load(Spacy.EN, disable=[Spacy.NER, Spacy.TAGGER])
VOCAB_FILENAME = os.path.join(os.path.curdir, 'vocab.pickle')
TRAINSET_FILENAME = os.path.join(os.path.curdir, 'train.dataset')
DEVSET_FILENAME = os.path.join(os.path.curdir, 'dev.dataset')
# The encoding for an unknown word
UNKNOWN = 2


def bidirectional_rnn(cell_fw, cell_bw, inputs_embedded, input_lengths, scope=None):
    """Bidirectional RNN with concatenated outputs and states.

    :param cell_fw: An instance of RNNCell, to be used for forward direction.
    :type cell_fw: RNNCell
    :param cell_bw: An instance of RNNCell, to be used for backward direction.
    :type cell_bw: RNNCell
    :param inputs_embedded: RNN inputs
    :type inputs_embedded: Tensor
    :param input_lengths: The lengths for each of the sequences in the batch.
    :type input_lengths: list
    :param scope: Variable scope.
    :type scope: tf.variable_scope
    :return: tuple(outputs, state)
            where
            - outputs = A tuple of forward and backward RNN outputs.
            - state = A tuple containing forward and backward final states of RNN.
    :rtype: ((Tensor, Tensor), Union[(Tensor, Tensor), (LSTMStateTuple, LSTMStateTuple)])
    """
    with tf.variable_scope(scope or "birnn") as scope:
        ((fw_outputs, bw_outputs), (fw_state, bw_state)) = (
            tf.nn.bidirectional_dynamic_rnn(cell_fw=cell_fw, cell_bw=cell_bw, inputs=inputs_embedded,
                                            sequence_length=input_lengths, dtype=tf.float32, swap_memory=True,
                                            scope=scope))
        outputs = tf.concat((fw_outputs, bw_outputs), 2)

        def concatenate_state(fw_state, bw_state):
            if isinstance(fw_state, LSTMStateTuple):
                state_c = tf.concat((fw_state.c, bw_state.c), 1, name='bidirectional_concat_c')
                state_h = tf.concat((fw_state.h, bw_state.h), 1, name='bidirectional_concat_h')
                state = LSTMStateTuple(c=state_c, h=state_h)
                return state
            elif isinstance(fw_state, tf.Tensor):
                return tf.concat((fw_state, bw_state), 1, name='bidirectional_concat')
            elif (isinstance(fw_state, tuple) and isinstance(bw_state, tuple) and len(fw_state) == len(bw_state)):
                # multilayer case
                return tuple(concatenate_state(fw, bw) for fw, bw in zip(fw_state, bw_state))
            else:
                raise ValueError('unknown state type: {}'.format((fw_state, bw_state)))
        state = concatenate_state(fw_state, bw_state)
        return outputs, state


def task_specific_attention(inputs, output_size,
                            initializer=layers.xavier_initializer(),
                            activation_fn=tf.tanh, scope=None):
    """
    Perform task-specific attention reduction, using learned attention context vector (constant within task).

    :param inputs: Tensor of shape [batch_size, units, input_size]
            `input_size` must be static (known)
            `units` axis will be attended over (reduced from output)
            `batch_size` will be preserved
    :type inputs: Tensor
    :param output_size: Size of output's inner (feature) dimension
    :type output_size: int
    :param initializer: Attention layer weights initializer.
    :type initializer: str
    :param activation_fn: A GUID that represents a run.
    :type activation_fn: xavier_initializer
    :param scope: Variable scope.
    :type scope: tf.variable_scope
    :return: tuple(outputs, attention_weights)
            where
            - outputs = Tensor of shape [batch_size, output_dim].
            - attention_weights = Attention layer weights.
    :rtype: (Tensor, Tensor)
    """
    assert len(inputs.get_shape()) == 3 and inputs.get_shape()[-1].value is not None

    with tf.variable_scope(scope or 'attention') as scope:
        attention_context_vector = tf.get_variable(name='attention_context_vector',
                                                   shape=[output_size],
                                                   initializer=initializer,
                                                   dtype=tf.float32)
        input_projection = layers.fully_connected(inputs, output_size,
                                                  activation_fn=activation_fn,
                                                  scope=scope)

        vector_attn = tf.reduce_sum(tf.multiply(input_projection, attention_context_vector), axis=2, keepdims=True)
        attention_weights = tf.nn.softmax(vector_attn, axis=1)
        weighted_projection = tf.multiply(input_projection, attention_weights)

        outputs = tf.reduce_sum(weighted_projection, axis=1)

        return outputs, attention_weights


def tokenize(text):
    """Tokenize by splitting text across non-word boundaries.

    :param text: Input text to tokenize.
    :type text: str
    :return: The split text by non-word boundaries.
    :rtype: list[str]
    """
    return re.split('(\W+)', text)


def parse_sentences(data, vocab):
    """Parse sentences from the given data and vocabulary.

    :param data: Input data to parse a list of list of sentences and tokens for.
    :type data: str
    :param vocab: Map from word to index.
    :type vocab: dict
    :return: A list for each sentence where each sentence contains a list of parsed tokens.
    :rtype: list[list[str]]
    """
    x = []
    if vocab is None:
        for sent in en(data).sents:
            x.append([orth for tok in sent for orth in tokenize(tok.orth_)])
    else:
        for sent in en(data).sents:
            x.append([vocab.get(orth, UNKNOWN) for tok in sent for orth in tokenize(tok.orth_)])
    return x


def build_word_frequency_distribution(train_data):
    """Build the frequency distribution for the training dataset.

    :param train_data: The training dataset.
    :type train_data: list[str]
    :return: A dictionary of word frequencies generated from the training data.
    :rtype: dict[str, int]
    """
    module_logger.info('building frequency distribution')
    freq = defaultdict(int)
    for i, review in enumerate(train_data):
        doc = en.tokenizer(review)
        for token in doc:
            for orth in tokenize(token.orth_):
                freq[orth] += 1
    return freq


def build_vocabulary(train_data):
    """Build the one-hot-encoded vocabulary dictionary from the training data.

    :param train_data: The training dataset.
    :type train_data: list[str]
    :return: A dictionary from word to a one-hot-encoded index.
    :rtype: dict[str, int]
    """
    freq = build_word_frequency_distribution(train_data)
    words = list(sorted(freq.items(), key=lambda x: -x[1]))
    vocab = {}
    i = 3
    for w, freq in words:
        vocab[w] = i
        i += 1
    # Save vocabulary to file to be able to load it later for tune/test scenario
    with open(VOCAB_FILENAME, 'w') as vocab_file:
        json_string = json.dumps(vocab)
        vocab_file.write(json_string)
    return vocab


def load_vocabulary():
    """Load the saved vocabulary built during the training phase.

    Return None if no vocab found.

    :return: A dictionary from word to a one-hot-encoded index.
    :rtype: dict[str, int] or None
    """
    try:
        with open(VOCAB_FILENAME, 'r') as vocab_file:
            json_string = vocab_file.read()
            vocab = json.loads(json_string)
            module_logger.info('vocabulary loaded')
            return vocab
    except IOError:
        err_message = 'failed to load vocabulary'
        module_logger.error(err_message)
        return None


def make_test(test_data):
    """Parse the test data into sentences of indexed words built during the training phase.

    :param test_data: The test dataset.
    :type test_data: list[str]
    :return: A list of sentences, where each sentence is a list of one-hot-encoded words.
    :rtype: list[list[int]]
    """
    vocab = load_vocabulary()
    return parse_sentences(test_data[0], vocab)


def make_tune(tune_data, tune_target, epochs=1):
    """Parse the tune data into sentences of indexed words built during the training phase.

    :param tune_data: The tune dataset.
    :type tune_data: list[str]
    :param tune_target: The target labels corresponding to the tuning dataset.
    :type tune_target: list[int]
    :param epochs: The number of times to re-train on the same tune dataset.
    :type epochs: int
    :return: tuple(sentences, score)
            where
            - sentences = A list of sentences, where each sentence is a list of one-hot-encoded words.
            - score = Target label.
    :rtype: (list[list[int]], int)
    """
    # get vocabulary
    vocab = load_vocabulary()
    e = 0
    while e < epochs:
        module_logger.info('epoch %s' % e)
        for review, score in tqdm(zip(tune_data, tune_target)):
            yield parse_sentences(review, vocab), score
        e += 1


def save_train_data(train_data, train_target, vocab, train_ratio):
    """Parse the train data into sentences of indexed words built during the training phase.

    Dumps the training data to a pickled file.

    :param train_data: The train dataset.
    :type train_data: list[str]
    :param train_target: The target labels corresponding to the training dataset.
    :type train_target: list[int]
    :param vocab: A map from word to index.
    :type vocab: dict
    """
    train_f = open(TRAINSET_FILENAME, 'wb')
    dev_f = open(DEVSET_FILENAME, 'wb')
    for review, score in tqdm(zip(train_data, train_target)):
        r = random.random()
        if r < train_ratio:
            f = train_f
        else:
            f = dev_f
        pickle.dump((parse_sentences(review, vocab), score), f)
    train_f.close()
    dev_f.close()


def make_word2vec_data(train_data, train_target, embedding_dim, train_ratio=0.9):
    """Parse the train data into sentences of indexed words built during the training phase.

    Uses word2vec on the training data to build the vocabulary.
    Dumps the training data to a pickled file.
    Returns the trained word2vec model.

    :param train_data: The train dataset.
    :type train_data: list[str]
    :param train_target: The target labels corresponding to the training dataset.
    :type train_target: list[int]
    :param embedding_dim: The embedding dimensionality.
    :type embedding_dim: int
    :param train_ratio: The ratio used to split train and dev data.
    :type train_ratio: float
    :return: The word2vec model.
    :rtype: gensim.models.word2vec.Word2Vec
    """
    def iterate_docs():
        for review in tqdm(train_data):
            yield parse_sentences(review, None)
    sentences = [sentence for doc in iterate_docs() for sentence in doc]
    word2vec_model = gensim.models.Word2Vec(sentences, min_count=1, size=embedding_dim,
                                            sg=1, workers=os.cpu_count())
    vocab = {}
    for word, voc in word2vec_model.wv.vocab.items():
        vocab[word] = voc.index
    # Save vocabulary to file to be able to load it later for tune/test scenario
    with open(VOCAB_FILENAME, 'w') as vocab_file:
        json_string = json.dumps(vocab)
        vocab_file.write(json_string)
    save_train_data(train_data, train_target, vocab, train_ratio)
    return word2vec_model


def make_data(train_data, train_target, train_ratio=0.9):
    """Parse the train data into sentences of indexed words built during the training phase.

    Dumps the training data to a pickled file.

    :param train_data: The train dataset.
    :type train_data: list[str]
    :param train_target: The target labels corresponding to the training dataset.
    :type train_target: list[int]
    """
    vocab = build_vocabulary(train_data)
    save_train_data(train_data, train_target, vocab, train_ratio)


def batch(inputs):
    """Encode the input data as a 3-D array by batch X document X sentence size.

    The encoding is in the one-hot-encoded word representation.

    :param inputs: The input data to reshape.
    :type inputs: list[list[int]]
    :return: tuple(word_encoding, document_sizes, sentence_sizes)
            where
            - word_encoding = The batched one-hot-encoding of the words in a 3-D array.
            - document_sizes = The document sizes.
            - sentence_sizes = The sentence sizes.
    :rtype: (np.array, np.array, np.array)
    """
    batch_size = len(inputs)

    document_sizes = np.array([len(doc) for doc in inputs], dtype=np.int32)
    document_size = document_sizes.max()

    sentence_sizes_ = [[len(sent) for sent in doc] for doc in inputs]

    def max_def_0(sent_sizes):
        return max(sent_sizes, default=0)

    sentence_size = max(map(max_def_0, sentence_sizes_))

    word_encoding = np.zeros(shape=[batch_size, document_size, sentence_size], dtype=np.int32)

    sentence_sizes = np.zeros(shape=[batch_size, document_size], dtype=np.int32)
    for i, document in enumerate(inputs):
        for j, sentence in enumerate(document):
            sentence_sizes[i, j] = sentence_sizes_[i][j]
            for k, word in enumerate(sentence):
                word_encoding[i, j, k] = word

    return word_encoding, document_sizes, sentence_sizes


def read_trainset(epochs=1):
    """Read the train dataset.

    :param epochs: The number of epochs or times to read the training dataset.
    :type epochs: int
    :return: tuple(training_data, target)
            where
            - training_data = The read training dataset.
            - target = The target label.
    :rtype: (list[list[int]], int)
    """
    return read_dataset(TRAINSET_FILENAME, epochs=epochs)


def read_devset(epochs=1):
    """Read the evaluation dataset.

    :param epochs: The number of epochs or times to read the evaluation dataset.
    :type epochs: int
    :return: tuple(evaluation_data, target)
            where
            - evaluation_data = The read evaluation dataset.
            - target = The target label.
    :rtype: (list[list[int]], int)
    """
    return read_dataset(DEVSET_FILENAME, epochs=epochs)


def read_dataset(fn, review_max_sentences=30, sentence_max_length=30, epochs=1):
    """Read the dataset.

    :param review_max_sentences: The cutoff for maximum number of sentences for each document.
    :type review_max_sentences: int
    :param sentence_max_length: The cutoff for maximum length of words per sentence for each document.
    :type sentence_max_length: int
    :param epochs: The number of epochs or times to read the dataset.
    :type epochs: int
    :return: tuple(dataset, target)
            where
            - dataset = The read dataset.
            - target = The target label.
    :rtype: (list[list[int]], int)
    """
    c = 0
    while 1:
        c += 1
        if epochs > 0 and c > epochs:
            return
        module_logger.info('epoch %s' % c)
        with open(fn, 'rb') as f:
            try:
                while 1:
                    x, y = pickle.load(f)
                    # clip review to specified max lengths
                    x = x[:review_max_sentences]
                    x = [sent[:sentence_max_length] for sent in x]
                    yield x, y
            except EOFError:
                continue


def batch_iterator(dataset, batch_size, max_epochs):
    """Iterate over the dataset for the specified number of epochs.

    :param dataset: The dataset to iterate over, represented as a list of sentences,
    where each sentence is a list of one-hot-encoded words.
    :type dataset: list[list[int]]
    :param batch_size: The batch size to yield for each step.
    :type batch_size: int
    :param max_epochs: The number of epochs or times to read the dataset.
    :type max_epochs: int
    :return: tuple(dataset, target)
            where
            - dataset = The batched dataset.
            - target = The batched target label.
    :rtype: (list[list[list[int]]], list[int])
    """
    for i in range(max_epochs):
        xb = []
        yb = []
        for ex in dataset:
            x, y = ex
            xb.append(x)
            yb.append(y)
            if len(xb) == batch_size:
                yield xb, yb
                xb, yb = [], []


def calculate_class_weights(dataset):
    """Calculate the class weights for the given dataset.

    :param dataset: The dataset to calculate the class weights for.
    :type dataset: list[list[int]]
    :return: The class weights.
    :rtype: dict[int, float]
    """
    module_logger.info('Calculating class weights')
    class_weights = pd.Series(Counter([l for _, l in dataset]))
    class_weights = 1 / (class_weights / class_weights.mean())
    return class_weights.to_dict()


class HANBaseModel(ChainedIdentity):
    """Base Implementation of Hierarchical Attention Network document model.

    The implementation is described in
    `Hierarchical Attention Networks for Document Classification (Yang et al., 2016)`
    (https://www.cs.cmu.edu/~diyiy/docs/naacl16.pdf).
    """

    __metaclass__ = ABCMeta

    def __init__(self, vocab_size, embedding_size, word_output_size, sentence_output_size,
                 max_grad_norm, dropout_keep_proba, learning_rate=1e-4, device=Tensorflow.CPU0, scope=None,
                 word_embedding_path=None, word2vec_model=None):
        """Initialize the HAN model."""
        import tensorflow as tf
        try:
            from tensorflow.contrib.rnn import GRUCell
        except ImportError:
            GRUCell = tf.nn.rnn_cell.GRUCell
        # Reset graph prior to creating the network
        tf.reset_default_graph()
        kwargs = {}
        super(HANBaseModel, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_size = embedding_size
        self.word_output_size = word_output_size
        self.sentence_output_size = sentence_output_size
        self.max_grad_norm = max_grad_norm
        self.dropout_keep_proba = dropout_keep_proba
        self.word_attention_weights = None
        self.sentence_attention_weights = None
        self.checkpoint_dir = None
        num_word_units = 100
        num_sentence_units = 100

        def get_gru_cell(units):
            return GRUCell(units)

        def word_cell_maker():
            # TODO: investigate using MultiRNNCell
            # return MultiRNNCell([get_gru_cell(num_word_units) for _ in range(num_layers)])
            return get_gru_cell(num_word_units)

        def sentence_cell_maker():
            # TODO: investigate using MultiRNNCell
            # return MultiRNNCell([get_gru_cell(num_sentence_units) for _ in range(num_layers)])
            return get_gru_cell(num_sentence_units)

        self.sentence_cell = sentence_cell_maker
        self.word_cell = word_cell_maker

        with tf.variable_scope(scope or 'tcm') as scope:
            self.global_step = tf.Variable(0, name='global_step', trainable=False)

            self.is_training = tf.placeholder(dtype=tf.bool, name='is_training')

            self.sample_weights = tf.placeholder(shape=(None,), dtype=tf.float32, name='sample_weights')

            # [document x sentence x word]
            self.inputs = tf.placeholder(shape=(None, None, None), dtype=tf.int32, name='inputs')

            # [document x sentence]
            self.word_lengths = tf.placeholder(shape=(None, None), dtype=tf.int32, name='word_lengths')

            # [document]
            self.sentence_lengths = tf.placeholder(shape=(None,), dtype=tf.int32, name='sentence_lengths')

            # [document]
            self.labels = tf.placeholder(shape=(None,), dtype=tf.int32, name='labels')

            (self.document_size, self.sentence_size, self.word_size) = tf.unstack(tf.shape(self.inputs))

            self._init_embedding(scope, word_embedding_path, word2vec_model)

            # embeddings cannot be placed on GPU
            with tf.device(device):
                self._init_body(scope)

        with tf.variable_scope('train'):
            self.loss = self._compute_loss()
            self.accuracy = self._compute_accuracy()
            tf.summary.scalar('loss', self.loss)
            tf.summary.scalar('accuracy', self.accuracy)

            tvars = tf.trainable_variables()

            grads, global_norm = tf.clip_by_global_norm(tf.gradients(self.loss, tvars), self.max_grad_norm)
            tf.summary.scalar('global_grad_norm', global_norm)
            opt = tf.train.AdamOptimizer(learning_rate)
            self.train_op = opt.apply_gradients(zip(grads, tvars), name='train_op', global_step=self.global_step)

            self.summary_op = tf.summary.merge_all()

    @abstractmethod
    def _compute_loss(self):
        pass

    @abstractmethod
    def _compute_accuracy(self):
        pass

    def _init_embedding(self, scope, word_embedding_path, word2vec_model):
        """Initialize the word embeddings."""
        initializer = None
        embedding_index = None
        embedding_shape = None
        if word2vec_model is not None:
            word_to_embedding = {}
            num_words = 0
            for word in word2vec_model.wv.vocab:
                coefs = np.asarray(word2vec_model.wv[word], dtype='float32')
                word_to_embedding[word] = coefs
                num_words += 1
            embedding_matrix = np.zeros((num_words + 1, self.embedding_size))

            for word, voc in word2vec_model.wv.vocab.items():
                i = voc.index
                embedding_matrix[i] = word_to_embedding.get(word)

            initializer = tf.constant_initializer(embedding_matrix)
            embedding_index = self.inputs
            embedding_shape = [num_words + 1, self.embedding_size]
        elif word_embedding_path is not None:
            # load existing vocab
            vocab = load_vocabulary()
            max_vocab_val = max(vocab.values()) + 1
            ordered_words = []
            for i in range(max_vocab_val):
                ordered_words.append(str(i) + "_placeholder")
            for k, v in vocab.items():
                ordered_words[v] = k
            vocab_mapping_string = tf.constant(ordered_words)
            word2idx = {}
            weights = []
            with open(word_embedding_path, 'r', encoding='utf8') as file:
                for index, line in enumerate(file):
                    if line:
                        # Word and weights separated by space
                        values = line.split()
                        # Word is first symbol on each line
                        word = values[0]
                        # Weights for word
                        word_weights = np.asarray(values[1:], dtype=np.float32)
                        word2idx[word] = index
                        weights.append(word_weights)
            exp_out_of_vocab_words = 100000
            # add some extra weights for words that may be out of vocabulary
            for i in range(exp_out_of_vocab_words):
                weights.append(np.copy(weights[i]))
            weights = np.asarray(weights)
            initializer = tf.constant_initializer(weights)
            word_at_array = []
            for i in range(len(word2idx)):
                word_at_array.append(str(i) + "_placeholder")
            for k, v in word2idx.items():
                word_at_array[v] = k
            embedding_mapping_string = tf.constant(word_at_array)
            vocab_table = tf.contrib.lookup.index_to_string_table_from_tensor(vocab_mapping_string,
                                                                              default_value="UNKNOWN")
            inverse_vocab = vocab_table.lookup(tf.cast(self.inputs, tf.int64))
            emb_table = tf.contrib.lookup.index_table_from_tensor(mapping=embedding_mapping_string,
                                                                  num_oov_buckets=exp_out_of_vocab_words,
                                                                  default_value=0)
            # word2idx[invvocab[self.input]] in tensorflow syntax
            embedding_index = emb_table.lookup(inverse_vocab)
            embedding_shape = [len(weights), self.embedding_size]
        else:
            initializer = layers.xavier_initializer()
            embedding_index = self.inputs
            embedding_shape = [self.vocab_size, self.embedding_size]

        with tf.variable_scope(scope):
            with tf.variable_scope("embedding") as scope:
                self.embedding_matrix = tf.get_variable(name="embedding_matrix", shape=embedding_shape,
                                                        initializer=initializer, trainable=True,
                                                        dtype=tf.float32)
                self.inputs_embedded = tf.nn.embedding_lookup(self.embedding_matrix, embedding_index)

    def _init_body(self, scope):
        """Initialize the word layer and sentence layer in the Hierarchical network."""
        with tf.variable_scope(scope):
            word_level_inputs = tf.reshape(self.inputs_embedded, [
                self.document_size * self.sentence_size,
                self.word_size,
                self.embedding_size
            ])
            word_level_lengths = tf.reshape(
                self.word_lengths, [self.document_size * self.sentence_size])

            with tf.variable_scope('word') as scope:
                word_encoder_output, _ = bidirectional_rnn(self.word_cell(), self.word_cell(),
                                                           word_level_inputs, word_level_lengths, scope=scope)

                with tf.variable_scope('attention') as scope:
                    word_level_output, word_attention_weights = task_specific_attention(word_encoder_output,
                                                                                        self.word_output_size,
                                                                                        scope=scope)

                with tf.variable_scope('dropout'):
                    word_level_output = layers.dropout(word_level_output, keep_prob=self.dropout_keep_proba,
                                                       is_training=self.is_training)

            sentence_level_inputs = tf.reshape(word_level_output, [self.document_size, self.sentence_size,
                                                                   self.word_output_size])

            with tf.variable_scope('sentence') as scope:
                sentence_encoder_output, _ = bidirectional_rnn(self.sentence_cell(), self.sentence_cell(),
                                                               sentence_level_inputs, self.sentence_lengths,
                                                               scope=scope)

                with tf.variable_scope('attention') as scope:
                    sentence_level_output, sentence_attention_weights = task_specific_attention(
                        sentence_encoder_output, self.sentence_output_size, scope=scope)

                with tf.variable_scope('dropout'):
                    sentence_level_output = layers.dropout(sentence_level_output, keep_prob=self.dropout_keep_proba,
                                                           is_training=self.is_training)
            self._init_output_layer(sentence_level_output)
            self.sentence_attention_weights = sentence_attention_weights
            self.word_attention_weights = word_attention_weights

    @abstractmethod
    def _init_output_layer(self, sentence_level_output):
        pass

    def get_feed_data(self, x, y=None, class_weights=None, is_training=True):
        """Construct the feed data to the model."""
        x_m, doc_sizes, sent_sizes = batch(x)
        fd = {
            self.inputs: x_m,
            self.sentence_lengths: doc_sizes,
            self.word_lengths: sent_sizes,
        }
        if y is not None:
            fd[self.labels] = y
            if class_weights is not None:
                fd[self.sample_weights] = [class_weights[yy] for yy in y]
            else:
                fd[self.sample_weights] = np.ones(shape=[len(x_m)], dtype=np.float32)
        fd[self.is_training] = is_training
        return fd

    def train_model(self, batch_iterator, class_weights, tflog_dir, sess, saver, checkpoint_path):
        """Trains the model on the given batch_iterator."""
        summary_writer = tf.summary.FileWriter(tflog_dir, graph=tf.get_default_graph())
        for i, (x, y) in enumerate(batch_iterator):
            fd = self.get_feed_data(x, y, class_weights=class_weights)
            t0 = time.clock()
            step, summaries, loss, accuracy, _ = sess.run([
                self.global_step,
                self.summary_op,
                self.loss,
                self.accuracy,
                self.train_op,
            ], fd)
            td = time.clock() - t0

            summary_writer.add_summary(summaries, global_step=step)
            if step % 1 == 0:
                module_logger.info('step %s, loss=%s, accuracy=%s, t=%s, inputs=%s' %
                                   (step, loss, accuracy, round(td, 2), fd[self.inputs].shape))
        module_logger.info("finished training, saving model to path: {}".format(checkpoint_path))
        saver.save(sess, checkpoint_path, global_step=step)

    def fine_tune_model(self, filteredData, prediction, epochs=1, batch_size=30):
        """Fine-tunes the trained model on the given filteredData."""
        filtered_tune = make_tune(filteredData, prediction)
        class_weights = calculate_class_weights(filtered_tune)
        filtered_tune = make_tune(filteredData, prediction, epochs=epochs)

        # tune HAN on prediction and inverse of data transform
        config = tf.ConfigProto(allow_soft_placement=True)
        tflog_dir = os.path.join(os.path.curdir, Tensorflow.TFLOG)
        with tf.Session(config=config) as sess:
            checkpoint = tf.train.get_checkpoint_state(self.checkpoint_dir)
            saver = tf.train.Saver(tf.global_variables())
            saver.restore(sess, checkpoint.model_checkpoint_path)
            init_l = tf.local_variables_initializer()
            sess.run(init_l)
            # need to initialize tables for embeddings lookup
            iterator = batch_iterator(filtered_tune, batch_size, 300)
            self.train_model(iterator, class_weights, tflog_dir, sess, saver, checkpoint.model_checkpoint_path)

    def get_feature_importance(self, golden_doc_list):
        """Calculate the feature importance values based on the word and sentence attention layer weights."""
        x_batch_test = make_test(golden_doc_list)
        x_m, doc_sizes, sent_sizes = batch([x_batch_test])

        # Calculate alpha coefficients for the first test example
        with tf.Session() as sess:
            checkpoint = tf.train.get_checkpoint_state(self.checkpoint_dir)
            saver = tf.train.Saver()
            saver.restore(sess, checkpoint.model_checkpoint_path)
            sentence_attention_weights = self.sentence_attention_weights
            word_attention_weights = self.word_attention_weights
            # need to initialize tables for embeddings lookup
            sess.run(tf.tables_initializer())
            # calculate word and sentence attention weights
            ps = sess.run([sentence_attention_weights], feed_dict={self.inputs: x_m,
                                                                   self.sentence_lengths: doc_sizes,
                                                                   self.word_lengths: sent_sizes,
                                                                   self.is_training: False})
            pw = sess.run([word_attention_weights], feed_dict={self.inputs: x_m,
                                                               self.sentence_lengths: doc_sizes,
                                                               self.word_lengths: sent_sizes,
                                                               self.is_training: False})
        # Build correct mapping from word to index and inverse
        with open('vocab.pickle', 'r') as vocab_file:
            json_string = vocab_file.read()
            word_index = json.loads(json_string)
            module_logger.info('vocabulary loaded')

        index_word = {value: key for key, value in word_index.items()}
        vfunc = np.vectorize(index_word.get)
        features = vfunc(x_m)

        module_logger.info("learned word attention weights: {}".format(pw))
        module_logger.info("learned sentence attention weights: {}".format(ps))

        # calculate feature importance:
        #     f_i = sqrt(ps) * pw
        # where ps is sentence attention weight and pw is word attention weight
        return (pw[0].reshape(*pw[0].shape[:1], -1) * ps[0].flatten()[:, np.newaxis]).flatten(), features


class HANClassifierModel(HANBaseModel):
    """Hierarchical Attention Network document classification model."""

    def __init__(self, vocab_size, classes, embedding_size, word_output_size, sentence_output_size,
                 max_grad_norm, dropout_keep_proba, learning_rate=1e-4, device=Tensorflow.CPU0, scope=None,
                 word_embedding_path=None, word2vec_model=None):
        """Initialize the HAN classification model.

        :param vocab_size: Vocabulary size.
        :type vocab_size: int
        :param classes: The number of classes.
        :type classes: int
        :param embedding_size: Word embedding vector length.
        :type embedding_size: int
        :param word_output_size: Maximum number of words per parsed sentence.
        :type word_output_size: int
        :param sentence_output_size: Maximum number of sentences per parsed document.
        :type sentence_output_size: int
        :param max_grad_norm: Max global gradient norm, used for clipping gradient above the threshold.
        :type max_grad_norm: float
        :param dropout_keep_proba: Probability to keep for dropout.
        :type dropout_keep_proba: float
        :param learning_rate: Learning rate.
        :type learning_rate: float
        :param device: The device to run on, CPU or GPU.
        :type device: str
        :param scope: Variable scope.
        :type scope: tf.variable_scope
        :param word_embedding_path: Path to word embedding file.
        :type word_embedding_path: str
        :param word2vec_model: Optional word2vec model for precomputed word embeddings used in initializing weights.
        :type word2vec_model: gensim.models.word2vec.Word2Vec
        :return: The HAN model for classification.
        :rtype: HANClassifierModel
        """
        self.classes = classes
        super(HANClassifierModel, self).__init__(vocab_size, embedding_size, word_output_size, sentence_output_size,
                                                 max_grad_norm, dropout_keep_proba, learning_rate=1e-4,
                                                 device=Tensorflow.CPU0, scope=scope,
                                                 word_embedding_path=word_embedding_path,
                                                 word2vec_model=word2vec_model)

    def _compute_loss(self):
        self.cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=self.labels,
                                                                            logits=self.logits)
        return tf.reduce_mean(tf.multiply(self.cross_entropy, self.sample_weights))

    def _compute_accuracy(self):
        return tf.reduce_mean(tf.cast(tf.nn.in_top_k(self.logits, self.labels, 1), tf.float32))

    def _init_output_layer(self, sentence_level_output):
        # In classification scenario output argmax of linear layer with as many output units as classes
        with tf.variable_scope('classifier'):
            self.logits = layers.fully_connected(sentence_level_output, self.classes, activation_fn=None)
        self.prediction = tf.argmax(self.logits, axis=-1)


class HANRegressorModel(HANBaseModel):
    """Hierarchical Attention Network document regression model."""

    def __init__(self, vocab_size, embedding_size, word_output_size, sentence_output_size, max_grad_norm,
                 dropout_keep_proba, learning_rate=1e-4, device=Tensorflow.CPU0, scope=None,
                 word_embedding_path=None, word2vec_model=None):
        """Initialize the HAN regression model.

        :param vocab_size: Vocabulary size.
        :type vocab_size: int
        :param embedding_size: Word embedding vector length.
        :type embedding_size: int
        :param word_output_size: Maximum number of words per parsed sentence.
        :type word_output_size: int
        :param sentence_output_size: Maximum number of sentences per parsed document.
        :type sentence_output_size: int
        :param max_grad_norm: Max global gradient norm, used for clipping gradient above the threshold.
        :type max_grad_norm: float
        :param dropout_keep_proba: Probability to keep for dropout.
        :type dropout_keep_proba: float
        :param learning_rate: Learning rate.
        :type learning_rate: float
        :param device: The device to run on, CPU or GPU.
        :type device: str
        :param scope: Variable scope.
        :type scope: tf.variable_scope
        :param word_embedding_path: Path to word embedding file.
        :type word_embedding_path: str
        :param word2vec_model: Optional word2vec model for precomputed word embeddings used in initializing weights.
        :type word2vec_model: gensim.models.word2vec.Word2Vec
        :return: The HAN model for classification.
        :rtype: HANClassifierModel
        """
        super(HANRegressorModel, self).__init__(vocab_size, embedding_size, word_output_size,
                                                sentence_output_size, max_grad_norm, dropout_keep_proba,
                                                learning_rate=1e-4, device=Tensorflow.CPU0, scope=scope,
                                                word_embedding_path=word_embedding_path,
                                                word2vec_model=word2vec_model)

    def _compute_loss(self):
        float_labels = tf.reshape(tf.to_float(self.labels), [-1])
        float_prediction = tf.reshape(tf.to_float(self.prediction), [-1])
        return tf.losses.mean_squared_error(labels=float_labels, predictions=float_prediction,
                                            weights=self.sample_weights)

    def _compute_accuracy(self):
        float_labels = tf.reshape(tf.to_float(self.labels), [-1])
        float_prediction = tf.reshape(tf.to_float(self.prediction), [-1])
        accuracy, _ = tf.metrics.root_mean_squared_error(float_labels,
                                                         float_prediction,
                                                         weights=self.sample_weights)
        return accuracy

    def _init_output_layer(self, sentence_level_output):
        # In regression scenario we just want linear output
        with tf.variable_scope('regressor'):
            self.prediction = layers.fully_connected(sentence_level_output, 1, activation_fn=None)


def create_checkpoint(model, session):
    """Create a checkpoint path for saving the HAN model to.

    :param model: The HAN model.
    :type model: HANBaseModel
    :param session: Current tensorflow session.
    :type session: Session
    :return: checkpoint_path, the model checkpoint path.
    :rtype: str
    """
    # Create unique checkpoint directory for this model
    checkpoint_dir = os.path.join(os.path.curdir, 'checkpoints', str(uuid.uuid4()))
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    model.checkpoint_dir = checkpoint_dir
    checkpoint_path = os.path.join(checkpoint_dir, str(uuid.uuid4()) + '-model')
    module_logger.info("Created checkpoint path at " + checkpoint_path)
    return checkpoint_path


def evaluate_accuracy(session, model, dataset, batch_size):
    """Evaluate the accuracy of the model on the dev dataset.

    :param model: The model to evaluate.
    :type model: Tensorflow model
    :param dataset: The evaluation dataset which contains a labels column.
    :type dataset: list[list[int]]
    :param batch_size: The batch size to iterate over.
    :type batch_size: int
    :return: The accuracy on the dev dataset.
    :rtype: float
    """
    predictions = []
    labels = []
    examples = []
    for x, y in tqdm(batch_iterator(dataset, batch_size, 1)):
        examples.extend(x)
        labels.extend(y)
        predictions.extend(session.run(model.prediction, model.get_feed_data(x, is_training=False)))

    df = pd.DataFrame({SKLearn.PREDICTIONS: predictions, SKLearn.LABELS: labels, SKLearn.EXAMPLES: examples})
    return (df[SKLearn.PREDICTIONS] == df[SKLearn.LABELS]).mean()


def train_HAN_model(model, batch_size=30, train_epochs=3):
    """Train a Hierarchical Attention Model on the training dataset.

    :param model: The model to train.
    :type model: HANBaseModel
    :param batch_size: The batch size.
    :type batch_size: int
    :param train_epochs: The number of epochs to train.
    :type train_epochs: bool
    """
    class_weights = calculate_class_weights(read_trainset(epochs=1))
    module_logger.info('Starting training...')
    tflog_dir = os.path.join(os.path.curdir, Tensorflow.TFLOG)
    config = tf.ConfigProto(allow_soft_placement=True)
    with tf.Session(config=config) as sess:
        # need to initialize tables for embeddings lookup
        sess.run(tf.tables_initializer())
        saver = tf.train.Saver(tf.global_variables())
        checkpoint_path = create_checkpoint(model, sess)
        sess.run(tf.global_variables_initializer())
        # Initialize local variables for root mean squared error metric in regression case
        sess.run(tf.local_variables_initializer())
        iterator = batch_iterator(read_trainset(epochs=train_epochs), batch_size, 300)
        model.train_model(iterator, class_weights, tflog_dir, sess, saver, checkpoint_path)
        module_logger.info('evaluating on dev dataset...')
        accuracy = evaluate_accuracy(sess, model, read_devset(epochs=1), batch_size)
        module_logger.info('dev accuracy: %.2f' % accuracy)
