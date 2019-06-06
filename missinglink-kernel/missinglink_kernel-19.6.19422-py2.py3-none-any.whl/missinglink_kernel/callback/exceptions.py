# -*- coding: utf-8 -*-


# most general project exceptions. all other exceptions that we raise should be inherited from this one
class MissingLinkException(Exception):
    pass


class ExperimentStopped(MissingLinkException):
    pass


class ImageUnavailableException(MissingLinkException):
    pass
