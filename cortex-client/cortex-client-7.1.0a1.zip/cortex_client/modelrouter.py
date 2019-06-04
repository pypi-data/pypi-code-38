"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import argparse
import base64
import json
import shlex
import subprocess
import sys

from .types import InputMessage
from .webserver import webserver_app
from .modelrunner import ModelRunner
from .modelprocess import ModelProcess

class ModelRouter:
    """
    Implements a CLI for running
    the ML algorithm and defines the CLI commands:

    - `--train` executes a train request.
    - `--inquire` executes an inquiry request.
    - `--inquire_init` executes an inquiry initialization request,
    - `--daemon` starts the web server / service to serve inquiry requests via HTTP.
    """

    def __init__(self, modelrunner):
        self.modelrunner = modelrunner

    @staticmethod
    def main(modelprocess: ModelProcess) -> None:
        """
        The function called to execute a ModelProcess.
        """
        output = ModelRouter(ModelRunner(modelprocess)).run()
        print("Output: ", output)

    def run(self):
        """
        Routing logic to run `train` or `predict` from the CLI.
        """
        args = vars(ModelRouter._build_parser().parse_args())
        if  args.get("daemon"):
            return self.run_service()
        else:
            context = self._parse_input(args["context"])
            if args.get("train"):
                return self.run_train(context)
            elif args.get("inquire"):
                return self.run_inquire(context)
            elif args.get("inquire_init"):
                return self.run_inquire_init(context)
            else:
                sys.exit("Illegal args: {}".format(args))

    def run_train(self, args):
        return self.modelrunner.run_train(args)

    def run_inquire(self, args):
        return self.modelrunner.run_inquire(args)

    def run_inquire_init(self, args):
        return self.modelrunner.run_inquire_init(args)

    def run_service(self):
        """
        Starts Flask service to receive inquiry requests.
        """
        try:
            # `serve` is a script that runs the prod-quality server
            subprocess.check_call(['serve'])
        except FileNotFoundError:
            # This path kept for backward compatibility...
            # TODO remove once all apps /services are moved to `serve` above
            print("Running Flask webserver...")
            webserver_app.modelrunner = self.modelrunner
            return webserver_app.run(host='0.0.0.0', debug=True, port=9091, use_reloader=False)

    @staticmethod
    def _build_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument('--context', required=False)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--train', action='store_true')
        group.add_argument('--inquire', action='store_true')
        group.add_argument('--inquire_init', action='store_true')
        group.add_argument('--daemon', action='store_true')
        return parser

    @staticmethod
    def _parse_input(input):
        try:
            input_j = json.loads(input)
        except Exception:
            input_b = base64.b64decode(input, validate=True)
            input_j = json.loads(input_b)
        return InputMessage.from_params(input_j)
