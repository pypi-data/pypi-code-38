from pprint import pprint
from databasetools.json import JSON
from databasetools.pickle import Pickle
import collections


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class DictTools:
    def __init__(self, path, protocol='json', enable_printing=True):
        """
        Save or load data to or from .npy dictionary file
        :param path: Directory to save or load file from
        :param protocol: Method for saving and loading dictionaries
        """
        # Get dictionary of protocals
        protocols_dict = self.protocol_options()

        # Remove leading '.' if included in protocol var
        self.choice = protocol.strip('.')
        try:
            self.protocol = protocols_dict[self.choice]
        except KeyError:
            # Use Numpy as default
            self.protocol = protocols_dict['json']

        self.enable_printing = enable_printing
        # Join root directory and save name to create full path
        self.save_name = str(path) + self.protocol['ext']

    def __iter__(self):
        return iter(self.load)

    @property
    def choices(self):
        """
        Print dictionary of protocal choices for reference
        :return: protocals dictionary
        """
        protocols_dict = self.protocol_options()
        pprint(protocols_dict)
        return protocols_dict

    @staticmethod
    def protocol_options():
        protocols_dict = {
            'pickle': {
                'class': Pickle,
                'ext': '.p'
            },
            'json': {
                'class': JSON,
                'ext': '.json'
            },
        }
        return protocols_dict

    def save(self, data_dict):
        dict_class = self.protocol['class']
        dict_class(self.save_name).write(data_dict)
        if self.enable_printing:
            print(self.choice + " saved to " + self.save_name)

    @property
    def load(self):
        try:
            dict_class = self.protocol['class']
            read_dictionary = dict_class(self.save_name).read()
            return read_dictionary
        except IOError:
            if self.enable_printing:
                print('Error: Unable to load file ' + str(self.save_name))

