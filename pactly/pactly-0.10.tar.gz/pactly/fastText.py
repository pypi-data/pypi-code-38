#! /usr/bin/env python3
import sys
import time
import os
import gc
RANDOM_SEED = 17
os.environ['PYTHONHASHSEED']=str(RANDOM_SEED)

import gzip
import random
import numpy
import dill as pickle
pickle.settings['recurse'] = True

from keras import backend as K
import tensorflow as tf

from keras.initializers import RandomUniform, glorot_uniform, Orthogonal
from keras.optimizers import Adam
from keras.utils import to_categorical
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding, GlobalAveragePooling1D, InputLayer
from keras.layers import Dropout, LSTM, Bidirectional, GlobalMaxPool1D
from keras.models import load_model, model_from_json
from keras.callbacks import TensorBoard, ReduceLROnPlateau, EarlyStopping


class Text2Dataset:
    def __init__(self, word_ngrams=1, min_count=1):
        self.word_ngrams = word_ngrams
        self.min_count = min_count

        self.word2idx = None
        self.words2idx = None
        self.label2idx = None
        self.idx2label = None
        self.train_X = None
        self.train_y = None
        self.max_features = None
        self.token_indice = None
        self.max_len = None

    def preprocess(self, strings):
        """
            Convert list of strings to fastText prediction input format.
        """
        preprocessed_strings = []

        for string in strings:
            text = (
                ",".join([words for words in string.split(",")])
                .strip()
                .replace("\n", "")
            )
            preprocessed_string = self.words2idx(text)
            preprocessed_string = self.add_ngram([preprocessed_string])
            preprocessed_string = sequence.pad_sequences(
                preprocessed_string, maxlen=self.max_len
            )
            preprocessed_strings.append(preprocessed_string)

        return preprocessed_strings

    def create_ngram_set(self, input_list, ngram_value=2):
        return set(zip(*[input_list[i:] for i in range(ngram_value)]))

    def add_ngram(self, sequences):
        new_sequences = []
        for input_list in sequences:
            new_list = input_list[:]
            for ngram_value in range(2, self.word_ngrams + 1):
                for i in range(len(new_list) - ngram_value + 1):
                    ngram = tuple(new_list[i : i + ngram_value])
                    if ngram in self.token_indice:
                        new_list.append(self.token_indice[ngram])
            new_sequences.append(new_list)

        return new_sequences

    def text2List(self, dataset):
        # Create lists of words and labels with input training dataset
        words_list = dataset["clean_text"].values.tolist()
        label_list = dataset["Label"].values.tolist()

        return words_list, label_list

    def load_dataset(self, train_data, val_data):
        """
            Crate n-grams dictionary of the dataset, return
            input and output vectors.
        """
        words_list, label_list = self.text2List(train_data)
        words_list_val, label_list_val = self.text2List(val_data)

        label_words_dict = {}
        for label, words in zip(label_list, words_list):
            if len(words) > self.min_count:
                if label in label_words_dict:
                    label_words_dict[label].append(words)
                else:
                    label_words_dict[label] = []

        self.label2idx = {label: idx for idx, label in enumerate(label_words_dict)}
        self.idx2label = {self.label2idx[label]: label for label in self.label2idx}
        self.word2idx = {
            word: idx for idx, word in enumerate(set(" ".join(words_list).split()))
        }
        self.words2idx = lambda words: [
            self.word2idx[word] for word in words.split() if word in self.word2idx
        ]

        self.train_X = [self.words2idx(words) for words in words_list]
        self.train_y = [self.label2idx[label] for label in label_list]
        self.max_features = len(self.word2idx)
        
        self.val_X = [self.words2idx(words) for words in words_list_val]
        self.val_y = [self.label2idx[label] for label in label_list_val]

        if self.word_ngrams > 1:
            print("Adding {}-gram features".format(self.word_ngrams))
            ngram_set = set()
            for input_list in self.train_X:
                for i in range(2, self.word_ngrams + 1):
                    set_of_ngram = self.create_ngram_set(input_list, ngram_value=i)
                    ngram_set.update(set_of_ngram)

            start_index = self.max_features + 1
            self.token_indice = {v: k + start_index for k, v in enumerate(ngram_set)}
            indice_token = {self.token_indice[k]: k for k in self.token_indice}

            self.max_features = numpy.max(list(indice_token.keys())) + 1

            self.train_X = self.add_ngram(self.train_X)
            self.val_X = self.add_ngram(self.val_X)
        return self.train_X, self.train_y, self.val_X, self.val_y


class FastText:
    def __init__(self, arch="shallow", word_ngrams=3, min_count=1, args=None):
        if args is None:
            self.text2Dataset = Text2Dataset(word_ngrams, min_count)
            self.arch = arch
            self.max_features = None
            self.maxlen = None
            self.batch_size = None
            self.embedding_dims = None
            self.epochs = None
            self.lr = None
            self.num_classes = None
            self.model = None
        else:
            (
                word_ngrams,
                min_count,
                word2idx,
                label2idx,
                token_indice,
                max_len,
                self.max_features,
                self.maxlen,
                self.batch_size,
                self.embedding_dims,
                self.epochs,
                self.lr,
                self.num_classes,
                model_weights,
                self.arch,
            ) = args
            self.text2Dataset = Text2Dataset(word_ngrams, min_count)
            self.text2Dataset.word2idx = word2idx
            self.text2Dataset.words2idx = lambda words: [
                word2idx[word] for word in words.split() if word in word2idx
            ]
            self.text2Dataset.label2idx = label2idx
            self.text2Dataset.idx2label = {
                label2idx[label]: label for label in label2idx
            }
            self.text2Dataset.token_indice = token_indice
            self.text2Dataset.max_len = max_len
            self.model = self.build_model(model_weights)

    def precision(self, y_true, y_pred):
        agreement = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        true_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        precision = agreement / (predicted_positives + K.epsilon())

        return precision

    def recall(self, y_true, y_pred):
        agreement = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        true_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = agreement / (true_positives + K.epsilon())

        return recall

    def build_model(self, weights=None):

        if self.arch == "deep":
            model = Sequential(
                [
                    InputLayer(input_shape=(self.maxlen,), dtype="int32"),
                    Embedding(
                        self.max_features, 
                        self.embedding_dims, 
                        input_length=self.maxlen,
                        embeddings_initializer=RandomUniform(seed=RANDOM_SEED)
                    ),
                    Bidirectional(LSTM(
                            50, 
                            return_sequences=True,
                            kernel_initializer=glorot_uniform(seed=RANDOM_SEED),
                            recurrent_initializer=Orthogonal(seed=RANDOM_SEED)
                        )
                    ),
                    GlobalMaxPool1D(),
                    Dropout(0.3, seed=RANDOM_SEED),
                    Dense(
                        50, 
                        activation="relu",
                        kernel_initializer=glorot_uniform(seed=RANDOM_SEED)),
                    Dropout(0.3, seed=RANDOM_SEED),
                    Dense(
                        2, 
                        activation="sigmoid",
                        kernel_initializer=glorot_uniform(seed=RANDOM_SEED)
                    ),
                ]
            )

        elif self.arch == "shallow":
            model = Sequential(
                [
                    InputLayer(input_shape=(self.maxlen,), dtype="int32"),
                    Embedding(
                        self.max_features, 
                        self.embedding_dims, 
                        input_length=self.maxlen,
                        embeddings_initializer=RandomUniform(seed=RANDOM_SEED)
                    ),
                    Bidirectional(LSTM(
                            16, 
                            return_sequences=True,
                            kernel_initializer=glorot_uniform(seed=RANDOM_SEED),
                            recurrent_initializer=Orthogonal(seed=RANDOM_SEED)
                        )
                    ),
                    GlobalMaxPool1D(),
                    Dense(
                        2, 
                        activation="sigmoid",
                        kernel_initializer=glorot_uniform(seed=RANDOM_SEED)
                    ),
                ]
            )

        model.compile(
            loss="binary_crossentropy",
            optimizer=Adam(lr=self.lr),
            metrics=["acc", self.recall],
        )

        if weights is not None:
            model.set_weights(weights)
        return model

    def train(
        self,
        train_data,
        val_data,
        maxlen=400,
        batch_size=32,
        embedding_dims=100,
        epochs=5,
        learning_rate=0.001,
        verbose=1,
    ):
        train_X, train_y, val_X, val_y = self.text2Dataset.load_dataset(train_data, val_data)
        del train_data, val_data

        self.max_features = self.text2Dataset.max_features
        self.maxlen = maxlen
        self.text2Dataset.max_len = self.maxlen
        self.batch_size = batch_size
        self.embedding_dims = embedding_dims
        self.epochs = epochs
        self.lr = learning_rate
        self.num_classes = len(set(train_y))

        self.model = self.build_model()

        train_X = sequence.pad_sequences(train_X, maxlen=self.maxlen)
        train_Y = to_categorical(train_y, self.num_classes)
        
        val_X = sequence.pad_sequences(val_X, maxlen=self.maxlen)
        val_Y = to_categorical(val_y, self.num_classes)
        """
        time_stamp = time.strftime("%Y_%m_%d_%H_%M_%S")
        kerasboard = TensorBoard(
            log_dir="logs/{}".format(time_stamp),
            batch_size=self.batch_size,
            histogram_freq=1,
            write_grads=False
        )
        early_stop = EarlyStopping(
            monitor='val_loss', 
            min_delta=0, patience=2, 
            verbose=0, mode='auto', 
            restore_best_weights=True
            )
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss', factor=0.1, 
            patience=1, verbose=0, mode='auto', 
            min_delta=0.0001, cooldown=0, min_lr=0)
        """
        #class_weights = {0: 2, 1: 1}
        self.model.fit(
            train_X,
            train_Y,
            batch_size=self.batch_size,
            epochs=self.epochs,
            verbose=verbose,
            validation_data=(val_X, val_Y),
            #callbacks=[kerasboard, early_stop],
        )
        #print(early_stop.stopped_epoch)
        #print("tensorboard --logdir="+kerasboard.log_dir)
        return self

    def save_model_json(self, model_path):
        model_json = self.model.to_json()
        with open("{0}.json".format(model_path), "w") as json_file:
            json_file.write(model_json)

        self.model.save_weights("{0}.h5".format(model_path))
        return

    def save_ngram_vectorizer(self, model_path):
        with open("{0}.pkl".format(model_path), "wb") as file:
            pickle.dump(self.text2Dataset, file, protocol=4)
        return

    def save_model(self, filename, directory):
        """
            Save the model in binary and json + h5 formats.
        """
        model_path = os.path.join(directory, filename)

        self.save_model_json(model_path)
        self.save_ngram_vectorizer(model_path)
        print("Model files are saved to {}.".format(directory))
        return

    def reset_session(self):
        K.clear_session()
        tf.reset_default_graph()
        return

    def predict(self, text, k=1):
        """
            Return the k most likely labels for the input text.
        """
        text = ",".join([words for words in text.split(",")]).strip().replace("\n", "")
        X = self.text2Dataset.words2idx(text)
        X = self.text2Dataset.add_ngram([X])
        X = sequence.pad_sequences(X, maxlen=self.maxlen)
        predict = self.model.predict(X).flatten()
        results = [
            (self.text2Dataset.idx2label[idx], predict[idx])
            for idx in range(len(predict))
        ]
        return sorted(results, key=lambda item: item[1], reverse=True)[:k]

    def calculate_accuracy_metrics(self, pred_val, true_val, show_results=True):
        """ 
            Calculate precision, recall and f1 score given arrays of predicted
            values and true values. 
        """
        model_metrics = {
            "true_pos": 0,
            "false_pos": 0,
            "true_neg": 0,
            "false_neg": 0,
            "precision": 0,
            "recall": 0,
            "f1_score": 0,
        }

        try:
            pred_val[pred_val > 0.5] = 1
            pred_val[pred_val <= 0.5] = 0
        except:
            pass

        model_metrics["true_pos"] = int(numpy.sum(
            numpy.logical_and(pred_val == 1, true_val == 1))
        )
        model_metrics["true_neg"] = int(numpy.sum(
            numpy.logical_and(pred_val == 0, true_val == 0))
        )
        model_metrics["false_pos"] = int(numpy.sum(
            numpy.logical_and(pred_val == 1, true_val == 0))
        )
        model_metrics["false_neg"] = int(numpy.sum(
            numpy.logical_and(pred_val == 0, true_val == 1))
        )

        try:
            model_metrics["precision"] = model_metrics["true_pos"] / (
                model_metrics["true_pos"] + model_metrics["false_pos"]
            )
        except ZeroDivisionError:
            model_metrics["precision"] = 0

        try:
            model_metrics["recall"] = model_metrics["true_pos"] / (
                model_metrics["true_pos"] + model_metrics["false_neg"]
            )
        except ZeroDivisionError:
            model_metrics["recall"] = 0

        try:
            model_metrics["f1_score"] = 2 * (
                (model_metrics["precision"] * model_metrics["recall"])
                / (model_metrics["precision"] + model_metrics["recall"])
            )
        except ZeroDivisionError:
            model_metrics["f1_score"] = 0

        if show_results:
            print("Precision: {0:4f}".format(model_metrics["precision"]))
            print("Recall: {0:4f}".format(model_metrics["recall"]))
            print("F1 Score: {0:4f}".format(model_metrics["f1_score"]))

        return model_metrics

    def get_accuracy_metrics(self, dataset):
        preds, real = [], []
        preds, real = numpy.array(preds), numpy.array(real)
        model = self.model
        for row in dataset.itertuples(index=True, name="Pandas"):
            if getattr(row, "Label") == "__label__0":
                real = numpy.append(real, 0)
            elif getattr(row, "Label") == "__label__1":
                real = numpy.append(real, 1)

            if self.predict(getattr(row, "clean_text"))[0][0] == "__label__0":
                preds = numpy.append(preds, 0)
            elif self.predict(getattr(row, "clean_text"))[0][0] == "__label__1":
                preds = numpy.append(preds, 1)

        metrics = self.calculate_accuracy_metrics(preds, real)
        return metrics

    def evaluate_performance(self, train_set, dev_set, test_set, acceptance_f1_score):
        """
            DEVNOTE: Train, dev and test sets need to evaluated separately. 
            evaluate_performance, calculate_accuracy_metrics and get_accuracy_metrics
            should be eliminated and a new function should be added to convert the fastText
            prediction output to the required input format of keras.evaluate().
        """

        train_results = self.get_accuracy_metrics(train_set)
        dev_results = self.get_accuracy_metrics(dev_set)
        test_results = self.get_accuracy_metrics(test_set)

        if dev_results["f1_score"] > acceptance_f1_score:
            deployable = True
        else:
            deployable = False

        return {
            "deployable": deployable,
            "results": {
                "train": train_results,
                "dev": dev_results,
                "test": test_results,
            },
        }


def train_supervised(
    train_data,
    val_data,
    model_arch,
    learning_rate=0.01,
    dim=100,
    epoch=5,
    min_count=1,
    word_ngrams=3,
    verbose=1,
    maxlen=100,
):  
    numpy.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    
    K.clear_session()
    tf.reset_default_graph()

    tf.set_random_seed(RANDOM_SEED)
    #sess = tf.Session(graph=tf.get_default_graph())
    session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
    sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
    K.set_session(sess)
    
    fastText = FastText(arch=model_arch, word_ngrams=word_ngrams, min_count=min_count)
    fastText.train(
        train_data=train_data,
        val_data=val_data,
        maxlen=maxlen,
        embedding_dims=dim,
        epochs=epoch,
        learning_rate=learning_rate,
        verbose=verbose,
    )
    return fastText