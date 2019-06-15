from abc import ABCMeta, abstractmethod

"""
Abstract transporter implementation. Transporter classes are used to establish a connection to G.A.I.A.
"""
class ITransporter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def transport(self, payload:{}): raise NotImplementedError
