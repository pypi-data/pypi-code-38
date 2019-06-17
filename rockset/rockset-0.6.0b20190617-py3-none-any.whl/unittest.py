import re
import sys
import unittest
from argparse import ArgumentParser

def main():
    ap = ArgumentParser(description='Rockset unittest main')
    ap.add_argument(
        '-b', '--buffer',
        help='Buffer output during run',
        action='store_true')
    ap.add_argument(
        '-c', '--catch',
        help='Catch Ctrl-C during run',
        action='store_true')
    ap.add_argument(
        '-f', '--failfast',
        help='Stop on first failure',
        action='store_true')
    ap.add_argument(
        '--locals',
        help='Show local variables in tracebacks',
        action='store_true')
    ap.add_argument(
        '-v', '--verbose',
        help='Verbose output',
        action='store_true')
    ap.add_argument(
        '-s', '--start-directory',
        help='Start directory',
        default='.')
    ap.add_argument(
        'patterns',
        help='Test regexes to run',
        nargs='*')

    args = ap.parse_args()
    patterns = [re.compile(p) for p in args.patterns]

    def filter_tests(tests):
        accepted = []
        for test in tests:
            if isinstance(test, unittest.TestSuite):
                accepted.append(test)
                continue
            test_id = test.id()
            if (not patterns) or any(p.match(test_id) for p in patterns):
                accepted.append(test)

        return unittest.TestSuite(accepted)

    if args.catch:
        unittest.installHandler()

    loader = unittest.TestLoader()
    loader.suiteClass = filter_tests
    suite = loader.discover(args.start_directory)
    runner = unittest.TextTestRunner(
        verbosity=2 if args.verbose else 1,
        failfast=args.failfast,
        buffer=args.buffer)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    main()
