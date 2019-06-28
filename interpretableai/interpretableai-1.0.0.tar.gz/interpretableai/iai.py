import os as _os


from .mixeddata import MixedData


# Load Julia with IAI_DISABLE_INIT to avoid interfering with stdout during load
_os.environ['IAI_DISABLE_INIT'] = 'True'
from julia import Main as _Main
del _os.environ['IAI_DISABLE_INIT']


# Run Julia setup code
_script_dir = _os.path.dirname(_os.path.realpath(__file__))
try:
    _Main.include(_os.path.join(_script_dir, "setup.jl"))
except ImportError as err:
    # Trim Julia stacktrace from message
    msg = str(err).split("\n")[0]
    from future.utils import raise_from
    raise_from(ImportError(msg), None)


# Hack to get a reference to IAI without `import`
import julia as _julia
_IAI = _julia.core.JuliaModuleLoader().load_module("Main.IAI")


# Import Julia modules
from julia import Random as _Random
def set_julia_seed(*args):
    """Set the random seed in Julia to `seed`.

    Julia Equivalent:
    `Random.seed! <https://docs.julialang.org/en/v1/stdlib/Random/index.html#Random.seed!>`

    Examples
    --------
    >>> set_julia_seed(seed)
    """
    return _Random.seed_b(*args)


# Load Julia packages
from .iaibase import *
from .iaitrees import *
from .optimaltrees import *
from .optimpute import *


def read_json(filename):
    """Read in a learner saved in JSON format from `filename`.

    Julia Equivalent:
    `IAI.read_json <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.read_json>`

    Examples
    --------
    >>> read_json(filename)
    """
    jl_obj = _IAI.read_json_convert(filename)

    if _Main.isa(jl_obj, _IAI.OptimalTreeClassifier):
        lnr = OptimalTreeClassifier()
    elif _Main.isa(jl_obj, _IAI.OptimalTreeRegressor):
        lnr = OptimalTreeRegressor()
    elif _Main.isa(jl_obj, _IAI.OptimalTreeSurvivor):
        lnr = OptimalTreeSurvivor()
    elif _Main.isa(jl_obj, _IAI.OptimalTreePrescriptionMinimizer):
        lnr = OptimalTreePrescriptionMinimizer()
    elif _Main.isa(jl_obj, _IAI.OptimalTreePrescriptionMaximizer):
        lnr = OptimalTreePrescriptionMaximizer()

    Learner.__init__(lnr, jl_obj)
    return lnr
