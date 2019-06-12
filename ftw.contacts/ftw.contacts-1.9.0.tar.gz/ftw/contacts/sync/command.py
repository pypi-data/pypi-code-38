import sys
import os


def do_sync_profiles(self, args):
    script = "{0}/sync.py".format(os.path.split(__file__)[0])
    # execfile() needs the source file
    if script.endswith('.pyc') or script.endswith('.pyo'):
        script = script[:-1]
    cmd = "import sys; sys.argv[:]=[];"
    if len(self.options.args) > 1:
        for arg in self.options.args[1:]:
            cmd += 'sys.argv.append(r\'%s\');' % arg
    cmd += 'execfile(r\'%s\')' % script
    cmdline = self.get_startup_cmd(self.options.python, cmd)
    exitstatus = os.system(cmdline)
    sys.exit(exitstatus)
