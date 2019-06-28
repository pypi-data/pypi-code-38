import subprocess
from pathlib import Path
import platform


def cp(source, target, *args):
	"""Copy a file, or rather synchornize it.

	On Windows, use robocopy.
	One would have to wrap the executables and use Wine on Linux.

	Args:
		source (Path or str): Path to the source.
		target (Path or str): Path to the target.
		*args: further arguments to, e.g. robocopy.
	"""
	s, t = Path(source), Path(target)
	if platform.system() == 'Windows':
		proc = subprocess.call(['robocopy', str(s.parent), str(t), str(s.name)] + list(args))
	else:
		pass


def test_cp():
	if platform.system() == 'Windows':
		cp('C:/test_s/test.ref', 'C:/test_t')
		assert next(Path('C:/test_t').iterdir()) == Path('C:/test_t/test.ref')
		Path('C:/test_t/test.ref').unlink()


def random_folder_name(k=20):
	"""Generate a random name for a folder.

	Args:
		k (int): The length of the out string.
	Returns:
		A folder names.
	"""
	from random import choice
	from string import ascii_letters, digits
	return ''.join(choice(ascii_letters+digits) for n in range(int(k)))