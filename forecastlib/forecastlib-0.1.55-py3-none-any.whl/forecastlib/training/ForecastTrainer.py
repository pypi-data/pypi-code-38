import numpy as np
import os
import pandas as pd
from azureml.core import Run, Datastore
from keras import Sequential
from keras.callbacks import Callback
from keras.layers import Dense, Dropout
from keras.regularizers import l1, l2
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.preprocessing import MinMaxScaler

from forecastlib.models.ForecastModel import ForecastModel
from forecastlib.training.Metrics import Metrics


class ForecastTrainer(object):
    MIN_EPOCH_COUNT = 10
    EPOCH_FLOATING_WINDOW_SIZE = 5

    def __init__(self, name, batch_size, epochs, nodes, test_data, train_data, accuracy_sample, features, dropout,
                 layers):
        self.name = name
        self.batch_size = batch_size
        self.epochs = epochs
        self.nodes = nodes
        self.features = features
        self.X_test = test_data[features]
        self.X_train = train_data[features]
        self.y_test = test_data["UPA_ACTUAL"]
        self.y_train = train_data["UPA_ACTUAL"]
        self.accuracy_sample = accuracy_sample
        self.layers = layers
        self.dropout = dropout
        self.regressor = Sequential()
        self.featureScaler = MinMaxScaler()  # TODO: parameter?
        self.labelScaler = MinMaxScaler()  # TODO: parameter?

        self.run = Run.get_context()

    def train(self):
        print('X_train:', pd.DataFrame(self.X_train).describe())
        print('y_train:', pd.DataFrame(self.y_train).describe())
        print('X_test:', pd.DataFrame(self.X_test).describe())
        print('X_test:', pd.DataFrame(self.y_test).describe())

        self.scale()
        self.build_regressor()
        return self.fit()

    def fit(self):
        self.callback = TimeHistory(self, self.epochs, self.accuracy_sample)
        losses = self.regressor.fit(self.X_train, self.y_train, callbacks=[self.callback])
        return losses, self.callback.accuracies

    def build_regressor(self):
        self.regressor = KerasRegressor(build_fn=self.setup_base_line_model, batch_size=self.batch_size,
                                        epochs=self.epochs, verbose=2)

    def setup_base_line_model(self):
        model = Sequential()

        model.add(Dense(self.nodes, input_dim=self.X_test.shape[1], activation='relu'))
        for x in range(self.layers):
            model.add(Dense(self.nodes, activation='relu'))
            model.add(Dropout(self.dropout))
        model.add(Dense(1, activation='linear'))
        model.compile(optimizer='adam', loss=ForecastTrainer.custom_loss_function, metrics=['mae'])

        return model

    def custom_loss_function(y_true, y_pred):
        return Metrics.absolute_relative_error(y_true, y_pred)

    def predict(self, x):
        if x.shape[0] == 0:
            return x

        xScaled = self.featureScaler.transform(x[self.features])
        y_pred = self.regressor.predict(xScaled)
        y_test_orig = self.labelScaler.inverse_transform(self.y_test)
        return self.labelScaler.inverse_transform(y_pred.reshape(-1, 1))

    def get_accuracy(self):
        y_pred = self.regressor.predict(self.X_test)
        y_test_orig = self.labelScaler.inverse_transform(self.y_test)
        y_pred_orig = self.labelScaler.inverse_transform(y_pred.reshape(-1, 1))

        return Metrics.model_accuracy(y_test_orig, y_pred_orig)

    def get_model_fit(self):
        y_pred = self.regressor.predict(self.X_train)
        y_test_orig = self.labelScaler.inverse_transform(self.y_train)
        y_pred_orig = self.labelScaler.inverse_transform(y_pred.reshape(-1, 1))

        return Metrics.model_accuracy(y_test_orig, y_pred_orig)

    def scale(self):
        self.X_train = self.featureScaler.fit_transform(self.X_train)
        self.X_test = self.featureScaler.transform(self.X_test)

        self.y_test = self.y_test.values.reshape(-1, 1)
        self.y_train = self.y_train.values.reshape(-1, 1)

        self.y_train = self.labelScaler.fit_transform(self.y_train)
        self.y_test = self.labelScaler.transform(self.y_test)

    # model, featureScaler, labelScaler, features):
    def get_model(self):
        return ForecastModel(self.regressor.model, self.featureScaler, self.labelScaler, self.features)

    def get_best_model(self):
        m = ForecastModel(self.regressor.model, self.featureScaler, self.labelScaler, self.features)
        m.model.load_weights(ForecastTrainer.get_weight_file_path(self.name))

        return m

    def save_best_model(self, model_name: str, path_prefix='/dbfs/mnt/ForecastStore/staging', ds: Datastore = None):
        if model_name is None or model_name == "None":  # due to invalid arg parsing
            return

        path = path_prefix.replace("/dbfs/", os.path.sep) + os.path.sep + model_name


        model = self.get_best_model()

        try:
            dbutils.fs.mkdirs(path)
        except (IOError, NameError) as detail:
            print(detail)
            print("dbutils not found, probably not running under DataBricks. Using OS filesystem")
            if not os.path.exists(path):
                os.makedirs(path)

        model.save(path + os.path.sep)

        print("Model {0} successfully saved to path: {1}".format(model_name, path))

        return path

    @staticmethod
    def get_weight_file_path(runId):
        return runId + ".weights.h5"


class TimeHistory(Callback):
    def __init__(self, m: ForecastTrainer, epochs, accuracy_sample):
        self.m = m
        self.accuracy_sample = accuracy_sample
        self.accuracies = []
        self.model_fits = []
        self.floating_score = 0

    def on_epoch_end(self, epoch, logs={}):
        if (self.accuracy_sample == 0):
            accuracy = self.m.get_accuracy()
            model_fit = self.m.get_model_fit()
        else:
            if (epoch % self.accuracy_sample == 0):
                accuracy = self.m.get_accuracy()
                model_fit = self.m.get_model_fit()
            else:
                accuracy = self.accuracies[epoch - 1]
                model_fit = self.model_fits[epoch - 1]

        self.accuracies.append(accuracy)
        self.model_fits.append(model_fit)
        self.m.run.log("accuracy", accuracy)
        self.m.run.log("model_fit", model_fit)

        self.checkpoint(epoch)

    def checkpoint(self, epoch):
        if epoch < ForecastTrainer.MIN_EPOCH_COUNT:
            return

        floating_score = np.mean(self.accuracies[-ForecastTrainer.EPOCH_FLOATING_WINDOW_SIZE:])

        if floating_score <= self.floating_score:
            return

        self.floating_score = floating_score
        self.floating_model_weights = self.m.regressor.model.save_weights(
            ForecastTrainer.get_weight_file_path(self.m.name))
        self.saved_epoch = epoch
