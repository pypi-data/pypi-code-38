import numpy as np
from .cary5000_acquired_data_handler import Cary5000AcquiredDataHandler


class Data:

    def __init__(self):
        self.wavelength = []
        self.transmission = []
        self.energy = None


class Cary5000FileReader:

    data_template = {
        'sample names': None,
        'acquired data': None
    }

    @staticmethod
    def read_data_from_gridfs(gridfs):
        data = Cary5000FileReader.data_template.copy()
        line = gridfs.readline()
        line_nr = 0
        while line is not b'':
            decoded_line = line.decode("utf-8")
            if line_nr == 0:
                data['sample names'] = Cary5000FileReader._read_sample_names(decoded_line)
            elif line_nr == 1:
                data_labels = Cary5000FileReader._read_data_labels(decoded_line)
                acquired_data_handler = Cary5000AcquiredDataHandler(data['sample names'], data_labels)
            elif line_nr > 1 and Cary5000FileReader._line_is_not_empty(decoded_line):
                acquired_data_handler.add_line_with_data(decoded_line)
            else:
                break
            line = gridfs.readline()
            line_nr += 1
        data['acquired data'] = acquired_data_handler.get_acquired_data()
        return data

    @staticmethod
    def _line_is_not_empty(line):
        line.rstrip()
        return len(line) > 2

    @staticmethod
    def read_data_from_file(filename):
        data = Cary5000FileReader.data_template.copy()
        with open(filename) as cary_5000_file:
            for line_nr, line in enumerate(cary_5000_file):
                if line_nr == 0:
                    data['sample names'] = Cary5000FileReader._read_sample_names(line)
                elif line_nr == 1:
                    data_labels = Cary5000FileReader._read_data_labels(line)
                    acquired_data_handler = Cary5000AcquiredDataHandler(data['sample names'], data_labels)
                elif line_nr > 1 and len(line) > 1:
                    acquired_data_handler.add_line_with_data(line)
                else:
                    break
        data['acquired data'] = acquired_data_handler.get_acquired_data()
        return data

    @staticmethod
    def _read_sample_names(line_with_sample_names):
        return line_with_sample_names.split(',,')[:-1]

    @staticmethod
    def _read_data_labels(line_with_data_labels):
        return line_with_data_labels.split(',')[:-1]

    @staticmethod
    def read_data(filename,**kwargs):

        if 'IgnoreEntries' in kwargs:
            ignore_entries = kwargs.get("IgnoreEntries")
        else:
            ignore_entries = []

        names = []
        wavelength = []
        transmission = []
        with open(filename, "br") as file:
            for count, line in enumerate(file):
                if line == b'\r\n':
                    break
                else:
                    line=str(line).strip('b\'')

                if count == 0:
                    for i,key in enumerate(line.split(',')):
                        if i%2==0 and i<len(line.split(','))-1:
                            names.append(key)
                    for i, tmp in enumerate(names):
                        transmission.append([])

                if count == 1:
                    pass    # maybe add or check the units and if its transmission
                if count > 1:
                    k=0
                    for i,key in enumerate(line.split(',')):
                        if i == 0:
                            wavelength.append(float(key))
                        elif i%2==1 and i<len(line.split(','))-1:
                            transmission[k].append(float(key))
                            k += 1

        data = dict()
        for i, key in enumerate(names):
            if key in ignore_entries:
                continue
            data[key]=Data()
            data[key].wavelength= np.array(wavelength)
            data[key].transmission = np.array(transmission[i])

        return data
