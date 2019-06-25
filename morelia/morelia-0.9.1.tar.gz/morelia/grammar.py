import copy
import itertools
import re
from abc import ABC, abstractmethod
from typing import Iterable, Type

from morelia.exceptions import MissingStepError
from morelia.i18n import TRANSLATIONS

PLACEHOLDER_RE = re.compile(r"\<(\w+)\>")


class Visitor(ABC):  # pragma: nocover
    @abstractmethod
    def visit_feature(self, node: "Feature", children: Iterable["Node"]) -> None:
        pass

    @abstractmethod
    def visit_scenario(self, node: "Scenario", children: Iterable["Node"]) -> None:
        pass

    @abstractmethod
    def visit_step(self, node: "Step", children: Iterable["Node"]) -> None:
        pass

    @abstractmethod
    def visit_background(self, node: "Background") -> None:
        pass

    @abstractmethod
    def visit_row(self, node: "Row") -> None:
        pass

    @abstractmethod
    def visit_examples(self, node: "Examples", children: Iterable["Node"]) -> None:
        pass

    @abstractmethod
    def visit_comment(self, node: "Comment") -> None:
        pass


class Node(ABC):
    allowed_parents = ()  # type: Iterable[Type[Node]]

    def __init__(
        self, source="", line_number=0, language="en", labels=None, predecessors=[]
    ):
        self.__source = source
        self.__line_number = line_number
        self.__language = language
        self.__labels = labels if labels is not None else []
        self.steps = []
        self.parent = None
        self.__predicate = self.__extract_predicate()
        self.parent = self.__find_parent(predecessors)
        self.__connect_to_parent()
        self._validate_predicate()

    def __connect_to_parent(self):
        if self.parent:
            self.parent.add_child(self)

    def __find_parent(self, predecessors):
        allowed_parents = self.allowed_parents
        if not allowed_parents and predecessors:
            self.enforce(False, "Only one Feature per file")
        for step in predecessors[::-1]:
            if isinstance(step, allowed_parents):
                return step
        return None

    def __extract_predicate(self):
        node_re = self.__get_compiled_pattern(self.__language)
        return node_re.sub("", self.source).strip()

    @classmethod
    def match(cls, line, language):
        node_re = cls.__get_compiled_pattern(language)
        return node_re.match(line)

    @classmethod
    def __get_compiled_pattern(cls, language, __memo={}):
        try:
            return __memo[cls, language]
        except KeyError:
            pattern = cls._get_pattern(language)
            node_re = __memo[cls, language] = re.compile(pattern)
            return node_re

    @classmethod
    def _get_pattern(cls, language):
        class_name = cls.__name__
        name = class_name.lower()
        name = TRANSLATIONS[language].get(name, class_name)
        return r"^\s*({name}):?(\s+|$)".format(name=name)

    @property
    def source(self):
        return self.__source

    @property
    def line_number(self):
        return self.__line_number

    @property
    def predicate(self):
        return self.__predicate

    def append_line(self, line):
        self.__source += "\n" + line
        self.__predicate = (self.__predicate + "\n" + line.strip()).strip()
        self._validate_predicate()

    def _validate_predicate(self):
        return  # looks good! (-:

    def get_labels(self):
        labels = self.__labels[:]
        if self.parent:
            labels.extend(self.parent.get_labels())
        return labels

    def get_all_steps(self):
        return itertools.chain.from_iterable(
            child.get_all_steps() for child in self.steps
        )

    def add_child(self, child):
        self.steps.append(child)

    def enforce(self, condition, diagnostic):
        if not condition:
            text = ""
            offset = 1
            if self.parent:
                text = self.parent.source
                offset = 5
            text += self.source
            text = text.replace("\n\n", "\n").replace("\n", "\n\t")
            raise SyntaxError(
                diagnostic, (self.get_filename(), self.line_number, offset, text)
            )

    def get_filename(self):
        try:
            return self.parent.get_filename() if self.parent else self.filename
        except AttributeError:
            return None

    def interpolated_source(self):
        return self.source + "\n"

    def format_fault(self, diagnostic):
        parent_reconstruction = ""
        if self.parent:
            parent_reconstruction = self.parent.source.strip("\n")
        args = (
            self.get_filename(),
            self.line_number,
            parent_reconstruction,
            self.source,
            diagnostic,
        )
        return '\n  File "%s", line %s, in %s\n %s\n%s' % args

    @abstractmethod
    def accept(self, visitor: Visitor) -> None:  # pragma: nocover
        pass


class Feature(Node):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_feature(self, self.steps)

    def prepend_steps(self, scenario):
        background = self.steps[0]
        try:
            background.prepend_steps(scenario)
        except AttributeError:
            pass


class Scenario(Node):
    allowed_parents = (Feature,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_indices = [0]

    def accept(self, visitor: Visitor) -> None:
        self.parent.prepend_steps(self)
        self.enforce(
            0 < len(self.steps),
            "Scenario without step(s) - Step, Given, When, Then, And, or #",
        )
        schedule = self.permute_schedule()

        old_row_indices = self.row_indices
        try:
            for indices in schedule:
                self.row_indices = indices
                visitor.visit_scenario(self, self.steps)
        finally:
            self.row_indices = old_row_indices

    def permute_schedule(self):
        dims = self.count_Row_dimensions()
        return _permute_indices(dims)

    def count_Row_dimensions(self):
        return [step.rows_number for step in self.steps if isinstance(step, RowParent)]

    def get_all_steps(self):
        return (step for step in self.steps if isinstance(step, Step))


class Background(Node):
    allowed_parents = (Feature,)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_background(self)

    def prepend_steps(self, scenario):
        try:
            return scenario.background_steps
        except AttributeError:
            background_steps = []
            for step in self.steps:
                new_step = copy.copy(step)
                new_step.parent = scenario
                background_steps.append(new_step)
            scenario.steps = background_steps + scenario.steps
            scenario.background_steps = background_steps
            return background_steps

    def count_Row_dimensions(self):
        return [0]

    def get_all_steps(self):
        return (step for step in self.steps if isinstance(step, Step))


class RowParent(Node):
    @property
    def rows_number(self):
        rows_number = len(self.get_rows()) - 1  # do not count header
        return max(0, rows_number)

    def get_rows(self):
        return [step for step in self.steps if isinstance(step, Row)]


class Step(RowParent):
    allowed_parents = (Scenario, Background)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload = ""

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_step(self, self.steps)

    def find_method(self, matcher):
        """Find method matching step.

        :param IStepMatcher matcher: object matching methods by given predicate
        :returns: (method, args, kwargs) tuple
        :rtype: tuple
        :raises MissingStepError: if method maching step not found
        """
        predicate = self.predicate
        augmented_predicate = self.__get_interpolated_predicate()
        method, args, kwargs = matcher.find(predicate, augmented_predicate)
        if method:
            return method, args, kwargs

        suggest, method_name, docstring = matcher.suggest(predicate)
        raise MissingStepError(predicate, suggest, method_name, docstring)

    def interpolated_source(self):
        augmented_predicate = self.__get_interpolated_predicate()
        return self.source.replace(self.predicate, augmented_predicate)

    def __get_interpolated_predicate(self):
        if self.parent is None:
            return self.predicate
        if self.__parent_has_no_rows():
            return self.predicate
        placeholders = PLACEHOLDER_RE.findall(self.predicate)
        if not placeholders:
            return self.predicate
        return self.__replace_placeholders_in_predicate(placeholders)

    def __parent_has_no_rows(self):
        dims = self.parent.count_Row_dimensions()
        return not any(dims)

    def __replace_placeholders_in_predicate(self, placeholders):
        copy = self.predicate[:]
        row_indices = self.parent.row_indices
        siblings = self.parent.steps
        for step_idx, row_idx in enumerate(row_indices):
            step = siblings[step_idx]
            table = step.get_rows()
            if len(table) > 1:
                header = table[0]
                body = table[1:]
                for column_idx, column_title in enumerate(header.values):
                    value = body[row_idx][column_idx]
                    copy = self.__replace_placeholders(
                        column_title, value, placeholders, copy
                    )
        return copy

    def __replace_placeholders(self, column_title, table_value, placeholders, copy):
        for placeholder in placeholders:
            if column_title == placeholder:
                return self.__replace_placeholder(copy, placeholder, table_value)
        return copy

    def __replace_placeholder(self, copy, placeholder, table_value):
        table_value = table_value.replace("\n", "\\n")
        return copy.replace(
            "<{placeholder}>".format(placeholder=placeholder), table_value
        )


class Given(Step):
    pass


class When(Step):
    pass


class Then(Step):
    pass


class And(Step):
    pass


class But(And):
    pass


class Examples(RowParent):
    allowed_parents = (Scenario,)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_examples(self, self.steps)


class Row(Node):
    allowed_parents = (Step, Examples)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_predicate()

    def _validate_predicate(self):
        # TODO: validate that grandparent is not Background
        row = re.split(r" \|", re.sub(r"\|$", "", self.predicate))
        self.__values = [s.strip() for s in row]

    def __getitem__(self, column_idx):
        return self.__values[column_idx]

    @property
    def values(self):
        return self.__values

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_row(self)

    @classmethod
    def _get_pattern(cls, language):
        return r"^\s*(\|):?\s+"


class Comment(Node):
    allowed_parents = (Node,)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_comment(self)

    @classmethod
    def _get_pattern(cls, language):
        return r"\s*(\#)"

    def _validate_predicate(self):
        self.enforce("\n" not in self.predicate, "linefeed in comment")


def _permute_indices(arr):
    product_args = list(_imap(arr))
    result = list(itertools.product(*product_args))
    return result
    #  tx to Chris Rebert, et al, on the Python newsgroup for curing my brainlock here!!


def _imap(*iterables):
    iterables = [iter(i) for i in iterables]
    while True:
        try:
            args = [next(i) for i in iterables]
            yield _special_range(*args)
        except StopIteration:
            return


def _special_range(n):
    return range(n) if n else [0]
