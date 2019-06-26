"""userfind"""
import sys

def userfind(pattern='1000', mode='user'):
	"""
	userfind function:
        >>> 0 = user
        >>> 1 = x
        >>> 2 = uid
        >>> 3 = gid
        >>> 4 = comment
        >>> 5 = home
        >>> 6 = shell
	"""
	pfmap = {
      'user': 0,
      'x': 1,
      'uid': 2,
      'gid': 3,
      'comment': 4,
      'home': 5,
      'shell': 6}
	mode = int(pfmap[mode])
	pstr = str(pattern)
	try:
		with open('/etc/passwd', 'r') as pwd:
			hits = [
                f.split(':') for f in [
                    l for l in pwd.readlines() if pstr in l]]
			if hits:
				return hits[0][mode]
	except PermissionError as err:
		return False
