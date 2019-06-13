from keras import models, layers
from keras.layers import Input, Dense
from keras.layers import Embedding, Dropout
from keras.layers import Conv1D
from keras.layers import GlobalMaxPooling1D
from keras.layers import Activation

from ..application import Application

from ...lib.general_lib import *

from ...lib.text_lib import get_words_from_text

import numpy as np

import random

from keras.preprocessing import sequence
from keras.models import load_model
import keras


class Sentiment_Analysis(Application):
    def __init__(self, model_path=None):
        """Initializes a model.

        Arguments:
            Application {class} -- A super class of neural network models.

        Keyword Arguments:
            model_path {str} -- A path of model file. (default: {None})
        """
        if not isinstance(model_path, type(None)):
            try:
                self.model = load_model(model_path)
                if isinstance(self.model, type(None)):
                    print('Nothing loaded')
            except Exception as e:
                print('Model loading failed')
                raise e
        Application.__init__(self)

    def set_input_dictionary(self, input_dictionary):
        self.model.input_dictionary = input_dictionary

    def init_input_data(self, sentiment_texts, max_num_of_words=150):
        x = []
        for i, text in enumerate(sentiment_texts):
            word_list = get_words_from_text(
                text.lower())  # we will lower all words
            single_element = list()
            for word in word_list:
                if word in self.model.input_dictionary:
                    single_element.append(self.model.input_dictionary[word])
            x.append(single_element)
        x = sequence.pad_sequences(x, maxlen=max_num_of_words)
        return x

    def prepare_train_data(
            self,
            sentiment_texts,
            sentiment_values,
            skip_top,
            num_of_words_to_consider,
            max_num_of_words=150):
        """Prepares training data.

        Arguments:
            sentiment_texts {list} -- A list of sentiment texts.
            sentiment_values {list} -- A list of sentiment values.
            skip_top {int} -- Top most frequent words to ignore. Like and, are, is, I, etc.
            num_of_words_to_consider {int} -- Top most frequent words to consider except skip_top.

        Keyword Arguments:
            max_num_of_words {int} -- A max number of words in each text of sentiment_texts (default: {150})
        """
        if hasattr(self, 'model') == False:
            word_freq_dict = dict()
            for text in sentiment_texts:
                word_list = get_words_from_text(
                    text.lower())  # we will lower all words
                for word in word_list:
                    if word in word_freq_dict:
                        word_freq_dict[word] += 1
                    else:
                        word_freq_dict[word] = 1
            sorted_words = sorted(word_freq_dict.items(),
                                  key=lambda x: x[1], reverse=True)
            words_to_consider = sorted_words[skip_top: skip_top +
                                             num_of_words_to_consider]
            input_dictionary = dict()
            for i, word_tuple in enumerate(words_to_consider):
                input_dictionary[word_tuple[0]] = i
            input_shape = (max_num_of_words, )
            num_classes = len(set(sentiment_values))
            self.model = self.create_model(
                input_shape, len(input_dictionary), num_classes)
            self.set_input_dictionary(input_dictionary)
        x = self.init_input_data(sentiment_texts, max_num_of_words)
        y = keras.utils.to_categorical(np.asarray(
            sentiment_values), num_classes=self.model.output_shape[1])
        return x, y

    def create_model(self, input_shape, input_dim, num_classes):
        input_layer = Input(shape=input_shape)
        embedding1 = Embedding(
            input_dim, 128, input_length=input_shape[0])(input_layer)
        drop1 = Dropout(0.2)(embedding1)
        conv1 = Conv1D(64, 5, padding='valid',
                       activation='relu', strides=1)(drop1)
        pool1 = GlobalMaxPooling1D()(conv1)
        dense1 = Dense(256)(pool1)
        drop2 = Dropout(0.2)(dense1)
        act1 = Activation('relu')(drop2)
        output_layer = Dense(num_classes, activation='sigmoid')(act1)
        return models.Model(inputs=input_layer, outputs=output_layer)

    def compile_model(self, optimizer, loss, metrics=['accuracy']):
        self.model.compile(optimizer, loss=loss, metrics=metrics)

    def train(self,
              x,
              y,
              optimizer='nadam',
              metrics=['accuracy'],
              batch_size=None,
              steps_per_epoch=None,
              epochs=1,
              verbose=1,
              callbacks=None,
              shuffle=True):
        self.compile_model(optimizer=optimizer,
                           loss='categorical_crossentropy', metrics=metrics)
        self.model.fit(
            x,
            y,
            batch_size=batch_size,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            verbose=verbose,
            callbacks=callbacks,
            shuffle=shuffle)

    def predict(self, data_array=None, batch_size=32, verbose=0, steps=None):
        probs = self.model.predict(
            data_array, batch_size=batch_size, verbose=verbose, steps=steps)
        predicted_classes = probs.argmax(axis=-1)
        return predicted_classes
