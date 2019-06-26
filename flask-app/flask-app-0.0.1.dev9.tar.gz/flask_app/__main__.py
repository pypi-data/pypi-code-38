import argparse
import os
import shutil
import sys


cwd = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))


def program(argv):
    parser = argparse.ArgumentParser(
        description='My flask  app boilerplate code')
    parser.add_argument('appname', help='The application name')
    parser.add_argument('-d', '--destination', help='Folder to copy code to')
    args = parser.parse_args()

    appname = args.appname
    fullpath = os.path.join(cwd, appname)
    destination = args.destination
    shutil.copytree(os.path.join(script_dir, destination), fullpath)
    os.remove(fullpath+'/__main__.py')
    # create .env file
    shutil.copy(fullpath+'/.env.sample', fullpath+'/.env')


def main():
    program(sys.argv)


if __name__ == '__main__':
    main()
