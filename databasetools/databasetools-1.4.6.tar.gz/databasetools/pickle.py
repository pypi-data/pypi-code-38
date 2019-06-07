try:
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle


class Pickle:
    """
    Save and load Python dictionaries in pickle .p format
    """
    def __init__(self, save_path):
        self.save_name = save_path

    def write(self, data_dict):
        with open(self.save_name, 'wb') as fp:
            pickle.dump(data_dict, fp, protocol=pickle.HIGHEST_PROTOCOL)

    def read(self):
        with open(self.save_name, 'rb') as fp:
            read_dictionary = pickle.load(fp)
            return dict(read_dictionary)