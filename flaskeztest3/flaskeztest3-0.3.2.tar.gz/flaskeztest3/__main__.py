"""Define functions which will be able to be ran through package."""

from importlib import import_module
import sys
import os
import logging

from .helpers import parse_module_name_from_filepath
from .eztest import EZTest


def flaskeztest_main():
    """
    Call this from main entry point of flaskeztest package.
    """

    # Get rid of annoying output for every request
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    flask_module = os.environ.get('FLASK_APP')
    if flask_module is None:
        print("ERROR: FLASK_APP enviromnet variable must be set")
        sys.exit(1)

    try:
        flask_module = import_module(parse_module_name_from_filepath(flask_module))
    except ImportError:
        print(("ERROR: Could not import flask module \"%s\"" % flask_module))
        sys.exit(1)

    try:
        app = flask_module.app
        db = flask_module.db
    except AttributeError:
        print("ERROR: Could not find app or db attribute on flask module.")
        sys.exit(1)

    eztest = EZTest()
    eztest.init_with_app_and_db(app, db)

    suite_name, testcase_name = parse_cmdline_args()

    # Start up flask app and run our tests against it
    eztest.run(suite_name, testcase_name)

    # To terminate the flask app thread started in eztest.run()
    sys.exit(0)


def parse_cmdline_args():

    suite_name = None
    testcase_name = None

    if len(sys.argv) == 1:
        # Run all tests
        pass
    elif len(sys.argv) == 2:
        # Run suite specific
        suite_name = sys.argv[1]
    elif len(sys.argv) == 3:
        # Run test case specific
        suite_name = sys.argv[1]
        testcase_name = sys.argv[2]
    else:
        print("Error: Too many args")
        sys.exit(1)

    return suite_name, testcase_name


if __name__ == '__main__':
    flaskeztest_main()
