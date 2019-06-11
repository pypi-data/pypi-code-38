"""
TimeReporter takes timing measurements made during
message processing and outputs them
to some external resource or service.

"""
from sparkplug.config import DependencyConfigurer
from sparkplug.logutils import LazyLogger
_log = LazyLogger(__name__)

import pkg_resources

import traceback

#################################################

registry = {}

#################################################

def parse_use(group, use, load_entry_point=pkg_resources.load_entry_point):
    """Parses and loads the entry point for a 'use' directive. The ``use``
    string is expected to look like ``dist#name`` and will be split on the
    first ``'#'`` into a ``dist, name`` pair. Then we pass the whole lot
    to the ``load_entry_point`` callback (using the same protocol as
    ``pkg_resources.load_entry_point``) and return whatever we get back.

    :param group: the entry point group to load from.
    :param use: the un-parsed ``use`` string.
    :param load_entry_point: the function that will actually load entry points.
    """
    dist, entry_point = use.split('#', 1)
    return load_entry_point(dist, group, entry_point)


class TimeReporterConfigurer(DependencyConfigurer):
    def __init__(self, name, use, aggregation_count, **kwargs):
        DependencyConfigurer.__init__(self)
        self.entry_point = parse_use('sparkplug.time_reporters', use)
        self.aggregation_count = max(int(aggregation_count),1)
        self.name = name
        self.kwargs = kwargs

    def start(self, channel):
        # instance the plugin and add it to the global registry:
        try:
            _log.debug("Creating time_reporter from %r", self.entry_point)
            registry[self.name] = self.entry_point(self.aggregation_count, **(self.kwargs))
        except:
            _log.error("Failure to start time_reporter %r", self.entry_point)
            _log.error(traceback.format_exc())

    def stop(self, channel):
        if self.name in registry :
           del registry[self.name]

    def __repr__(self):
        return "TimeReporter(name={}, aggregation_count={})".format(self.name, self.aggregation_count)
