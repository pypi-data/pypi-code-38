import shlex
from subprocess import PIPE, Popen


def get_exitcode_stdout_stderr(cmd):
	"""
	Execute the external command and get its exitcode, stdout and stderr.
	"""
	args = shlex.split(cmd)

	sub_p = Popen(args, stdout=PIPE, stderr=PIPE)
	out, err = sub_p.communicate()
	exitcode = sub_p.returncode

	return exitcode, out, err
