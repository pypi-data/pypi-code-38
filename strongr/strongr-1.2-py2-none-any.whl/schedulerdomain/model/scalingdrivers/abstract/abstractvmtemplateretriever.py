from abc import ABCMeta, abstractmethod

class AbstractVmTemplateRetriever(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_vm_max_age(self, vm_name):
        pass

    @abstractmethod
    def get_templates(self):
        pass
