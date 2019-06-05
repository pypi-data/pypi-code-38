import pickle as pk
import os

def digest (field, word, version = "1.0"):
	return _delune.wint4 (hash (field + ":" + word))

def serialize (d):
	return pk.dumps (d, 1)

def deserialize (d):	
	return pk.loads (d)

def check_config (path):
	from rs4 import confparse
	this = confparse.ConfParse (path)
	confdir, alias = os.path.split (path)
	for file in os.listdir (confdir):
		if file == alias: continue
		other = confparse.ConfParse (os.path.join (confdir, file))
		for this_home in this.getopt ("home"):
			try:
				other.getopt ("home").index (this_home)
			except:
				continue
			else:
				raise LookupError("Directory `%s' is in used by `%s' index" % (this_home, file))
