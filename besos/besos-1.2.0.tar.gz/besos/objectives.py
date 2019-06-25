from typing import List, Dict, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

import os
import re
from itertools import chain
import pandas as pd

import config
from errors import ModeError
from IO_Objects import Objective
import eppy_funcs as ef


def get_data_dict_regex():
    """Generates a regex expression that can parse a line of the data dictionary in the .mtr file
    Various assumptions are made about the exact composition of names."""
    report_code = r'(?P<report_code>\d+)'  # report code of digits
    num_items = r'(?P<num_items>\d+)'  # number of items composed of digits
    name = r'(?P<name>[^\[\]]+?)'  # assumes that name can be anything without '[]' characters, may be wrong
    units = r'\[(?P<units>[^\]]*?)\]'  # units are enclosed in square brackets.
    frequency = r'!(?P<frequency>[\w|,]+)'  # frequency preceded by a '!'
    remainder = r'(?:  ?\[(?P<remainder>[^\]]+)\])?'  # can be preceded by 1-2 spaces based on experience
    data_dict_line = re.compile(fr'^{report_code},{num_items},{name} {units} {frequency}{remainder}$')
    return data_dict_line


_values_collection = List[List[float]]


@dataclass
class EPResults:
    """Represents the information about a Meter read from a .mtr file."""
    name: str
    frequency: str
    units: str
    data: pd.DataFrame

    # TODO: Consider improving the index for the DataFrame
    # index derived from the section headers (i.e. Design day winter hour=1) converted to a timestamp
    # this would simplify manipulating time series
    # Also consider nicer handling of duplicate names than just numbering

    @classmethod
    def from_pieces(cls, name, frequency, units, items, data, prefix=None) -> 'EPResults':
        if prefix is True:
            prefix = name
        unq_names = {}
        for i, original in enumerate(items):
            unq_names[original] = unq_names.get(original, []) + [i]
        new_names = items[:]
        for name, values in unq_names.items():
            if len(values) == 1:
                continue  # not a duplicate, leave the name alone
            for count, index in enumerate(values):
                new_names[index] = f'{name}_{count}'
        if prefix is not None:
            names = [f'{prefix}_{name}' for name in new_names]
        else:
            names = new_names
        df = pd.DataFrame({name: values for name, values in zip(names, zip(*data))})
        return cls(name, frequency, units, df)


_results_format = Dict[Tuple[str, str], EPResults]


def read_eso(out_dir: str = config.out_dir, file_name="eplusout.eso") -> _results_format:
    """Retrieve information from an Energy-Plus simulation, with outputs in out_dir

    returns a dictionary with keys of the form {(MeterName, Reporting_Frequency or None):EPResults dataclass}"""
    # output format described here:
    # https://energyplus.net/sites/default/files/pdfs_v8.3.0/OutputDetailsAndExamples.pdf

    with open(os.path.join(out_dir, file_name), 'r') as file:
        f = file.readlines()  # may cause memory errors on very large files

    # TODO: Find a way to avoid hardcoding these values to make things portable between versions
    # or move them to a version-dependant config of some kind
    data_dictionary_start = 1  # omit the first line, it is E+ version info
    data_dictionary_header = 6  # header is always 5 lines for E+ 8.8 and 6 lines for E+ 9.0
    data_dictionary_end = f.index('End of Data Dictionary\n')
    data_end = -2  # omit the End of Data line and the Number of Records Written line

    header = f[data_dictionary_start:data_dictionary_header]  # header currently ignored
    requested_vars = f[data_dictionary_header + 1: data_dictionary_end]
    data = f[data_dictionary_end + 1:data_end]

    data_dict_line = get_data_dict_regex()
    codes = {}
    keys = set()
    # currently ignores the header
    for line in requested_vars:
        match = re.search(data_dict_line, line)
        if match is None:
            raise ValueError(f'could not match: {line}')
        name = match.group('name')
        frequency = match.group('frequency')
        items = match.group('remainder')
        items = ['Value'] if items is None else items.split(',')
        report_code = match.group('report_code')
        key = (name, frequency)
        assert report_code not in codes, f'already found report code {report_code}'
        assert key not in keys, f'already found item with {key}'

        result = dict(name=name, frequency=frequency,
                      units=match.group('units'),
                      items=items, data=[])

        codes[report_code] = result
        keys.add(key)
    for line in data:
        report_code, *values = line.split(',')
        if report_code in codes:
            values = [float(value) for value in values]
            codes[report_code]['data'].append(values)

    return {(result['name'], result['frequency']): EPResults.from_pieces(**result) for result in codes.values()}

#TODO: Finish
def time_series_values(results: EPResults):
    """Returns the entire value column from some results formated as a pandas DF

    :param values: the values to display
    :return: the formated DF of the values in the collection.
    """

    
    #Already is a pandas DF [to_dict() can be used to convert it to the timeseries dict now or later in a differnt function?(maybe)]
    #possibly unit conversions as well? (althoug that should maybe be done in a different function at a differnt time - would be easy if its a pandas dataframe)
    return results.data['Value']

def sum_values(results: EPResults) -> float:
    """Returns the sum over the Value column from some results

    :param values: the values to sum over
    :return: the sum of the first value for each entry in the collection.
    """
    return results.data['Value'].sum()


# TODO make "all" clear all optional output, currently incomplete (i.e. csv files)
def clear_outputs(building, outputs: Union[str, List[str]] = 'all') -> None:
    """Disable certain types of output.

    :param building: the building to modify
    :param outputs: Can be the class_name of the output to clear,
        a shortcut for different types of output,
        or a list that combines the above.
    :return: None
    """
    # `empty` is used so that different fields do not reference each the same container
    mode = ef.get_mode(building)
    if mode == 'idf':
        building_items = building.idfobjects
        empty = list
    elif mode == 'json':
        building_items = building
        empty = dict
    else:
        raise ModeError(mode)

    def find(prefix):
        return {x for x in building_items if x.startswith(ef.convert_format(prefix, 'class', mode))}

    # These lists are probably incomplete!
    class_names = dict()
    # ENVIRONMENTALIMPACTFACTORS adds a bunch of meters, but is not a meter itself
    class_names['output_meters'] = find('Output:Meter:') | {'Output:Meter', 'Output:EnvironmentalImpactFactors'}
    class_names['internal_meters'] = {'Meter:Custom', 'Meter:CustomDecrement'}
    class_names['tables'] = find('Output:Table:')

    class_names['output'] = find('Output:')
    class_names['outputcontrol'] = find('OutputControl:')

    class_names['meters'] = class_names['output_meters'] | class_names['internal_meters']

    if outputs == 'all':
        outputs = chain(*class_names.values())
    else:
        if isinstance(outputs, str):  # make outputs a list
            outputs = [outputs]
        # convert each element in outputs via the class_names shortcuts
        outputs = set(chain(*(class_names.get(output, [output]) for output in outputs)))
    # clear the selected outputs
    for output in outputs:
        building_items[output] = empty()


class EPReader(Objective, ABC):
    field_pairs = NotImplemented

    def __init__(self, class_name, frequency: str = None, func=sum_values, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name
        self.frequency = frequency
        # class name has a nonzero default, so this may be adding noise to the repr
        # but it does provide a more complete picture
        self._add_reprs(['class_name', 'frequency'], check=True)

        self._process = func
        self._add_repr('func', '_process')

    def check_all(self, objective, mode):
        if mode == 'idf':
            def get(attribute):
                return getattr(objective, attribute)
        elif mode == 'json':
            def get(attribute):
                return objective[attribute]
        else:
            raise ModeError(mode)
        for self_attr, objective_attr in self.field_pairs:
            self_value = getattr(self, self_attr)
            objective_value = get(ef.convert_format(objective_attr, 'field', mode))
            if self_value is not None and objective_value != self_value:
                return False
        return True

    def get_objective(self, building):
        mode = ef.get_mode(building)
        if mode == 'idf':
            objectives = building.idfobjects[ef.convert_format(self.class_name, 'class', mode)]
        elif mode == 'json':
            objectives = building[ef.convert_format(self.class_name, 'class', mode)].values()
        else:
            raise ModeError(mode)
        for objective in objectives:
            if self.check_all(objective, mode):
                return objective
        raise ValueError(f'Cannot find the objective for {repr(self)}')

    def add_objective(self, building):
        """Creates and adds the meter needed by this objective to the building.

        :param building: the building to modify
        :return: None
        """
        try:
            self.get_objective(building)
        except ValueError:
            pass  # the objective is not present
        else:
            raise ValueError(f'Objective for {repr(self)} already exists')

        mode = ef.get_mode(building)
        new_object_dict = {ef.convert_format(field, 'field', mode): getattr(self, attr)
                           for attr, field in self.field_pairs if getattr(self, attr)}
        if self.frequency is None:
            new_object_dict[ef.convert_format('Reporting_Frequency', 'field', mode)] = 'Hourly'
        if mode == 'idf':
            building.newidfobject(key=ef.convert_format(self.class_name, 'class', mode), **new_object_dict)
        elif mode == 'json':
            # this is equivalent to appending, but e+ uses a dictionary instead of a list
            objectives = building[self.class_name]
            num = len(objectives)
            new_key = f'{self.class_name} {num}'
            assert new_key not in building, f'The building has incorrectly numbered {self.class_name} entries'
            objectives[new_key] = new_object_dict

    def validate(self, building):
        self.get_objective(building)

    def setup(self, building) -> None:
        """Prepares an idf so that it's output can be read by this meter.

        :param building: the idf to modify
        :return: None
        """
        try:
            self.get_objective(building)
        except ValueError:
            self.add_objective(building)
        self.validate(building)

    @abstractmethod
    def results_name(self):
        pass

    def __call__(self, results: _results_format) -> float:
        results_name = self.results_name()
        if self.frequency:
            meter_results = results[(results_name, self.frequency)]
        else:
            for (name, _), v in results.items():
                if name == results_name:
                    meter_results = v
                    break
            else:
                raise ValueError(f'No meter with name {results_name} found')
        return self._process(meter_results)


class MeterReader(EPReader):
    field_pairs = (('key_name', 'Key_Name'), ('frequency', 'Reporting_Frequency'))

    def __init__(self, key_name, class_name=config.objective_meter_type,
                 frequency: str = None, func=sum_values, **kwargs):
        super().__init__(class_name=class_name, frequency=frequency,
                         func=func, **kwargs)
        self.key_name = key_name
        self._add_repr('key_name', check=True)

    def results_name(self):
        return self.key_name

    @property
    def _default_name(self):
        return self.key_name


class VariableReader(EPReader):
    field_pairs = (('key_value', 'Key_Value'),
                   ('variable_name', 'Variable_Name'),
                   ('frequency', 'Reporting_Frequency'))

    def __init__(self, key_value, variable_name='*', class_name=config.objective_variable_type,
                 frequency: str = None, func=sum_values, **kwargs):
        super().__init__(class_name=class_name, frequency=frequency, func=func, **kwargs)
        self.key_value = key_value
        self._add_repr('key_value')
        self.variable_name = variable_name
        if self.variable_name != '*':
            self._add_repr('variable_name')

    def results_name(self):
        return f'{self.key_value},{self.variable_name}'

    @property
    def _default_name(self):
        return self.variable_name

# TODO: Remove objectives from idf output automatically
