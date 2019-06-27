# coding=utf-8
from __future__ import absolute_import, print_function

import suanpan
from suanpan.utils import json
from tests.test_auto_args import Demo

env = {"STORAGE_TYPE": "local", "STORAGE_LOCAL_TEMP_STORE": "tmp"}
params = {
    "inputData1": "input_test",
    "outputData1": "output_test",
    "param1": json.dumps({"b": 2}),
}

suanpan.run("tests.test_auto_args.Demo", env=env, **params)

suanpan.run(Demo, env=env, **params)

with suanpan.env(**env):
    suanpan.run(Demo, **params)
