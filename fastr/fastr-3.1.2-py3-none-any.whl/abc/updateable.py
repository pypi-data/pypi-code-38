# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains both the Updateable class and UpdateableMeta meta-class
for objects which support updates within the fastr system
"""

from abc import ABCMeta, abstractmethod
import os
import types
import threading

from .. import exceptions
from ..helpers import log


class UpdateableMeta(ABCMeta):
    """
    A metaclass for objects which are updateable and need some methods/properties
    to trigger an update.
    """

    @classmethod
    def calcmro(mcs, bases):
        """Calculate the Method Resolution Order of bases using the C3 algorithm.

        Suppose you intended creating a class K with the given base classes. This
        function returns the MRO which K would have, *excluding* K itself (since
        it doesn't yet exist), as if you had actually created the class.

        Another way of looking at this, if you pass a single class K, this will
        return the linearization of K (the MRO of K, *including* itself).

        :param bases: the list of bases for which create the MRO
        :return: the list representing the entire MRO, except the (non-existing) class itself

        Note: Taken from http://code.activestate.com/recipes/577748-calculate-the-mro-of-a-class/
              Created by Steven D'Aprano and licensed under the MIT license
        """
        seqs = [list(C.__mro__) for C in bases] + [list(bases)]
        res = []
        while True:
            non_empty = [item for item in seqs if item]
            if not non_empty:
                # Nothing left to process, we're done.
                return tuple(res)
            for seq in non_empty:  # Find merge candidates among seq heads.
                candidate = seq[0]
                not_head = [s for s in non_empty if candidate in s[1:]]
                if not_head:
                    # Reject the candidate.
                    candidate = None
                else:
                    break
            if not candidate:
                raise TypeError("inconsistent hierarchy, no C3 MRO is possible")
            res.append(candidate)
            for seq in non_empty:
                # Remove candidate.
                if seq[0] == candidate:
                    del seq[0]

    @classmethod
    def find_member(mcs, name, parents, dct):
        """
        Find  a member of the class in the same way as Python would if it had a given dict and set of bases

        :param mcs: metaclass at work
        :param name: name of the class to be created
        :param parents: list of the bases for the new class
        :param dct: the dict of the class being created
        :return: the firstly resolved member or None if nothing found
        """
        if name in dct:
            return dct[name]

        for cls in mcs.calcmro(parents):
            if hasattr(cls, name):
                return getattr(cls, name)

        return None

    def __new__(mcs, name, parents, dct):
        if '__updatetriggers__' in dct:
            triggers = dct['__updatetriggers__']

            for trigger in triggers:
                fnc = mcs.find_member(trigger, parents, dct)

                if fnc is not None:
                    if isinstance(fnc, (types.FunctionType, types.MethodType, types.BuiltinMethodType)):
                        log.debug('Adding update trigger {} to {}'.format(trigger, name))
                        dct[trigger] = mcs.updatetrigger(fnc)
                    else:
                        log.debug('Skipping trigger {} for {} (wrong type: {})'.format(trigger, name, type(fnc).__name__))
                else:
                    log.debug('Skipping trigger {} for {} (not in dct)'.format(trigger, name))
                    raise ValueError()

        return super(UpdateableMeta, mcs).__new__(mcs, name, parents, dct)

    @staticmethod
    def updatetrigger(fnc):
        """
        Function decorator to make a function trigger an update after being
        called. This is a way to easily have function trigger an update
        after setting a value without writing tons of wrapper functions.
        The function keeps the original docstring and appends a note to it.
        """
        def wrapper(self, *args, **kwargs):
            """
            Decorator wrapper around a function. This docstring will be
            changed for each wrapped function
            """
            # First call the wrapped function
            fnc(self, *args, **kwargs)
            # Call the update function
            # This function name is chosen so that it has low chance of conflicts
            if self.__updating__:
                self.__updatefunc__()

        # Add a note to the docstring indicating what is going on
        original = '{}.{}'.format(fnc.__module__, fnc.__name__)
        docstring = fnc.__doc__.lstrip('\n')
        indent = docstring[:len(docstring) - len(docstring.lstrip())]
        extra_doc = ('\n.. note::\n'
                     '    This is a wrapped version of ``{orig}``\n'
                     '    which triggers an update of  the object after\n'
                     '    being called').format(orig=original)
        extra_doc = '\n{}'.format(indent).join(extra_doc.splitlines())
        wrapper.__doc__ = docstring.rstrip() + "\n{indent}\n{indent}{extra_doc}\n{indent}".format(indent=indent, extra_doc=extra_doc)
        return wrapper


class Updateable(object, metaclass=UpdateableMeta):

    """
    Super class for all classes that can be updated and have a status.
    These objects can be valid/invalid state. These states are set by
    the function update. This allows for interactively checking the network.
    """

    #: Which methods need to be wrapped to trigger an update. Override this
    #: value to have the functions automatically wrapped. E.g.
    #: ``__update_triggers__ = ['append', 'insert', '__setitem__']`` to have
    #: these functions wrapped.
    __updatetriggers__ = []

    #: Flag to indicate that this object is allowed to update
    __updating__ = True

    #: Lock to avoid multiple updates happening at the same time
    __updateinprogress__ = threading.Lock()

    def __init__(self):
        """
        Constructor, creates the status field

        :return: newly created object
        """
        self._status = {'key': None, 'valid': None, 'messages': []}

    def __getstate__(self):
        """
        Retrieve the state of the object, make sure the status is not part of
        the description as it will not be valid after re-creating the object.

        :return: the state of the object
        :rtype dict:
        """
        return {}

    def __setstate__(self, state):
        """
        Set the state of the object by the given state. This adds a clean
        status field, making sure it is not unintended, outdated information
        from before serialization.

        :param dict state: The state to populate the object with
        """
        self._status = {'key': None, 'valid': None, 'messages': []}

    @property
    def messages(self):
        """
        The messages of the last update
        """
        return self._status['messages']

    @property
    def valid(self):
        """
        Flag indicating that the object is valid
        """
        return self._status['valid']

    def update(self, key=None, forward=True, backward=False):
        """
        Default function for updating, it can be called without key to have a
        new update started with a new key.

        :param int key: a key for this update, should be different than the
                        last update key
        :param bool forward: flag indicating to update forward in the network
        :param bool backward: flag indicating to update backward in the network
        """
        # If updating is disable, we don't do anything
        if not self.__updating__:
            return

        # If this is the first update function called in this round, create a key
        lock = False
        if key is None:
            key = hash(os.urandom(128))

            # Block update until previous updates are finished
            log.debug('Getting update lock')
            lock = Updateable.__updateinprogress__.acquire()
            log.debug('Got update lock')

        # Only update if not update in this update round
        if key == self._status['key']:
            # Release updatable lock, this should never be needed, but if not done when needed causes a deadlock
            if lock:
                log.warning('Releasing lock in unexpected place! Might be a bug!')
                Updateable.__updateinprogress__.release()
                log.debug('Released update lock')
            return

        # Store key to mark last update round
        self._status['key'] = key

        # Run the update func
        self._update(key, forward, backward)

        # Release updatable lock
        if lock:
            Updateable.__updateinprogress__.release()
            log.debug('Released update lock')

        return key

    # Set the update function for the trigger functions to call
    __updatefunc__ = update

    @abstractmethod
    def _update(self, key, forward=True, backward=False):
        """
        The actual update function to be used. This is an abstract function
        that Updateable objects must implement.

        :param int key: a key for this update, should be different than the
                        last update key
        :param bool forward: flag indicating to update forward in the network
        :param bool backward: flag indicating to update backward in the network
        """
        raise exceptions.FastrNotImplementedError('Purposefully not implemented')
