#!/usr/bin/python
"""
This script runs all tests in the current directory and will return the best
next problem to work on in order.
"""

import sys
import glob
import unittest

Esc = '.FE'

class NextError(object):
    def __init__(self):
        self._key = None
        self._wait = 0

    def write(self, content):
        if not content.strip() or content[:3] in ("===", "---"):
            return

        if len(content) == 1:
            if content in Esc and Esc.index(content) > self._wait:
                self._wait = Esc.index(content)
            return

        if content[:9] == 'Traceback':
            if Esc.index(self._key[0]) == self._wait:
                self._write(self._key)
                self._write("")
                self._write(content.split('\n',1)[1])
                self._write("")
                self._wait = -1
            return

        if content.strip()[0] == '(':
            content = "\n".join(content.upper().replace(',','')[2:-1].split())

        if ': test_' in content:
            self._key = content
        elif content != "FAILED":
            self._write(content)

    def _write(self, c):
        sys.stderr.write(c.strip()+"\n")

    def flush(self):
        pass


output_to = sys.stderr

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['--next', '-n']:
        output_to = NextError()

    test_files = glob.glob('test_*.py')
    modules = [s[:-3] for s in test_files if 'compat' not in s]
    suites = [unittest.defaultTestLoader.loadTestsFromName(s) for s in modules]
    testSuite = unittest.TestSuite(suites)

    unittest.TextTestRunner(stream=output_to, descriptions=False).run(testSuite)
