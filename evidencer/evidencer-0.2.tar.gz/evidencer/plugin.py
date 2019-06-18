import abc
import os


class WorkingDirectorySwitch:
    def __init__(self):
        self.original_working_directory = os.getcwd()

    def save(self):
        self.original_working_directory = os.getcwd()

    def set(self, new_working_directory):
        os.chdir(new_working_directory)

    def return_saved_working_directory(self):
        os.chdir(self.original_working_directory)


def working_directory_context(decorated_method):
    def wrapper(instance, configuration, *args, **kwargs):
        working_directory_switch = WorkingDirectorySwitch()
        working_directory_switch.save()
        working_directory_switch.set(configuration["working_directory"])
        result = decorated_method(instance, configuration, *args, **kwargs)
        working_directory_switch.return_saved_working_directory()
        return result
    return wrapper


def save_configuration(decorated_method):
    def wrapper(instance, configuration, *args, **kwargs):
        instance.configuration = configuration
        result = decorated_method(instance, configuration, *args, **kwargs)
        return result
    return wrapper


# TODO: Extractor schema checker

class AbstractExtractor:
    def __init__(self):
        self.configuration = None

    @abc.abstractmethod
    @working_directory_context
    def extract(self, configuration):
        pass


