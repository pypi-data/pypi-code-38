"""
This file is the base of the wms object
"""
# python included package
import xml.etree.ElementTree as ET

# Third party package
import requests

# Usefull class and functions

class struct(object):
	# This class will be used to contain variable
	pass

def inheritWMS130(layerList):
	# This function will do the inheritance on the layer attributes
	for layer in layerList:
		# Add inheritance on child

		# Add parent style to child
		ls = layer.style
		for lay in layer.layer:
			# For every child in layer, append parent style to the children one
			lay.style += ls

		# Add parent CRS to child
		crs = layer.crs
		for lay in layer.layer:
			# For every child layer, append parent crs list to the children one
			lay.crs += crs

		# try default to parent ex_GeographicBoundingBox
		for lay in layer.layer:
			# check if ex_GeographicBoundingBox exists in child
			try:
				# If it exists, use the child definition
				lay.exGeographicBoundingBox
			except AttributeError:
				# If it doesn't exist, try using the parent definition
				try:
					lay.exGeographicBoundingBox = layer.exGeographicBoundingBox
				except AttributeError:
					# If the parent has no definition, do nothing
					pass

		# try default to parent boundingBox
		for bbox in layer.boundingBox:
			# Go threw every bbox of the parent layer
			for lay in layer.layer:
				# To every child, do the folowing:
				try:
					# If a child has a bbox with the same crs, don't add the parent bbox to its available bbox.
					crs = bbox.crs
					if crs not in [subbou.crs for subbou in lay.boundingBox ]:
						# Add the parent boundingBox to the child
						lay.boundingBox.append(bbox)
				except AttributeError:
					pass

		# Replace Dimension
		for dim in layer.dimension:
			# Go threw every dimension of the parent layer
			for lay in layer.layer:
				# To every child, do the folowing:
				try:
					# If a child has a dimension with the same name, don't add the parent dimension to its available bbox
					name = dim.name
					if name not in [subdim.name for subdim in lay.dimension]:
						# Add the parent dimension to the child
						lay.dimension.append(dim)
				except AttributeError:
					pass

		# Replace Attribution
		for lay in layer.layer:
			# check if Attribution exists in child
			try:
				# If it exists, use the child definition
				lay.attribution
			except AttributeError:
				# If it doesn't exist, try using the parent definition
				try:
					lay.attribution = layer.attribution
				except AttributeError:
					# If the parent has no definition, do nothing
					pass

		# Add AuthorityURL
		aut = layer.authorityURL
		for lay in layer.layer:
			# For every child layer, append parent authorityURL list to the children one
			lay.authorityURL += aut

		# Replace minScaleDenominator
		for lay in layer.layer:
			# for every child, check if there is a minScaleDenominator attribute
			try:
				lay.minScaleDenominator
			except AttributeError:
				# If not defined, try to default to minScaleDenominator of parent
				try:
					lay.minScaleDenominator = layer.minScaleDenominator
				except AttributeError:
					pass

		# Replace maxScaleDenominator
		for lay in layer.layer:
			# for every child, check if there is a minScaleDenominator attribute
			try:
				lay.maxScaleDenominator
			except AttributeError:
				# If not defined, try to default to minScaleDenominator of parent
				try:
					lay.maxScaleDenominator = layer.maxScaleDenominator
				except AttributeError:
					pass


		# Replace layer attributes
		# Replace queryable
		for lay in layer.layer:
			# for every child, check if there is a queryable attribute
			try:
				lay.queryable
			except AttributeError:
				# If not defined, try to default to queryable of parent
				try:
					lay.queryable = layer.queryable
				except AttributeError:
					pass

		# Replace cascaded
		for lay in layer.layer:
			# for every child, check if there is a cascaded attribute
			try:
				lay.cascaded
			except AttributeError:
				# If not defined, try to default to queryable of parent
				try:
					lay.cascaded = layer.cascaded
				except AttributeError:
					pass

		# Replace opaque
		for lay in layer.layer:
			# for every child, check if there is a opaque attribute
			try:
				lay.opaque
			except AttributeError:
				# If not defined, try to default to opaque of parent
				try:
					lay.opaque = layer.opaque
				except AttributeError:
					pass

		# Replace noSubsets
		for lay in layer.layer:
			# for every child, check if there is a noSubsets attribute
			try:
				lay.noSubsets
			except AttributeError:
				# If not defined, try to default to noSubsets of parent
				try:
					lay.noSubsets = layer.noSubsets
				except AttributeError:
					pass

		# Replace fixedWidth
		for lay in layer.layer:
			# for every child, check if there is a fixedWidth attribute
			try:
				lay.fixedWidth
			except AttributeError:
				# If not defined, try to default to fixedWidth of parent
				try:
					lay.fixedWidth = layer.fixedWidth
				except AttributeError:
					pass

		# Replace fixedHeight
		for lay in layer.layer:
			# for every child, check if there is a fixedHeight attribute
			try:
				lay.fixedHeight
			except AttributeError:
				# If not defined, try to default to fixedHeight of parent
				try:
					lay.fixedHeight = layer.fixedHeight
				except AttributeError:
					pass

		# Try apply function on children
		try:
			inheritWMS130(layer.layer)
		except AttributeError:
			pass

def defaultWMS130(layerList):
	for layer in layerList:
		# Apply default
		# Queryable
		if layer.queryable is None:
			layer.queryable = False
		# Cascaded
		if layer.cascaded is None:
			layer.cascaded = 0
		# Opaque
		if layer.opaque is None:
			layer.opaque = False
		# NoSubsets
		if layer.noSubsets is None:
			layer.noSubsets = False
		# FixedWidth
		if layer.fixedWidth is None:
			layer.fixedWidth = 0
		# FixedHeight
		if layer.fixedHeight is None:
			layer.fixedHeight = 0

		# Apply to child
		try:
			defaultWMS130(layer.layer)
		except AttributeError:
			pass

def addlayers(layerDictList):
	# This fuction returns a list of layers and sublayers and fill the
	# information in a struct class
	layer = []
	for layerDict in layerDictList:
		layer.append(struct())
		# Add queryable attribute
		try:
			layer[-1].queryable = int(layerDict[1]["queryable"]) == 1
		except KeyError:
			layer[-1].queryable = None

		# Add cascaded attribute
		try:
			layer[-1].cascaded = int(layerDict[1]["cascaded"])
		except KeyError:
			layer[-1].cascaded = None

		# Add opaque attribute
		try:
			layer[-1].opaque = int(layerDict[1]["opaque"])
		except KeyError:
			layer[-1].opaque = None

		# Add noSubsets
		try:
			layer[-1].noSubsets = int(layerDict[1]["noSubsets"]) > 0
		except KeyError:
			layer[-1].noSubsets = None

		# Add fixedWidth
		try:
			layer[-1].fixedWidth = int(layerDict[1]["fixedWidth"])
		except KeyError:
			layer[-1].fixedWidth = None

		# Add fixedHeight
		try:
			layer[-1].fixedHeight = int(layerDict[1]["fixedHeight"])
		except KeyError:
			layer[-1].fixedHeight = None



		# Get title (There can only be one)
		layer[-1].title = layerDict[0]["Title"][0][2]

		# Add name Optional
		try:
			# Get name (There can only be one)
			layer[-1].name = layerDict[0]["Name"][0][2]
		except KeyError:
			# If there is no name, do nothing
			pass
		# O CRS
		try:
			layer[-1].crs = []
			for tup in layerDict[0]["CRS"]:
				layer[-1].crs.append(tup[2])
		except KeyError:
			# If there is no crs, do nothing
			pass

		# O Abstract (0/1)
		try:
			layer[-1].abstract = layerDict[0]["Abstract"][0][2]
		except KeyError:
			# If there is no abstract, do nothing
			pass

		# O KeywordList (0/1)
		try:
			layer[-1].keywordList = [tup[2] for tup in layerDict[0]["KeywordList"][0][0]["Keyword"]]
		except KeyError:
			# If there is no keywords, do nothing
			pass

		# Style
		try:
			layer[-1].style = []
			for sty in layerDict[0]["Style"]:
				layer[-1].style.append(struct())

				# Add name
				try:
					layer[-1].style[-1].name = sty[0]["Name"][0][2]
				except KeyError:
					pass

				# Add title
				try:
					layer[-1].style[-1].title = sty[0]["Title"][0][2]
				except KeyError:
					pass

				# Add abstract
				try:
					layer[-1].style[-1].abstract = sty[0]["Abstract"][0][2]
				except KeyError:
					pass

				# Add legendURL
				try:
					leg = sty[0]["LegendURL"][0]
					layer[-1].style[-1].legendURL = struct()

					# Add width
					try:
						layer[-1].style[-1].legendURL.width = int(leg[1]["width"])
					except KeyError:
						pass

					# Add height
					try:
						layer[-1].style[-1].legendURL.height = int(leg[1]["height"])
					except KeyError:
						pass

					# Add format
					try:
						layer[-1].style[-1].legendURL.format = leg[0]["Format"][0][2]
					except KeyError:
						pass

					# Add onlineResource
					try:
						layer[-1].style[-1].legendURL.onlineResource = leg[0]["OnlineResource"][0][1]["href"]
					except KeyError:
						pass

				except KeyError:
					pass

				# Add styleSheetURL

				try:
					she = sty[0]["StyleSheetURL"][0]
					layer[-1].style[-1].styleSheetURL = struct()

					# Add format
					try:
						layer[-1].style[-1].styleSheetURL.format = she[0]["Format"][0][2]
					except KeyError:
						pass

					# Add onlineResource
					try:
						layer[-1].style[-1].styleSheetURL.onlineResource = she[0]["OnlineResource"][0][1]["href"]
					except KeyError:
						pass

				except KeyError:
					pass

		except KeyError:
			pass

		# exGeographicBoundingBox
		try:
			exgeo = layerDict[0]["EX_GeographicBoundingBox"][0][0]
			# Create struct if exgeo exists
			layer[-1].exGeographicBoundingBox = struct()

			layer[-1].exGeographicBoundingBox.westBoundLongitude = float(  exgeo["westBoundLongitude"][0][2] )
			layer[-1].exGeographicBoundingBox.eastBoundLongitude = float( exgeo["eastBoundLongitude"][0][2] )
			layer[-1].exGeographicBoundingBox.southBoundLatitude = float( exgeo["southBoundLatitude"][0][2] )
			layer[-1].exGeographicBoundingBox.northBoundLatitude = float( exgeo["northBoundLatitude"][0][2] )
		except:
			pass

		# Add boundingBox
		# Create the list of struct
		layer[-1].boundingBox = []
		try:
			for bbox in layerDict[0]["BoundingBox"]:
				# Create the structure
				layer[-1].boundingBox.append(struct())

				# Add crs from attributes to struct
				layer[-1].boundingBox[-1].crs = bbox[1]["CRS"]

				# Add minx, maxx, miny, maxy from attributes to struct
				layer[-1].boundingBox[-1].minx = float( bbox[1]["minx"] )
				layer[-1].boundingBox[-1].miny = float( bbox[1]["miny"] )
				layer[-1].boundingBox[-1].maxx = float( bbox[1]["maxx"] )
				layer[-1].boundingBox[-1].maxy = float( bbox[1]["maxy"] )

				# Try to add resx and resy
				try:
					layer[-1].boundingBox[-1].resx = float( bbox[1]["resx"] )
					layer[-1].boundingBox[-1].resy = float( bbox[1]["resy"] )
				except:
					# If you can't, don't create these variable
					pass
		except KeyError:
			pass

		# Add attribution if exist
		try:
			att = layerDict[0]["Attribution"][0][0]
			layer[-1].attribution = struct()

			# Add title
			try:
				layer[-1].attribution.title = att["Title"][0][2]
			except KeyError:
				pass

			# Add online onlineResource
			try:
				layer[-1].attribution.onlineResource = att["OnlineResource"][0][1]["href"]
			except KeyError:
				pass

			# Add LogoURL
			try:
				logo = att["LogoURL"][0]
				layer[-1].attribution.logoURL = struct()

				# Add width
				try:
					layer[-1].attribution.logoURL.width = int(logo[1]["width"])
				except KeyError:
					pass

				# Add Height
				try:
					layer[-1].attribution.logoURL.height = int(logo[1]["height"])
				except KeyError:
					pass

				# Add format
				try:
					layer[-1].attribution.logoURL.format = logo[0]["Format"][0][2]
				except KeyError:
					pass

				# Add onlineResource for logo
				try:
					layer[-1].attribution.logoURL.onlineResource = logo[0]["OnlineResource"][0][1]["href"]
				except KeyError:
					pass

			except KeyError:
				pass
		except KeyError:
			pass

		# Add authorityURL
		try:
			layer[-1].authorityURL = []
			for aut in layerDict[0]["AuthorityURL"]:
				# Add struct to authorityURL list
				layer[-1].authorityURL.append(struct())

				# Add name
				try:
					layer[-1].authorityURL[-1].name = aut[1]["name"]
				except KeyError:
					pass

				# Add onlineResource of authorityURL
				try:
					layer[-1].authorityURL[-1].onlineResource = aut[0]["OnlineResource"][0][1]["href"]
				except KeyError:
					pass


		except KeyError:
			pass

		# Add identifier
		try:
			layer[-1].identifier = []
			for ide in layerDict[0]["Identifier"]:
				# Add struct to identifier list
				layer[-1].identifier.append(struct())

				# Add id
				layer[-1].identifier[-1].id = ide[2]

				# Add authority
				try:
					layer[-1].identifier[-1].authority = ide[1]["authority"]
				except KeyError:
					pass
		except KeyError:
			pass

		# Add metadataURL
		try:
			layer[-1].metadataURL = []
			for meta in layerDict[0]["MetadataURL"]:
				# Add strcut to metadataURL list
				layer[-1].metadataURL.append(struct())

				# Add type
				try:
					layer[-1].metadataURL[-1].type = meta[1]["type"]
				except KeyError:
					pass

				# Add format
				try:
					layer[-1].metadataURL[-1].format = meta[0]["Format"][0][2]
				except KeyError:
					pass

				# Add onlineResource of metadata
				try:
					layer[-1].metadataURL[-1].onlineResource = meta[0]["OnlineResource"][0][1]["href"]
				except KeyError:
					pass
		except KeyError:
			pass

		# Add dataURL
		try:
			dat = layerDict[0]["DataURL"][0]
			layer[-1].dataURL = struct()

			# Add format
			try:
				layer[-1].dataURL.format = dat[0]["Format"][0][2]
			except KeyError:
				pass

			# Add onlineResource
			try:
				layer[-1].dataURL.onlineResource = dat[0]["OnlineResource"][0][1]["href"]
			except KeyError:
				pass

		except KeyError:
			pass

		# Add featureListURL
		try:
			fea = layerDict[0]["FeatureListURL"][0]
			layer[-1].featureListURL = struct()

			# Add format
			try:
				layer[-1].featureListURL.format = fea[0]["Formaat"][0][2]
			except KeyError:
				pass

			# Add onlineResource
			try:
				layer[-1].featureListURL.onlineResource = fea[0]["OnlineResource"][0][1]["href"]
			except KeyError:
				pass

		except KeyError:
			pass

		# Add minScaleDenominator
		try:
			layer[-1].minScaleDenominator = float( layerDict[0]["MinScaleDenominator"][0][2] )
		except KeyError:
			pass

		# Add maxScaleDenominator
		try:
			layer[-1].maxScaleDenominator = float( layerDict[0]["MaxScaleDenominator"][0][2] )
		except KeyError:
			pass

		# Dimension
		try:
			layer[-1].dimension = []
			for dim in layerDict[0]["Dimension"]:
				layer[-1].dimension.append(struct())

				# Add name
				try:
					layer[-1].dimension[-1].name = dim[1]["name"]
				except KeyError:
					pass

				# Add units
				try:
					layer[-1].dimension[-1].units = dim[1]["units"]
				except KeyError:
					pass

				# Add unitSymbol
				try:
					layer[-1].dimension[-1].unitSymbol = dim[1]["unitSymbol"]
				except KeyError:
					pass

				# Add default
				try:
					layer[-1].dimension[-1].default = dim[1]["default"]
				except KeyError:
					pass

				# Add multipleValues
				try:
					layer[-1].dimension[-1].multipleValues = dim[1]["multipleValues"]
				except KeyError:
					pass

				# Add nearestValue
				try:
					layer[-1].dimension[-1].nearestValue = dim[1]["nearestValue"]
				except KeyError:
					pass

				# Add current
				try:
					layer[-1].dimension[-1].current = dim[1]["current"]
				except KeyError:
					pass

				# Add extent
				try:
					layer[-1].dimension[-1].extent = dim[2]
				except KeyError:
					pass

		except KeyError:
			pass

		# Add sub layers, if any, to the layers
		try:
			layer[-1].layer = addlayers(layerDict[0]["Layer"])
		except KeyError as e:
			# If there is no layer, do nothing
			pass


	return layer

def explore(root):
	# This function will explore the xml and return a dictionary
	theXML = {}
	# Go threw the tags at root level
	for tag in list(root):
		# Get name tag and remove the namespace
		name = tag.tag.split("}")[-1]

		# Check if that name is registered in the dictionary
		try:
			theXML[name]
		except KeyError:
			# If it is not registered, do it
			theXML[name] = []

		# Retrive the values to create tuple associated with the tag

		# Get childs
		if len(list(tag)) > 0:
			# If the element has child add keep them in a dict
			child = explore(tag)
		else:
			# Create an empty dict
			child = {}

		# Get Attributes and remove namespace if needed
		attributes = {}
		for katt, vatt in tag.attrib.items():
			attributes[katt.split("}")[-1]] = vatt


		# Get text of tag
		text = tag.text

		# Create a tuple and add it to the list of this tag name
		theXML[name].append( (child,attributes,text) )

	# Return the dict containing the xml struc from this point
	return theXML

class WMS:
	# This class implement the method necessary to do request to a wms server
	defaultVersion = "1.3.0"
	session = None
	autoDecode = None

	def __int__(self):
		self.version = defaultVersion
		self.autoDecode = autoDecode

	def getcapabilities(self,url,request="GetCapabilities",
						service="WMS",
						version=False,**kargs):
		# This method does a simple gercap request to a wms server

		# Check if a version karg as been passed to the method
		if version is False:
			# Place default value for version
			version = self.version

		# Add all parameters to a dict called params
		params = {"request":request,"service":service,"version":version}
		params.update(kargs)

		# Do a get request to the url, send it the params in the url and
		# download content right away (stream), do not wait for r.text
		r = requests.get(url, params=params, stream=False)


		# Send the response in a new getCapabilitiesObject
		gco = getCapabilitiesObject(r, self.autoDecode)

		# Return the getCapabilitiesObject to the user
		return gco

class getCapabilitiesObject:
	def __init__(self, response, autoDecode):
		self.response = response
		
		# Get text from the response
		if autoDecode is None:
			#Auto Decode
			text = self.response.text
		else:
			text = self.response.content.decode(autoDecode,"replace")

		# Verify that the response is of type xml before trying to parse it
		type = self.response.headers['content-type'] # Get type of document
		# test type
		if type == 'application/xml':
			# Parse the xml
			self.root = ET.fromstring(text)

			# Since etree is a piece of garbage maintened poorly [1], I'll use
			# a filling strategy so I'm expecting a few fields but instead of
			# looking for them they'll look for me.

			# This dict will contain every variable and list every child
			self.getCapDict=explore(self.root)

			# If the standard describe that a field can only be there once, The next part will just use the first one and ignore the rest

			# Create the GetCapabilities structure
			self.getCapStruct = struct()

			# Create the service variable
			self.getCapStruct.service = struct()
			# Create the capability variable
			self.getCapStruct.capability = struct()

			# Filling of the service metadata
			# Get name (There can only be one)
			self.getCapStruct.service.name = self.getCapDict["Service"][0][0]["Name"][0][2]
			# Get title (There can only be one)
			self.getCapStruct.service.title = self.getCapDict["Service"][0][0]["Title"][0][2]
			# O Get abstract (There can only be one)
			try:
				self.getCapStruct.service.abstract = self.getCapDict["Service"][0][0]["Abstract"][0][2]
			except KeyError:
				# If there is no abstract, do nothing
				pass

			# OnlineResource
			self.getCapStruct.service.onlineResource = self.getCapDict["Service"][0][0]["OnlineResource"][0][1]["href"]

			# O keywordList
			try:
				self.getCapStruct.service.keywordList = []
				for keyword in self.getCapDict["Service"][0][0]["KeywordList"][0][0]["Keyword"]:
					self.getCapStruct.service.keywordList.append(keyword[2])
			except KeyError:
				# If there is no keywords, do nothing.
				pass

			# O Contact information
			try:
				# Check if there is a ContactInformation tag
				ci = self.getCapDict["Service"][0][0]["ContactInformation"][0][0]
				# Create a struct
				self.getCapStruct.service.contactInformation = struct()
				# Add contactPersonPrimary
				try:
					cip = ci["ContactPersonPrimary"][0][0]
					self.getCapStruct.service.contactInformation.contactPersonPrimary = struct()
					# Add contactPerson
					try:
						self.getCapStruct.service.contactInformation.contactPersonPrimary.contactPerson = cip["ContactPerson"][0][2]
					except KeyError:
						# If there is no contactperson, do nothing.
						pass
					# Add contactOrganisation
					try:
						self.getCapStruct.service.contactInformation.contactPersonPrimary.contactOrganization = cip["ContactOrganization"][0][2]
					except KeyError:
						# If there is no contactperson, do nothing.
						pass

				except KeyError:
					# If there is no contactPersonPrimary, do nothing.
					pass

				# Add contactPosition
				try:
					self.getCapStruct.service.contactInformation.contactPosition = ci["ContactPosition"][0][2]
				except KeyError:
					# If there is no ContactPosition, do nothing.
					pass

				# Add ContactAddress
				try:
					cia = ci["ContactAddress"][0][0]
					self.getCapStruct.service.contactInformation.contactAddress = struct()

					# Add addressType
					try:
						self.getCapStruct.service.contactInformation.contactAddress.addressType = cia["AddressType"][0][2]
					except KeyError:
						# If there is no AddressType, do nothing.
						pass

					# Add address
					try:
						self.getCapStruct.service.contactInformation.contactAddress.address = cia["Address"][0][2]
					except KeyError:
						# If there is no Address, do nothing.
						pass

					# Add city
					try:
						self.getCapStruct.service.contactInformation.contactAddress.city = cia["City"][0][2]
					except KeyError:
						# If there is no city, do nothing.
						pass

					# Add stateOrProvince
					try:
						self.getCapStruct.service.contactInformation.contactAddress.stateOrProvince = cia["StateOrProvince"][0][2]
					except KeyError:
						# If there is no city, do nothing.
						pass

					# Add postCode
					try:
						self.getCapStruct.service.contactInformation.contactAddress.postCode = cia["PostCode"][0][2]
					except KeyError:
						# If there is no city, do nothing.
						pass

					# Add country
					try:
						self.getCapStruct.service.contactInformation.contactAddress.country = cia["Country"][0][2]
					except KeyError:
						# If there is no country, do nothing
						pass

				except KeyError:
					# If there is no ContactAddress, do nothing.
					pass

				# Add contactVoiceTelephone
				try:
					self.getCapStruct.service.contactInformation.contactVoiceTelephone = ci["ContactVoiceTelephone"][0][2]
				except:
					# If there is no contactVoiceTelephone, do nothing.
					pass

				# Add contactElectronicMailAddress
				try:
					self.getCapStruct.service.contactInformation.contactElectronicMailAddress = ci["ContactElectronicMailAddress"][0][2]
				except:
					# If there is no contactElectronicMailAddress, do nothing.
					pass

			except KeyError:
				# if there is no contact information, do nothing.
				pass

			# O LayerLimit
			try:
				self.getCapStruct.service.layerLimit = int(self.getCapDict["Service"][0][0]["LayerLimit"][0][2])
			except KeyError:
				# If there is no LayerLimit, do nothing.
				pass

			# O MaxWidth
			try:
				self.getCapStruct.service.maxWidth = int(self.getCapDict["Service"][0][0]["MaxWidth"][0][2])
			except KeyError:
				# If there is no MaxWidth, do nothing.
				pass

			# O MaxHeight
			try:
				self.getCapStruct.service.maxHeight = int(self.getCapDict["Service"][0][0]["MaxHeight"][0][2])
			except KeyError:
				# If there is no MaxHeight, do nothing.
				pass

			# O Fees
			try:
				self.getCapStruct.service.fees = self.getCapDict["Service"][0][0]["Fees"][0][2]
			except KeyError:
				# If there is no Fees, do nothing.
				pass

			# O accessConstraints
			try:
				self.getCapStruct.service.accessConstraints = self.getCapDict["Service"][0][0]["AccessConstraints"][0][2]
			except KeyError:
				# If there is no AccessConstraints, do nothing.
				pass

			# Filling of the capability metadata
			# Lack of documentation in ogc for request
			# Fill Exception
			try:
				# Go threw every exception
				self.getCapStruct.capability.exception = []
				for ex in self.getCapDict["Capability"][0][0]["Exception"][0][0]["Format"]:
					self.getCapStruct.capability.exception.append(ex[2])
			except KeyError:
				pass
			# O Fill layers arg with a list of layers
			try:
				self.getCapStruct.capability.layer = addlayers( self.getCapDict["Capability"][0][0]["Layer"])
			except KeyError:
				# If there is no layer, do nothing
				pass


			# Add inheritance
			inheritWMS130(self.getCapStruct.capability.layer)
			# Add default
			defaultWMS130(self.getCapStruct.capability.layer)




		else:
			# End there since this unknow object should not be processed
			return

	def getLayers(self):
		# Return a list of all the name of the named layers
		layer = []
		def addlayers(layerStructList, layerList):
			for lay in layerStructList:
				# Add named layer to the list
				try:
					lay.name
					layerList.append(lay.name)
				except AttributeError:
					pass
				# Add named layer of the child
				try:
					addlayers(lay.layer, layerList)
				except AttributeError:
					pass
		addlayers(self.getCapStruct.capability.layer, layer)
		return layer
# REFS:
# [1] : https://bugs.python.org/issue18304
