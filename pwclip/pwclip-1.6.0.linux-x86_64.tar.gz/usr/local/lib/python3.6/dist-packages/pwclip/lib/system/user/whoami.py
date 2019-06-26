"""system.user.whoami module"""
from os import environ
try:
	from os import getuid
	def whoami():
		"""whoami function like linux 'whoami' program"""
		with open('/etc/passwd', 'r') as pwf:
			pwl = pwf.readlines()
		return [
            u.split(':')[0] for u in pwl if int(u.split(':')[2]) == getuid()][0]
except ImportError:
	def whoami(): """whoami faker function""" ;return environ['USERNAME']

