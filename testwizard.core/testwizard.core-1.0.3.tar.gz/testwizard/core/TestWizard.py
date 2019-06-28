from pprint import pprint
from argparse import ArgumentParser
import atexit
import os
import sys

from testwizard.core.Robot import Robot
from testwizard.core.Robot import TestSystemError
from testwizard.core.Session import Session

from testwizard.core.ResultCodes import ResultCodes

class TestWizard(object):
    def __enter__(self):
        parser = ArgumentParser()
        parser.add_argument("-s", "--sidecar", dest="sidecar", help="location of the sidecar file" )
        parser.add_argument("-t", "--testrun", dest="testrun", help="testrun" )
        args = parser.parse_args()
        #add the script filename to the args
        args.fileName = os.path.basename(sys.argv[0])
        #add the scriptpath to the args
        args.scriptPath = os.getcwd() + "\\" + args.fileName
        self.robot = Robot(args)
        self.session = Session(self.robot, args.testrun)

        return self

    def __exit__(self, type, value, traceback):
        if isinstance(value, TestSystemError):
            self.session.setResult(ResultCodes.SYSTEMERROR, str(value))
        elif isinstance(value, Exception):
            self.session.setResult(ResultCodes.SCRIPTERROR, str(value))

        self.session.dispose()
        self.robot.dispose()
