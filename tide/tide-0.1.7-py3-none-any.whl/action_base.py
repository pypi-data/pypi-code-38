from abc import ABC, abstractmethod

class action_base(ABC):

    @abstractmethod
    def run(self, command_item, buffer_name=""):
        raise NotImplementedError('run() must be implemented')
