# ptypes.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0912,R0916

# Standard library imports
import math

# PyPI imports
import numpy as np
import pexdoc.pcontracts


###
# Global variables
###
_SUFFIX_TUPLE = (
    "y",
    "z",
    "a",
    "f",
    "p",
    "n",
    "u",
    "m",
    " ",
    "k",
    "M",
    "G",
    "T",
    "P",
    "E",
    "Z",
    "Y",
)


###
# Functions
###
def _check_increasing_real_numpy_vector(obj):
    # pylint: disable=C0103
    if isinstance(obj, np.ndarray) and (len(obj.shape) == 1) and (obj.shape[0] > 0):
        otype = obj.dtype.name
        result = any([otype.startswith(item) for item in ("int", "float")])
        return not (
            bool(result)
            and (
                (obj.shape[0] == 1) or ((obj.shape[0] > 1) and (min(np.diff(obj)) > 0))
            )
        )
    return True


def _check_number_numpy_vector(obj):
    if isinstance(obj, np.ndarray) and (len(obj.shape) == 1) and (obj.shape[0] > 0):
        otype = obj.dtype.name
        result = any([otype.startswith(item) for item in ("int", "float", "complex")])
        return not bool(result)
    return True


def _check_real_numpy_vector(obj):
    if isinstance(obj, np.ndarray) and (len(obj.shape) == 1) and (obj.shape[0] > 0):
        otype = obj.dtype.name
        result = any([otype.startswith(item) for item in ("int", "float")])
        return not bool(result)
    return True


@pexdoc.pcontracts.new_contract()
def engineering_notation_number(obj):
    r"""
    Validate if an object is an :ref:`EngineeringNotationNumber` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    try:
        obj = obj.rstrip()
        float(obj[:-1] if obj[-1] in _SUFFIX_TUPLE else obj)
        return None
    except (AttributeError, IndexError, ValueError):
        # AttributeError: obj.rstrip(), object could not be a string
        # IndexError: obj[-1], when an empty string
        # ValueError: float(), when not a string representing a number
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def engineering_notation_suffix(obj):
    r"""
    Validate if an object is an :ref:`EngineeringNotationSuffix` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the *name* of the argument the
     contract is attached to

    :rtype: None
    """
    try:
        assert obj in _SUFFIX_TUPLE
    except AssertionError:
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def increasing_real_numpy_vector(obj):
    r"""
    Validate if an object is :ref:`IncreasingRealNumpyVector` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_increasing_real_numpy_vector(obj):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def number_numpy_vector(obj):
    r"""
    Validate if an object is a :ref:`NumberNumpyVector` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_number_numpy_vector(obj):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def real_numpy_vector(obj):
    r"""
    Validate if an object is a :ref:`RealNumpyVector` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_real_numpy_vector(obj):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def touchstone_data(obj):
    r"""
    Validate if an object is an :ref:`TouchstoneData` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if (not isinstance(obj, dict)) or (
        isinstance(obj, dict)
        and (sorted(obj.keys()) != sorted(["points", "freq", "pars"]))
    ):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not (isinstance(obj["points"], int) and (obj["points"] > 0)):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_increasing_real_numpy_vector(obj["freq"]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not isinstance(obj["pars"], np.ndarray):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    vdata = ["int", "float", "complex"]
    if not any([obj["pars"].dtype.name.startswith(item) for item in vdata]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if obj["freq"].size != obj["points"]:
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    nports = int(math.sqrt(obj["pars"].size / obj["freq"].size))
    if obj["points"] * (nports ** 2) != obj["pars"].size:
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def touchstone_noise_data(obj):
    r"""
    Validate if an object is an :ref:`TouchstoneNoiseData` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if isinstance(obj, dict) and (not obj):
        return None
    if (not isinstance(obj, dict)) or (
        isinstance(obj, dict)
        and (sorted(obj.keys()) != sorted(["points", "freq", "nf", "rc", "res"]))
    ):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not (isinstance(obj["points"], int) and (obj["points"] > 0)):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_increasing_real_numpy_vector(obj["freq"]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_real_numpy_vector(obj["nf"]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if _check_number_numpy_vector(obj["rc"]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not (
        isinstance(obj["res"], np.ndarray)
        and (len(obj["res"].shape) == 1)
        and (obj["res"].shape[0] > 0)
        and np.all(obj["res"] >= 0)
    ):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    sizes = [obj["freq"].size, obj["nf"].size, obj["rc"].size, obj["res"].size]
    if set(sizes) != set([obj["points"]]):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    return None


@pexdoc.pcontracts.new_contract()
def touchstone_options(obj):
    r"""
    Validate if an object is an :ref:`TouchstoneOptions` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if (not isinstance(obj, dict)) or (
        isinstance(obj, dict)
        and (sorted(obj.keys()) != sorted(["units", "ptype", "pformat", "z0"]))
    ):
        raise ValueError(pexdoc.pcontracts.get_exdesc())
    if not (
        (obj["units"].lower() in ["ghz", "mhz", "khz", "hz"])
        and (obj["ptype"].lower() in ["s", "y", "z", "h", "g"])
        and (obj["pformat"].lower() in ["db", "ma", "ri"])
        and isinstance(obj["z0"], float)
        and (obj["z0"] >= 0)
    ):
        raise ValueError(pexdoc.pcontracts.get_exdesc())


@pexdoc.pcontracts.new_contract()
def wave_interp_option(obj):
    r"""
    Validate if an object is a :ref:`WaveInterpOption` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if not isinstance(obj, str):
        raise ValueError(exdesc)
    if obj.upper() in ["CONTINUOUS", "STAIRCASE"]:
        return None
    raise ValueError(exdesc)


@pexdoc.pcontracts.new_contract()
def wave_scale_option(obj):
    r"""
    Validate if an object is a :ref:`WaveScaleOption` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if not isinstance(obj, str):
        raise ValueError(exdesc)
    if obj.upper() in ["LINEAR", "LOG"]:
        return None
    raise ValueError(exdesc)


@pexdoc.pcontracts.new_contract()
def wave_vectors(obj):
    r"""
    Validate if an object is a :ref:`WaveVectors` pseudo-type object.

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if not isinstance(obj, list) or (isinstance(obj, list) and not obj):
        raise ValueError(exdesc)
    if any([not (isinstance(item, tuple) and len(item) == 2) for item in obj]):
        raise ValueError(exdesc)
    indep_vector, dep_vector = zip(*obj)
    if _check_increasing_real_numpy_vector(np.array(indep_vector)):
        raise ValueError(exdesc)
    if _check_real_numpy_vector(np.array(dep_vector)):
        raise ValueError(exdesc)
