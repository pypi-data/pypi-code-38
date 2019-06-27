# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.docker import DockerComponent as dc
from suanpan.docker.arguments import Json
from suanpan.utils import json


@dc.input(Json(key="inputData1", required=True))
@dc.output(Json(key="outputData1", required=True))
@dc.param(Json(key="param1", required=True))
def Demo(context):
    args = context.args
    return args.inputData1


if __name__ == "__main__":
    Demo(  # pylint: disable=all
        inputData1="input_test", outputData1="output_test", param1=json.dumps({"b": 2})
    )
