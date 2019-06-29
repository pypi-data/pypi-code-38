"""
Functions used throught the program.
"""

"""
Generic library imports
"""
import os
import json

"""
Functional imports
"""
import pyshellwrapper.defs 	as defs

def check_method_validity(type):
	def wrapper(fn):
		def wrapper_exec(self):
			return fn(self) if self.type == type else False
		return wrapper_exec
	return wrapper