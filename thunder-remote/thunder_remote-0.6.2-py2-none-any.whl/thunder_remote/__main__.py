import argparse
import thunder_remote

from setup.PatchLibrary import PatchLibrary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='thunder_remote commandline interface')
    parser.add_argument('-p', '--patch', action='store_true', help='patches the inputs library for non-blocking usage')
    parser.add_argument('-v', '--version', action='store_true', help='Display the version and exits')
    args = parser.parse_args()

    if args.version:
        print(thunder_remote.__version__)
        quit(0)

    if args.patch:
        PatchLibrary.start()
        quit(0)

    print(parser.format_help())
