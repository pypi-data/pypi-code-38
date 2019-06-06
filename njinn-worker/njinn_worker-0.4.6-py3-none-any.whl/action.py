import configparser
import importlib
import io
import json
import os
import re
import signal
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout

import requests
from requests_jwt import JWTAuth, payload_path

from api_client import NjinnAPI
from cryptography.fernet import Fernet, InvalidToken


class Task():

    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.log = None
        self.preperation_log = io.StringIO()
        self.result = dict()
        self.state_info = ""

    def read_input_file(self):
        # load parameters
        with open(self.input_file_path) as input_file:
            self.input = json.load(input_file)

        self.working_dir = os.path.dirname(
            os.path.abspath(self.input_file_path))

        self.action = self.input["action"]
        self.pack = self.input["pack"]
        self.config_path = self.input["config_path"]
        self.execution_id = self.input['action_context']['njinn_execution_id']

    def load_action(self):
        # import action (try)
        action_entry_point = self.action.split(':')
        action_module = action_entry_point[0]
        action_class_name = action_entry_point[1]

        module = f"packs.{self.pack}.{action_module}"
        mod = importlib.import_module(module)
        action_class = getattr(mod, action_class_name)

        print(
            f"Running Action: {self.pack}.{action_class_name} ({self.pack}.{self.action})", file=self.preperation_log)
        self.action = action_class()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)

        self.njinn_api = config['DEFAULT']['njinn_api']
        self.secret = config['DEFAULT']['secret']
        self.worker_name = config['DEFAULT']['name']
        self.secrets_key = config['DEFAULT']['secrets_key']

    def load_njinn_api(self):
        self.njinn = NjinnAPI(self.njinn_api, self.secret,
                              self.worker_name, self.execution_id)
        setattr(self.action, '_njinn', self.njinn)

    def decrypt_secret_value(self, value, pattern=r'SECRET\(([-A-Za-z0-9+_=]+)\)'):
        """
        Looks for an encrypted variable and decrypt if found and
        also replaces it with the decrypted variable in ``value``.
        """

        original_value = value
        value_log = str(original_value)

        if isinstance(original_value, dict):
            value = {}
            value_log = {}
            for k, v in original_value.items():
                value[k], value_log[k] = self.decrypt_secret_value(v)
        elif isinstance(original_value, str):
            secret_values = re.findall(pattern, value)
            if secret_values:
                for secret_value in secret_values:
                    f = Fernet(self.secrets_key)
                    encrypted_variable = secret_value.encode()

                    try:
                        variable = f.decrypt(encrypted_variable).decode()
                        value = re.sub(pattern, variable, value, count=1)
                    except InvalidToken:
                        print("Invalid token for decryption of secret values.",
                              file=self.preperation_log)

                value_log = re.sub(pattern, '*' * 6, original_value)

        if len(value_log) > 40:
            value_log = value_log[:40] + '...'

        return value, value_log

    def prep_files_from_storage(self, value, pattern=r'FILE\(([0-9]+)\)'):
        """
        Looks for a file reference and downloads it. If found, replace the
        reference with the temp path to the file.
        """

        original_value = value

        if isinstance(original_value, dict):
            value = {}
            value_log = {}
            for k, v in original_value.items():
                value[k] = self.prep_files_from_storage(v)
        elif isinstance(original_value, str):
            files = re.findall(pattern, value)
            if files:
                for file in files:
                    file_path = self.njinn.download_file(
                        file, self.working_dir, self.preperation_log)
                    value = re.sub(pattern, file_path, value, count=1)

        return value

    def set_action_parameters(self):
        params = self.input['action_context']['parameters']

        for param, value in params.items():
            value = self.prep_files_from_storage(value)
            value, value_log = self.decrypt_secret_value(value)

            print(f"Setting \"{param}\" to \"{value_log}\"",
                  file=self.preperation_log)
            setattr(self.action, param, value)

        print("", file=self.preperation_log)

    def write_output_file(self):
        # writes self.stdout, self.stderr, self.run_return, ... to output file
        self.result['output'] = self.output
        self.result['log'] = self.preperation_log.getvalue(
        ) + self.log + f"\n{self.state.capitalize()}"
        self.result['state'] = self.state
        self.result['state_info'] = self.state_info

        with open(os.path.join(self.working_dir, 'out.json'), 'w') as fp:
            json.dump(self.result, fp)

    def setup_signals(self):
        """
        Sets up handler to process signals from the OS.
        """

        def signal_handler(signum, frame):
            """Setting kill signal handler"""
            # self.log.error("Killing subprocess")
            self.action.on_kill()
            raise Exception("Task received SIGTERM signal")

        signal.signal(signal.SIGTERM, signal_handler)

    def run_action(self):

        self.output = None
        self.log = ""
        stdout = io.StringIO()

        try:
            self.read_input_file()
            self.load_action()
            self.load_config()
            self.load_njinn_api()
            self.set_action_parameters()
            self.setup_signals()

            os.chdir(self.working_dir)

            with redirect_stdout(stdout):
                with redirect_stderr(stdout):
                    action_return = self.action.run()

            self.log = stdout.getvalue()

            if action_return is not None:
                if isinstance(action_return, dict):
                    self.output = action_return
                else:
                    self.output = {'result': action_return}

            self.state = "SUCCESS"

        except (Exception, KeyboardInterrupt) as e:
            error = traceback.format_exc()
            self.state_info = error
            self.output = {"error": self.state_info}
            self.state = "ERROR"
            if stdout:
                self.log = stdout.getvalue()
            self.log += self.state_info

        finally:
            self.write_output_file()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Invalid call. Require exactly one argument, which is the path to the inputfile.")
        sys.exit(1)

    task = Task(sys.argv[1])
    task.run_action()
