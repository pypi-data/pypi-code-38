from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import subprocess
import sys
import os


try:
    typhoon_dir = os.environ["TYPHOON"]
except KeyError:
    raise Exception('"TYPHOON" environment variable was not detected.'
                    ' Make sure Typhoon HIL Control Center is properly installed.')


def run_allure(alluredir):
    # alluredir is an absolute path, because our working directory is the plugin folder so it can find allure bat script.
    allure_path = os.path.join(typhoon_dir, "allure", "bin", "allure_typhoon.bat")
    cmd = "\"{}\" serve \"{}\"".format(allure_path, alluredir)
    subprocess.call(cmd)


def main():
    arg1 = sys.argv[1]
    cwd = os.getcwd()
    abs_path = os.path.join(cwd, arg1)
    print("Absolute test report path: {}".format(abs_path))
    run_allure(abs_path)


if __name__ == "__main__":
    main()
