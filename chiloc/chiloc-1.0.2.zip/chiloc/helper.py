import pandas as pd
import numpy as np
import json
from urllib.request import urlopen, quote
import os 

def city_code_init():
	"""
	This function initiate the very first csv file of city code,
	which will be applied to other function to seek the local routes of subway.
	
	INPUT:
		NONE
	OUTPUT:
		City_codes.csv: A .csv file that gathers cities and codes world-widely.
	"""
	if os.path.isfile('City_codes.csv') == False:
	
		req = urlopen('http://map.baidu.com/?qt=subwayscity&t=123457788')
		res = req.read().decode()
		temp = json.loads(res)
		
		city_code_list = pd.DataFrame()
		city_code_list['City'], city_code_list['Code'] =  np.nan, np.nan
		cities = temp['subways_city']['cities']

		city, code = [], []

		for i in range(len(cities)):
			city.append(cities[i]['cn_name'])
			code.append(cities[i]['code'])
			
		city_code_list['City'], city_code_list['Code'] = city, code
		city_code_list.to_csv('City_codes.csv', index = False)
