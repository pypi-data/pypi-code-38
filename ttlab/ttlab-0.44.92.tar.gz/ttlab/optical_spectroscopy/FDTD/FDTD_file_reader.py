import numpy as np


class Data:

    def __init__(self):
        self.wavelength = []
        self.cross_section = []
        self.energy = None

class FDTDFileReader:

    @staticmethod
    def read_data(filename_cross_section, filename_wavelength, simulation_names):
        names = []
        wavelength = []
        cross_section = []
        for i, _ in enumerate(simulation_names):
            cross_section.append([])

        with open(filename_wavelength, "r") as file:
            for count, line in enumerate(file):
                wavelength.append(float(line))
        with open(filename_cross_section, "r") as file:
            for count, line in enumerate(file):
                for i, number in enumerate(line.split('\t')):
                    cross_section[i].append(float(number))

        data = dict()
        for i, key in enumerate(simulation_names):
            data[key] = Data()
            data[key].wavelength = np.array(wavelength) * 1e9  # convert to nm
            data[key].cross_section = np.array(cross_section[i])

        return data

