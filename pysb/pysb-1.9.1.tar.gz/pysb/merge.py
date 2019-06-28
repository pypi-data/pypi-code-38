import abc
import copy
from pysb.logging import get_logger


class MergeStrategy(abc.ABC):
    """ Base class for building model merging strategies """
    def __init__(self, model1, model2):
        self._log = get_logger(__name__, model=model1)
        self.m1 = model1
        self.m2 = model2
        self.m1_mapping = None
        self.m2_mapping = None

    @abc.abstractmethod
    def merge(self):
        """ Merge model1 and model2 to return a new, combined model """
        pass

    def _rename(self, source_namespace, target_namespace, name):
        """ Propose a new name for a component in target_namespace """
        new_name = name
        i = 1
        while new_name in source_namespace or new_name in target_namespace:
            new_name = '{}__{}'.format(name, i)
            i += 1

        return new_name

    def _combine_models(self):
        m_out = copy.deepcopy(self.m1)
        m_out.name += '_merge_{}'.format(self.m2.name)
        target_namespace = set(m_out.components.keys())
        source_namespace = set(self.m2.components.keys())
        m2_copy = copy.deepcopy(self.m2)

        self.m1_mapping = dict(zip(source_namespace, source_namespace))
        self.m2_mapping = {}

        for c in m2_copy.components:
            if c.name in target_namespace:
                c_name = self._rename(source_namespace,
                                      target_namespace,
                                      c.name)
                self._log.debug('{} {} was renamed to {}'.format(
                    c.__class__.__name__, c.name, c_name
                ))
                c.rename(c_name)
            else:
                c_name = c.name
            target_namespace.add(c_name)
            self.m2_mapping[c.name] = c_name
            m_out.add_component(c)

        # Copy initial conditions
        m_out.initial_conditions += m2_copy.initial_conditions

        # Copy annotations
        m_out.annotations += m2_copy.annotations

        return m_out


class NoOverlapMerge(MergeStrategy):
    """ Naive strategy in which all components are assumed to be distinct """

    def merge(self):
        return self._combine_models()
