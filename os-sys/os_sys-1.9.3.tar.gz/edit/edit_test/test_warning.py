'''Test warnings replacement in pyshell.py and run.py.

This file could be expanded to include traceback overrides
(in same two modules). If so, change name.
Revise if output destination changes (http://bugs.python.org/issue18318).
Make sure warnings module is left unaltered (http://bugs.python.org/issue18081).
'''
from edit import run
from edit import pyshell as shell
import unittest
from test.support import captured_stderr
import warnings

# Try to capture default showwarning before edit modules are imported.
showwarning = warnings.showwarning
# But if we run this file within edit, we are in the middle of the run.main loop
# and default showwarnings has already been replaced.
running_in_edit = 'edit' in showwarning.__name__

# The following was generated from pyshell.edit_formatwarning
# and checked as matching expectation.
editmsg = '''
Warning (from warnings module):
  File "test_warning.py", line 99
    Line of code
UserWarning: Test
'''
shellmsg = editmsg + ">>> "


class RunWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_edit, "Does not work when run within edit.")
    def test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        run.capture_warnings(True)
        self.assertIs(warnings.showwarning, run.edit_showwarning_subproc)
        run.capture_warnings(False)
        self.assertIs(warnings.showwarning, showwarning)

    def test_run_show(self):
        with captured_stderr() as f:
            run.edit_showwarning_subproc(
                    'Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            # The following uses .splitlines to erase line-ending differences
            self.assertEqual(editmsg.splitlines(), f.getvalue().splitlines())


class ShellWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_edit, "Does not work when run within edit.")
    def test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        shell.capture_warnings(True)
        self.assertIs(warnings.showwarning, shell.edit_showwarning)
        shell.capture_warnings(False)
        self.assertIs(warnings.showwarning, showwarning)

    def test_edit_formatter(self):
        # Will fail if format changed without regenerating editmsg
        s = shell.edit_formatwarning(
                'Test', UserWarning, 'test_warning.py', 99, 'Line of code')
        self.assertEqual(editmsg, s)

    def test_shell_show(self):
        with captured_stderr() as f:
            shell.edit_showwarning(
                    'Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            self.assertEqual(shellmsg.splitlines(), f.getvalue().splitlines())


if __name__ == '__main__':
    unittest.main(verbosity=2)
