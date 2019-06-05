import requests
import os
import json
import delune
from rs4 import pathtool
import time
import socket
import pickle
from rs4.psutil import processutil
import sys, getopt
from rs4.psutil import service, daemon_class
from . import indexer

DUPLICATE_LOCK = "replicate-%s" % socket.getfqdn ()
DEBUG = True


class	Replicator (indexer.Indexer):
	NAME = "replicator"

	def __init__ (self, logpath, varpath, consol, config):
		indexer.Indexer.__init__ (self, logpath, varpath, consol, config)
		self.config_dir = None
		self.resource_dir = self.config.get ("resource_dir")
	
	def normpath (self, d):
		d = d.replace ("\\", "/")				
		if self.resource_dir:
			s = d.find ("/delune/config")
			if s == -1:
				s = d.find ("/delune/collections")
			d = os.path.join (self.resource_dir, d [s + 1:])			
		return d
		
	def download (self, alias, session, item):
		origin = self.config ["origin"]
		
		remotepath, savepath	= item
		pathtool.mkdir (os.path.split (savepath)[0])
		surl = "cols/" + remotepath
		url = "%s/%s" % (origin, surl)
		self.log ("downloading from %s" % url, "info", alias)
		
		response = session.get(url, stream=True)
		cl = int (response.headers ["Content-Length"])						
		rl = 0
		
		if not response.ok:
			self.log ("download failed  HTTP %d: %s" % (response.status_code, url), 'fail', alias)
			return -1
			
		with open(savepath, 'wb') as handle:
			if cl:
				for block in response.iter_content(1024):
					if self.enter_shutdown:
						raise daemon_class.ExitNow
					rl += len (block)
					if rl % 10240000 == 0:
						self.log ("%d%% downloaded %s" % (rl/cl * 100, surl), "info", alias)
					handle.write(block)				
				self.log ("downloaded %d of %d (%d%%) from %s" % (rl, cl, rl/cl * 100, surl), alias)
				
		if rl != cl:
			self.log ("incomplete download: %s" % url, 'fail', alias)
			return -1
		return 1			
	
	def replicate_collection (self, alias, remote_session, remote_status):
		origin = self.config ["origin"]
		keep_going = True		
		for name, ctime in remote_status ["locks"]:
			if name == "index":
				self.log ("origin is under indexing, skip updating index...", "warn", alias)
				return
		
		if keep_going:			
			local_segments = remote_status ["segments"][0]
			if not os.path.isfile (local_segments):
				local_latest_segments = -1				
			else:
				with open (local_segments, "rb") as f:
					temp = pickle.load (f)
				local_latest_segments = max (list(temp.segmentInfo.keys ()))
			origin_segments = [seginfo [0] for seginfo in remote_status ['segmentinfos']]
			
			if not origin_segments:
				self.log ("origin %s is empty", "warn", alias)
				keep_going = False
			elif max (origin_segments) < local_latest_segments:
				self.log ("origin is older version, maybe next time...", "warn", alias)
				keep_going = False
		
		que = []
		new_file = False		
		if keep_going:
			for d in remote_status ['indexdirs']:
				pathtool.mkdir (self.normpath (d))
			
			for group in remote_status ["segmentfiles"]:
				segs = remote_status ["segmentfiles"][group]
				
				if 'segments' in segs:
					sfn = segs.pop ('segments')[0]
					dfn = self.normpath (sfn)
					if group == "primary":
						que.append (("{}/devices/{}/segments".format (alias, group), dfn + ".new"))
					else:
						que.insert (0, ("{}/devices/{}/segments".format (alias, group), dfn))
				
				for seg, files in segs.items ():					
					if group == "primary" and int (seg) not in origin_segments:
						continue
					
					for sfn, ssize, smtime in files:
						dfn = self.normpath (sfn)
						if not os.path.isfile (dfn):
							que.insert (0, ("{}/devices/{}/segments/{}".format (alias, group, str(seg) + sfn [-4:]), dfn))
							new_file = True
						else:	
							dmtime = os.path.getmtime (dfn)
							dsize = os.path.getsize (dfn)
							if dsize == ssize and smtime <= dmtime:
								continue
							que.insert (0, ("{}/devices/{}/segments/{}".format (alias, group, str (seg) + sfn [-4:]), dfn))
							new_file = True
		
		if new_file:
			self.log ("downliad segments", "echo", alias)
			failed = 0
			for item in que:				
				#col, entity, group, fn, savepath
				if self.download (alias, remote_session, item) == -1:
					failed += 1
			
			local_segments = self.normpath (remote_status ["segments"][0])
			if failed:
				self.log ("replication failed, maybe mext time", "fail", alias)
				os.remove (local_segments + ".new")
			else:
				if os.path.isfile (local_segments):
					os.remove (local_segments)	
				os.rename (local_segments + ".new", local_segments)			
		
		colopt = remote_status ["colopt"]
		dcolopt = self.normpath (colopt ['path'])
		if not os.path.isfile (dcolopt) or colopt ["mtime"] > os.path.getmtime (dcolopt) or colopt ["size"] != os.path.getsize (dcolopt):
			with open (dcolopt, "w") as out:
				out.write (json.dumps (colopt ['data']))			
			self.log ("update collection configure", "info", alias)
		
	def replicate (self):
		remote_session = requests.Session ()
		origin = self.config ["origin"]
		
		while 1:
			alias = self.q.get ()
			if not alias:
				return
			if self.enter_shutdown:
				return
			with self.lock: self.working [alias] = None
			self.log ("checking...", "echo", alias)
			local_col = None
			try:
				remote_session.post ("%s/cols/%s/locks/%s" % (origin, alias, DUPLICATE_LOCK))
				r = remote_session.get ("%s/cols/%s" % (origin, alias))
				remote_status = r.json ()
				if self.config_dir is None:
					self.config_dir = self.normpath (os.path.dirname (remote_status ["colopt"]["path"]))
					pathtool.mkdir (self.config_dir)
					
				local_col = delune.collection (indexdir = [self.normpath (d) for d in remote_status ['indexdirs']], mode = delune.MODIFY)
				if local_col.lock.isplocked ("replicate") and not self.config.get ("ignore_lock", False):
					self.log ("on replicating, maybe next", "warn", alias)
					continue
				local_col.lock.lock ("index", str (os.getpid ()))		
				self.replicate_collection(alias, remote_session, remote_status)				
				local_col.removeDeletables ()
			
			except Exception as why:
				if not isinstance (why, daemon_class.ExitNow):
					self.trace ()

			try:
				remote_session.delete ("%s/cols/%s/locks/%s" % (origin, alias, DUPLICATE_LOCK))
			except:
				self.trace ()
			
			local_col and local_col.lock.unlock ("index")
			with self.lock: del self.working [alias]
			if self.enter_shutdown: return
	
	def maintern (self, origin_side):
		if not origin_side:
			# possibly error
			return
		if not self.config_dir:
			return 
		for alias in os.listdir (self.config_dir):
			if alias not in origin_side:
				if alias [0] in "#-":
					continue
				os.rename (os.path.join (self.config_dir, alias), os.path.join (self.config_dir, "-" + alias))
				self.log ("remote collection has been removed", 'warn', alias)
		indexer.Indexer.maintern (self, self.config_dir)
						
	def run (self):
		self.threading (self.replicate)
		while 1:			
			try:
				origin_side = requests.get ("%s/cols/" % self.config ["origin"]).json ()["collections"]
			except:
				self.trace ()
			else:
				self.maintern (origin_side) 
				self.reque (origin_side)
						
			if not self.wait_for_interval ():
				break			
							
	 	
def usage ():
	print ("""usage: 
  delune replicate [options] [start|stop|status|restart]

options:
  -d: daemonize
  -e, --exclude: <alias,...>
  -o, --origin: <origin>  
  -i, --interval: <int> interval seconds 
  -t, --threads: <int>
  
example:
  delune replicate -i 300 -vo http://192.168.1.200:5000/v1
	""")
	sys.exit ()

VARPATH = "/var/tmp/delune/replicator"
LOGPATH = "/var/log/delune/replicator"

def replicate (origin, model_root, ignore_lock = False):	
	f = Replicator (os.path.isdir (LOGPATH) and LOGPATH or None, VARPATH, True, {"origin": origin, "resource_dir": model_root, "ignore_lock": ignore_lock})
	f.start ()	
		 
def main ():
	cmd, config, console = indexer.parse_argv ("dv:o:t:i:e:", ["exclude=", "origin=", "threads=", "interval=", "resource-dir", "help"], usage)
	if not cmd or cmd in ("start", "restart"):
		assert "origin" in config, "origin required"	
		
	pathtool.mkdir (VARPATH)
	servicer = service.Service ("delune/{}".format (Replicator.NAME), VARPATH)
	if cmd and not servicer.execute (cmd):
		return
	if console and servicer.status (False):
		raise SystemError ("daemon is running")
	
	s = Replicator (LOGPATH, VARPATH, console, config)
	s.start ()	


if __name__ == "__main__":
	main ()	