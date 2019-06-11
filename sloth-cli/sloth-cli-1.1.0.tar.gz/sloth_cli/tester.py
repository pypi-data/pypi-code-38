import time
import typing
from argparse import ArgumentParser


def parser(arguments: typing.List[str] = None):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')  # noqa
    slowness = subparsers.add_parser(
        'fake', description='Shows seconds spent per line'
    )
    slowness.add_argument(
        '--fake-arg', '--fa',
        help='The file name to analyse',
        dest='filename'
    )
    return vars(parser.parse_args(args=arguments))


def run(arguments: typing.List[str] = None):
    r = parser(arguments)
    print('filename', r.get('filename'))
    for i in range(3):
        print(i)
        time.sleep(1)

        for i in range(3):
            print(i)


if __name__ == '__main__':
    run()
