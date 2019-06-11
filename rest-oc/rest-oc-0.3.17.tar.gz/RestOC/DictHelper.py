# coding=utf8
""" Dictionary Helper Module

Several useful helper methods for use with dicts
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

# Python imports
import sys

def clone(src):
	"""Clone

	Goes through the dict and any child dicts copying the values so that we
	don't have any references

	Arguments:
		src {dict} -- The source dict

	Returns:
		dict
	"""

	# Check the argument
	if not isinstance(src, dict):
		raise ValueError('%s is not a valid value for src argument of %s' % (str(src), sys._getframe().f_code.co_name))

	# Initialise the new dict
	dRet = {}

	# Get each key of the source dict
	for k in src:

		# If the key points to another dict
		if isinstance(src[k], dict):

			# Call clone on it
			dRet[k] = clone(src[k])

		# Else if the key points to a list
		elif isinstance(src[k], list):

			# Use list magic to copy it
			dRet[k] = src[k][:]

		# Else it's a standard variable
		else:
			dRet[k] = src[k]

	# Return the new dict
	return dRet

def combine(first, second):
	"""Combine

	Generates a new dict by combining the two passed, values in second will
	overwrite values in first

	Arguments:
		first {dict} -- The dict to be changed/overwritten
		second {dict} -- The dict that will do the overwriting

	Returns:
		dict
	"""

	# Make sure both arguments are actual dicts
	if not isinstance(first, dict):
		raise ValueError('%s is not a valid value for first of %s' % (str(first), sys._getframe().f_code.co_name))
	if not isinstance(second, dict):
		raise ValueError('%s is not a valid value for second of %s' % (str(second), sys._getframe().f_code.co_name))

	# Copy the first dict
	dRet = clone(first)

	# Get each key of the second dict
	for m in second:

		# If the value is another dict and it exists in first as well
		if isinstance(second[m], dict) and m in dRet and isinstance(dRet[m], dict):

			# Call combine
			dRet[m] = combine(dRet[m], second[m])

		# else we overwrite the value as is
		else:
			dRet[m] = second[m]

	# Return the new dict
	return dRet

# Evaluate function
def eval(src, contains):
	"""Eval(uate)

	Goes through a dict looking for keys from contains

	Arguments:
		src {dict} -- The dict we are evaluating
		contains {list} -- A list of values to check for, if the value is a dict
			rather than a string, epects keys to be keys pointing to further
			lists of keys

	Return:
		A list of errors, or None
	"""

	# Initialise the list of errors
	lErrs = []

	# Go through each contains value
	for s in contains:

		# If the value is a string
		if isinstance(s, str):

			# If value does not exist in the source
			if s not in src or (isinstance(src[s], str) and not src[s]):
				lErrs.append(s)

		# Else, if we got a dict
		elif isinstance(s, dict):

			# Go through the key/value pairs in the dict
			for k,v in s.items():

				# If the key doesn't exist in the source or has no value
				if k not in src or not src[k]:
					lErrs.append(k)

				# Else, check the children
				else:

					# Call the eval on the child dict
					lChildErrs = eval(src[k], v)

					# Add errors to the list
					if lChildErrs:
						for sErr in lChildErrs:
							lErrs.append(k + '.' + sErr)

		# We got an unknown type of key
		else:
			lErrs.append(str(s))

	# If there's any errors
	if lErrs:
		raise ValueError(*lErrs)
