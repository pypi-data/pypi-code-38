import abc
import os


class WorkingDirectorySwitch:
    def __init__(self):
        self.original_working_directory = os.getcwd()

    def save(self):
        self.original_working_directory = os.getcwd()

    def set(self, new_working_directory):
        os.chdir(new_working_directory)

    def return_original_working_directory(self):
        os.chdir(self.original_working_directory)


class AbstractExtractor(abc.ABC):
    def __init__(self):
        self.original_working_directory = os.getcwd()
        self.configuration = None
        self.working_directory_switch = WorkingDirectorySwitch()

    def working_context(decorated_method):
        def wrapper(extractor_instance, configuration, *args, **kwargs):
            extractor_instance.configuration = configuration
            extractor_instance.working_directory_switch.save()
            extractor_instance.working_directory_switch.set(configuration["working_directory"])
            decorated_method(extractor_instance, configuration, *args, **kwargs)
            extractor_instance.working_directory_switch.return_original_working_directory()
        return wrapper

    @abc.abstractmethod
    @working_context
    def extract(self, configuration):
        print(os.getcwd())
