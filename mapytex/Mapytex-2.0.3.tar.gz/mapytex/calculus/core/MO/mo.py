#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

from abc import ABC, abstractmethod
from .exceptions import MOError
from ..renders import tree2txt, tree2tex

__all__ = ["MO"]


class MO(ABC):

    """MO for math object

    It is an abstract class with wrap recognizable math objects.

    There is 2 types of MO:
    - Atom which are compose of single value builtin.
    - Molecule which are more complex objects organised in a tree.

    """

    MAINOP = None

    @classmethod
    def factory(cls, value):
        """ Factory to ensure that a value is a MO before using it 

        Idempotent

        >>> MO.factory("x")
        <MOstr x>
        >>> MO.factory(2)
        <MOnumber 2>
        >>> MO.factory(2.3)
        <MOnumber 2.29999999999999982236431605997495353221893310546875>
        >>> x = MO.factory("x")
        >>> MO.factory(x)
        <MOstr x>
        >>> from decimal import Decimal
        >>> MO.factory(Decimal("2.3"))
        <MOnumber 2.3>
        """
        if isinstance(value, MO):
            return value

        return Atom.factory(value)

    @abstractmethod
    def content(self):
        """ content of the mo """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__txt__}>"

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __txt__(self):
        pass

    @abstractmethod
    def __tex__(self):
        pass

    def __hash__(self):
        try:
            return self._tree.__hash__()
        except AttributeError:
            return self._value.__hash__()

    def __eq__(self, other):
        """ == a MOnumber """
        try:
            return self.content == other.content
        except AttributeError:
            return self.content == other

    @property
    def signature(self):
        """ Name of the mo in the API

        :example:
        >>> from .atoms import MOnumber, MOstr
        >>> MOnumber(3).signature
        'scalar'
        >>> MOstr("x").signature
        'monome1'
        """
        return self._signature


class Atom(MO):

    """ Base Math Object with only one component.

    It is a wrapping of int, Décimal and str builtin python object

    Its wrapping builtin can be access throw .value property
    """

    MAINOP = None

    @classmethod
    def factory(cls, value):
        """ Build the appropriate atom from the value
        """
        for sub in cls.__subclasses__():
            try:
                return sub(value)
            except MOError:
                pass
        raise MOError(f"Can't build an atom from {type(value)}")

    def __init__(self, value):
        """ Initiate an atom MO
        """
        try:
            # if the value is already an atom
            self._value = value.value
        except AttributeError:
            self._value = value

        self.is_scalar = True
        self._signature = None

    @property
    def value(self):
        return self._value

    @property
    def content(self):
        return self.value

    def __str__(self):
        return str(self.value)

    @property
    def __txt__(self):
        return str(self.value)

    @property
    def __tex__(self):
        return str(self.value)


class Molecule(MO):

    """ Complex Math Object composed of multiple components

    It is a wrapping of tree

    Its wrapping tree can be access throw .tree property
    """

    MAINOP = None

    def __init__(self, value):
        """ Initiate the MO

        It should be idempotent.

        """
        try:
            self._tree = value._tree
        except AttributeError:
            self._tree = value

        self.is_scalar = True
        self._signature = None

    @property
    def tree(self):
        return self._tree

    @property
    def content(self):
        return self._tree

    def __str__(self):
        return str(self.__txt__)

    @property
    def __txt__(self):
        return tree2txt(self._tree)

    @property
    def __tex__(self):
        return tree2tex(self._tree)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
