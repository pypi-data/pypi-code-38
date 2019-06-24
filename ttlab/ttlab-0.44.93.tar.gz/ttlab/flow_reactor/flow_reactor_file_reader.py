import re
from .flow_reactor_date_handler import FlowReactorDateHandler
from .flow_reactor_set_and_measured_values_handler import FlowReactorSetAndMeasuredValuesHandler


class FlowReactorFileReader:

    data_template = {
        'start time': None,
        'gases': None,
        'gas concentrations': None,
        'mfcs': None,
        'max flow rates': None,
        'k factors': None,
        'set values': None,
        'measured values': None
    }

    @staticmethod
    def read_data_from_file(filename):
        data = FlowReactorFileReader.data_template.copy()
        with open(filename) as flow_reactor_file:
            for line_nr, line in enumerate(flow_reactor_file):
                if line_nr == 1:
                    data['gases'] = FlowReactorFileReader._read_gases(line)
                elif line_nr == 2:
                    data['mfcs'] = FlowReactorFileReader._read_mfcs(line)
                    set_and_measured_values_handler = FlowReactorSetAndMeasuredValuesHandler(data['mfcs'])
                elif line_nr == 4:
                    data['max flow rates'] = FlowReactorFileReader._read_max_flow_rates(line)
                elif line_nr == 5:
                    data['k factors'] = FlowReactorFileReader._read_k_factors(line)
                elif line_nr == 7:
                    data['gas concentrations'] = FlowReactorFileReader._read_gas_concentrations(line)
                elif line_nr == 14:
                    data['start time'] = FlowReactorFileReader._read_start_time(line)
                elif line_nr > 14:
                    set_and_measured_values_handler.add_line_of_data(line)
            data['set values'] = set_and_measured_values_handler.set_values
            data['measured values'] = set_and_measured_values_handler.measured_values
        return data

    @staticmethod
    def read_data_from_gridfs(gridfs):
        data = FlowReactorFileReader.data_template.copy()
        line = gridfs.readline()
        line_nr = 0
        while line is not b'':
            decoded_line = line.decode("utf-8").rstrip()
            if line_nr == 1:
                data['gases'] = FlowReactorFileReader._read_gases(decoded_line)
            elif line_nr == 2:
                data['mfcs'] = FlowReactorFileReader._read_mfcs(decoded_line)
                set_and_measured_values_handler = FlowReactorSetAndMeasuredValuesHandler(data['mfcs'])
            elif line_nr == 4:
                data['max flow rates'] = FlowReactorFileReader._read_max_flow_rates(decoded_line)
            elif line_nr == 5:
                data['k factors'] = FlowReactorFileReader._read_k_factors(decoded_line)
            elif line_nr == 7:
                data['gas concentrations'] = FlowReactorFileReader._read_gas_concentrations(decoded_line)
            elif line_nr == 14:
                data['start time'] = FlowReactorFileReader._read_start_time(decoded_line)
            elif line_nr > 14:
                set_and_measured_values_handler.add_line_of_data(decoded_line)
            line = gridfs.readline()
            line_nr += 1
        data['set values'] = set_and_measured_values_handler.set_values
        data['measured values'] = set_and_measured_values_handler.measured_values
        return data


    @staticmethod
    def _read_gases(line_with_gases):
        list_with_gases = line_with_gases.split('\t')
        return list(filter((lambda x: not (x == '' or x == 'Gas Name:' or x == '\n')), list_with_gases))

    @staticmethod
    def _read_mfcs(line_with_mfcs):
        list_with_mfcs = line_with_mfcs.split('\t')
        return list(filter((lambda x: not (x == '' or x == 'MFC Name:' or x == '\n')), list_with_mfcs))

    @staticmethod
    def _read_max_flow_rates(line_with_flow_rates):
        list_with_flow_rates = line_with_flow_rates.split('\t')
        list_with_flow_rates = list(
            filter((lambda x: not (x == '' or x == 'Max Flow:' or x == '\n')), list_with_flow_rates))
        return list(map((lambda x: float(x)), list_with_flow_rates))

    @staticmethod
    def _read_k_factors(line_with_k_factors):
        list_with_k_factors = line_with_k_factors.split('\t')
        list_with_k_factors = list(
            filter((lambda x: not (x == '' or x == 'K-factor:' or x == '\n')), list_with_k_factors))
        list_with_k_factors = list(map((lambda x: x.replace(',', '.')), list_with_k_factors))
        return list(map((lambda x: float(x)), list_with_k_factors))

    @staticmethod
    def _read_gas_concentrations(line_with_gas_concentrations):
        list_with_gas_concentrations = line_with_gas_concentrations.split('\t')
        list_with_gas_concentrations = list(
            filter((lambda x: not (x == '' or x == 'Gas Conc.:' or x == '\n')), list_with_gas_concentrations))
        return list(map((lambda x: float(x.replace(',','.'))), list_with_gas_concentrations))

    @staticmethod
    def _read_start_time(line_with_start_time):
        date = FlowReactorFileReader._extract_date(line_with_start_time)
        return FlowReactorDateHandler.convert_date_to_unix_time(date)

    @staticmethod
    def _extract_date(string):
        date = re.findall('\d+-\d+-\d+\s\d+.\d+.\d+.', string)[0]
        return date
