class DataSetIsEmpty(Exception):
    def __init__(self, message):
        super(DataSetIsEmpty, self).__init__(message)


class ModelIsNotTrained(Exception):
    def __init__(self, message):
        super(ModelIsNotTrained, self).__init__(message)