import pandas as pd
import numpy as np
import json
from urllib.request import urlopen, quote
import os 


class Chiloc():
	"""
	China locator class aims to give more details about a given location.
	In the very basic function, it would offer the longitude and latitude 
	
	Attributes:
		name(string): representing the name of the location.
		lng(float): representing the longitude of the location.
		lat(float): representing the latitude of the location.
	"""

	def __init__(self, place_name = '北京大学国家发展研究院', city = '北京'):
		"""
		The instantiate function. 
		
		Args: 
			place_name(string): the name of the location, default is  '北京大学国家发展研究院'
		
		Return:
			None
		"""

		self.name = place_name
		self.city = city
		self.lng = self.getlnglat(self.name)[0]
		self.lat = self.getlnglat(self.name)[1]
		
	def getlnglat(self, place_name):
		"""
		
		"""
		
		url = 'http://api.map.baidu.com/place/v2/search?query='
		output = 'json'
		ak = 'H3bQs5XVuBaLnoQ3CvIzZUiEYrr5Bym4'
		# re-code mandrian
		add = quote(place_name) 
		region = quote(self.city)
		url = url + add + '&region=' + region + '&output=' + output + '&ak=' + ak
		req = urlopen(url)
		# decode as unicode 
		res = req.read().decode()
		temp = json.loads(res)
		
		lng = temp['results'][0]['location']['lng']
		lat = temp['results'][0]['location']['lat']
		
		return lng, lat
	
	
	def __repr__(self):
	
		return 'Place: {}, lng: {}, lat: {}'.format(self.name, self.lng, self.lat)
	
	