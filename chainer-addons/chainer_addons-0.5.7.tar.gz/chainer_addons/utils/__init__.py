
def all_children(model):
	"""
		Iterate over all links in a (nested) chain.
	"""

	for child in model.children():
		grand_children = list(child.children())
		if grand_children:
			for grand_child in all_children(child):
				yield grand_child
		else:
			yield child

import os
import logging, simplejson as json
from os.path import isdir, isfile, join

def prepare_output(output, args):

	if not isdir(output):
		os.makedirs(output)

	if not isfile(join(output, ".nobackup")):
		open(join(output, ".nobackup"), "w").close()

	args_dump = join(output, "args.json")
	logging.info("Saving arguments to \"{}\"".format(args_dump))
	with open(args_dump, "w") as f:
		json.dump(args, f, indent=2)
