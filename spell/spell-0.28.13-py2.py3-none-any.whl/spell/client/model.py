import abc

import six
from future.utils import raise_from


@six.add_metaclass(abc.ABCMeta)
class SpellModel(object):
    """An abstract base class for Spell objects.

    Wraps an underlying :py:class:`spell.api.models.Model` API object. Child classes extend a
    specific :py:class:`spell.api.models.Model` and provide higher level operations on that object.

    Attributes:
        model: an abstract property of type string indicating the specific model name for the class (e.g., 'run')
    """

    model = abc.abstractproperty()

    def __getattr__(self, name):
        try:
            return getattr(getattr(self, self.model), name)
        except AttributeError:
            raise_from(AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name)), None)

    def __repr__(self):
        return repr(getattr(self, self.model))
