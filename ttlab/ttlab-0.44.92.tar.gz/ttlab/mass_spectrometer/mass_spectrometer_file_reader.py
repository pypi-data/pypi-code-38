import re
from .mass_spectrometer_acquired_data_handler import MassSpectrometerAcquiredDataHandler
from .mass_spectrometer_date_handler import MassSpectrometerDateHandler


class MassSpectrometerFileReader:
    data_template = {
        'start time': None,
        'end time': None,
        'gases': None,
        'acquired data': None
    }

    @staticmethod
    def read_data_from_file(filename):
        data = MassSpectrometerFileReader.data_template.copy()
        with open(filename) as mass_spectrometer_file:
            for line_nr, line in enumerate(mass_spectrometer_file):
                if line_nr == 3:
                    data['start time'] = MassSpectrometerFileReader._read_start_time(line)
                elif line_nr == 4:
                    data['end time'] = MassSpectrometerFileReader._read_end_time(line)
                elif line_nr == 6:
                    data['gases'] = MassSpectrometerFileReader._read_gases(line)
                    acquired_data_handler = MassSpectrometerAcquiredDataHandler(data['gases'])
                elif line_nr > 7:
                    acquired_data_handler.add_line_of_data(line)
        data['acquired data'] = acquired_data_handler.acquired_data
        return data

    @staticmethod
    def read_data_from_gridfs(gridfs):
        data = MassSpectrometerFileReader.data_template.copy()
        line = gridfs.readline()
        line_nr = 0
        while line is not b'':
            decoded_line = line.decode("utf-8")
            if line_nr == 3:
                data['start time'] = MassSpectrometerFileReader._read_start_time(decoded_line)
            elif line_nr == 4:
                data['end time'] = MassSpectrometerFileReader._read_end_time(decoded_line)
            elif line_nr == 6:
                data['gases'] = MassSpectrometerFileReader._read_gases(decoded_line)
                acquired_data_handler = MassSpectrometerAcquiredDataHandler(data['gases'])
            elif line_nr > 7:
                acquired_data_handler.add_line_of_data(decoded_line)
            line = gridfs.readline()
            line_nr += 1
        data['acquired data'] = acquired_data_handler.acquired_data
        return data

    @staticmethod
    def _read_start_time(line_with_start_time):
        date = MassSpectrometerFileReader._extract_date(line_with_start_time)
        return MassSpectrometerDateHandler.convert_date_to_unix_time(date)

    @staticmethod
    def _read_end_time(line_with_end_time):
        date = MassSpectrometerFileReader._extract_date(line_with_end_time)
        return MassSpectrometerDateHandler.convert_date_to_unix_time(date)

    @staticmethod
    def _read_gases(line_with_gas_names):
        gases = line_with_gas_names.split('\t')
        return list(filter((lambda x: not (x == '' or x == '\n')), gases))

    @staticmethod
    def _extract_date(string):
        return re.findall('\d+/\d+/\d\d\d\d\s\d\d\:\d\d\:\d\d\.\d+\s\D\D', string)[0]

    @staticmethod
    def _read_line_nr(filename, nr):
        file = open(filename, 'r')
        i = 0
        for line in file:
            if i == nr:
                file.close()
                return line
            i += 1
        raise ValueError('Line nr: ' + str(nr) + ' does not exist in file ' + filename)
