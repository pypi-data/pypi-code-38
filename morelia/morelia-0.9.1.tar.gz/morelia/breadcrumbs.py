from morelia.visitors import VisitorObserver


class Breadcrumbs(VisitorObserver):
    def __init__(self):
        self.__feature = None
        self.__scenario = None
        self.step = None

    def feature_started(self, node):
        self.feature = node

    def scenario_started(self, node):
        self.scenario = node

    def step_started(self, node):
        self.step = node

    @property
    def feature(self):
        return self.__feature

    @feature.setter
    def feature(self, value):
        self.__feature = value
        self.scenario = None

    @property
    def scenario(self):
        return self.__scenario

    @scenario.setter
    def scenario(self, value):
        self.__scenario = value
        self.step = None

    def __str__(self):
        feature = self.feature.interpolated_source() if self.feature else ""
        scenario = self.scenario.interpolated_source() if self.scenario else ""
        step = self.step.interpolated_source() if self.step else ""
        return "\n{}{}{}".format(feature, scenario, step)
