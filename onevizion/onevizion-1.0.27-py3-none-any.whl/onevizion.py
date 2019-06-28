import requests
import urllib
import json
import smtplib
import os
import sys
import datetime
import base64
from collections import OrderedDict

Config = {
	"Verbosity":0,
	"ParameterFile":None,
	"ParameterData":{},
	"SMTPToken":None,
	"Trace":OrderedDict(),
	"Error":False
	}

#Let's add some compatibility between Python 2 and 3
try:
	unicode = unicode
except NameError:
	# 'unicode' is undefined, must be Python 3
	str = str
	unicode = str
	bytes = bytes
	basestring = (str,bytes)
	Config["PythonVer"] = "3"
else:
	# 'unicode' exists, must be Python 2
	str = str
	unicode = unicode
	bytes = str
	basestring = basestring
	Config["PythonVer"] = "2"


Config["Platform"] = sys.platform
if Config["Platform"] != 'win32':
	import fcntl


def Message(Msg,Level=0):
	"""Prints a message depending on the verbosity level set on the command line"""
	if Level <= Config["Verbosity"]:
		print (Msg)

def TraceMessage(Msg,Level=0,TraceTag=None):
	if TraceTag is None:
		Tag = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
	else:
		Tag = TraceTag
	Message(Msg,Level)
	Config["Trace"][Tag]=Msg

class Singleton(object):
	""" Make sure this process is only running once.  It does a quiet quit() if it's already running.
		* May use any Lockfile name you like, default is ScriptName.lck.
		* May choose what happens if a process collision happens
			"silent" - exit with normal quit
			"error" - exit with error signal
			"none" - do nothing but set property to check, for custom things
		* May set custom Quit Message.

		This was mostly taken from the tendo library, releassed under the Python License allowing derivations
		https://github.com/pycontribs/tendo/blob/master/tendo/singleton.py
		My reason for creating this offshoot was because the tendo version forces any error code -1 exit,
		which does not work for my purposes.
	"""
	def __init__(self,LockFileName=None,QuitMode="silent",Msg="Previous process Still Running.  Quitting."):
		""" LockFileName - can be specified, or if left blank, it will default to ScriptName.lck
			QuitMode - determines how to respond to finding an already running process. Possible Options are:
				"silent" - exit silently with no error code.
				"error" - exit with error code -1
				"none" - set property and continue running
			Msg - Allows for a custom Message to be sent to console
		"""
		def Quit():
			"""Handle Quitting (or not) as specified
			"""
			if Msg is not None and Msg != "":
				Message(Msg)
			self.foundProcess = True
			if QuitMode.lower() == "silent":
				quit()
			elif QuitMode.lower() == "error":
				sys.exit(-1)

		self.initialized = False
		self.foundProcess = False
		self.platform = Config["Platform"]
		if self.platform != 'win32':
			import fcntl
		# Choose Filename for Lock File
		if LockFileName is None:
			import __main__
			self.LockFileName = __main__.__file__[:-3]+".lck"
		else:
			self.LockFileName = LockFileName
		# Make Sure this script is not still running from last time before we run
		if self.platform == 'win32':
			try:
				# file already exists, we try to remove (in case previous
				# execution was interrupted)
				if os.path.exists(self.LockFileName):
					os.unlink(self.LockFileName)
				self.LockFile = os.open(
					self.LockFileName, os.O_CREAT | os.O_EXCL | os.O_RDWR)
			except OSError:
				type, e, tb = sys.exc_info()
				if e.errno == 13:
					Quit()
		else:  # non Windows
			import fcntl
			self.LockFile = open(self.LockFileName, 'w')
			self.LockFile.flush()
			try:
				fcntl.lockf(self.LockFile, fcntl.LOCK_EX | fcntl.LOCK_NB)
			except IOError:
				Quit()
		self.initialized = True

	def __del__(self):
		# Clean up File on Exit
		if not self.initialized:
			return
		try:
			if self.platform == 'win32':
				if hasattr(self, 'LockFile'):
					os.close(self.LockFileName)
					os.unlink(self.LockFileName)
			else:
				fcntl.lockf(self.LockFile, fcntl.LOCK_UN)
				# os.close(self.fp)
				if os.path.isfile(self.LockFileName):
					os.unlink(self.LockFileName)
		except Exception as e:
			Message("Unknown error: %s" % e)
			sys.exit(-1)


class curl(object):
	"""Wrapper for requests.request() that will handle Error trapping and try to give JSON for calling.
	If URL is passed on Instantiation, it will automatically run, else, it will wait for you to set
	properties, then run it with runQuery() command.  Erors should be trapped and put into "errors" array.
	If JSON is returned, it will be put into "data" as per json.loads

	Attributes:
		method: GET, PUT, POST, PATCH, DELETE methods for HTTP call
		url: URL to send the request
		**kwargs:  any other arguments to send to the request
	"""

	def __init__(self, method='GET', url=None, **kwargs):
		self.method = method
		self.url = url
		self.params = None
		self.data = None
		self.headers = None
		self.cookies = None
		self.files = None
		self.auth = None
		self.timeout = None
		self.allow_redirects = True
		self.proxies = None
		self.hooks = None
		self.stream = None
		self.verify = None
		self.cert = None
		self.json = None
		self.request = None
		self.errors = []
		self.jsonData = {}
		self.args = {}
		self.duration = None
		self.sentUrl = None
		self.sentArgs = None
		for key, value in kwargs.items():
			self.args[key] = value
			setattr(self, key, value)

		if self.url is not None:
			self.runQuery()



	def setArg(self, key, value):
		if value is not None:
			self.args[key] = value

	def runQuery(self):
		self.setArg('params', self.params)
		self.setArg('data', self.data)
		self.setArg('headers', self.headers)
		self.setArg('cookies', self.cookies)
		self.setArg('files', self.files)
		self.setArg('auth', self.auth)
		self.setArg('timeout', self.timeout)
		self.setArg('allow_redirects', self.allow_redirects)
		self.setArg('proxies', self.proxies)
		self.setArg('hooks', self.hooks)
		self.setArg('stream', self.stream)
		self.setArg('verify', self.verify)
		self.setArg('cert', self.cert)
		self.setArg('json', self.json)

		self.errors = []
		self.jsonData = {}
		self.sentUrl = self.url
		self.sentArgs = self.args
		before = datetime.datetime.utcnow()
		try:
			self.request = requests.request(self.method, self.url, **self.args)
		except Exception as e:
			self.errors.append(str(e))
		else:
			if self.request.status_code not in range(200,300):
				self.errors.append(str(self.request.status_code)+" = "+self.request.reason+"\n"+str(self.request.text))
			try:
				self.jsonData = json.loads(self.request.text)
			except Exception as err:
				pass
		after = datetime.datetime.utcnow()
		delta = after - before
		self.duration = delta.total_seconds()





class OVImport(object):
	"""Wrapper for calling OneVizion Imports.  We have the
	following properties:

	Attributes:
		URL: A string representing the website's main URL for instance "trackor.onevizion.com".
		userName: the username used to login to the system
		password: the password used to gain access to the system
		impSpecId: the numeric identifier for the Import this file is to be applied to
		action: "INSERT_UPDATE", "INSERT", or "UPDATE"
		comments: Comments to add tot the Import
		incemental: Optional value to pass to incremental import parameter
		file: the path and file name of the file to be imported

		errors: array of any errors encounterd
		request: the requests object of call to the web api
		data: the json data converted to python array
		processId: the system processId returned from the API call
	"""

	def __init__(self, URL=None, userName=None, password=None, impSpecId=None, file=None, action='INSERT_UPDATE', comments=None, incremental=None, paramToken=None):
		self.URL = URL
		self.userName = userName
		self.password = password
		self.impSpecId = impSpecId
		self.file = file
		self.action = action
		self.comments = comments
		self.incremental = incremental
		self.errors = []
		self.request = {}
		self.jsonData = {}
		self.processId = None

		if paramToken is not None:
			if self.URL is None:
				self.URL = Config["ParameterData"][paramToken]['url']
			if self.userName is None:
				self.userName = Config["ParameterData"][paramToken]['UserName']
			if self.password is None:
				self.password = Config["ParameterData"][paramToken]['Password']

		# If all info is filled out, go ahead and run the query.
		if self.URL != None and self.userName != None and self.password != None and self.impSpecId != None and self.file != None:
			self.makeCall()

	def makeCall(self):

		self.Import = Import(
			URL=self.URL,
			userName=self.userName,
			password=self.password,
			impSpecId=self.impSpecId,
			file=self.file,
			action=self.action,
			comments=self.comments,
			incremental=self.incremental
			)
		self.errors = self.Import.errors
		if len(self.Import.errors) == 0:
			self.request = self.Import.request
			self.jsonData = self.Import.jsonData
			self.processId = self.Import.processId



class Trackor(object):
	"""Wrapper for calling the Onvizion API for Trackors.  You can Delete, Read, Update or Create new
		Trackor instances with the like named methods.

	Attributes:
		trackorType: The name of the TrackorType being changed.
		URL: A string representing the website's main URL for instance "trackor.onevizion.com".
		userName: the username used to login to the system
		password: the password used to gain access to the system

		errors: array of any errors encounterd
		OVCall: the requests object of call to the web api
		jsonData: the json data converted to python array
	"""

	def __init__(self, trackorType = "", URL = "", userName="", password="", paramToken=None):
		self.TrackorType = trackorType
		self.URL = URL
		self.userName = userName
		self.password = password
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl()
		self.request = None

		if paramToken is not None:
			if self.URL == "":
				self.URL = Config["ParameterData"][paramToken]['url']
			if self.userName == "":
				self.userName = Config["ParameterData"][paramToken]['UserName']
			if self.password == "":
				self.password = Config["ParameterData"][paramToken]['Password']



	def delete(self,trackorId):
		""" Delete a Trackor instance.  Must pass a trackorId, the unique DB number.
		"""
		FilterSection = "trackor_id=" + str(trackorId)

		URL = "https://{URL}/api/v3/trackor_types/{TrackorType}/trackors?{FilterSection}".format(URL=self.URL, TrackorType=self.TrackorType, FilterSection=FilterSection)
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('DELETE',URL,auth=(self.userName,self.password))
		Message(URL,2)
		Message("Deletes completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] =  URL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request




	def read(self,
		trackorId=None,
		filterOptions=None,
		filters={},
		search=None,
		viewOptions=None,
		fields=[],
		sort={},
		page=None,
		perPage=1000
		):
		""" Retrieve some field data from a set of Trackor instances. List of Trackors must be
			identified either by trackorId or filterOptions, and data fields to be retieved must be
			identified either by viewOptions or a list of fields.

			fields is an array of strings that are the Configured Field Names.
		"""

		URL = "https://{Website}/api/v3/trackor_types/{TrackorType}/trackors".format(
			Website=self.URL,
			TrackorType=self.TrackorType
			)
		Method='GET'

		FilterSection = ""
		SearchBody = {}
		if trackorId is None:
			if filterOptions is None:
				if search is None:
					#Filtering based on "filters" fields
					for key,value in filters.items():
						FilterSection = FilterSection + key + '=' + URLEncode(str(value)) + '&'
					FilterSection = FilterSection.rstrip('?&')
				else:
					#Filtering based on Search Criteria
					URL += "/search"
					SearchBody = {"data": search}
					Method='POST'
			else:
				#Filtering basd on filterOptions
				FilterSection = "filter="+URLEncode(filterOptions)
		else:
			#Filtering for specific TrackorID
			URL = "https://{Website}/api/v3/trackors/{TrackorID}".format(
				Website=self.URL,
				TrackorID=str(trackorId)
				)

		if len(FilterSection) == 0:
			ViewSection = ""
		else:
			ViewSection = "&"
		if viewOptions is None:
			ViewSection += 'fields=' + ",".join(fields)
		else:
			ViewSection += 'view=' + URLEncode(viewOptions)

		SortSection=""
		for key,value in sort.items():
			SortSection=SortSection+","+key+":"+value
		if len(SortSection)>0:
			SortSection="&sort="+URLEncode(SortSection.lstrip(','))

		PageSection=""
		if page is not None:
			PageSection = "&page="+str(page)+"&per_page="+str(perPage)

		URL += "?"+FilterSection+ViewSection+SortSection+PageSection

		self.errors = []
		self.jsonData = {}
		self.OVCall = curl(Method,URL,auth=(self.userName,self.password),**SearchBody)
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message(json.dumps(SearchBody,indent=2),2)
		Message("{TrackorType} read completed in {Duration} seconds.".format(
			TrackorType=self.TrackorType,
			Duration=self.OVCall.duration
			),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			Config["Trace"][TraceTag+"-PostBody"] = json.dumps(SearchBody,indent=2)
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True


	def update(self, trackorId=None, filters={}, fields={}, parents={}, charset=""):
		""" Update data in a list of fields for a Trackor instance.
			"trackorId" is the direct unique identifier in the databse for the record.  Use this or Filters.
			"filters" is a list of ConfigFieldName:value pairs that finds the unique
				Trackor instance to be updated.  Use "TrackorType.ConfigFieldName" to filter
				with parent fields.
			"fields" is a ConfigFieldName:Value pair for what to update.  The Value can either
				be a string, or a dictionary of key:value pairs for parts fo teh field sto be updated
				such as in and EFile field, one can have {"file_name":"name.txt","data":"Base64Encoded Text"}
			"parents" is a list of TrackorType:Filter pairs.
				"Filter" is a list of ConfigFieldName:value exactly like the about "filters"
		"""

		# First build a JSON package from the fields and parents dictionaries given
		JSONObj = {}

		FieldsSection = {}
		for key, value in fields.items():
			if isinstance(value, dict):
				CompoundField = {}
				for skey,svalue in value.items():
					CompoundField[skey] = JSONEndValue(svalue)
				FieldsSection[key] = CompoundField
			else:
				FieldsSection[key] = JSONEndValue(value)

		ParentsSection = []
		Parentx={}
		for key, value in parents.items():
			Parentx["trackor_type"] = key
			FilterPart = {}
			for fkey,fvalue in value.items():
				FilterPart[fkey]=JSONEndValue(fvalue)
			Parentx["filter"] = FilterPart
			ParentsSection.append(Parentx)

		if len(FieldsSection) > 0:
			JSONObj["fields"] = FieldsSection
		if len(ParentsSection) > 0:
			JSONObj["parents"] = ParentsSection
		JSON = json.dumps(JSONObj)

		# Build up the filter to find the unique Tackor instance
		if trackorId is None:
			Filter = '?'
			for key,value in filters.items():
				Filter = Filter + key + '=' + URLEncode(str(value)) + '&'
			Filter = Filter.rstrip('?&')
			URL = "https://{Website}/api/v3/trackor_types/{TrackorType}/trackors{Filter}".format(
					Website=self.URL,
					TrackorType=self.TrackorType,
					Filter=Filter
					)
		else:
			URL = "https://{Website}/api/v3/trackors/{TrackorID}".format(
					Website=self.URL,
					TrackorID=trackorId
					)
			JSON = json.dumps(FieldsSection)

		Headers = {'content-type': 'application/x-www-form-urlencoded'}
		if charset != "":
			Headers['charset'] = charset
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('PUT',URL, data=JSON, headers=Headers, auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message(json.dumps(JSONObj,indent=2),2)
		Message("{TrackorType} update completed in {Duration} seconds.".format(
			TrackorType=self.TrackorType,
			Duration=self.OVCall.duration
			),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			Config["Trace"][TraceTag+"-PostBody"] = json.dumps(JSONObj,indent=2)
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True


	def create(self,fields={},parents={}, charset=""):
		""" Create a new Trackor instance and set some ConfigField and Parent values for it.
			"filters" is a list of ConfigFieldName:value pairs that finds the unique
				Trackor instance to be updated.  Use "TrackorType.ConfigFieldName" to filter
				with parent fields.
			"fields" is a ConfigFieldName:Value pair for what to update.  The Value can either
				be a string, or a dictionary of key:value pairs for parts fo teh field sto be updated
				such as in and EFile field, one can have {"file_name":"name.txt","data":"Base64Encoded Text"}
			"parents" is a list of TrackorType:Filter pairs.
				"Filter" is a list of ConfigFieldName:value pairs that finds the unique
					Trackor instance to be updated.  Use "TrackorType.ConfigFieldName" to filter
					with parent fields.
		"""

		# First build a JSON package from the fields and parents dictionaries given
		JSONObj = {}

		FieldsSection = {}
		for key, value in fields.items():
			if isinstance(value, dict):
				CompoundField = {}
				for skey,svalue in value.items():
					CompoundField[skey] = JSONEndValue(svalue)
				FieldsSection[key] = CompoundField
			else:
				FieldsSection[key] = JSONEndValue(value)

		ParentsSection = []
		Parentx={}
		for key, value in parents.items():
			Parentx["trackor_type"] = key
			FilterPart = {}
			for fkey,fvalue in value.items():
				FilterPart[fkey]=JSONEndValue(fvalue)
			Parentx["filter"] = FilterPart
			ParentsSection.append(Parentx)

		if len(FieldsSection) > 0:
			JSONObj["fields"] = FieldsSection
		if len(ParentsSection) > 0:
			JSONObj["parents"] = ParentsSection
		JSON = json.dumps(JSONObj)

		URL = "https://{URL}/api/v3/trackor_types/{TrackorType}/trackors".format(URL=self.URL, TrackorType=self.TrackorType)

		Headers = {'content-type': 'application/json'}
		if charset != "":
			Headers['charset'] = charset
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('POST',URL, data=JSON, headers=Headers, auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message(json.dumps(JSONObj,indent=2),2)
		Message("{TrackorType} create completed in {Duration} seconds.".format(
			TrackorType=self.TrackorType,
			Duration=self.OVCall.duration
			),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			Config["Trace"][TraceTag+"-PostBody"] = json.dumps(JSONObj,indent=2)
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True


	def assignWorkplan(self,trackorId, workplanTemplate, name=None, startDate=None, finishDate=None):
		""" Assign a Workplan to a given Trackor Record.

			trackorID: the system ID for the particular Trackor record that this is being assigned to.
			workplanTemplate: the name of the Workplan Template to assign
			name: Name given to the newly created Workplan instance, by default it is the WPTemplate name
			startDate: if given will set the Start Date of the Workplan and calculate baseline dates
			finishDate: if given will place the finish of the Workplan and backwards calculate dates.
		"""

		URL = "https://{website}/api/v3/trackors/{trackor_id}/assign_wp?workplan_template={workplan_template}".format(
				website=self.URL,
				trackor_id=trackorId,
				workplan_template=workplanTemplate
				)

		if name is not None:
			URL += "&"+URLEncode(name)

		if startDate is not None:
			if isinstance(startDate, (datetime.datetime,datetime.date)):
				dt = startDate.strftime('%Y-%m-%d')
			else:
				dt = str(startDate)
			URL += "&"+URLEncode(dt)

		if finishDate is not None:
			if isinstance(finishDate, (datetime.datetime,datetime.date)):
				dt = finishDate.strftime('%Y-%m-%d')
			else:
				dt = str(finishDate)
			URL += "&"+URLEncode(dt)

		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('POST',URL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message("{TrackorType} assign workplan completed in {Duration} seconds.".format(
			TrackorType=self.TrackorType,
			Duration=self.OVCall.duration
			),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True


	def GetFile(self, trackorId, fieldName):
		""" Get a File from a particular Trackor record's particular Configured field

			trackorID: the system ID for the particular Trackor record that this is being assigned to.
			fieldName: should be the Configured Field Name, not the Label.
		"""

		def get_filename_from_cd(cd):
			"""
			Get filename from content-disposition
			"""
			if not cd:
				return None
			import re
			fname = re.findall("filename[\*]*=(?>UTF-8'')*(.+)", cd)
			if len(fname) == 0:
				return None
			return fname[0]


		URL = "https://{Website}/api/v3/trackor/{TrackorID}/file/{ConfigFieldName}".format(
				Website=self.URL,
				TrackorID=trackorId,
				ConfigFieldName=fieldName
				)
		self.errors = []
		self.jsonData = {}

		tmpFileName = str(trackorId)+fieldName+".tmp"
		before = datetime.datetime.utcnow()
		try:
			# NOTE the stream=True parameter
			self.request = requests.get(URL, stream=True, auth=(self.userName,self.password),allow_redirects=True)
			with open(tmpFileName, 'wb') as f:
				for chunk in self.request.iter_content(chunk_size=1024):
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
						#f.flush() commented by recommendation from J.F.Sebastian
		except Exception as e:
			self.errors.append(str(e))
		else:
			if self.request.status_code not in range(200,300):
				self.errors.append(str(self.request.status_code)+" = "+self.request.reason)
		after = datetime.datetime.utcnow()
		delta = after - before
		self.duration = delta.total_seconds()

		Message(URL,2)
		Message("{TrackorType} get file completed in {Duration} seconds.".format(
			TrackorType=self.TrackorType,
			Duration=self.duration
			),1)
		if len(self.errors) > 0:
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.request.text),0,TraceTag+"-Body")
			except Exception as e:
				pass
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True

		# return the name of the fiel that was downloaded.
		newFileName = get_filename_from_cd(self.request.headers.get('content-disposition'))
		if newFileName is not None and len(newFileName) > 0:
			os.rename(tmpFileName,newFileName)
			return newFileName
		else:
			return tmpFileName



	def UploadFile(self, trackorId, fieldName, fileName, newFileName=None):
		""" Get a File from a particular Trackor record's particular Configured field

			trackorID: the system ID for the particular Trackor record that this is being assigned to.
			fieldName: should be the Configured Field Name, not the Label.
			fileName: path and file name to file you want to upload
			newFileName: Optional, rename file when uploading.
		"""

		URL = "https://{Website}/api/v3/trackor/{TrackorID}/file/{ConfigFieldName}".format(
				Website=self.URL,
				TrackorID=trackorId,
				ConfigFieldName=fieldName
				)
		if newFileName is not None:
			URL += "?file_name="+URLEncode(newFileName)
			File = {'file': (os.path.basename(newFileName), open(fileName, 'rb'))}
		else:
			URL += "?file_name="+URLEncode(os.path.basename(fileName))
			File = {'file': (os.path.basename(fileName), open(fileName, 'rb'))}

		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('POST',URL,auth=(self.userName,self.password),files=File)
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message("FileName: {FileName}".format(FileName=fileName),2)
		Message("{TrackorType} upload file completed in {Duration} seconds.".format(
			TrackorType=self.TrackorType,
			Duration=self.OVCall.duration
			),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			Config["Trace"][TraceTag+"-FileName"] = fileName
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True



	#https://trackor.onevizion.com/api/v3/trackor/{TrackorID}/file/{ConfigFieldName}?file_name={NewFileName}



class WorkPlan(object):
	"""Wrapper for calling the OneVizion API for WorkPlans.  You can Read or Update
		WorkPlan instances with the like named methods.

	Attributes:
		URL: A string representing the website's main URL for instance "trackor.onevizion.com".
		userName: the username used to login to the system
		password: the password used to gain access to the system

		errors: array of any errors encounterd
		OVCall: the requests object of call to the web api
		jsonData: the json data converted to python array
	"""

	def __init__(self, URL = "", userName="", password="", paramToken=None):
		self.URL = URL
		self.userName = userName
		self.password = password
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl()
		if paramToken is not None:
			if self.URL == "":
				self.URL = Config["ParameterData"][paramToken]['url']
			if self.userName == "":
				self.userName = Config["ParameterData"][paramToken]['UserName']
			if self.password == "":
				self.password = Config["ParameterData"][paramToken]['Password']

	def read(self, workplanId = None, workplanTemplate = "", trackorType = "", trackorId = None):
		""" Retrieve some data about a particular WorkPlan.WorkPlan must be
			identified either by workplanId or by a WorkPlanTemplate, TrackorType, and TrackorID
		"""
		FilterSection = ""
		if workplanId is None:
			#?wp_template=Augment%20Workplan&trackor_type=SAR&trackor_id=1234
			FilterSection = "?wp_template={WPTemplate}&trackor_type={TrackorType}&trackor_id={TrackorID}".format(
				WPTemplate=URLEncode(workplanTemplate),
				TrackorType=URLEncode(trackorType),
				TrackorID=trackorId
				)
		else:
			#1234
			FilterSection = str(trackorId)

		URL = "https://{URL}/api/v3/wps/{FilterSection}".format(URL=self.URL, FilterSection=FilterSection)
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('GET',URL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message("Workplan read completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True



class Task(object):

	def __init__(self, URL = "", userName="", password="", paramToken=None):
		self.URL = URL
		self.userName = userName
		self.password = password
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl()
		if paramToken is not None:
			if self.URL == "":
				self.URL = Config["ParameterData"][paramToken]['url']
			if self.userName == "":
				self.userName = Config["ParameterData"][paramToken]['UserName']
			if self.password == "":
				self.password = Config["ParameterData"][paramToken]['Password']

	def read(self, taskId = None, workplanId=None, orderNumber=None):
		""" Retrieve some data about a particular WorkPlan Tasks. Tasks must be
			identified either by workplanId, workplanId and orderNumber or by a taskId
		"""
		if taskId is not None:
			URL = "https://{URL}/api/v3/tasks/{TaskID}".format(URL=self.URL, TaskID=taskId)
		elif orderNumber is not None:
			URL = "https://{URL}/api/v3/tasks?workplan_id={WorkPlanID}&order_number={OrderNumber}".format(URL=self.URL, WorkPlanID=workplanId, OrderNumber=orderNumber)
		else:
			URL = "https://{URL}/api/v3/wps/{WorkPlanID}/tasks".format(URL=self.URL, WorkPlanID=workplanId)

		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('GET',URL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message("Task read completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True


	def update(self, taskId, fields={}, dynamicDates=[]):

		if len(dynamicDates)>0:
			fields['dynamic_dates'] = dynamicDates

		JSON = json.dumps(fields)

		URL = "https://{URL}/api/v3/tasks/{TaskID}".format(URL=self.URL, TaskID=taskId)
		#payload = open('temp_payload.json','rb')
		Headers = {'content-type': 'application/x-www-form-urlencoded'}
		self.errors = []
		self.jsonData = {}
		self.OVCall = curl('PUT',URL, data=JSON, headers=Headers, auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(URL,2)
		Message(json.dumps(fields,indent=2),2)
		Message("Task update completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = URL
			Config["Trace"][TraceTag+"-PostBody"] = json.dumps(fields,indent=2)
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True


class Import(object):

	def __init__(
		self,
		URL=None,
		userName=None,
		password=None,
		impSpecId=None,
		file=None,
		action='INSERT_UPDATE',
		comments=None,
		incremental=None,
		paramToken=None
		):
		self.URL = URL
		self.userName = userName
		self.password = password
		self.impSpecId = impSpecId
		self.file = file
		self.action = action
		self.comments = comments
		self.incremental = incremental
		self.errors = []
		self.warnings = []
		self.request = {}
		self.jsonData = {}
		self.processId = None
		self.status = None
		self.processList = []
		if paramToken is not None:
			if self.URL is None:
				self.URL = Config["ParameterData"][paramToken]['url']
			if self.userName is None:
				self.userName = Config["ParameterData"][paramToken]['UserName']
			if self.password is None:
				self.password = Config["ParameterData"][paramToken]['Password']

		# If all info is filled out, go ahead and run the query.
		if self.URL != None and self.userName != None and self.password != None and self.impSpecId != None and self.file != None:
			self.run()

	def run(self):
		self.ImportURL = "https://{URL}/api/v3/imports/{ImpSpecID}/run?action={Action}".format(
			URL=self.URL,
			ImpSpecID=self.impSpecId,
			Action=self.action
			)
		if self.comments is not None:
			self.ImportURL += '&comments=' + URLEncode(self.comments)
		if self.incremental is not None:
			self.ImportURL += '&is_incremental=' + str(self.incremental)
		self.ImportFile = {'file': (os.path.basename(self.file), open(self.file,'rb'))}
		self.OVCall = curl('POST',self.ImportURL,files=self.ImportFile,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(self.ImportURL,2)
		Message("FileName: {FileName}".format(FileName=self.ImportFile),2)
		Message("Import Send completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		TraceTag="{TimeStamp}:{FileName}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'),FileName=self.file)
		self.TraceTag = TraceTag
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			Config["Trace"][TraceTag+"-URL"] = self.ImportURL
			Config["Trace"][TraceTag+"-FileName"] = self.ImportFile
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		else:
			if "error_message" in self.jsonData and len(self.jsonData["error_message"]) > 0:
				self.errors.append(self.jsonData["error_message"])
				Config["Trace"][TraceTag+"-URL"] = self.ImportURL
				Config["Trace"][TraceTag+"-FileName"] = self.ImportFile
				TraceMessage("Eror Message: {Error}".format(Error=self.jsonData["error_message"]),0,TraceTag+"-ErrorMessage")
				Config["Error"]=True
			if "warnings" in self.jsonData and len(self.jsonData["warnings"]) > 0:
				self.warnings.extend(self.jsonData["warnings"])
				Config["Trace"][TraceTag+"-URL"] = self.ImportURL
				Config["Trace"][TraceTag+"-FileName"] = self.ImportFile
				TraceMessage("Eror Message: {Error}".format(Error=self.jsonData["warnings"]),0,TraceTag+"-Warnings")
			if "process_id" in self.jsonData:
				self.processId = self.jsonData["process_id"]
				self.status = self.jsonData["status"]
				Message("Success!  ProcessID: {ProcID}".format(ProcID=self.processId),1)

	def interrupt(self,ProcessID=None):
		if ProcessID is None:
			PID = self.processId
		else:
			PID = ProcessID
		self.ImportURL = "https://{URL}/api/v3/imports/runs/{ProcID}/interrupt".format(
			URL=self.URL,
			ProcID=PID
			)
		self.OVCall = curl('POST',self.ImportURL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(self.ImportURL,2)
		Message("Interupt Process completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = self.ImportURL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		else:
			self.processId = PID
			Message("Successful Interrupt  ProcessID: {ProcID}".format(ProcID=self.processId),1)

		if "status" in self.jsonData:
			self.status = self.jsonData['status']

	def getProcessData(self,
		processId=None,
		status=None,
		comments=None,
		importName=None,
		owner=None,
		isPdf=None
		):
		def addParam(paramName,param):
			if param is not None:
				if not self.ImportURL.endswith("?"):
					self.ImportURL += "&"
				self.ImportURL += paramName + "=" +URLEncode(str(param))

		self.ImportURL = "https://{URL}/api/v3/imports/runs".format(
			URL=self.URL
			)
		if status is not None or comments is not None or importName is not None or owner is not None or isPdf is not None:
			self.ImportURL += "?"
			if status is not None:
				self.ImportURL += "status="
				if type(status) is list:
					self.ImportURL += ",".join(status)
				else:
					self.ImportURL += str(status)
			addParam('comments',comments)
			addParam('import_name',importName)
			addParam('owner',owner)
			addParam('is_pdf',comments)
		else:
			if processId is None:
				self.ImportURL += "/"+str(self.processId)
			else:
				self.ImportURL += "/"+str(processId)

		self.OVCall = curl('GET',self.ImportURL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(self.ImportURL,2)
		Message("Get Process Data completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = self.ImportURL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		if "status" in self.jsonData:
			self.status = self.jsonData['status']
		else:
			self.status = 'No Status'
		Message("Status: {Status}".format(Status=self.status),1)

		return self.jsonData






class Export(object):

	def __init__(
		self,
		URL=None,
		userName=None,
		password=None,
		trackorType=None,
		filters={},
		fields=[],
		exportMode="CSV",
		delivery="File",
		viewOptions=None,
		filterOptions=None,
		fileFields=None,
		comments=None,
		paramToken=None
		):
		self.URL = URL
		self.userName = userName
		self.password = password
		self.trackorType = trackorType
		self.exportMode = exportMode
		self.delivery = delivery
		self.comments = comments
		self.filters = filters
		self.fields = fields
		self.viewOptions = viewOptions
		self.filterOptions = filterOptions
		self.fileFields = fileFields
		self.errors = []
		self.request = {}
		self.jsonData = {}
		self.status = None
		self.processId = None
		self.processList = []
		self.content = None
		if paramToken is not None:
			if self.URL is None:
				self.URL = Config["ParameterData"][paramToken]['url']
			if self.userName is None:
				self.userName = Config["ParameterData"][paramToken]['UserName']
			if self.password is None:
				self.password = Config["ParameterData"][paramToken]['Password']

		# If all info is filled out, go ahead and run the query.
		if self.URL is not None and self.userName is not None and self.password is not None and self.trackorType is not None and (self.viewOptions is not None or len(self.fields)>0 or self.fileFields is not None) and (self.filterOptions is not None or len(self.filters)>0):
			self.run()

	def run(self):
		self.ImportURL = "https://{URL}/api/v3/exports/{TrackorType}/run?export_mode={ExportMode}&delivery={Delivery}".format(
			URL=self.URL,
			TrackorType=self.trackorType,
			ExportMode=self.exportMode,
			Delivery=self.delivery
			)

		ViewSection = ""
		if self.viewOptions is None:
			ViewSection = '&fields=' + ",".join(self.fields)
		else:
			ViewSection = '&view=' + URLEncode(self.viewOptions)
		self.ImportURL += ViewSection

		FilterSection = "&"
		if self.filterOptions is None:
			for key,value in self.filters.items():
				FilterSection += key + '=' + URLEncode(str(value)) + '&'
			FilterSection = FilterSection.rstrip('?&')
		else:
			FilterSection = "&filter="+URLEncode(self.filterOptions)
		self.ImportURL += FilterSection

		if self.comments is not None:
			self.ImportURL += '&comments=' + URLEncode(self.comments)
		self.OVCall = curl('POST',self.ImportURL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(self.ImportURL,2)
		Message("Run Export completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = self.ImportURL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		else:
			if "error_message" in self.jsonData and len(self.jsonData["error_message"]) > 0:
				self.errors.append(self.jsonData["error_message"])
			if "warnings" in self.jsonData and len(self.jsonData["warnings"]) > 0:
				self.warnings.extend(self.jsonData["warnings"])
			if "process_id" in self.jsonData:
				self.processId = self.jsonData["process_id"]
			if "status" in self.jsonData:
				self.status = self.jsonData["status"]
		return self.processId

	def interrupt(self,ProcessID=None):
		if ProcessID is None:
			PID = self.processId
		else:
			PID = ProcessID
		self.ImportURL = "https://{URL}/api/v3/exports/runs/{ProcID}/interrupt".format(
			URL=self.URL,
			ProcID=PID
			)
		self.OVCall = curl('POST',self.ImportURL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(self.ImportURL,2)
		Message("Get Interupt Export completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = self.ImportURL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		else:
			self.processId = PID
		if "status" in self.jsonData:
			self.status = self.jsonData['status']

	def getProcessStatus(self,ProcessID=None):
		if ProcessID is None:
			PID = self.processId
		else:
			PID = ProcessID
		self.ImportURL = "https://{URL}/api/v3/exports/runs/{ProcID}".format(
			URL=self.URL,
			ProcID=PID
			)
		self.OVCall = curl('GET',self.ImportURL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(self.ImportURL,2)
		Message("Get Process Status for Export completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			self.TraceTag = TraceTag
			Config["Trace"][TraceTag+"-URL"] = self.ImportURL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		if "status" in self.jsonData:
			self.status = self.jsonData['status']
		else:
			self.status = 'No Status'
		return self.status

	def getFile(self,ProcessID=None):
		if ProcessID is None:
			PID = self.processId
		else:
			PID = ProcessID
		self.ImportURL = "https://{URL}/api/v3/exports/runs/{ProcID}/file".format(
			URL=self.URL,
			ProcID=PID
			)

		self.OVCall = curl('GET',self.ImportURL,auth=(self.userName,self.password))
		self.jsonData = self.OVCall.jsonData
		self.request = self.OVCall.request

		Message(self.ImportURL,2)
		Message("Get File for Export completed in {Duration} seconds.".format(Duration=self.OVCall.duration),1)
		if len(self.OVCall.errors) > 0:
			self.errors.append(self.OVCall.errors)
			TraceTag="{TimeStamp}:".format(TimeStamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'))
			Config["Trace"][TraceTag+"-URL"] = self.ImportURL
			try:
				TraceMessage("Status Code: {StatusCode}".format(StatusCode=self.OVCall.request.status_code),0,TraceTag+"-StatusCode")
				TraceMessage("Reason: {Reason}".format(Reason=self.OVCall.request.reason),0,TraceTag+"-Reason")
				TraceMessage("Body:\n{Body}".format(Body=self.OVCall.request.text),0,TraceTag+"-Body")
			except Exception as e:
				TraceMessage("Errors:\n{Errors}".format(Errors=json.dumps(self.OVCall.errors,indent=2)),0,TraceTag+"-Errors")
			Config["Error"]=True
		else:
			self.content = self.request.content
		return self.content







class EMail(object):
	"""Made to simplify sending Email notifications in scripts.

	Attributes:
		server: the SSL SMTP server for the mail connection
		port: the port to conenct to- 465 by default
		security: None, SSL, or STARTTLS
		tls: True if TLS is needed, else false.  Provided for Backwards compatibility
		userName: the "From" and login to the SMTP server
		password: the password to conenct to the SMTP server
		to: array of email addresses to send the message to
		subject: subject of the message
		info: dictionary of info to send in the message
		message: main message to send
		files: array of filename/paths to attach
	"""

	def __init__(self,SMTP={}):
		self.server = "mail.onevizion.com"
		self.port = 587
		self.security = "STARTTLS"
		self.tls = "False"
		self.userName = ""
		self.password = ""
		self.to = []
		self.cc = []
		self.subject = ""
		self.info = OrderedDict()
		self.message = ""
		self.body = ""
		self.files = []
		self.duration = 0
		if SMTP == {}:
			if Config["SMTPToken"] is not None:
				SMTP = Config["ParameterData"][Config["SMTPToken"]]
				#self.parameterData(Config["ParameterData"][SMTP])
		if 'UserName' in SMTP and 'Password' in SMTP and 'Server' in SMTP:
			self.parameterData(SMTP)

	def passwordData(self,SMTP={}):
		self.parameterData(SMTP)

	def parameterData(self,SMTP={}):
		"""This allows you to pass the SMTP type object from a PasswordData.  Should be a Dictionary.

		Possible Attributes(Dictionary Keys) are:
			UserName: UserName for SMTP server login (required)
			Password: Password for SMTP login (required)
			Server: SMTP server to connect (required)
			Port: Port for server to connect, default 587
			Security: Security Type, can be STARTTLS, SSL, None.
			To: Who to send the email to.  Can be single email address as string , or list of strings
			CC: CC email, can be single email adress as sting, or a list of strings.
		"""
		if 'UserName' not in SMTP or 'Password' not in SMTP or 'Server' not in SMTP:
			raise ("UserName,Password,and Server are required in the PasswordData json")
		else:
			self.server = SMTP['Server']
			self.userName = SMTP['UserName']
			self.password = SMTP['Password']
		if 'Port' in SMTP:
			self.port = int(SMTP['Port'])
		if 'TLS' in SMTP:
			self.tls = SMTP['TLS']
			self.security = 'STARTTLS'
		if 'Security' in SMTP:
			self.security = SMTP['Security']
		if 'To' in SMTP:
			if type(SMTP['To']) is list:
				self.to.extend(SMTP['To'])
			else:
				self.to.append(SMTP['To'])
		if 'CC' in SMTP:
			if type(SMTP['CC']) is list:
				self.cc.extend(SMTP['CC'])
			else:
				self.cc.append(SMTP['CC'])


	def sendmail(self):
		"""Main work body, sends email with preconfigured attributes
		"""
		import mimetypes

		from optparse import OptionParser

		from email import encoders
		#from email.message import Message
		from email.mime.audio import MIMEAudio
		from email.mime.base import MIMEBase
		from email.mime.image import MIMEImage
		from email.mime.multipart import MIMEMultipart
		from email.mime.text import MIMEText
		msg = MIMEMultipart()
		msg['To'] = ", ".join(self.to )
		msg['From'] = self.userName
		msg['Subject'] = self.subject

		body = self.message + "\n"

		for key,value in self.info.items():
			body = body + "\n\n" + key + ":"
			if isinstance(value, basestring):
				svalue = value.encode('ascii', 'ignore').decode('ascii', 'ignore')
			else:
				svalue = str(value)
			if "\n" in svalue:
				body = body + "\n" + svalue
			else:
				body = body + " " + svalue
		self.body = body

		part = MIMEText(body, 'plain')
		msg.attach(part)

		for file in self.files:
			ctype, encoding = mimetypes.guess_type(file)
			if ctype is None or encoding is not None:
				# No guess could be made, or the file is encoded (compressed), so
				# use a generic bag-of-bits type.
				ctype = 'application/octet-stream'
			maintype, subtype = ctype.split('/', 1)
			if maintype == 'text':
				fp = open(file)
				# Note: we should handle calculating the charset
				attachment = MIMEText(fp.read(), _subtype=subtype)
				fp.close()
			elif maintype == 'image':
				fp = open(file, 'rb')
				attachment = MIMEImage(fp.read(), _subtype=subtype)
				fp.close()
			elif maintype == 'audio':
				fp = open(file, 'rb')
				attachment = MIMEAudio(fp.read(), _subtype=subtype)
				fp.close()
			else:
				fp = open(file, 'rb')
				attachment = MIMEBase(maintype, subtype)
				attachment.set_payload(fp.read())
				fp.close()
				# Encode the payload using Base64
				encoders.encode_base64(attachment)
			# Set the filename parameter
			attachment.add_header('Content-Disposition', 'attachment', filename=file)
			msg.attach(attachment)



		before = datetime.datetime.utcnow()
		Message("Sending Email...",1)
		Message("To: {ToList}".format(ToList=msg['To']),2)
		Message("From: {From}".format(From=msg['From']),2)
		Message("Subject: {Subject}".format(Subject=msg['Subject']),2)
		Message("Body:\n{Body}".format(Body=self.body),2)

		if self.security.upper() in ['STARTTLS','TLS']:
			send = smtplib.SMTP(self.server, int(self.port))
			send.starttls()
		elif self.security.upper() in ['SSL','SSL/TLS']:
			send = smtplib.SMTP_SSL(self.server, self.port)
		else:
			send = smtplib.SMTP(self.server, int(self.port))
		send.login(str(self.userName), str(self.password))
		send.sendmail(str(self.userName),self.to, msg.as_string())
		send.quit()

		after = datetime.datetime.utcnow()
		delta = after - before
		self.duration = delta.total_seconds()
		Message("Sent Mail in {Duration} seconds.".format(Duration=self.duration),1)



ParameterExample = """Parameter File required.  Example:
{
	"SMTP": {
		"UserName": "mgreene@onevizion.com",
		"Password": "IFIAJKAFJBJnfeN",
		"Server": "mail.onevizion.com",
		"Port": "587",
		"Security": "STARTTLS",
		"To":['jsmith@onevizion.com','mjones@onevizion.com'],
		"CC":['bbrown@xyz.com','eric.goete@xyz.com']
	},
	"trackor.onevizion.com": {
		"url": "trackor.onevizion.com",
		"UserName": "mgreene",
		"Password": "YUGALWDGWGYD"
	},
	"sftp.onevizion.com": {
		"UserName": "mgreene",
		"Root": ".",
		"Host": "ftp.onevizion.com",
		"KeyFile": "~/.ssh/ovftp.rsa",
		"Password": "Jkajbebfkajbfka"
	},
}"""

PasswordExample = ParameterExample


def GetPasswords(passwordFile=None):
	return GetParameters(passwordFile)

def GetParameters(parameterFile=None):
	if parameterFile is None:
		parameterFile = Config["ParameterFile"]
	if not os.path.exists(parameterFile):
		print (ParameterExample)
		quit()

	with open(parameterFile,"rb") as ParameterFile:
		ParameterData = json.load(ParameterFile)
	Config["ParameterData"] = ParameterData
	Config["ParameterFile"] = parameterFile

	return ParameterData

def CheckPasswords(PasswordData,TokenName,KeyList, OptionalList=[]):
	return CheckParameters(PasswordData,TokenName,KeyList, OptionalList)

def CheckParameters(ParameterData,TokenName,KeyList, OptionalList=[]):
	Missing = False
	msg = ''
	if TokenName not in ParameterData:
		Missing = True
	else:
		for key in KeyList:
			if key not in ParameterData[TokenName]:
				Missing = True
				break
	if Missing:
		msg = "Parameters.json section required:\n"
		msg = msg + "\t'%s': {" % TokenName
		for key in KeyList:
			msg = msg + "\t\t'%s': 'xxxxxx',\n" % key
		if len(OptionalList) > 0:
			msg = msg + "\t\t'  optional parameters below  ':''"
			for key in OptionalList:
				msg = msg + "\t\t'%s': 'xxxxxx',\n" % key
		msg = msg.rstrip('\r\n')[:-1] + "\n\t}"

	return msg


def URLEncode(strToEncode):
	if strToEncode is None:
		return ""
	else:
		try:
			from urllib.parse import quote_plus
		except Exception as e:
			from urllib import quote_plus

		return quote_plus(strToEncode)



def JSONEncode(strToEncode):
	if strToEncode is None:
		return ""
	else:
		return strToEncode.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\b', '\\b').replace('\t', '\\t').replace('\f', '\\f')


def JSONValue(strToEncode):
	if strToEncode is None:
		return 'null'
	elif isinstance(strToEncode, (int, float, complex)):
		return str(strToEncode)
	else:
		return '"'+JSONEncode(strToEncode)+'"'

def JSONEndValue(objToEncode):
	if objToEncode is None:
		return None
	elif isinstance(objToEncode, (int, float)):
		return objToEncode
	elif isinstance(objToEncode, datetime.datetime):
		return objToEncode.strftime('%Y-%m-%dT%H:%M:%S')
	elif isinstance(objToEncode, datetime.date):
		return objToEncode.strftime('%Y-%m-%d')
	else:
		return str(objToEncode)

def EFileEncode(FilePath,NewFileName=None):
	if NewFileName is None:
		FileName = os.path.basename(FilePath)
	else:
		FileName = NewFileName
	File={"file_name": FileName}
	with open(FilePath,"rb") as f:
		EncodedFile = base64.b64encode(f.read())

	#python3 compatibility
	if isinstance(EncodedFile, bytes):
	   File["data"]=EncodedFile.decode()
	else:
	   File["data"]=EncodedFile

	return File



