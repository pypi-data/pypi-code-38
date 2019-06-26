#!/usr/bin/python3
"""command module of executor"""
from os import access, environ, X_OK, name as osname
try:
	from os import getuid, getresuid
except ImportError:
	def getuid(): return 1000
	def getresuid(): return 1000
from os.path import abspath, join as pjoin

from sys import stdout as _stdout, stderr as _stderr

from subprocess import run, Popen, PIPE
# for legacy subprocess compatibility while DEVNULL is new in subprocess
try:
	from subprocess import DEVNULL
except ImportError:
	DEVNULL = open('/dev/null')

_echo_ = _stdout.write
_puke_ = _stderr.write

#from system.which import which

class Command(object):
	"""Command class"""
	sh_ = True
	su_ = False
	dbg = False
	timeout = None
	def __init__(self, *args, **kwargs):
		for arg in args:
			if hasattr(self, str(arg)):
				setattr(self, arg, True)
			elif hasattr(self, '%s_'%arg):
				setattr(self, '%s_'%arg, True)
		if self.dbg:
			cb = '\033[1;30m'
			ce = '\033[0m'
			if osname == 'nt':
					cb = ''
					ce = ''
			_echo_('%s%s\n  %s\n  %s'%(
				cb, str(Command.__mro__),
				'\n  '.join('%s = %s'%(k, v) for \
					(k, v) in self.__dict__.items()), ce))

	@staticmethod
	def __which(prog):
		"""which function like the linux 'which' program"""
		delim = ';' if osname == 'nt' else ':'
		__path = ''
		for path in environ['PATH'].split(delim):
			if access(pjoin(path, prog), X_OK):
				__path = pjoin(abspath(path), prog)
		return __path

	@staticmethod
	def _str(commands):
		"""list/tuple to str converter"""
		#print(commands)
		return ' '.join(str(command) for command in list(commands))

	@staticmethod
	def __sucmd(sudobin, commands):
		if 'sudo' in commands[0]:
			del commands[0]
		if int(getuid()) != 0:
			commands.insert(0, sudobin)
		return commands

	def _list(self, commands):
		"""
		commands string to list converter assuming at least one part
		"""
		#print(commands)
		for cmd in list(commands):
			if cmd and max(len(c) for c in cmd if c) == 1 and len(cmd) >= 1:
				return list(commands)
			return self._list(list(cmd))

	def _sudo(self, commands=None):
		"""privilege checking function"""
		sudo = self.__which('sudo')
		if not commands:
			if getuid() == 0: return True
			if int(run([sudo, '-v']).returncode) == 0:
				return True
			sucmds = None
		else:
			sucmds = self.__sucmd(sudo, commands)
		return sucmds

	def __cmdprep(self, commands, func):
		commands = self._list(commands)
		if self.su_:
			commands = self._sudo(commands)
		if self.sh_:
			commands = self._str(commands)
		if self.dbg:
			_echo_('\033[01;30m%s\n  `%s`\t{sh: %s, su: %s}\033[0m\n'%(
                func, commands, self.sh_, self.su_))
		return commands

	def run(self, *commands):
		"""just run the command and return the processes PID"""
		commands = self.__cmdprep(commands, self.run)
		return Popen(
            commands,
            stdout=DEVNULL, stderr=DEVNULL, shell=self.sh_).pid

	def call(self, *commands, stdout=True, stderr=True, inputs=None, b2s=None):
		"""
		default command execution
		prints STDERR, STDOUT and returns the exitcode
		"""
		inputs = inputs.encode() if (inputs and b2s) else inputs
		stderr = stderr if stderr else DEVNULL
		stdout = stdout if stdout else DEVNULL
		commands = self.__cmdprep(commands, self.call)
		return int(run(
            commands, shell=self.sh_, stdout=stdout,
            stderr=stderr, timeout=self.timeout, input=inputs).returncode)

	def stdx(self, *commands, inputs=None, b2s=True):
		"""command execution which returns STDERR and/or STDOUT"""
		commands = self.__cmdprep(commands, self.stdx)
		inputs = inputs.encode() if (inputs and b2s) else inputs
		prc = Popen(
		    commands, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=self.sh_)
		out, err = prc.communicate(timeout=self.timeout, input=inputs)
		if b2s:
			out = u'%s'%(out).decode()
		if b2s:
			err = u'%s'%(err).decode()
		return out, err

	def stdo(self, *commands, inputs=None, b2s=True):
		"""command execution which returns STDOUT only"""
		inputs = inputs.encode() if (inputs and b2s) else inputs
		commands = self.__cmdprep(commands, self.stdo)
		prc = Popen(
		    commands, stdin=PIPE, stdout=PIPE, stderr=DEVNULL, shell=self.sh_)
		out, _ = prc.communicate(input=inputs, timeout=self.timeout)
		if b2s:
			out = u'%s'%(out).decode()
		return out

	def stde(self, *commands, inputs=None, b2s=True):
		"""command execution which returns STDERR only"""
		inputs = inputs.encode() if (inputs and b2s) else inputs
		commands = self.__cmdprep(commands, self.stde)
		prc = Popen(
		    commands, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=self.sh_)
		_, err = prc.communicate(timeout=self.timeout, input=inputs)
		if b2s:
			err = u'%s'%(err).decode()
		return err

	def erno(self, *commands, inputs=None, b2s=True):
		"""command execution which returns the exitcode only"""
		inputs = inputs.encode() if (inputs and b2s) else inputs
		commands = self.__cmdprep(commands, self.erno)
		prc = Popen(commands, stdin=PIPE, stdout=DEVNULL,
            stderr=DEVNULL, shell=self.sh_)
		prc.communicate(timeout=self.timeout, input=inputs)
		return int(prc.returncode)

	def oerc(self, *commands, inputs=None, b2s=True):
		"""command execution which returns STDERR only"""
		inputs = inputs.encode() if (inputs and b2s) else inputs
		commands = self.__cmdprep(commands, self.oerc)
		prc = Popen(
		    commands, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=self.sh_)
		out, err = prc.communicate(timeout=self.timeout, input=inputs)
		if b2s:
			out = u'%s'%(out).decode()
		if b2s:
			err = u'%s'%(err).decode()
		return out, err, int(prc.returncode)


command = executor = Command('sh')
sudo = sucommand = Command('sh', 'su')

def sudofork(*args):
	"""sudo command fork wrapper function"""
	if not [i for i in getresuid() if i != 0]: return 0
	eno = 0
	try:
		eno = int(sucommand.call(args))
	except KeyboardInterrupt:
		_echo_('\033[34maborted by keystroke\033[0m\n')
		eno = 431
	return eno

if __name__ == '__main__':
	exit(1)
