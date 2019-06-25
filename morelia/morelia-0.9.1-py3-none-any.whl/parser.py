# -*- coding: utf-8 -*-
#            __  __                _ _
#           |  \/  | ___  _ __ ___| (_) __ _
#           | |\/| |/ _ \| '__/ _ \ | |/ _` |
#           | |  | | (_) | | |  __/ | | (_| |
#           |_|  |_|\___/|_|  \___|_|_|\__,_|
#                             o        o     |  o
#                                 ,_       __|      ,
#                        |  |_|  /  |  |  /  |  |  / \_
#                         \/  |_/   |_/|_/\_/|_/|_/ \/
import re
import textwrap

from morelia.breadcrumbs import Breadcrumbs
from morelia.config import TOMLConfig
from morelia.exceptions import InvalidScenarioMatchingPattern, MissingStepError
from morelia.formatters import Writer
from morelia.grammar import (
    And,
    Background,
    But,
    Comment,
    Examples,
    Feature,
    Given,
    Row,
    Scenario,
    Step,
    Then,
    When,
)
from morelia.i18n import TRANSLATIONS
from morelia.visitors import TestVisitor


def execute_script(
    script_root,
    suite,
    scenario=".*",
    formatter=None,
    matchers=None,
    show_all_missing=True,
    config=None,
):
    try:
        scenario_re = re.compile(scenario)
    except re.error as e:
        raise InvalidScenarioMatchingPattern(
            'Invalid scenario matching regex "{}": {}'.format(scenario, e)
        )
    if config is None:
        config = TOMLConfig("default")
    matchers = __prepare_matchers(config, matchers, suite)
    wip = config["wip"]
    if not wip and show_all_missing:
        not_found = _find_missing_steps(script_root, matchers, scenario_re)
        message = "Cannot match steps:\n\n{}".format("".join(not_found))
        assert not_found == set(), message
    test_visitor = TestVisitor(suite, matchers, scenario_re)
    breadcrumbs = Breadcrumbs()
    test_visitor.register(breadcrumbs)
    __prepare_writers(config, formatter, test_visitor)
    try:
        script_root.accept(test_visitor)
    except Exception as exc:
        exc.__traceback__.tb_frame.f_locals
        tb = exc.__traceback__.tb_next
        while tb and not tb.tb_frame.f_locals.get("__tracebackhide__", False):
            tb = tb.tb_next
        if not tb:
            del tb
            raise
        exc.__traceback__ = tb.tb_next
        del tb
        raise exc from AssertionError(breadcrumbs)


def __prepare_matchers(config, matchers, suite):
    if matchers is None:
        matchers = config.get_matchers()
    matcher = _create_matchers_chain(suite, matchers)
    return matcher


def _create_matchers_chain(suite, matcher_classes):
    root_matcher = None
    for matcher_class in matcher_classes:
        matcher = matcher_class(suite)
        try:
            root_matcher.add_matcher(matcher)
        except AttributeError:
            root_matcher = matcher
    return root_matcher


def _find_missing_steps(feature, matcher, scenario_re):
    not_matched = {}  # "ordered dict/set" since 3.6 ;)
    for step in feature.get_all_steps():
        try:
            step.find_method(matcher)
        except MissingStepError as e:
            parent = step.parent
            if not isinstance(parent, Scenario) or scenario_re.match(
                step.parent.predicate
            ):
                not_matched[e.suggest] = True
    return not_matched.keys()


def __prepare_writers(config, formatter, test_visitor):
    writers = config.get_writers()
    if formatter is not None:
        writers.append(Writer(formatter))
    for writer in writers:
        test_visitor.register(writer)


class Parser:
    def __init__(self, language=None):
        self.__node_classes = [
            Feature,
            Background,
            Scenario,
            Given,
            When,
            Then,
            And,
            But,
            Row,
            Comment,
            Examples,
            Step,
        ]
        self.nodes = []
        if language is None:
            language = "en"
        self.__language = language
        self.__continuation_marker_re = re.compile(r"\\\s*$")

    def parse_features(self, prose):
        self.parse_feature(str(prose))
        feature = self.nodes[0]
        feature.filename = getattr(prose, "filename", "<stdin>")
        assert isinstance(feature, Feature), "Exactly one Feature per file"
        feature.enforce(
            any(isinstance(step, Scenario) for step in feature.steps),
            "Feature without Scenario(s)",
        )
        return self.nodes[0]

    def parse_feature(self, lines):
        self.__line_producer = LineSource(lines)
        self.__docstring_parser = DocStringParser(self.__line_producer)
        self.__language_parser = LanguageParser(default_language=self.__language)
        self.__labels_parser = LabelParser()
        try:
            while True:
                line = self.__line_producer.get_line()
                if line:
                    self.__parse_line(line)
        except StopIteration:
            pass
        return self.nodes

    def __parse_line(self, line):
        if self.__language_parser.parse(line):
            self.__language = self.__language_parser.language
            return

        if self.__labels_parser.parse(line):
            return

        if self.__docstring_parser.parse(line):
            previous = self.nodes[-1]
            previous.payload = self.__docstring_parser.payload
            return

        if self.__parse_node(line):
            return

        if 0 < len(self.nodes):
            self.__append_to_previous_node(line)
        else:
            line_number = self.__line_producer.line_number
            s = Step(line, line_number=line_number)
            feature_name = TRANSLATIONS[self.__language_parser.language].get(
                "feature", "Feature"
            )
            feature_name = feature_name.replace("|", " or ")
            s.enforce(False, "feature files must start with a %s" % feature_name)

    def __parse_node(self, line):
        line_number = self.__line_producer.line_number
        folded_lines = self.__read_folded_lines(line)
        line = line.rstrip()
        source = line + folded_lines
        for node_class in self.__node_classes:
            if node_class.match(line, self.__language):
                labels = self.__labels_parser.pop_labels()
                node = node_class(
                    source=source,
                    line_number=line_number,
                    labels=labels,
                    predecessors=self.nodes,
                    language=self.__language,
                )
                self.nodes.append(node)
                return node

    def __read_folded_lines(self, line):
        folded_lines = [""]
        while self.__continuation_marker_re.search(line):
            line = self.__line_producer.get_line()
            folded_lines.append(line)
        return "\n".join(folded_lines)

    def __append_to_previous_node(self, line):
        previous = self.nodes[-1]
        previous.append_line(line)


class LabelParser:
    def __init__(self, labels_pattern=r"@\w+"):
        self._labels = []
        self._labels_re = re.compile(labels_pattern)
        self._labels_prefix_re = re.compile(r"^\s*@")

    def parse(self, line):
        """Parse labels.

        :param str line: line to parse
        :returns: True if line contains labels
        :side effects: sets self._labels to parsed labels
        """
        if self._labels_prefix_re.match(line):
            matches = self._labels_re.findall(line)
            if matches:
                self._labels.extend(matches)
                return True
        return False

    def pop_labels(self):
        """Return labels.

        :returns: labels
        :side effects: clears current labels
        """
        labels = [label.strip("@") for label in self._labels]
        self._labels = []
        return labels


class LanguageParser:
    def __init__(self, lang_pattern=r"^# language: (\w+)", default_language=None):
        if default_language is None:
            default_language = "en"
        self.__language = default_language
        self.__lang_re = re.compile(lang_pattern)

    def parse(self, line):
        """Parse language directive.

        :param str line: line to parse
        :returns: True if line contains language directive
        :side effects: sets self.language to parsed language
        """
        match = self.__lang_re.match(line)
        if match:
            self.__language = match.groups()[0]
            return True
        return False

    @property
    def language(self):
        return self.__language


class DocStringParser:
    def __init__(self, source, pattern=r'\s*"""\s*'):
        self.__source = source
        self.__docstring_re = re.compile(pattern)
        self.__payload = []

    def parse(self, line):
        """Parse docstring payload.

        :param str line: first line to parse
        :returns: True if docstring parsed
        :side effects: sets self.payload to parsed docstring
        """
        match = self.__docstring_re.match(line)
        if match:
            start_line = line
            self.__payload = []
            line = self.__source.get_line()
            while line != start_line:
                self.__payload.append(line)
                line = self.__source.get_line()
            return True
        return False

    @property
    def payload(self):
        return textwrap.dedent("\n".join(self.__payload))


class LineSource:
    def __init__(self, text):
        self.__lines = iter(line for line in text.split("\n") if line)
        self.__line_number = 0

    def get_line(self):
        """Return next line.

        :returns: next line of text
        """
        self.__line_number += 1
        return next(self.__lines)

    @property
    def line_number(self):
        return self.__line_number
