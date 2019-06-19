#!/usr/bin/env python
# -*- coding: utf-8 -*-

# for py.test.
# this doesnt work if the module is under otree.bots, so i put it here
from otree.session import SESSION_CONFIGS_DICT


def pytest_addoption(parser):
    parser.addoption("--session_config_name")
    parser.addoption("--num_participants", type=int)
    parser.addoption("--export_path")


def pytest_generate_tests(metafunc):
    '''pass command line args to the test function'''
    option = metafunc.config.option

    metafunc.parametrize(
        "session_config_name,num_participants,export_path",
        [[option.session_config_name, option.num_participants, option.export_path]]
    )
