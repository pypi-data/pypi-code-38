import spinpy.solid_state.solid_state as sp
import spinpy.parameter_classes.parameters as prmt


class SpinPyInterface:

    def __init__(self):
        # public properties
        self.parameters = dict()
        self.result = None
        # protected properties
        self._exp = prmt.ExperimentalParameters()
        self._opt = prmt.OptionalParameters()
        self._sys = prmt.SpinSystem()
        self._x_data = None
        self._y_data = None
        self._yaml_obj = None
        self._path = None
        self._simulation_routine = None

    def simulate(self):
        """Execute all necessary methods."""
        self._set_sys_exp_opt()
        self._get_simulation_routine()
        self._perform_simulation()

    def _set_sys_exp_opt(self):
        """Set the sys, exp and opt attributes."""
        for key in self.parameters['simulation']['Sys']:
            setattr(self._sys, key, self.parameters['simulation']['Sys'][key])
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
