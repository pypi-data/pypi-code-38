import numpy as np
import pandas as pd

from .Config import config
from .BaseModel import BaseModel
from glob import glob


class MultiModels:
    """
    Class that represents all the data in the program
    """
    COLUMN_NAMES = config.DATA_COLUMNS + [config.CLASS_TAG]

    def __init__(self, files_list, filters=None, mode='pandas'):
        """

        :param im_shape: Tuple image dimensions in pixels
        :param balance: bool true if you want the same number of data of every class
        """
        self.__data_files = files_list
        self.last = len(self.__data_files) - 1
        self.filters = filters
        self.mode = mode

    def __iter__(self):
        self.current = 0
        return self

    def __next__(self):
        """

        :return: string, BaseModel
        """
        if self.current <= self.last:
            file = self.__data_files[self.current]
            if self.mode == 'pandas':
                result = BaseModel(
                    df=pd.DataFrame(np.load(file), columns=self.COLUMN_NAMES),
                    filters=self.filters
                )

            else:
                result = np.load(file)

            self.current += 1
            return file, result
        else:
            raise StopIteration

    def __getitem__(self, item):
        if item <= self.last:
            file = self.__data_files[item]
            if self.mode == 'pandas':
                result = BaseModel(
                    df=pd.DataFrame(np.load(file), columns=self.COLUMN_NAMES),
                    filters=self.filters
                )

            else:
                result = np.load(file)

            return file, result
        else:
            raise StopIteration

    def __len__(self):
        return len(self.__data_files)


class TrainModels(MultiModels):

    def __init__(self, filters=None, mode='pandas'):
        files = glob(config.FILE_DATA)
        if len(files) == 0:
            raise Exception("No models found in:" + str(config.FILE_DATA))
        super().__init__(
            files,
            filters,
            mode
        )


class TestModels(MultiModels):

    def __init__(self, filters=None, mode='pandas'):
        super().__init__(
            glob(config.FILE_TEST_DATA),
            filters,
            mode
        )

    def fullModel(self):
        dfs = []
        for file in self.__data_files:
            dfs.append(
                pd.DataFrame(np.load(file), columns=self.COLUMN_NAMES)
            )

        return BaseModel(
            pd.concat(dfs, ignore_index=True),
            filters=self.filters
        )
