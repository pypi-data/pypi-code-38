try: from kiwipiepycore import *
except:
	import os
	raise Exception("Sorry. kiwipiepy does not support current system '{}'.".format(os.name))