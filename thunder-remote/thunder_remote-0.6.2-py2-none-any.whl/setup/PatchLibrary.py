import imp
from shutil import copyfile

from setuptools import Command


class PatchLibrary(Command):
    """
    Update 'inputs.py' for non-blocking gamepad access
    """

    description = 'patches inputs.py to be non-blocking'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        PatchLibrary.start()

    @staticmethod
    def start():
        patch = 'thunder_remote/patch/inputs.py'
        path = imp.find_module('inputs')[1]

        print("copying {0} -> {1}".format(patch, path))
        copyfile(patch, path)
