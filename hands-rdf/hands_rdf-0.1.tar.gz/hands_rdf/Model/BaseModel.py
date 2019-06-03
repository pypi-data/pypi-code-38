import numpy as np
from sklearn.model_selection import train_test_split
from .Config import config


class BaseModel:

    numeric_types = ["float64", "float32", "int32", "int64"]

    def __init__(self, df, filters=None):

        if filters is not None:
            df = BaseModel.filter_df(df, filters)

        self.df = df.copy()

    def labels(self):
        """
        Get a L
        :return:
        """
        return self.df[config.CLASS_TAG]

    def data_labels(self):
        df = self.df.copy()
        y_train = np.asarray(df[config.CLASS_TAG].copy())
        X_train = df.drop(config.CLASS_TAG, axis=1)
        return X_train[config.DATA_COLUMNS], y_train

    def training_split(self, columns=None, porc=0.8):
        """
        Get a training and test set, splitted
        :param columns: string[] Colums to use
        :param porc: float porcentage of data onto the traing set
        :return:
        """

        data = self.df.copy()
        if columns is not None:
            data = data[columns]
        train, test = train_test_split(data, test_size=1-porc, random_state=0)

        y_train = np.asarray(train[config.CLASS_TAG].copy())
        X_train = train.drop(config.CLASS_TAG, axis=1)

        y_test = np.asarray(test[config.CLASS_TAG].copy())
        X_test = test.drop(config.CLASS_TAG, axis=1)

        return X_train, y_train, X_test, y_test

    @staticmethod
    def filter_df(df, filters):
        """

        :param df: DataFrame
        :param filters: dict
                key => column, value => array of values of column of rows to discard
        :return:
        """
        df = df.copy()
        if filters is None or type(filters) is not dict:
            return df

        for key in filters:
            for value in filters[key]:
                i_delete = df.index[df[key] == value].tolist()
                df.drop(i_delete, inplace=True)
        return df