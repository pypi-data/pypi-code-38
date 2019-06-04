import numpy as np


class Survey:

    def __init__(self):
        self.energy = []
        self.counts = []


class Multi:

    def __init__(self):
        self.energy = {}
        self.counts = {}


class XPSDataReader:

    @staticmethod
    def read_survey(filename=None,gridfs=None):
        survey = Survey()
        if filename:
            with open(filename, "r") as file:
                for count, line in enumerate(file):
                    if count == 2:
                        if not XPSDataReader._is_survey(line):
                            raise ImportError(filename + ' is not a survey')
                    elif count == 4:
                        start_energy = float(line)
                    elif count == 5:
                        step_size = float(line)
                    elif count == 6:
                        data_points = int(line)
                        survey.energy = np.linspace(start_energy, start_energy + ((data_points-1) * step_size), data_points)
                    elif 6 < count< data_points + 7:
                        survey.counts.append(float(line))

                survey.counts = np.array(survey.counts)
            return survey
        elif gridfs:
            line = gridfs.readline()
            count=0
            while line is not b'':
                decoded_line = line.decode("utf-8")
                if count == 2:
                    if not XPSDataReader._is_survey(decoded_line):
                        raise ImportError(filename + ' is not a survey')
                elif count == 4:
                    start_energy = float(decoded_line)
                elif count == 5:
                    step_size = float(decoded_line)
                elif count == 6:
                    data_points = int(decoded_line)
                    survey.energy = np.linspace(start_energy, start_energy + ((data_points - 1) * step_size),
                                                data_points)
                elif 6 < count < data_points + 7:
                    survey.counts.append(float(line))
                count+=1
                line=gridfs.readline()

            survey.counts = np.array(survey.counts)
            return survey
        else:
            return

    @staticmethod
    def read_multi(filename=None,gridfs=None):
        multi = Multi()
        if filename:
            with open(filename, "r") as file:
                count = 0
                for line in file:
                    if count == 2:
                        if XPSDataReader._is_survey(line):
                            raise ImportError(filename + ' is a survey')
                        orbital = line.rstrip()
                        if orbital in multi.counts.keys():
                            count_orbitals = 0
                            for key in multi.counts.keys():
                                if orbital in key:
                                    count_orbitals+=1
                            orbital += '_' + str(count_orbitals)
                        multi.counts[orbital] = []
                        multi.energy[orbital] = []
                    elif count == 4:
                        start_energy = float(line)
                    elif count == 5:
                        step_size = float(line)
                    elif count == 6:
                        data_points = int(line)
                        multi.energy[orbital] = np.linspace(start_energy, start_energy + ((data_points-1) * step_size), data_points)
                    elif 6 < count < data_points + 7:
                        multi.counts[orbital].append(float(line))
                    elif count > 6 and count == data_points + 7:
                        multi.counts[orbital] = np.array(multi.counts[orbital])
                        count = -1
                    count += 1
            return multi
        elif gridfs:
            line = gridfs.readline()
            count = 0
            while line is not b'':
                decoded_line = line.decode("utf-8")
                if count == 2:
                    if XPSDataReader._is_survey(decoded_line):
                        raise ImportError(filename + ' is a survey')
                    orbital = str(decoded_line.rstrip())
                    multi.counts[orbital] = []
                    multi.energy[orbital] = []
                elif count == 4:
                    start_energy = float(decoded_line)
                elif count == 5:
                    step_size = float(decoded_line)
                elif count == 6:
                    data_points = int(decoded_line)
                    multi.energy[orbital] = np.linspace(start_energy, start_energy + ((data_points - 1) * step_size),
                                                        data_points)
                elif 6 < count < data_points + 7:
                    multi.counts[orbital].append(float(decoded_line))
                elif count > 6 and count == data_points + 7:
                    multi.counts[orbital] = np.array(multi.counts[orbital])
                    count = -1
                count += 1
                line = gridfs.readline()
            return multi
        else:
            return

    @staticmethod
    def _is_survey(line):
        return line.rstrip() == 'Sur1'

    @staticmethod
    def _is_multi(line):
        return line.rstrip() == 'Full'
