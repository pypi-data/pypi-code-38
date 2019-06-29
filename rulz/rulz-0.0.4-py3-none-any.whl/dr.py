"""
This module implements an inversion of control framework. It allows
dependencies among functions and classes to be declared with decorators and the
resulting dependency graphs to be executed.
"""
import copy
import logging
import traceback
from collections import defaultdict
from functools import reduce as _reduce
from time import time

log = logging.getLogger(__name__)

HANDLERS = {}


class Skip(Exception):
    """
    Raise this exception when a component should be silently skipped.
    """


class Missing(Exception):
    """
    Raised when a component has missing dependencies.
    """
    def __init__(self, deps):
        self.deps = deps
        super(Missing, self).__init__(deps)


class plugin(object):
    """
    Base class of all plugin decorators. Subclasses can specialize the
    decorator interface or component invocation.
    """
    group = None
    tags = set()
    metadata = {}

    def __init__(self, *reqs, optional=None, group=None, tags=None,
            metadata=None, **kwargs):
        self.dep_spec = reqs
        self.optional = optional or []
        self.dep_list = self.__flatten(reqs) + self.optional
        self.deps = set(self.dep_list)
        self.group = group

        self.tags = set(self.__class__.tags)
        if tags is not None:
            self.tags |= set(tags)

        self.metadata = dict(self.__class__.metadata)
        if metadata is not None:
            self.metadata.update(metadata)

        self._update_attrs(kwargs)
        self.comp = None
        self.dependents = set()

    def __call__(self, comp):
        """
        Registers the component and its handler in the global ``HANDLERS``
        dictionary.
        """
        self.comp = comp
        HANDLERS[comp] = self
        for d in self.deps:
            if d in HANDLERS:
                HANDLERS[d].dependents.add(comp)
        return comp

    def get_missing(self, broker):
        """
        Examines the broker to see if it contains the dependencies needed to
        proceed with invocation of the component.
        """
        required = []
        at_least_one = []

        for s in self.dep_spec:
            if isinstance(s, list):
                if not any(d in broker for d in s):
                    at_least_one.append(s)
            else:
                if s not in broker:
                    required.append(s)

        if required or at_least_one:
            return (required, at_least_one)

    def invoke(self, broker):
        """
        Invokes the component with the arguments retrieved from the broker.
        This function can be overridden in subclasses to specialize the calling
        convention.
        """
        args = [broker.get(d) for d in self.dep_list]
        return self.comp(*args)

    def process(self, broker):
        """
        Checks for missing dependencies and calls invoke if the checks succeed.
        """
        missing = self.get_missing(broker)
        if missing is not None:
            raise Missing(missing)
        return self.invoke(broker)

    def _update_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise Exception(f"{self.__class__} has no attr named {key}.")

    @staticmethod
    def __flatten(reqs):
        tmp = []
        for r in reqs:
            if type(r) is not list:
                tmp.append(r)
            else:
                tmp.extend(r)
        return tmp


class Broker(dict):
    """
    Holds the state of an ongoing evaluation. Allows the registration of
    callbacks that get invoked after each component has attempted to execute.
    Also saves tracebacks and execution timings per component.
    """
    def __init__(self, seed=None):
        super().__init__(seed or {})
        self.observers = defaultdict(list)
        self.missing = {}
        self.timings = {}
        self.exceptions = defaultdict(list)

        if isinstance(seed, Broker):
            self.observers.update(seed.observers)
            self.exceptions.update(seed.exceptions)

    def __setitem__(self, component, instance):
        if component in self:
            raise KeyError(f"Already exists in broker with key: {component}")
        super().__setitem__(component, instance)

    def add_observer(self, callback, plugin_type=None):
        if isinstance(plugin_type, (set, list)):
            for pt in plugin_type:
                self.observers[pt].append(callback)
        else:
            self.observers[plugin_type].append(callback)

    def fire_observers(self, comp):
        plugin_type = type(HANDLERS[comp])
        for _type, observers in self.observers.items():
            if _type is None or issubclass(plugin_type, _type):
                for o in observers:
                    try:
                        o(comp, self)
                    except Exception as ex:
                        log.exception(ex)

    def add_exception(self, comp, ex):
        log.exception(ex)
        self.exceptions[comp].append(traceback.format_exc())


def get_group(group=None):
    """
    Get the set of components in the group along with their dependencies.
    """
    return {c: h.deps for c, h in HANDLERS.items() if h.group == group}


def get_subgraphs(graph):
    """
    Given a graph of possibly disconnected components, generate all subgraphs
    of connected components. graph is a dictionary of dependencies. Keys are
    components, and values are sets of components on which they depend.
    """
    keys = set(graph)
    frontier = set()
    seen = set()
    while keys:
        frontier.add(keys.pop())
        while frontier:
            component = frontier.pop()
            seen.add(component)
            frontier |= set([d for d in HANDLERS[component].deps if d in graph])
            frontier |= set([d for d in HANDLERS[component].dependents if d in graph])
            frontier -= seen
        yield {s: HANDLERS[s].deps for s in seen}
        keys -= seen
        seen.clear()


def get_graph(c):
    """
    Get the entire dependency graph starting with component(s) c. Does not
    include dependents.
    """
    keys = set(c if isinstance(c, (list, set)) else [c])

    frontier = set()
    seen = set()
    graph = {}
    while keys:
        frontier.add(keys.pop())
        while frontier:
            component = frontier.pop()
            seen.add(component)
            frontier |= set([d for d in HANDLERS[component].deps if d in HANDLERS])
            frontier -= seen
        graph.update({s: HANDLERS[s].deps for s in seen})
        keys -= seen
        seen.clear()

    return graph


def toposort(graph):
    """
    Order the graph so dependencies run first.

    Yields:
        a component at a time in an order that satisfies dependencies.
    """
    g = copy.deepcopy(graph)
    extra_items = _reduce(set.union, graph.values(), set()) - graph.keys()
    g.update({c: set() for c in extra_items})
    while g:
        ready = set(c for c, v in g.items() if not v)
        yield from ready
        g = {c: v - ready for c, v in g.items() if c not in ready}


def run_graph(graph=None, broker=None):
    """
    Executes each component of the graph using broker to maintain state.
    """
    graph = graph if graph is not None else get_group()
    broker = broker if broker is not None else Broker()
    for comp in toposort(graph):
        if comp in graph and comp not in broker and comp in HANDLERS:
            log.debug("Trying: %s", comp)
            start = time()
            try:
                broker[comp] = HANDLERS[comp].process(broker)
            except Missing as md:
                broker.missing[comp] = md.deps
                log.debug(md)
            except Skip:
                pass
            except Exception as ex:
                broker.add_exception(comp, ex)
            finally:
                broker.timings[comp] = time() - start
                broker.fire_observers(comp)
                log.debug("Result of %s: %s", comp, broker.get(comp))
    return broker


def run_subgraphs(graph=None, broker=None, pool=None):
    """
    Breaks the graph into subgraphs and executes each subgraph independently
    using broker as the starting state for each. If pool is passed, each
    subgraph is executed in parallel using the pool. pool must be a
    ``concurrent.futures.ThreadPoolExecutor``.

    Yields:
        Broker instance per subgraph
    """
    graph = graph if graph is not None else get_group()
    seed_broker = broker if broker is not None else Broker()

    def generate():
        for g in get_subgraphs(graph):
            yield g, Broker(seed_broker)

    if pool:
        futures = []
        for g, _broker in generate():
            futures.append(pool.submit(run_graph, graph, _broker))

        for f in futures:
            yield f.result()
    else:
        for g, _broker in generate():
            yield run_graph(g, broker=_broker)
