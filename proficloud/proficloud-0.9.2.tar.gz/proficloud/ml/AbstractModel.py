from abc import ABC, abstractmethod
import jsonpickle

class AbstractModelClass(ABC):
    """
    This is the base Class for Models.
    It provides a standard interface with train, predict, predict_sample and summary methods for the model.
    It further provides save and load functionality.
    """
    
    def __init__(self):
        self.signal_names = None
        """Signal / feature names used within the model"""

        super(AbstractOperation, self).__init__()

    @abstractmethod
    def train(self, data):
        """
        This is the method to train the model. 
        The data parameter is the dataframe to use.
        Must be implemented by Model.

        :type data: pandas.DataFrame
        :param data: Dataframe to train the model.
        :return: Does not return. Throw on exception during training.
        :rtype: void
        """
        pass

    @abstractmethod
    def predict(self, data):
        """
        This is the method to predict a whole dataset. 
        The data parameter is the dataframe to use.
        Must be implemented by Model.

        :type data: pandas.DataFrame
        :param data: Dataframe to evaluate
        :return: Returns list with an entry for each row of the dataframe.
        :rtype: list
        """
        pass

    @abstractmethod
    def predict_sample(self, sample):
        """
        This is the method to predict a single sample. 
        The sample parameter is sample to predict.
        Must be implemented by Model.

        :type sample: pandas.Series / numpy.array
        :param sample: Single sample to predict
        :return: Returns prediction for sample
        :rtype: any
        """
        pass

    @abstractmethod
    def summary(self):
        """
        A summary method for the model

        :return: Summary text
        :rtype: str
        """
        pass

    def save(self, file_name):
        """
        Save model to json.

        :type file_name: str
        :param file_name: Target file name.
        """
        jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        jsonModel = jsonpickle.encode(self, make_refs=True, max_depth=1000, keys=False)
        f = open(file_name, "wb")
        f.write(jsonModel.encode('utf-8'))
        f.close()

    @staticmethod
    def load(file_name):
        """
        Load model from json file.

        :type file_name: str
        :param file_name: Source file name.
        :return: Model instance
        :rtype: AbstractModelClass
        """
        f = open(file_name, "r")
        jsonRead = f.read().encode('utf-8').decode("utf-8")
        f.close()
        model_read = jsonpickle.decode(jsonRead, classes=[StateTimingModel], keys=False)
        return model_read