# 2017. 3. 13 by Hans Roh (hansroh@gmail.com)

from atila import Atila
import delune
from rs4 import pathtool
import os
import json
import codecs
import time
import shutil
import time

from services.admin import index
from services.v1 import api, collections, collection, documents

app = Atila (__name__)
app.last_maintern = time.time ()

app.mount ("/v1", api)
app.mount ("/admin", index)
app.mount ("/v1/cols", collections, collection, documents)

@app.before_mount
def before_mount (wasc):
	app.config.numthreads = wasc.numthreads	
	app.config.plock = wasc.get_lock (__name__)
	permission_check_handler = wasc.app.config.get ("permission_check_handler")
	if permission_check_handler:
		app.permission_check_handler (permission_check_handler)
		
	delune.configure (app.config.numthreads, wasc.logger.get ("app"), 16384, 128)
	pathtool.mkdir (api.getdir ("config"))
	
	for alias in os.listdir (api.getdir ("config")):
		if alias.startswith ("-"): # remove dropped col
			with app.config.plock:
				with codecs.open (api.getdir ("config", alias), "r", "utf8") as f:
					colopt = json.loads (f.read ())
				for d in [api.getdir ("collections", api.normpath(d)) for d in colopt ['data_dir']]:
					if os.path.isdir (d):
						shutil.rmtree (d)
				os.remove (api.getdir ("config", alias))
		elif alias.startswith ("#"): # unused col
			continue
		else:
			api.load_data (alias, app.config.numthreads, app.config.plock)
	app.store.set (delune.SIG_UPD, time.time ())
	  
@app.umounted
def umounted (wasc):
	delune.shutdown ()

@app.before_request
def before_request (was):
	if was.request.args.get ('alias') and not (was.request.routed.__name__ == "collections2" and was.request.method == "POST"):
		alias = was.request.args.get ('alias')
		if not delune.get (alias):
			return was.response.Fault ("404 Not Found", 40401, "resource %s not exist" % alias)

@app.maintain
def maintain_collections (was, now, count):
	configs = os.listdir (api.getdir ("config"))	
	for alias in configs:
		if os.path.getmtime (api.getdir ("config", alias)) <= app.store.get (delune.SIG_UPD):
			continue
		delune.close (alias)
		api.load_data (alias, app.config.numthreads, app.config.plock)
		was.setlu (delune.SIG_UPD)
		
	if was.getlu (delune.SIG_UPD) <= app.store.get (delune.SIG_UPD):
		return
	
	was.log ('collection changed, maintern ({}th)...' .format (count))										
	for alias in configs:
		if alias [0] in "#-" and delune.get (alias [1:]):
			delune.close (alias [1:])
		elif not delune.get (alias):
			api.load_data (alias, app.config.numthreads, app.config.plock)
	app.store.set (delune.SIG_UPD, was.getlu (delune.SIG_UPD))

#----------------------------------------------------------------------------

@app.route ("/status")
@app.permission_required (["index", "replica"])
def status (was):
	return was.status ()


