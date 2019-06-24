#!/usr/bin/env python
# -*- coding: utf-8 -*-


class IncompatibilityError(Exception):
    """
    Raised if the dataframes *vertices* and *terminals* are incompatible.

    Used in the module *dhd.evolve*.
    """

    pass


class NoConnectionError(Exception):
    """
    Raised if a terminal without connection is in the set to be connected.

    Used in the module *dhd.evolve*.
    """

    pass


class GeometryError(Exception):
    """
    Raised when an operation between different geometries of the system fails.

    Used in the modules *dhd.city* and *dhd.connect*.
    """

    pass


class SourceError(Exception):
    """
    Raised when a heating source of the system cannot be treated normally.

    Used in the modules *dhd.load* and *dhd.city*.
    """

    pass


class NoMorePipe(Exception):
    """
    Raised when all the pipes have been merged into pipelines.

    Used in the module *dhd.load*.
    """

    pass


class BarrierError(Exception):
    """
    Raised when a natural barrier of the system cannot be treated normally.

    Used in the module *dhd.city*.
    """

    pass
