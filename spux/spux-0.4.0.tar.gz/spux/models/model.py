# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base model class
# All class methods can be extended by inheriting and overwriting
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from ..utils.setup import isolate, plant
from ..utils.seed import Seed
from ..utils import shell
from ..utils import evaluations
from ..utils import serialize
from ..io.report import report

# List of Model class variables (identical for all instances)
# that could be modified in the custom constructor of the this inherited base class
# self.sandboxing - enable (set to 1), the default option, or disable (set to 0) sandboxing (see below for self.sandbox () usage)

# List of Model instance variables (different for each instance) set by 'isolate/plant' methods and available in all other methods:
# self.sandbox () - path to an isolated sandbox directory (if self.sandboxing == 1)
# self.verbosity - a integer indicating verbosity level for 'print ()' intensity management
# self.seed () - a list containing all hierarchical seeds
# self.seed.cumulative () - a (large) integer seed obtained by combining all hierarchical seeds
# self.rng - numpy.random.RandomState instance for use as 'random_state' in the scipy.stats distributions

# List of basic Model instance methods to be added or modified by the user:
# [optional] self.__init__ (...) - constructor to set internal model properties
# [mandatory] self.init (...) - initialization routine to set initial model state
# [mandatory] self.run (...) - routine to execute the model

# List of advanced Model instance methods to be added or modified by the user:
# [optional] self.exit (...) - finalization routine to clean up model output files
# [optional] self.save (...) - routine to save model state (for non-Python models)
# [optional] self.load (...) - routine to load model state (for non-Python models)
# [optional] self.state (...) - routine to construct an empty model state (for non-Python models)

# NOTE ON SANDBOXING:
# if sandboxing is enabled (and the 'template' argument is specified for the sandbox),
# in any of the above Model instance methods (except self.__init__),
# calling 'self.sandbox ()' returns a path to an isolated (clone of the 'template') directory

class Model (object):
    """Template class for users' Models."""

    # sandboxing enabled by default
    sandboxing = 1

    @property
    def name (self):

        return type(self).__name__

    @property
    def component (self):

        return 'Model'

    @property
    def evaluations (self):

        return evaluations.construct (self, 1)

    # attach an executor
    def attach (self, executor):
        """Attach an executor."""

        report (self, 'attach')

        self.executor = executor
        self.executor.setup (self)

    # isolate model to a sandbox
    # NOTE: 'isolate (...)' is called before each 'init (...)' and before each 'load (...)'
    def isolate (self, sandbox=None, verbosity=1, trace=1):
        """Isolate particle to its sandbox and propagate the 'verbosity' and 'trace' flags."""

        isolate (self, sandbox, verbosity, trace)

        if self.sandbox is not None:
            self.sandbox.copyin ()

    # plant model using specified 'seed'
    # NOTE: 'plant (...)' is called before the 'init (...)' and before each 'run (...)'
    def plant (self, seed=Seed(), informative=0):
        """Plant model using specified 'seed' and propagate the 'informative' flag."""

        plant (self, seed, informative)

    def shell (self, command):
        """Execute an application command (including any arguments) in a command line shell."""

        sandbox = self.sandbox () if self.sandboxing else None
        code = shell.execute (command, sandbox, self.verbosity)
        return code

    # initialize model using specified 'inputset' and 'parameters'
    def init (self, inputset, parameters):
        """Initialize model using specified 'inputset' and 'parameters'."""

        extras = {'parameters' : parameters}
        if inputset is not None:
            extras ['inputset'] = inputset
        report (self, 'init', extras = extras)

        # inherit this base class and write a custom 'init (...)' method
        # you can additionally execute base method by:
        # 'Model.init (self, inputset, parameters)'

    # run model up to specified 'time' and return the prediction
    def run (self, time):
        """Run model up to specified 'time' and return the prediction."""

        report (self, 'run', extras = {'time' : time})

        # inherit this base class and write a custom 'run (...)' method
        # you can additionally execute base method by 'Model.run (self, time)'

        # NOTE, that 'self.seed ()', 'self.seed.cumulative ()' and 'self.rng' change for _each_ call of 'self.run ()'

        # to return annotated results, use 'annotate' from spux.utils.annotate, e.g.
        # (here you can also return additional (not present in the datasets) prediction variables,
        # such as system energy, latent (hidden) stochastic parameters, etc.):
        # 'return annotate (y, ['y'], time)'

        # the full state of some complex models, for instance, in computational fluid dynamics,
        # consisting of large multi-dimensional arrays instead of just a couple of scalar values
        # can be assigned to the 'auxiliary' argument in the annotate (...) call:
        # 'return annotate (y, ['y'], time, auxiliary=any_python_object)'
        # By doing so, the predictions in the error model’s distribution (...) method
        # will instead be a dictionary containing predictions ['scalars'] as a pandas.DataFrame formed from the provided scalars,
        # and predictions ['auxiliary'] as a arbitrary Python object assigned by the model.
        # This auxiliary object will be accessible only in the error model, and will be discarded immidiately afterwards.

    # finalize model
    def exit (self):
        """Finalize model."""

        report (self, 'exit')

        # OPTIONAL: inherit this base class and write a custom 'exit (...)' method
        # you can additionally execute base method by 'Model.exit (self)'

    # save current model into its state
    # this is a fully functional method for pure Python models
    # OPTIONAL: inherit this base class and write a custon 'save (...)' method for other models
    # you can use helper routines in spux/drivers/ - check their sample usage in examples/
    def save (self):
        """Save the whole model into 'state'."""

        report (self, 'save')

        ignore = list (type(self).__dict__.keys ()) + ['sandbox', 'verbosity', 'trace'] + ['seed', 'informative']
        statedict = {key : value for key, value in self.__dict__.items () if key not in ignore}

        if not self.sandboxing:
            state = serialize.save (statedict)
        else:
            state = serialize.save ({'sandbox' : self.sandbox.save (), 'model' : statedict})

        return state

    # load specified model from its state
    # this is a fully functional method for pure Python models
    # OPTIONAL: inherit this base class and write a custon 'load (...)' method for other models
    # you can use helper routines in spux/drivers/ - check their sample usage in examples/
    def load (self, state):
        """Load the whole model previously saved in 'state'."""

        report (self, 'load')

        # ADVICE: as in 'init (...)', create all needed dynamical links to your model (loaded DLLs, Java Virtual Machine, etc.)
        # RATIONALE: 'model.load (...)' is called immediately after 'model.isolate (...)', i.e. without calling 'model.init (...)' beforehand

        if self.sandboxing:
            state = serialize.load (state)
            self.sandbox.load (state ['sandbox'])
            statedict = state ['model']
        else:
            statedict = serialize.load (state)

        self.__dict__.update (statedict)

    # construct a data container for model state with a specified size
    def state (self, size):
        """Construct a data container for model state with a specified size."""

        return serialize.state (size)
