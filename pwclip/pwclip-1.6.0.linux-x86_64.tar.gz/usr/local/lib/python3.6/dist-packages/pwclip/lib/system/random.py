"""randomisation functions"""
from re import search
try:
	from os import urandom as getrandom
except ImportError:
	from random import random as urandom
	def getrandom(): return urandom()

def random(limit=10, regex=r'[\w -~]'):
	"""random character by limit"""
	rets = []
	while True:
		try:
			out = getrandom(1)
		except UnicodeDecodeError as err:
			continue
		try:
			out = out.decode('utf-8')
		except (AttributeError, UnicodeDecodeError) as err:
			#print(err)
			continue
		try:
			if search(regex, out).group(0):
				rets.append(out.strip())
		except AttributeError:
			continue
		if len(''.join(rets)) >= int(limit):
			break
	return ''.join(r for r in rets)

def biggerrand(num):
	"""greater random number"""
	while True:
		try:
			g = int(random(int(len(str(num))+1), regex=r'[0-9]*'))
		except ValueError:
			continue
		if g > int(num):
			break
	return g

def lowerrand(num):
	"""lower random number"""
	while True:
		try:
			g = int(random(int(len(str(num))), regex=r'[0-9]*'))
		except ValueError:
			continue
		if g > 1 and g < int(num):
			break
	return g

def randin(top, low=0):
	"""number in between low and top"""
	if low:
		low, top = top, low
	while True:
		try:
			g = int(random(int(len(str(top))), regex=r'[0-9]*'))
		except ValueError:
			continue
		if g > int(low) and g < int(top):
			break
	return g
