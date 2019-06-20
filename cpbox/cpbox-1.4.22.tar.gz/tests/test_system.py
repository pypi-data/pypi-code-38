import unittest

from cpbox.tool import system
from cpbox.tool import file
from cpbox.tool.testutils import RandomDir
from cpbox.tool.datatypes import NameIdDict

class TestSystem(unittest.TestCase, RandomDir):

    def setUp(self):
        RandomDir.setUp(self)

    def tearDown(self):
        RandomDir.tearDown(self)

    def test_all(self):
        cmd = 'git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3'
        self._check(cmd)

        cmd = 'some command unknown'
        self._check(cmd)

    def _check(self, cmd):
        ret = system.run_cmd(cmd)

        file_name = self.temp_dir + '/shell-run.out'
        with open(file_name, 'w') as stdout_file:
            returncode = system.shell_run(cmd, stdout=stdout_file, exit_on_error=False, stderr=stdout_file)
        output = file.file_get_contents(file_name).rstrip('\n')
        self.assertEqual(ret[0], returncode)
        self.assertEqual(ret[1], output)

if __name__ =='__main__':
    unittest.main()
