# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log
from _sadm.deploy.loader import loadenv

def cmdArgs(parser):
	p = parser.add_parser('import', help = 'import sadm.env')
	p.add_argument('filename', help = 'sadm.env file to import')
	p.set_defaults(command = 'import')

def main(args):
	log.debug("import %s" % args.filename)
	return loadenv(args.filename)
