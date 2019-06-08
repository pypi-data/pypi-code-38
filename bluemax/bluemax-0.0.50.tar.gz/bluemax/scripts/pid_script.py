import argparse
import logging
import os
import signal


logger = logging.getLogger(__name__)


class Stoppable:
    def __init__(self):
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="script to control the process that"
            " runs the threads in the background."
        )
        self.parser.add_argument(
            "command",
            metavar="command",
            help="the command to be run, may be `stop` or `start`",
        )
        self.parser.add_argument(
            "-p",
            "--pid",
            dest="pid_file",
            required=True,
            metavar="/path/to/pid/file",
            help="the path to where the pid file will be / is stored",
        )
        self.args = None

    def write_pid(self):
        pid = os.getpid()
        with open(self.args.pid_file, "w") as f:
            f.write(f"{pid}")

    def _start(self):
        self.write_pid()
        self.start()

    def start(self):
        pass

    def stop(self):
        pid_file = self.args.pid_file
        try:
            with open(pid_file, "r") as f:
                contents = f.read()
            pid = int(contents)
            os.kill(pid, signal.SIGINT)
            os.remove(pid_file)
        except:
            logger.info("could not find %s", pid_file)

    def main(self):
        self.args = self.parser.parse_args()
        if self.args.command == "start":
            self._start()
        elif self.args.command == "stop":
            self.stop()
