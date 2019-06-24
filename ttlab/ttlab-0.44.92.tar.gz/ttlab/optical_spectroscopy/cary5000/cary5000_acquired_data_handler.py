import numpy as np


class Cary5000AcquiredDataHandler:

    def __init__(self,sample_names, data_labels):
        self.sample_names = sample_names
        self.data_labels = data_labels
        self.acquired_data = self._create_acquired_data_dictionary(sample_names, data_labels)

    def add_line_with_data(self,line_with_data_values):
        values = Cary5000AcquiredDataHandler._read_float_values_from_line(line_with_data_values)
        for index, name in enumerate(self.sample_names):
            self.acquired_data[name][self.data_labels[index * 2]] = np.append(self.acquired_data[name][self.data_labels[index*2]], values[index*2])
            self.acquired_data[name][self.data_labels[index * 2 + 1]] = np.append(self.acquired_data[name][self.data_labels[index*2+1]], values[index*2+1])

    def get_acquired_data(self):
        return self.acquired_data.copy()

    @staticmethod
    def _read_float_values_from_line(line):
        values = line.split(',')[:-1]
        return Cary5000AcquiredDataHandler._convert_to_floats(values)

    @staticmethod
    def _convert_to_floats(list_with_strings):
        return list(map(float, list_with_strings))

    @staticmethod
    def _create_acquired_data_dictionary(sample_names,data_labels):
        acquired_data = Cary5000AcquiredDataHandler._create_dictionary_with_sample_names_as_keys(sample_names)
        Cary5000AcquiredDataHandler._add_dictionary_with_data_labels_to_each_key(acquired_data,data_labels)
        return acquired_data

    @staticmethod
    def _create_dictionary_with_sample_names_as_keys(sample_names):
        dictionary = {}
        for name in sample_names:
            dictionary[name] = {}
        return dictionary

    @staticmethod
    def _add_dictionary_with_data_labels_to_each_key(dictionary,data_labels):
        for index,key in enumerate(dictionary.keys()):
            dictionary[key][data_labels[index*2]] = np.array([])
            dictionary[key][data_labels[index*2+1]] = np.array([])