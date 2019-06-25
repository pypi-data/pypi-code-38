from typing import Union, List, Dict, Callable, Iterable

import pandas as pd
import numpy as np
import platypus
import warnings

import IO_Objects
import config
import objectives
import parameters

# from pyehub_funcs import name_getter


# TODO: Consider storing the constraint bounds with the constraints themselves, not in the problem
# also consider storing the direction of optimisation inside the objectives
# might be able to inherit some of the constraint parsing from platypus, not sure if that is worth the hassle
class Problem(IO_Objects.ReprMixin):
    """A class that collects all of the inputs, outputs and constraints related to a building."""
    valid_parts: List[str] = ['inputs', 'outputs', 'constraints', 'violation']
    default_converters = {'outputs': IO_Objects.Objective, 'constraints': IO_Objects.Objective}

    def __init__(self, inputs: Union[int, List[Union[str, IO_Objects.Descriptor]]] = None,
                 outputs: Union[int, List[Union[str, IO_Objects.Objective]]] = None,
                 constraints: Union[int, List[Union[str, IO_Objects.Objective]]] = None, *,
                 constraint_bounds: List[str] = None, minimize_outputs: List[bool] = None,
                 converters: Dict[str, Callable[[str], IO_Objects.IOBase]] = None):
        """

        :param inputs: A list of Parameters, or an integer.
            If a list  is used, strings are converted to Parameters and this list determines the valid inputs.
            If an integer, this problem accepts that many inputs.
        :param outputs: A list of Objectives, or an integer.
            If a list  is used, strings are converted to Objectives and this list determines the valid inputs.
            If an integer, this problem requires that many outputs
        :param constraints:
        :param constraint_bounds:
        :param minimize_outputs:
        :param converters:
        """
        super().__init__()
        self.converters = converters or self.default_converters
        extra_keys = set(self.converters.keys()) - set(self.valid_parts)
        if extra_keys:
            raise ValueError(f'The keys {extra_keys} are not valid for this Problem. Only {self.valid_parts} are valid')

        self.inputs = self._io_to_list(inputs, 'inputs')
        self.num_inputs = len(self.inputs)

        self.outputs = self._io_to_list(outputs, 'outputs')
        self.num_outputs = len(self.outputs)
        self.minimize_outputs = minimize_outputs or [True] * self.num_outputs
        msg = 'outputs and minimize_outputs must have the same length'
        assert len(self.minimize_outputs) == self.num_outputs, msg

        self.constraints = self._io_to_list(constraints, 'constraints')
        self.num_constraints = len(self.constraints)
        # TODO: consider using platypus's constraints here
        self.constraint_bounds = constraint_bounds or []
        msg = 'constraints and constraint_bounds must have the same length'
        assert len(self.constraint_bounds) == self.num_constraints, msg
        self.fix_names()
        self._add_reprs(['inputs', 'outputs', 'minimize_outputs',
                         'constraints', 'constraint_bounds', 'converters'],
                        check=True)

    def fix_names(self):
        mapping = {}
        duplicates = []
        for obj in self:
            mapping[obj.name] = mapping.get(obj.name, []) + [obj]
        for name, objects in mapping.items():
            if len(objects) != 1:
                duplicates.append((name, objects))
        if duplicates:
            warnings.warn(RuntimeWarning(f'Duplicate names found. (duplicate, repetitions): '
                                         f'{[(name, len(objects)) for name, objects in duplicates]}'
                                         f'\nAttempting to fix automatically'))
        for name, objects in duplicates:
            for i, obj in enumerate(objects):
                obj.name = f'{obj.name}_{i}'

    def _io_to_list(self, io_objects: Union[int, List[IO_Objects.IOBase], None], part):
        """Converts a list of objects to a standard form:
        numbered placeholders, original datatype or io_object that match the part provided.
        """
        if io_objects is None:
            return []
        if isinstance(io_objects, int):
            if part == 'inputs':
                class_ = parameters.Parameter
            elif part in ['outputs', 'constraints']:
                class_ = IO_Objects.Objective
            else:
                raise ValueError(f'Cannot produce dummy values for part {part}')
            return [class_(name=f'{part}_{i}') for i in range(io_objects)]
        if isinstance(io_objects, (str, IO_Objects.IOBase)):
            io_objects = [io_objects]
        return [self.convert(o, part) for o in io_objects]

    def convert(self, io_object, part) -> IO_Objects.IOBase:
        """

        :param io_object: An object that should be converted to a parameter, objective or constraint
        :param part: one of 'inputs', 'outputs' or 'constraints' describing what to convert `io_object` to
        :return: the converted object
        """
        if isinstance(io_object, IO_Objects.IOBase):
            return io_object
        if part in self.converters:
            f = self.converters[part]
            try:
                return f(io_object)
            except TypeError as e:
                try:
                    if isinstance(io_object, dict):
                        return f(**io_object)
                    if isinstance(io_object, Iterable):
                        return f(*io_object)
                except:
                    pass
                raise TypeError(f'Cannot convert {io_object} to {part}') from e
        return io_object

    def expand_parts(self, parts: Union[str, List[str]]) -> List[str]:
        """Expands 'auto' and 'all' to the correct lists of parts, and wraps single parts in a list"""
        if parts == 'auto':
            if self.num_constraints == 0:
                parts = ['inputs', 'outputs']
            else:
                parts = 'all'
        if parts == 'all':
            parts = self.valid_parts
        elif isinstance(parts, str):
            parts = [parts]

        if not set(parts) <= set(self.valid_parts):
            raise ValueError(f"parts must be a subset of {self.valid_parts + ['all']}, not {parts}")
        return parts

    def names(self, parts: Union[str, List[str]] = 'auto') -> List[str]:
        """

        :param parts: one of {'inputs', 'outputs', 'constraints', 'violation', 'all', 'auto'}
        :return: the names requested
        """
        parts = self.expand_parts(parts)
        names = []
        for attr in parts:
            if attr == 'violation':
                names.append('violation')
            else:
                part = getattr(self, attr)
                if part is None:
                    raise ValueError(f'{attr} names not available')
                names.extend(IO_Objects.get_name(i) for i in part)
        return names

    # TODO: Add support for pareto-optimal column
    # TODO: Consolidate the different to_df code (ie from optimizer.py)
    def to_df(self, table: Union[np.array, pd.DataFrame], parts: Union[str, List[str]] = 'auto') -> pd.DataFrame:
        """Converts the given table to a DataFrame that matches this problem's input/output format

        :param table: a table to be converted to a DataFrame. Must have the right number of columns.
        :param parts: inputs, outputs, constraints or all, depending on which data the DataFrame contains
        :return: A DataFrame containing the same data as the original table.
        """
        columns = self.names(parts)
        types = [p.pd_type if hasattr(p, 'pd_type') else None for p in self.expand_parts(parts)]
        if isinstance(table, pd.DataFrame):
            if len(table.columns) != len(columns):
                raise ValueError(f'columns: {columns} requested but {list(table.columns)} found')
            return table[columns]

        df = pd.DataFrame(table, columns=columns)
        # TODO: Make the categorical columns have the type category instead of object (attempt commented out below)
        # for col, type_ in zip(df, types):
        #     if type_:
        #         df[col] = df[col].astype(type_)
        return df

    def partial_df(self, table: Union[np.array, pd.DataFrame], parts='all'):
        parts = self.expand_parts(parts)
        for i in range(1, len(parts) + 1):
            partial_parts = parts[:i]
            try:
                return self.to_df(table, partial_parts), partial_parts
            except ValueError:
                continue
        raise ValueError('Could not find a matching DataFrame')

    def to_platypus(self) -> platypus.Problem:
        """Converts this problem to a platypus problem.
        No evaluator will be included.

        :return: A corresponding platypus problem
        """
        problem = platypus.Problem(self.num_inputs, self.num_outputs, self.num_constraints)
        for i, parameter in enumerate(self.inputs):
            problem.types[i] = parameter.platypus_type
        for i, direction in enumerate(self.minimize_outputs):
            problem.directions[i] = platypus.Problem.MINIMIZE if direction else platypus.Problem.MAXIMIZE
        for i, bound in enumerate(self.constraint_bounds):
            problem.constraints[i] = bound
        return problem

    def __eq__(self, other):
        return (self.__class__ is other.__class__
                and self.inputs == other.inputs
                and self.outputs == other.outputs
                and self.constraints == other.constraints)

    def __iter__(self):
        return iter(self.inputs + self.outputs + self.constraints)


# TODO: consider having shortcuts for the converters instead of making this a whole different class
class EPProblem(Problem):
    """A problem with defaults that are appropriate for EnergyPlus simulations"""
    default_converters = {'outputs': objectives.MeterReader, 'constraints': objectives.MeterReader}

    def __init__(self, inputs=None, outputs=config.objectives,
                 constraints=None, converters=None, **kwargs):
        super().__init__(inputs=inputs, outputs=outputs, constraints=constraints, converters=converters, **kwargs)

class EHProblem(Problem):
    """A problem that works with PyEHub models"""
    #TODO: Restructure if possible to be more like other problems.
    def __init__(self, inputs = [], outputs = ['total_cost'], constraints = None, converters = None, **kwargs):
        super().__init__(inputs=inputs, outputs=outputs, constraints=constraints, converters=converters, **kwargs)

    #Overwritten functions to work with EvaluatorEH:
    def fix_names(self):
        pass
    
