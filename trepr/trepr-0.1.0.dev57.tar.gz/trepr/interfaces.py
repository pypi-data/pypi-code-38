"""
Interfaces between trepr and other packages.
"""

import collections
import numpy as np

import fitpy.fitpy as fp
import spinpy.parameter_classes.parameters as prmt
import spinpy.solid_state.solid_state as sp


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class DimensionError(Error):
    """Exception raised when the dimension of the dataset isn't 1."""
    def __init__(self, message=''):
        self.message = message


class SpinPyInterface:

    def __init__(self):
        # public properties
        self.parameters = dict()
        self.result = None
        # protected properties
        self._exp = prmt.ExperimentalParameters()
        self._opt = prmt.OptionalParameters()
        self._sys = list()
        self._x_data = None
        self._y_data = None
        self._yaml_obj = None
        self._path = None
        self._simulation_routine = None

    def simulate(self):
        """Execute all necessary methods."""
        self._check_input_format()
        self._set_sys_exp_opt()
        self._get_simulation_routine()
        self._perform_simulation()

    def _is_input_format(self, identifier=''):
        return self.parameters['format']['type'].lower().\
            startswith(identifier.lower())

    def _check_input_format(self):
        if not self._is_input_format(identifier='spinpy'):
            if self._is_input_format(identifier='fitpy'):
                self._convert_fitpy_to_spinpy_input()
            else:
                raise TypeError

    def _convert_fitpy_to_spinpy_input(self):
        parameters = {'simulation': dict()}
        for key in ['Sys', 'Exp', 'Opt', 'SimulationRoutine']:
            parameters['simulation'][key] = self.parameters['fitting'][key]
        if 'thetaoff' in self.parameters['fitting']['FitOpt']:
            parameters['simulation']['Opt']['oritheta'][0] \
                += self.parameters['fitting']['FitOpt']['thetaoff'][0]
        self.parameters = parameters

    def _set_sys_exp_opt(self):
        """Set the sys, exp and opt attributes."""
        for i in range(len(self.parameters['simulation']['Sys'])):
            self._sys.append(prmt.SpinSystem())
            for key in self.parameters['simulation']['Sys'][i]:
                setattr(self._sys[i], key,
                        self.parameters['simulation']['Sys'][i][key])
        for key in self.parameters['simulation']['Exp']:
            setattr(self._exp, key, self.parameters['simulation']['Exp'][key])
        for key in self.parameters['simulation']['Opt']:
            setattr(self._opt, key, self.parameters['simulation']['Opt'][key])

    def _get_simulation_routine(self):
        """Get the full class name of the fitting routine."""
        self._simulation_routine = \
            self.parameters['simulation']['SimulationRoutine']

    def _perform_simulation(self):
        simulation_object = sp.SolidStateSimulation()
        simulation_object.spin_system = self._sys
        simulation_object.experimental_parameters = self._exp
        simulation_object.optional_parameters = self._opt
        simulation_object.simulate()
        self.result = simulation_object.result


class FitPyInterface:
    """Interface between the trepr and fitpy packages.

    One main aspect of connecting the trepr package to FitPy is a functional
    interface.Call FitPy with given fitting parameters and a given dataset.

    In order to interpret a spectrum, it is essential to know the parameters
    that make up the shape of the spectrum. To achieve this, the spectrum can
    be fitted and the best possible parameters determined using a least-square.

    Attributes
    ----------
    datasets : list or :obj:`trepr.dataset.Dataset`
        List of :obj:`trepr.dataset.Dataset` objects or a single
        :obj:`trepr.dataset.Dataset` object to work with.

    parameters : dict
        Dictionary containing all necessary fitting parameters.

    result : list
        List containing all numeric values of the fitted dataset. The intensity
        is stored in the last element of the list.

    Raises
    ------
    DimensionError
        Raised if the dimension of the dataset isn't 2.

    """

    def __init__(self):
        # public properties
        self.datasets = None
        self.parameters = dict()
        self.result = None
        # protected properties
        self._exp = prmt.ExperimentalParameters()
        self._opt = prmt.OptionalParameters()
        self._fit_opt = fp.FitOpt()
        self._sys = list()
        self._vary = list()
        self._exp_list = list()
        self._x_data = None
        self._y_data = None
        self._yaml_obj = None
        self._path = None
        self._number_of_datasets = None
        self._simulation_routine = None

    def fit(self):
        """Execute all necessary methods."""
        self._get_number_of_datasets()
        self._convert_angle_to_radian()
        self._preallocate_matrices_for_dataset()
        self._set_x_and_y_data()
        self._set_sys_exp_opt_fitopt()
        self._set_vary()
        self._get_simulation_routine()
        self._perform_fitting()

    def _get_number_of_datasets(self):
        """Get the number of datasets that will be fitted."""
        try:
            self._number_of_datasets = len(self.datasets)
        except:
            self._number_of_datasets = 1

    def _convert_angle_to_radian(self):
        """Convert all given angles to radians."""
        if 'thetaoff' in self.parameters['fitting']['FitOpt'].keys():
            self.parameters['fitting']['FitOpt']['thetaoff'] = \
                [angle / 180 * np.pi
                 for angle in
                 self.parameters['fitting']['FitOpt']['thetaoff']]

    def _preallocate_matrices_for_dataset(self):
        """Prepare arrays for x and y data."""
        self._x_data = np.zeros(
            [self._number_of_datasets,
             self.parameters['fitting']['Opt']['points']])
        self._y_data = np.zeros(
            [self._number_of_datasets,
             self.parameters['fitting']['Opt']['points']])

    def _set_x_and_y_data(self):
        """Set x and y data to the prepared arrays."""
        for i in range(self._number_of_datasets):
            if self._number_of_datasets is 1:
                self._check_dimension(self.datasets)
                self._x_data = self.datasets.data.axes[0].values
                self._y_data = self.datasets.data.data
            else:
                self._check_dimension(self.datasets[i])
                self._x_data[i, :] = self.datasets[i].data.axes[0].values
                self._y_data[i, :] = self.datasets[i].data.data
                self._y_data[i, :] = self._y_data[i, :] / sum(
                    abs(self._y_data[i, :]))

    @staticmethod
    def _check_dimension(dataset):
        """Check weather the dimension of the dataset is 2."""
        if len(dataset.data.axes) != 2:
            raise DimensionError('Dimension of the dataset needs to be 1.')

    def _set_sys_exp_opt_fitopt(self):
        """Set the sys, exp, opt and fitopt attributes."""
        for i in range(len(self.parameters['fitting']['Sys'])):
            self._sys.append(prmt.SpinSystem())
            for key in self.parameters['fitting']['Sys'][i]:
                setattr(self._sys[i], key,
                        self.parameters['fitting']['Sys'][i][key])
        for key in self.parameters['fitting']['Exp']:
            setattr(self._exp, key,
                    self.parameters['fitting']['Exp'][key])
        for i in range(self._number_of_datasets):
            self._exp_list.append(self._exp)
        for key in self.parameters['fitting']['Opt']:
            setattr(self._opt, key,
                    self.parameters['fitting']['Opt'][key])
        for key in self.parameters['fitting']['FitOpt']:
            setattr(self._fit_opt, key,
                    self.parameters['fitting']['FitOpt'][key])

    def _set_vary(self):
        """Prepare the vary list."""
        for i in range(len(self.parameters['fitting']['Vary'])):
            vary_dict = collections.OrderedDict()
            for key in self.parameters['fitting']['Vary'][i]:
                vary_dict[key] = \
                    self.parameters['fitting']['Vary'][i][key]
            self._vary.append(vary_dict)

    def _get_simulation_routine(self):
        """Get the full class name of the fitting routine."""
        self._simulation_routine = \
            self.parameters['fitting']['SimulationRoutine']

    def _perform_fitting(self):
        """Call fitpy.FitPy to fit the dataset."""
        if self._number_of_datasets is 1:
            fitting_object = fp.FitPy(self._y_data,
                                      self._sys,
                                      self._vary,
                                      self._exp,
                                      self._opt,
                                      self._fit_opt,
                                      self._simulation_routine,
                                      self.parameters)
        else:
            fitting_object = fp.FitPy(tuple(self._y_data),
                                      self._sys,
                                      self._vary,
                                      tuple(self._exp_list),
                                      self._opt,
                                      self._fit_opt,
                                      self._simulation_routine,
                                      self.parameters)
        fitting_object.fit()
        self.result = fitting_object.result

if __name__ == '__main__':
    obj = SpinPyInterface()
    obj.parameters = '/home/jara/Dokumente/masterthesis/Parametre_Input/Simualtion1.yaml'
    obj.simulate()
    print(obj.result)
