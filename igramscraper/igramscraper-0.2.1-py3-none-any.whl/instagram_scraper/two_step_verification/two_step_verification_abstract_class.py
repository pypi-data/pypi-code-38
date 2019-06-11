from abc import ABC, abstractmethod


class TwoStepVerificationAbstractClass(ABC):

    '''
     Parameters: array possible_values
     Returns: string
     '''
    @abstractmethod
    def get_verification_type(self, possible_values):
        pass

    '''
     Returns: string
     '''
    @abstractmethod
    def get_security_code(self):
        pass
