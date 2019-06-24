class FlowReactorSetAndMeasuredValuesHandler:
    set_values_keys = ['Time', 'Temperature', 'Flow Rate']
    measured_values_keys = ['Time', 'Temperature', 'Flow Rate']
    temperature_keys = ['Reactor', 'Sample']

    def __init__(self, mfcs):
        self.mfcs = mfcs
        self.set_values = {}
        self.measured_values = {}
        self._initialize_set_values()
        self._initialize_measured_values()

    def _initialize_set_values(self):
        self.set_values = \
            {
                self.set_values_keys[0]: [],
                self.set_values_keys[1]:
                    {
                        self.temperature_keys[0]: [],
                        self.temperature_keys[1]: []
                    },
                self.set_values_keys[2]: {}
            }
        for mfc in self.mfcs:
            self.set_values[self.set_values_keys[2]][mfc] = []

    def _initialize_measured_values(self):
        self.measured_values = \
            {
                self.measured_values_keys[0]: [],
                self.measured_values_keys[1]:
                    {
                        self.temperature_keys[0]: [],
                        self.temperature_keys[1]: []
                    },
                self.measured_values_keys[2]: {}
            }
        for mfc in self.mfcs:
            self.measured_values[self.measured_values_keys[2]][mfc] = []

    def add_line_of_data(self, line):
        line = line.replace(',','.')
        list_of_values = line.rstrip('\n').split('\t')
        self._append_time_to_set_and_measured_values(list_of_values)
        self._append_flow_rates_to_set_and_measured_values(list_of_values)
        self._append_temperatures_to_set_and_measured_values(list_of_values)

    def _append_time_to_set_and_measured_values(self,list_of_values):
        time = float(list_of_values[0])
        self.set_values[self.set_values_keys[0]].append(time)
        self.measured_values[self.measured_values_keys[0]].append(time)

    def _append_flow_rates_to_set_and_measured_values(self,list_of_values):
        index_of_set_flow_rates = 1
        for mfc in self.mfcs:
            set_flow_rate = float(list_of_values[index_of_set_flow_rates])
            self._append_flow_rate_to_set_values(mfc, set_flow_rate)
            index_of_measured_flow_rates = index_of_set_flow_rates + len(self.mfcs) + 2
            measured_flow_rate = float(list_of_values[index_of_measured_flow_rates])
            self._append_flow_rate_to_measured_values(mfc, measured_flow_rate)
            index_of_set_flow_rates += 1

    def _append_flow_rate_to_set_values(self, mfc, value):
        self.set_values[self.set_values_keys[2]][mfc].append(value)

    def _append_flow_rate_to_measured_values(self, mfc, value):
        self.measured_values[self.set_values_keys[2]][mfc].append(value)

    def _append_temperatures_to_set_and_measured_values(self, list_of_values):
        set_reactor_temperature = float(list_of_values[len(self.mfcs)+1])
        self.set_values[self.set_values_keys[1]][self.temperature_keys[0]].append(set_reactor_temperature)
        measured_reactor_temperature = float(list_of_values[2*len(self.mfcs)+3])
        measured_sample_temperature = float(list_of_values[len(list_of_values)-3])
        self.measured_values[self.measured_values_keys[1]][self.temperature_keys[0]].append(measured_reactor_temperature)
        self.measured_values[self.measured_values_keys[1]][self.temperature_keys[1]].append(measured_sample_temperature)
