from smsframework.exc import ProviderError, RequestError


class AfricasTalkingProviderError(ProviderError):

    def __init__(self, message):
        super().__init__(message)


class InvalidNumberError(AfricasTalkingProviderError):

    def __init__(self, number, message='Invalid Phone Number', **kwargs):
        super().__init__(message)

        self.number = number

        for key, value in kwargs.items():
            setattr(self, key, value)
