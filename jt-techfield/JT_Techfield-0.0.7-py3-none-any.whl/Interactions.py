'''
Jacob Thompson

Feature Interaction
'''
import numpy as np
import pandas as pd

class Interaction():
	def Eval(self, feature):
		return self.Evaluate(feature)

class Inflation_Adjust(Interaction):
	def __init__(self, data_1, data_2):
		self.name = 'Adjust for Inflation'
		self.suffix = '_adjusted'
		cpi_data = pd.read_excel('CPI.xlsx', sheet_name = 'Data').to_numpy()
		self.to_current_dollars = cpi_data[:, [-1]]
		self.years = cpi_data[:, [1]]
		
	def Evaluate(self, value, year):
		return (year == self.years.T) @ self.to_current_dollars * value
		
class Multiply(Interaction):
	def __init__(self, data_1, data_2):
		self.name = 'Multiply'
		self.suffix = '_multiplied'
	
	def Evaluate(self, feature_1, feature_2):
		return (feature_1 * feature_2)