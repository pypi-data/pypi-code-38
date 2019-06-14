from __future__ import (absolute_import, division, print_function, unicode_literals)

import abc


class JobAbstract(object):
    _source = False
    _destination = False
    _require_attributes = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(k, str) and not k.startswith('_'):
                setattr(self, k, v)
        self.context = kwargs
        for attr in self._require_attributes:
            if not hasattr(self, attr):
                raise ValueError('the class [%s] should define the attribute [%s]' % (self.__class__, attr))


class JobExtractorBase(JobAbstract, metaclass=abc.ABCMeta):
    _source = False

    def __init__(self, **kwargs):
        super(JobExtractorBase, self).__init__(**kwargs)
        if not self._source:
            raise ValueError('Please define the source, static attribute _source')
        if self._source not in self.context:
            raise ValueError('The source [%s] not passed to Job, check the names' % self._source)

    def get_source(self):
        return self.context[self._source]()


class JobLoaderBase(JobAbstract, metaclass=abc.ABCMeta):
    _destination = False

    def __init__(self, **kwargs):
        super(JobLoaderBase, self).__init__(**kwargs)
        if not self._destination:
            raise ValueError('Please define the destination, static attribute _destination')
        if self._destination not in self.context:
            raise ValueError('The destination [%s] not passed to Job, check the names' % self._destination)

    def get_destination(self):
        return self.context[self._destination]()


class JobExtractorAbstract(JobExtractorBase, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def extract(self, methods, queued_data, pool):
        pass

    @abc.abstractmethod
    def count(self):
        pass


class JobLoaderAbstract(JobLoaderBase, metaclass=abc.ABCMeta):
    _destination = False

    @abc.abstractmethod
    def load(self, methods, queued_data, pool):
        pass


class JobTransformerAbstract(JobExtractorBase, JobLoaderBase, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def transform(self, methods, queued_data, pool):
        pass


class JobErrorAbstract(JobExtractorBase, JobLoaderBase, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def error(self, methods, queued_data, pool):
        pass
