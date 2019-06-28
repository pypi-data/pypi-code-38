# -*- coding: utf-8 -*-

"""
Module which implements all CLI command entry points.
"""

from __future__ import unicode_literals

import os
import sys
import time

from .loader import load_modules
from .matcher import merge_steps
from .stepregistry import StepRegistry
from .hookregistry import HookRegistry
from .runner import Runner
from .exceptions import ScenarioNotFoundError
from .terrain import world
from . import utils


def load_features(core, features, feature_tags=None, scenario_tags=None):
    """
    Load the given features
    """
    feature_files = []
    for given_feature in features:
        if not os.path.exists(given_feature):
            raise FeatureFileNotFoundError(given_feature)

        if os.path.isdir(given_feature):
            feature_files.extend(utils.recursive_glob(given_feature, "*.feature"))
            continue

        feature_files.append(given_feature)

    # parse feature and scenario tag expressions
    feature_tag_expression = None
    if feature_tags:
        feature_tag_expression = tagexpressions.parse(feature_tags)

    scenario_tag_expression = None
    if scenario_tags:
        scenario_tag_expression = tagexpressions.parse(scenario_tags)
    core.parse_features(feature_files, feature_tag_expression, scenario_tag_expression)

    if not core.features or sum(len(f.scenarios) for f in core.features) == 0:
        print(
            colorful.bold_red("Error: ")
            + colorful.red("please specify at least one feature to run")
        )
        if feature_tag_expression or scenario_tag_expression:
            print(
                colorful.red(
                    "You have specified a feature or scenario expression. Make sure those are valid and actually yield some features to run."
                )
            )
        return False
    return True


def show_features(core):
    """
    Show the parsed features
    """
    # load user's feature files
    if not load_features(core, world.config.features):
        return 1

    # set needed configuration
    world.config.write_steps_once = True
    if not sys.stdout.isatty():
        world.config.no_ansi = True

    runner = Runner(HookRegistry(), show_only=True)
    runner.start(core.features_to_run, marker="show")
    return 0


def show_steps(core):
    """
    Show all loaded steps within the basedir.
    """
    # load user's custom python files
    load_modules(world.config.basedir)
    for sentence, func in StepRegistry().steps.items():
        print(sentence)
        print(func)


def run_features(core):
    """
    Run the parsed features

    :param Core core: the radish core object
    """
    # We want to expand all features (preconditions)
    world.config.expand = True

    # load user's feature files
    if not load_features(
        core,
        world.config.features,
        world.config.feature_tags,
        world.config.scenario_tags,
    ):
        return 1

    # load user's custom python files
    load_modules(world.config.basedir)

    # match feature file steps with user's step definitions
    merge_steps(core.features, StepRegistry().steps)

    # run parsed features
    if world.config.marker == "time.time()":
        world.config.marker = int(time.time())

    # scenario choice
    amount_of_scenarios = sum(len(f.scenarios) for f in core.features_to_run)
    if world.config.scenarios:
        world.config.scenarios = [int(s) for s in world.config.scenarios.split(",")]
        for s in world.config.scenarios:
            if not 0 < s <= amount_of_scenarios:
                raise ScenarioNotFoundError(s, amount_of_scenarios)

    runner = Runner(HookRegistry(), early_exit=world.config.early_exit)
    return runner.start(core.features_to_run, marker=world.config.marker)
