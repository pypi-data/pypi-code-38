"""which module to find executables"""
from os import X_OK, access, environ, name as osname
from os.path import abspath, join as pjoin

def which(prog):
	"""which function like the linux 'which' program"""
	delim = ';' if osname == 'nt' else ':'
	for path in environ['PATH'].split(delim):
		if access(pjoin(path, prog), X_OK):
			return pjoin(abspath(path), prog)
	return ''
