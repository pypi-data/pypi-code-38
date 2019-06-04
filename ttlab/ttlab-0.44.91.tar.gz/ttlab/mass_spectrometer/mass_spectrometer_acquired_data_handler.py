from .mass_spectrometer_date_handler import MassSpectrometerDateHandler


class MassSpectrometerAcquiredDataHandler:

    acquired_data_keys = ['Time', 'Time Relative [s]', 'Ion Current [A]']


    def __init__(self, gases):
        self.gases = gases
        self.acquired_data = {}
        self._initialize_acquired_data(gases)

    def _initialize_acquired_data(self, gases):
        for gas in gases:
            self.acquired_data[gas] = {
                self.acquired_data_keys[0]: [],
                self.acquired_data_keys[1]: [],
                self.acquired_data_keys[2]: []
            }

    def add_line_of_data(self,line):
        values = line.rstrip('\n').split('\t')
        value_count = 0
        gas_count = 0
        for value in values:
            if value_count == 0:
                unix_time_stamp = MassSpectrometerDateHandler.convert_date_to_unix_time(value)
                self.acquired_data[self.gases[gas_count]][self.acquired_data_keys[value_count]].append(unix_time_stamp)
            elif value_count == 1:
                self.acquired_data[self.gases[gas_count]][self.acquired_data_keys[value_count]].append(float(value))
            elif value_count == 2:
                self.acquired_data[self.gases[gas_count]][self.acquired_data_keys[value_count]].append(float(value))

            value_count += 1
            if value_count % 3 == 0:
                gas_count += 1
                value_count = 0


