"""
This file is the base of the session object
"""

def session(inheritance):
	# This function is made to dinamically inherite the session object.
	# This is important becanse sessions are supposed to support every
	# method supported by the service that's calling it

	class Session(inheritance):
		def __init__(self,*args, **kargs):
			# This method should have two behavior if an url is given,
			# Do a Getcapabilities at this url, else just create the object

			# Go fetch the service default version and use it as the default
			# in the new session
			self.version = self.defaultVersion

			# Create a dict that will contain all the sources and their
			# respective informations
			self.sources = {}

			# Check to see if an url arguments was passed
			if not args == ():
				# Go request a Getcapabilities and store valuable informations
				# at the right place
				getCapRes = self.getcapabilities(*args, **kargs)

				# Add the Getcapabilities to the dictionary of sources
				self.sources[args[0]] = getCapRes
		def update(self,*args,**kargs):
			# This method update information about layers with new
			# Getcapabilities
			if args == ():
				# If no url where given, update all
				for sou in self.sources:
					self.sources[sou] = self.getcapabilities(sou)
			else:
				# If a url where given, update/add only this url.
				try:
					self.sources[args[0]] = self.getcapabilities(*args,**kargs)
				except:
					pass
				
		def add(self,*args,**kargs):
			# This method will add a source in the session and do a getCap
			try:
				# Do nothing if there is already a source named after this url
				self.sources[args[0]]
			except KeyError:
				self.sources[args[0]] = self.getcapabilities(*args,**kargs)
				return self.sources[args[0]]




		def reset(self,*args,**kargs):
			# This method erase old information about layers and reload it with
			# a new GetCapabilities
			if args == ():
				# If no url where given, reset all
					self.sources = {}
			else:
				# If a url where given, update/add only this url.
				try:
					self.sources = {}
					self.sources[args[0]] = self.getcapabilities(*args,**kargs)
				except:
					pass
	return Session
