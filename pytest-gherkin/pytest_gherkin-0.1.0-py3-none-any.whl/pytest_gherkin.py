# -*- coding: utf-8 -*-
import re
from os.path import join, dirname
from os import listdir
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import product
from inspect import signature
from gherkin.parser import Parser
from pprint import pformat
import logging
import pytest


LOGGER = logging.getLogger(__file__)
_AVAILABLE_ACTIONS = dict()


@pytest.fixture(autouse=True)
def _install_request(request):
    assert False
    _install_request.request = request
    yield
    del _install_request.request


def pytest_collect_file(parent, path):
    if path.ext == ".feature":
        return FeatureFile(path, parent)


class FeatureFile(pytest.File):
    def _get_example_sets(self, examples_list):
        """
        Scenarios can have multiple tables, I guess
        the idea is to make permutations of each row.
        """
        result = []
        seen_keys = set()
        for example in examples_list:
            table_keys = [cell["value"] for cell in example["tableHeader"]["cells"]]
            table_keys_set = set(table_keys)
            duplicated_keys = table_keys_set & seen_keys
            assert not duplicated_keys, f"Found some duplicated_keys: {duplicated_keys}"
            seen_keys |= table_keys_set
            table_value_dicts = []
            for table_row in example["tableBody"]:
                table_value_dicts.append(
                    dict(
                        zip(table_keys, [cell["value"] for cell in table_row["cells"]])
                    )
                )
            result.append(table_value_dicts)
        return product(*result)

    def collect(self):
        parser = Parser()
        with self.fspath.open() as handle:
            feature = parser.parse(handle.read())

            # Group the feature's children by type
            children = defaultdict(list)
            for child in feature["feature"].get("children", []):
                children[child["type"]].append(child)

            backgrounds = children.get("Background", [])

            # FIXME: support non-outline
            assert sorted(children) == ["Background", "ScenarioOutline"]

            for scenario_outline in children["ScenarioOutline"]:
                for example in self._get_example_sets(scenario_outline["examples"]):
                    yield ScenarioOutline(
                        name=scenario_outline["name"],
                        parent=self,
                        spec=scenario_outline,
                        example=example,
                        backgrounds=backgrounds,
                    )


class ScenarioOutline(pytest.Item):
    def __init__(self, *, name, parent, spec, example, backgrounds):
        super().__init__(name, parent)
        self.spec = spec
        self.example = example
        self.backgrounds = backgrounds

    def runtest(self):
        try:
            context = dict()
            steps = []
            for background in self.backgrounds:
                steps.extend(background["steps"])
            steps.extend(self.spec["steps"])
            for step in steps:
                print("step is", step)
                # Identify the action which will handle this step, along
                # with the parameter names which need to be passed in
                # explicitly from the gherkin feature file
                stripped_step = _ACTION_REGEX.sub("<>", step["text"])
                step_arg_names = [
                    match.group(1) for match in _ACTION_REGEX.finditer(step["text"])
                ]
                if stripped_step not in _AVAILABLE_ACTIONS:
                    raise GherkinException(self, "Undefined step", stripped_step)
                action, explicit_args = _AVAILABLE_ACTIONS[stripped_step]

                # This defines how examples are mapped into keywords for the
                # step function
                argument_map = dict(zip(step_arg_names, explicit_args))

                # add any extra args requested, which aren't specifically provided in params
                desired_kwargs = set(signature(action).parameters)
                arguments = {
                    argument_map[example_key]: example_value
                    for example_table in self.example
                    for example_key, example_value in example_table.items()
                    if argument_map.get(example_key) in desired_kwargs
                }

                # Respect any literal values in the step, assuming that any token
                # which didn't match an example is literal
                for literal_argument_value, argument_name in argument_map.items():
                    if argument_name not in arguments:
                        arguments[argument_name] = literal_argument_value

                for context_key, context_value in context.items():
                    if context_key not in arguments and context_key in desired_kwargs:
                        arguments[context_key] = context_value
                desired_kwargs -= set(arguments)
                for desired_kwarg in desired_kwargs:
                    # TODO: get this argument from a fixture, using request,
                    # when I have access to it
                    if desired_kwarg == "basket":
                        arguments["basket"] = dict()
                result = action(**arguments)
                if isinstance(result, dict):
                    # Update the context available for future steps with the result of this step
                    context.update(result)
        except:
            LOGGER.exception("Problem in pytest_gherkin")
            raise

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, GherkinException):
            return "\n".join(
                [
                    "usecase execution failed",
                    "   spec failed: %r: %r" % excinfo.value.args[1:3],
                    "   no further details known at this point.",
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name


class GherkinException(Exception):
    pass


_ACTION_REGEX = re.compile(r"<([^>]+)>")


def action(name):
    arg_names = [match.group(1) for match in _ACTION_REGEX.finditer(name)]
    stripped_name = _ACTION_REGEX.sub("<>", name)

    def decorator(fn):
        _AVAILABLE_ACTIONS[stripped_name] = (fn, arg_names)
        return fn

    return decorator
