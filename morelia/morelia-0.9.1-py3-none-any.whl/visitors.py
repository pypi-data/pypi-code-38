import inspect
from abc import ABC
from typing import Iterable, List

from morelia.exceptions import MissingStepError
from morelia.grammar import Feature, Node, Scenario, Step, Visitor


class VisitorObserver(ABC):
    def feature_started(self, node: Feature) -> None:
        self.node_started(node)

    def feature_finished(self, node: Feature) -> None:
        self.node_finished(node)

    def scenario_started(self, node: Scenario) -> None:
        self.node_started(node)

    def scenario_finished(self, node: Scenario) -> None:
        self.node_finished(node)

    def step_started(self, node: Step) -> None:
        self.node_started(node)

    def step_finished(self, node: Step) -> None:
        self.node_finished(node)

    def step_failed(self, node: Step) -> None:
        pass

    def step_errored(self, node: Step) -> None:
        pass

    def node_started(self, node: Node) -> None:
        pass

    def node_finished(self, node: Node) -> None:
        pass


class ObservableVisitor:
    def __init__(self):
        self.__observers = []  # type: List[VisitorObserver]

    def register(self, observer: VisitorObserver) -> None:
        self.__observers.append(observer)

    def feature_started(self, node: Feature) -> None:
        for observer in self.__observers:
            observer.feature_started(node)

    def feature_finished(self, node: Feature) -> None:
        for observer in self.__observers:
            observer.feature_finished(node)

    def scenario_started(self, node: Scenario) -> None:
        for observer in self.__observers:
            observer.scenario_started(node)

    def scenario_finished(self, node: Scenario) -> None:
        for observer in self.__observers:
            observer.scenario_finished(node)

    def step_started(self, node: Step) -> None:
        for observer in self.__observers:
            observer.step_started(node)

    def step_failed(self, node: Step) -> None:
        for observer in self.__observers:
            observer.step_failed(node)

    def step_errored(self, node: Step) -> None:
        for observer in self.__observers:
            observer.step_errored(node)

    def step_finished(self, node: Step) -> None:
        for observer in self.__observers:
            observer.step_finished(node)

    def node_started(self, node: Node) -> None:
        for observer in self.__observers:
            observer.node_started(node)

    def node_finished(self, node: Node) -> None:
        for observer in self.__observers:
            observer.node_finished(node)


class TestVisitor(ObservableVisitor, Visitor):
    """Visits all steps and run step methods."""

    def __init__(self, suite, matcher, scenario_re):
        super().__init__()
        self.__prepare_setup_and_teardown(suite)
        self.__matcher = matcher
        self.__scenario_re = scenario_re

    def __prepare_setup_and_teardown(self, suite):
        self.setUpFeature = getattr(suite, "setUpFeature", self.noop)
        self.tearDownFeature = getattr(suite, "tearDownFeature", self.noop)
        self.setUpScenario = getattr(suite, "setUpScenario", self.noop)
        self.tearDownScenario = getattr(suite, "tearDownScenario", self.noop)
        self.setUpStep = getattr(suite, "setUpStep", self.noop)
        self.tearDownStep = getattr(suite, "tearDownStep", self.noop)

    def noop(self):
        pass

    def visit_feature(self, node: Feature, children: Iterable[Node] = []) -> None:
        self.setUpFeature()
        try:
            self.feature_started(node)
            self.__visit_children(children)
        finally:
            self.tearDownFeature()
            self.feature_finished(node)

    def visit_scenario(self, node: Scenario, children: Iterable[Node] = []) -> None:
        if not self.__scenario_re.match(node.predicate):
            return
        self.setUpScenario()
        try:
            self.scenario_started(node)
            self.__visit_children(children)
        finally:
            self.tearDownScenario()
            self.scenario_finished(node)

    def visit_step(self, node: Step, children: Iterable[Node] = []) -> None:
        self.step_started(node)
        self.setUpStep()
        try:
            self.__execute_step(node)
            self.__visit_children(children)
        except (MissingStepError, AssertionError):
            self.step_failed(node)
            raise
        except (SystemExit, Exception):
            self.step_errored(node)
            raise
        finally:
            self.tearDownStep()
            self.step_finished(node)

    def __execute_step(self, node: Step) -> None:
        __tracebackhide__ = True
        method, args, kwargs = node.find_method(self.__matcher)
        spec = inspect.getfullargspec(method)
        arglist = spec.args + spec.kwonlyargs
        if "_labels" in arglist:
            kwargs["_labels"] = node.get_labels()
        if "_text" in arglist:
            kwargs["_text"] = node.payload
        method(*args, **kwargs)

    def visit(self, node: Node, children: Iterable[Node] = []) -> None:
        try:
            self.node_started(node)
            self.__visit_children(children)
        finally:
            self.node_finished(node)

    visit_background = visit_row = visit_examples = visit_comment = visit

    def __visit_children(self, children: Iterable[Node]) -> None:
        for child in children:
            child.accept(self)
