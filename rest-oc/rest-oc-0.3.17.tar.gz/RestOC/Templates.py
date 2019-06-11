# coding=utf8
""" Templates Module

Holds methods for handling templates
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-17"

# Pip imports
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pdfkit

# jinja2 environment
__moEnv = None

# preloaded templates
__mdTpls = {}

def init(folder):
	"""Init

	Initialise the Templates module

	Arguments:
		folder {str} -- The folder to find templates in

	Returns:
		None
	"""

	# Import the module variable
	global __moEnv

	# Init the template environment
	__moEnv = Environment(
		loader=FileSystemLoader(folder, followlinks=True, encoding='utf-8'),
		lstrip_blocks=True,
		trim_blocks=True
	)

def generate(tpl, data = {}, locale = 'en_US', pdf = False):
	"""Generate

	Generate content from a template and return it

	Arguments:
		tpl {str} -- The template to load
		data {dict} -- The keys/values to use in the template
		locale {str} -- The language to use, i.e. which folder to get the
			template from
		pdf {bool} -- Set to True to return a PDF of the generated template

	Returns:
		str
	"""

	# Import the module variables
	global __moEnv, __mdTpls

	# Generate the full path
	sPath = "%s/%s" % (locale, tpl)

	# If we don't already have the template
	if sPath not in __mdTpls:
		__mdTpls[sPath] = __moEnv.get_template(sPath)

	# Generate the template
	sContent = __mdTpls[sPath].render(**data)

	# If we want a PDF
	if pdf:
		return b64encode(pdfkit.from_string(sContent), False)

	# Return the content
	return sContent
