"""Exceptions used throughout Eelbrain"""


class DefinitionError(Exception):
    "MneExperiment definition error"


class DimensionMismatchError(Exception):
    "Trying to align NDVars with mismatching dimensions"


class WrongDimension(Exception):
    "Dimension that is supported"


class IncompleteModel(Exception):
    "Function requires a fully specified model"


class OldVersionError(Exception):
    "Trying to load a file from a version that is no longer supported"


class ZeroVariance(Exception):
    "Trying to do test on data with zero variance"
