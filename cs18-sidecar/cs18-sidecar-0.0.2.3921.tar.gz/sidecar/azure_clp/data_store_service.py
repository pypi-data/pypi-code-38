import abc


class DataStoreService(metaclass=abc.ABCMeta):

    def __init__(self):
        pass

    def find_data_by_id(self, data_id: str) -> dict:
        pass

    def update_data(self, data_id: str, data: str, column_name: str):
        pass
