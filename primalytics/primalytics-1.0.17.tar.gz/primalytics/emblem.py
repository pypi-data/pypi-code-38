import numpy
import pandas
import operator
import math
import csv
import copy
import warnings

from primalytics.tools import linear, reciprocal, logit


class Emblem:
    def __init__(self, filename: str = None, debug=False, sep: str = ',', sheet_name=0):
        self.__is_model_present = False
        self.__debug = debug
        self.__file = []
        self.__file_len = None

        # Coefficients ----------------------------------------------------------------------------
        self.base_weight = None

        # Rows ------------------------------------------------------------------------------------
        self.__start_univariate_row = 0
        self.__last_univariate_row = 0

        self.univariate_beta = {}
        self.bivariate_beta = {}

        # Variables -------------------------------------------------------------------------------
        self.__end_bivariates_reached = False
        self.__int_formats = (int, numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64)
        self.__float_formats = (float, numpy.float, numpy.float16, numpy.float32, numpy.float64)
        self.__numeric_formats = tuple(list(self.__int_formats) + list(self.__float_formats))
        self.__operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }
        self.__link_functions = {
            'exp': numpy.exp,
            'log': numpy.log,
            'linear': numpy.vectorize(linear),
            'reciprocal': numpy.vectorize(reciprocal),
            'logit': logit
        }

        self.__nans = [
            '', '#N/A', '#N/A', 'N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', 'N/A', 'NULL', 'NaN', 'n/a', 'nan', 'null'
        ]

        # Startup functions -----------------------------------------------------------------------
        if filename is not None:
            self.__read_input_file(filename, sep, sheet_name)
            self.__read_base_level()
            self.__read_univariates()
            self.__read_bivariates()
            self.__flatten_bivariates()
            self.__is_model_present = True

    def __read_input_file(self, filename, sep, sheet_name):
        ext = filename.split('.')[-1]
        if ext == 'csv':
            with open(filename, 'rt') as csvfile:
                spamreader = csv.reader(csvfile, quotechar='"', delimiter=sep)
                for row in spamreader:
                    self.__file.append(numpy.array(row).astype(str))
        elif ext in ('xlsx', 'xls'):
            self.__file = list(map(numpy.array, pandas.read_excel(io=filename, sheet_name=sheet_name, keep_default_na=False, na_values=self.__nans, header=0).fillna('').values))
        else:
            raise Exception('Invalid extension \'{}\' for Emblem filename'.format(ext))
        self.__file_len = len(self.__file)

    def __read_base_level(self):

        self.base_weight = float(self.__file[0][2])
        self.__start_univariate_row = 5

    def __read_univariates(self):
        if self.__file[5][0] != '':
            univariate_levels_cols = numpy.array(numpy.where(self.__file[self.__start_univariate_row] != '')[0])
            self.univariate_beta = {}
            self.__last_univariate_row = 0

            for col in univariate_levels_cols:
                single_univariate_beta = {}
                row = self.__start_univariate_row + 1
                single_univariate_end_reached = False
                univariate_name = self.__file[row - 1][col]
                if self.__debug:
                    print('{:-<100}'.format('{} '.format(univariate_name)))

                while not single_univariate_end_reached:

                    if self.__file_len == row + 1:
                        single_univariate_end_reached = True
                        self.__end_bivariates_reached = True
                    elif self.__file[row + 1][col + 1] == '':
                        single_univariate_end_reached = True
                    try:
                        level = float(self.__file[row][col])
                    except ValueError:
                        level = self.__file[row][col]

                    if self.__debug:
                        print('\trow: {:<6}| col: {:<6}| level: {:<40}| value: {:<8}'.format(row, col, level, self.__file[row][col + 1]))

                    single_univariate_beta.update({level: float(self.__file[row][col + 1])})
                    row += 1

                self.univariate_beta.update({univariate_name: single_univariate_beta})
                self.__last_univariate_row = max(self.__last_univariate_row, row)
        else:
            self.__last_univariate_row = self.__start_univariate_row

    def __read_bivariates(self):
        row = self.__last_univariate_row + 2
        self.bivariate_beta = {}

        if not self.__end_bivariates_reached:
            if not (self.__file[row - 2][0] == 'Orthogonal Polynomial Equations' or self.__file[row - 1][0] == 'Orthogonal Polynomial Equations' or self.__file[row][
                0] == 'Orthogonal Polynomial Equations'):
                # cycle over bivariate matrices
                while not self.__end_bivariates_reached:
                    first_bivariate_name = self.__file[row][2]
                    second_bivariate_name = self.__file[row + 2][0]
                    bivariate_interaction_name = first_bivariate_name + '|' + second_bivariate_name

                    try:
                        second_bivariate_levels = list(map(float, self.__file[row + 1][numpy.where(self.__file[row + 1] != '')]))
                    except ValueError:
                        second_bivariate_levels = self.__file[row + 1][numpy.where(self.__file[row + 1] != '')]

                    row += 2

                    # cycle over bivariate matrix's rows
                    single_bivariate_end_reached = False
                    single_bivariate_beta = {}
                    while not single_bivariate_end_reached:
                        try:
                            second_bivariate_level = float(self.__file[row][1])
                        except ValueError:
                            second_bivariate_level = self.__file[row][1]
                        second_bivariate_level = second_bivariate_level if str(second_bivariate_level) != '' else 'nan'

                        single_bivariate_beta.update({second_bivariate_level: dict(zip(second_bivariate_levels, list(map(float, self.__file[row][2:2 + len(second_bivariate_levels)]))))})

                        if row >= self.__file_len - 1:
                            single_bivariate_end_reached = True
                            self.__end_bivariates_reached = True
                        elif self.__file[row + 1][2] == '':
                            single_bivariate_end_reached = True

                            if row < self.__file_len - 1:
                                if self.__file[row + 2][0] == 'Orthogonal Polynomial Equations':
                                    self.__end_bivariates_reached = True

                        row += 1

                    row += 3

                    self.bivariate_beta.update({bivariate_interaction_name: single_bivariate_beta})

    def __flatten_bivariates(self):
        self.__bivariate_beta_flat = {}
        for interaction_name, bivariate_dict in self.bivariate_beta.items():
            bivariate_df = pandas.DataFrame(bivariate_dict)

            if bivariate_df.index.values.dtype in self.__float_formats:
                out_format = '{:0.3f}'
            else:
                out_format = '{}'

            bivariate_df.index = [out_format.format(x) for x in bivariate_df.index]

            if bivariate_df.columns.values.dtype in self.__float_formats:
                out_format = '{:0.3f}'
            else:
                out_format = '{}'

            bivariate_df.columns = [out_format.format(x) for x in bivariate_df.columns]

            self.__bivariate_beta_flat.update({interaction_name: {'{}|{}'.format(k[0], k[1]): v for k, v in bivariate_df.T.unstack().items()}})

    def __check_model_presence(self):
        if not self.__is_model_present:
            raise Exception('Error! No model present in class Emblem. use set_univariates(...), set_bivariates(...) methods to insert values')

    def __get_univariate_beta(self, df, variable, debug=False):
        if debug:
            try:
                result = df[variable].apply(lambda x: self.univariate_beta[variable][x])
            except KeyError as ke:
                print(variable, ke)
                raise KeyError
        else:
            result = df[variable].map(self.univariate_beta[variable])

        return result

    def __get_bivariate_beta(self, df, interaction_name, debug=False, return_levels: bool=False):
        first_bivariate = interaction_name.split('|')[0]
        second_bivariate = interaction_name.split('|')[1]

        first_bivariate_values = df[first_bivariate]
        second_bivariate_values = df[second_bivariate]

        if first_bivariate_values.dtype in self.__numeric_formats:
            first_bivariate_values = first_bivariate_values.apply(lambda x: '{:0.3f}'.format(x))
        else:
            first_bivariate_values = first_bivariate_values.astype(str)

        if second_bivariate_values.dtype in self.__numeric_formats:
            second_bivariate_values = second_bivariate_values.apply(lambda x: '{:0.3f}'.format(x))
        else:
            second_bivariate_values = second_bivariate_values.astype(str)

        compact_bivariate = first_bivariate_values + pandas.Series(['|' for _ in range(len(df))], index=df.index) + second_bivariate_values

        if debug:
            try:
                result = compact_bivariate.apply(lambda x: self.__bivariate_beta_flat[interaction_name][x])
            except KeyError as ke:
                try:
                    ke = float(str(ke))
                except (TypeError, ValueError):
                    pass
                else:
                    if math.isnan(ke):
                        error_condition = compact_bivariate.apply(lambda x: math.isnan(x) if isinstance(x, float) else False)
                    else:
                        error_condition = compact_bivariate.isin([ke])

                    print(interaction_name, ke, '\n')
                    print(pandas.concat([first_bivariate_values, second_bivariate_values, compact_bivariate], axis=1)[error_condition].iloc[0:10, :])
                raise KeyError
        else:
            result = compact_bivariate.map(self.__bivariate_beta_flat[interaction_name])

        if return_levels:
            return result, compact_bivariate
        else:
            return result

    def set_univariates(self, univariates: dict, base_weight=None):
        if base_weight is None:
            if self.base_weight is None:
                raise Exception('Error! base_waight is not set. Specify its value using base_weight=<value>')
        else:
            self.base_weight = base_weight

        self.univariate_beta = univariates
        self.__flatten_bivariates()
        self.__is_model_present = True

    def set_bivariates(self, bivariates: dict, base_weight=None):
        if base_weight is None:
            if self.base_weight is None:
                raise Exception('Error! base_waight is not set. Specify its value using base_weight=<value>')
        else:
            self.base_weight = base_weight

        self.bivariate_beta = bivariates
        self.__flatten_bivariates()
        self.__is_model_present = True

    def linear_predictor(self, df: pandas.DataFrame, vars_subset: list = None, excluded_vars=None, return_levels: bool = False, debug=False) -> numpy.array:
        if return_levels:
            coeffs_df, levels_df = self._get_coeffs(df=df, vars_subset=vars_subset, excluded_vars=excluded_vars, return_levels=return_levels, debug=debug)
            return coeffs_df.sum(axis=1, skipna=False).values, coeffs_df, levels_df
        else:
            return self._get_coeffs(df=df, vars_subset=vars_subset, excluded_vars=excluded_vars, return_levels=return_levels, debug=debug).sum(axis=1, skipna=False).values

    def product(self, df: pandas.DataFrame, vars_subset: list = None, excluded_vars=None, return_levels: bool = False, debug=False) -> numpy.array:
        if return_levels:
            coeffs_df, levels_df = self._get_coeffs(df=df, vars_subset=vars_subset, excluded_vars=excluded_vars, return_levels=return_levels, debug=debug)
            return coeffs_df.prod(axis=1, skipna=False).values, coeffs_df, levels_df
        else:
            return self._get_coeffs(df=df, vars_subset=vars_subset, excluded_vars=excluded_vars, return_levels=return_levels, debug=debug).prod(axis=1, skipna=False).values

    def _get_coeffs(self, df: pandas.DataFrame, vars_subset: list = None, excluded_vars: list = None, return_levels: bool = False, debug=False) -> numpy.array:
        self.__check_model_presence()

        coeffs_df = pandas.DataFrame(index=df.index)
        levels_df = pandas.DataFrame(index=df.index)

        if excluded_vars is None:
            excluded_vars = []

        if vars_subset is not None:
            excluded_vars = [x for x in self.univariate_beta.keys() if x not in vars_subset]
            bivs = [x.split('|') for x in self.bivariate_beta.keys()]
            for biv in bivs:
                if biv[0] not in vars_subset and biv[1] not in vars_subset:
                    excluded_vars += biv
                elif biv[0] not in vars_subset and biv[1] in vars_subset:
                    raise Exception('Also variable \'{0}\' must appear in var_subset as \'{1}\' appears in it and bivariate \'{0}|{1}\' exists'.format(biv[0], biv[1]))
                elif biv[0] in vars_subset and biv[1] not in vars_subset:
                    raise Exception('Also variable \'{1}\' must appear in var_subset as \'{0}\' appears in it and bivariate \'{0}|{1}\' exists'.format(biv[0], biv[1]))


        for variable in self.univariate_beta.keys():
            if variable not in excluded_vars:
                coeffs = self.__get_univariate_beta(df=df, variable=variable, debug=debug).values
                coeffs_df[variable] = coeffs
                if return_levels:
                    levels_df[variable] = df[variable]

        for interaction_name in self.__bivariate_beta_flat.keys():
            first_bivariate = interaction_name.split('|')[0]
            second_bivariate = interaction_name.split('|')[1]

            if not ((first_bivariate in excluded_vars) or (second_bivariate in excluded_vars)):
                if return_levels:
                    coeffs, compact_bivariate = self.__get_bivariate_beta(df=df, interaction_name=interaction_name, debug=debug, return_levels=return_levels)
                    levels_df[interaction_name] = compact_bivariate
                else:
                    coeffs = self.__get_bivariate_beta(df=df, interaction_name=interaction_name, debug=debug, return_levels=return_levels)

                coeffs_df[interaction_name] = coeffs.values

        null_values = coeffs_df.isna().sum().sum()

        if null_values > 0:
            warnings.warn('{} null values found in result'.format(null_values), Warning)

        if return_levels:
            return coeffs_df, levels_df
        else:
            return coeffs_df

    def predict(self, df: pandas.DataFrame, link_function, excluded_vars=None, debug=False) -> pandas.Series:
        self.__check_model_presence()

        if isinstance(link_function, str):
            link_function = self.__link_functions[link_function]
        if link_function is None:
            raise Exception('Error! Invalid link_function specified! Valid values are \'{}\''.format("', '".join(list(self.__link_functions.keys()))))
        else:
            link_function = numpy.vectorize(link_function)
        return pandas.Series(data=link_function(self.linear_predictor(df=df, excluded_vars=excluded_vars, debug=debug)), index=df.index)

    def get_beta(self, df: pandas.DataFrame, vars_subset: list = None, index_variable=None):
        if vars_subset is None:
            vars_subset = list(df.columns)

        self.__check_model_presence()
        beta_values = []
        for idx, row in df.iterrows():
            beta_values_tmp = {
                'index': idx if index_variable is None else row[index_variable],
                'base_weight': self.base_weight,
                'weights': {}
            }
            for variable, beta_dict in self.univariate_beta.items():
                if variable in vars_subset:
                    beta_values_tmp['weights'].update({variable: {row[variable]: beta_dict.get(row[variable])}})

            for interaction_name, interaction_dict in self.bivariate_beta.items():
                first_bivariate = interaction_name.split('|')[0]
                second_bivariate = interaction_name.split('|')[1]
                if first_bivariate in vars_subset and second_bivariate in vars_subset:
                    beta_values_tmp['weights'].update({
                        '{}|{}'.format(first_bivariate, second_bivariate): {'{}|{}'.format(row[first_bivariate], row[second_bivariate]): interaction_dict[row[first_bivariate]][row[second_bivariate]]}
                    })

            beta_values.append([beta_values_tmp])

        return pandas.DataFrame(data=beta_values, index=df.index, columns=['beta_values'])

    def rescale(self, variables_with_levels: dict, rescale_to: int):
        """
        :param variables_with_levels: dict with variables to rescale and levels to set as base levels
        :param rescale_to: value to set for the base level: valid values {0, 1}
        """
        self.__check_model_presence()

        if rescale_to == 1:
            operation = operator.truediv
            inverse_operation = operator.mul
        elif rescale_to == 0:
            operation = operator.sub
            inverse_operation = operator.add
        else:
            raise Exception('Invalid recaling value \'{}\'. Valid values are {{0, 1}}'.format(rescale_to))

        rescaled = self.copy()

        for variable, base_level in variables_with_levels.items():
            if variable in self.univariate_beta:
                try:
                    rescaling_value = self.univariate_beta[variable][base_level]
                except KeyError as ke:
                    raise Exception('KeyError! invalid key \'{}\' for variable \'{}\''.format(ke, variable))

                rescaled.univariate_beta[variable] = {k: operation(v, rescaling_value) for k, v in rescaled.univariate_beta[variable].items()}
                rescaled.base_weight = inverse_operation(rescaled.base_weight, rescaling_value)
            elif variable in self.bivariate_beta:
                try:
                    rescaling_value = self.bivariate_beta[variable][base_level[0]][base_level[1]]
                except KeyError as ke:
                    raise Exception('KeyError! invalid key {} for variable {}'.format(ke, variable))
                rescaled.bivariate_beta[variable] = {k1: {k2: operation(v2, rescaling_value) for k2, v2 in v1.items()} for k1, v1 in rescaled.bivariate_beta[variable].items()}
            else:
                raise Exception('KeyError! variable \'{}\' not found in univariate or bivariate dict'.format(variable))

        return rescaled

    def copy(self, deep: bool = True):
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)

    def write_to_file(self, filename: str):
        ext = filename.split('.')[-1]
        if ext == 'xlsx':
            shift = 1
        else:
            shift = 0

        self.__check_model_presence()

        base_weight_len = 3 + shift

        n_univariates = len(self.univariate_beta)
        if n_univariates > 0:
            n_max_univariate_levels = max([len(x) for x in self.univariate_beta.values()])
            univariate_len = 3 + n_max_univariate_levels
        else:
            univariate_len = 0

        n_bivariates = len(self.bivariate_beta)
        if n_bivariates > 0:
            bivariate_len = 5 * n_bivariates + sum([len(x) for x in self.bivariate_beta.values()]) - 1
            n_max_bivariate_leves = max([len(x[list(x.keys())[0]]) for x in self.bivariate_beta.values()])
        else:
            n_max_bivariate_leves = 0
            bivariate_len = 0

        file_width = max(3 * n_univariates - 1, n_max_bivariate_leves + 1)
        file_length = base_weight_len + univariate_len + bivariate_len

        file_array = [['' for _ in range(file_width)] for _ in range(file_length)]

        file_array[shift][0] = 'Base'
        file_array[shift][2] = self.base_weight

        for (i, (variable, levels_values)) in enumerate(self.univariate_beta.items()):
            file_array[shift + 3][3 * i] = variable
            file_array[shift + 5][3 * i] = variable

            for (j, (level, value)) in enumerate(levels_values.items()):
                file_array[shift + 6 + j][3 * i] = level
                file_array[shift + 6 + j][3 * i + 1] = value

        previous_bivariates_len = 0
        for (i, (interaction, matrix)) in enumerate(self.bivariate_beta.items()):
            first_bivariate, second_bivariate = interaction.split('|')
            file_array[base_weight_len + univariate_len + previous_bivariates_len][0] = '{} * {}'.format(first_bivariate, second_bivariate)
            file_array[base_weight_len + univariate_len + previous_bivariates_len + 2][2] = first_bivariate
            file_array[base_weight_len + univariate_len + previous_bivariates_len + 4][0] = second_bivariate

            n_second_bivariate_levels = len(matrix[list(matrix.keys())[0]])
            file_array[base_weight_len + univariate_len + previous_bivariates_len + 3][2:2 + n_second_bivariate_levels] = [k for k in matrix[list(matrix.keys())[0]].keys()]

            for (j, (level, levels_values)) in enumerate(matrix.items()):
                file_array[base_weight_len + univariate_len + previous_bivariates_len + 4 + j][1] = level
                file_array[base_weight_len + univariate_len + previous_bivariates_len + 4 + j][2:2 + n_second_bivariate_levels] = [v for v in levels_values.values()]

            previous_bivariates_len += 5 + len(self.bivariate_beta[interaction])

        with open(filename, 'w') as f:
            f.writelines([','.join(map(str, x)) + '\n' for x in file_array])
