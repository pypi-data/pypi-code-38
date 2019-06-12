# # # # # # # # # # # # # # # # # # # # # # # # # #
# Executor base class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from ..io.formatter import compactify
from ..io import dumper
from ..utils import environment
from ..report import generate

class AddressCall (object):
    """MPI addresses, hirerachy and resources"""

    def __init__ (self, root, owner, name, resources, addresscall):
        """Do bookkeeping"""

        self.root = root
        self.owner = owner
        self.name = name
        self.resources = resources
        self.addresscall = addresscall

    def __call__ (self, peers):
        "Return rank in 'peers' intra-communicator with hirerachy of higher resources and tasks"

        address = self.addresscall (peers)
        return self.root + [{'owner' : self.owner, 'name' : self.name, 'resources' : self.resources, 'address' : address}]

    def __str__ (self):
        "Assemble hirerachy of resources and tasks"

        out = '.'
        for level in self.root:
            out += '/%s-%s%s' % (level ['owner'], level ['name'], '-%d' % level ['address'] if level ['address'] is not None else '')
        out += '/%s-%s%s' % (self.owner, self.name, '-address()' if self.addresscall is not None else '')

        return out

class Executor (object):
    """Base class for instances of type Executor, which execute tasks."""

    verbosity = 0
    connector = None

    @property
    def name (self):

        return type(self).__name__

    def setup (self, owner=None, rootcall=None, verbose=0, task=None):
        """Base method to setup instances of type Executor.

        This includes taking the task either from the higher level (owner) or from the 'task' variable
        """

        if owner is not None:
            self.task = owner.task
            self.owner = type(owner).__name__
            self.ownerbase = type(owner).__bases__[0].__name__
            if self.ownerbase == 'object':
                self.ownerbase = 'model'
        else:
            if task is not None:
                self.task = task
            else:
                self.task = None
            self.owner = 'none'
            self.ownerbase = 'none'
        self.rootcall = rootcall

        if self.verbosity and verbose:
            print ('%s executor setup: %s with rootcall: %s' % (self.owner, self.name, self.rootcall))

    # initialize executor
    def init (self, connector=None, peers=None, internal=0, directory='report'):
        """Base method to initialize instances of type Executor."""

        # set connector
        if connector is not None:
            self.connector = connector

        # if this is not an internal init
        if not internal:

            # store environment
            entries = [{'Descriptor' : key, 'Value' : environment.entries [key]} for key in environment.headers]
            headers = ['Descriptor', 'Value']
            title = 'Computational environment'
            dumper.report (directory, 'environment', environment, title, entries, headers)

            # assemble resources
            resources = self.resources ()

            # report and store resources
            entries, headers, title, align = self.table (resources, verbosity = 0)
            dumper.report (directory, 'resources', resources, title, entries, headers, align)

            # init connector
            if self.connector is not None:
                self.connector.init (resources)

        # set root
        if self.rootcall is not None:
            self.root = self.rootcall (peers)
        else:
            self.root = []

        # prepare template task
        self.prepare (self.task)

        # bootup executor
        self.port = self.bootup (peers)
        if self.verbosity:
            print ('%s executor init: %s for a task %s with root %s and port %s' % (self.owner, self.name, type(self.task).__name__, compactify (self.root), self.port))

        return self.port

    # format resources into table entries and text with advice
    def table (self, resources = None, verbosity = 1):
        """Organize information for nice printouts."""

        if resources is None:
            resources = self.resources ()

        # estimate the percentage of the manager cores
        managers = 0
        for resource in resources [::-1]:
            managers = resource ['manager'] + resource ['workers'] * managers
        total = resources [0] ['cumulative']
        percentage = round (100 * managers / total)

        # costruct table entries
        headers = ['Component', 'Class', 'Task', 'Executor', 'manager', 'workers', 'resources', 'cumulative']
        entries = []
        if resources [-1] ['resources'] == 1:
            entries += [{'Component' : 'Model', 'Class' : resources [-1] ['Task'], 'Task' : '-', 'Executor' : '-', 'manager' : 0, 'workers' : 1, 'resources' : 1, 'cumulative' : 1}]
        entries += resources [::-1]
        title = 'Required computational resources'
        if total > 1:
            title += ' (~%d%% managers)' % percentage
        align = (['l'] * 4) + (['r'] * 4)

        # construct table
        text = generate.txt_table (entries, headers, title, align)

        # advice on parallelization, if needed
        if percentage > 20 and total > 8:
            text += ' :: WARNING: Managers of parallel executors consume more than 20%% of total computational resources.' + '\n'
            text += '  : -> For production runs (more than 8 cores), consider improving parallelization configuration:' + '\n'
            text += '  : -> Allocate most workers to the executors of the outer-most SPUX component(s) (e.g. ``sampler``).' + '\n'
            text += '  : -> Replace parallel executors with few workers (less than 4) by ``Serial`` executors.'

        if verbosity:
            print (text)

        return entries, headers, title, align

    # finalize executor
    def exit (self):
        """Base method to shutdown instances of type Executor."""

        # shutdown executor
        self.shutdown ()
        if self.verbosity:
            print ('%s executor exit: %s for a task %s' % (self.owner, self.name, type(self.task).__name__))

    # bind executor to a worker
    def bind (self, root, port):
        """Base method to bind instances of type Executor to a worker."""

        # set root
        self.root = root

        # set port
        self.port = port

        # report
        if self.verbosity:
            print ('%s executor bind: %s with root %s and port %s' % (self.owner, self.name, compactify (self.root), self.port))

    # prepate (setup) task executor
    def prepare (self, task):
        """Base method to prepare (by 'setup') the 'executor' of 'task'."""

        task.rootcall = self.addresscall ()
        if hasattr (task, 'executor'):
            task.executor.connector = self.connector
            task.executor.setup (task, rootcall=self.addresscall(), verbose=1)

    def resources (self, verbose=0):
        """Base method to compute the needed resources of an instance of type Executor.

        It accounts for all the downstream levels requirements.
        """

        task_resources = self.task.executor.resources () if hasattr (self.task, 'executor') and hasattr (self.task.executor, 'resources') else []
        resources = task_resources [0] ['cumulative'] if len (task_resources) != 0 else 1
        cumulative = self.manager + self.workers * resources
        if self.verbosity and verbose:
            if hasattr (self, 'info'):
                print ('%s executor: %s with info:' % (self.owner, self.name), self.info ())
            print ('%s executor: %s with resources for each %s task:' % (self.owner, self.name, type(self.task).__name__), resources)
            print ('%s executor: %s with cumulative resources: %s%s x %d = %d' % (self.owner, self.name, '1 + ' if self.manager else '', self.workers, resources, cumulative))

        dictionary = {}
        dictionary ['Component'] = self.ownerbase
        dictionary ['Class'] = self.owner
        dictionary ['Task'] = type(self.task).__name__
        dictionary ['Executor'] = self.name
        dictionary ['manager'] = self.manager
        dictionary ['workers'] = self.workers
        dictionary ['resources'] = resources
        dictionary ['cumulative'] = cumulative
        return [dictionary] + task_resources

    def addresscall (self):
        """Base method to return level resources of an instance of type Executor."""

        return AddressCall (self.root, self.owner, self.name, self.resources () [0] ['resources'], self.address)

    def capabilities (self, methods):
        """Base method to check whether requested 'methods' are available for this type of Executor."""

        if not all ([hasattr (self, method) for method in methods]):
            print (' :: ERROR: executor %s does not have all capabilities required by %s: %s' % (self.name, self.owner, methods))
            self.abort ()
