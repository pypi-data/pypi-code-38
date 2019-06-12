import os
import numpy as np
import pandas as pd
import itertools
import collections
import geojson
from typing import Iterable,Callable

def constrained_sequence(seq_length,vals=None):
	values=[0]
	if not vals is None:
		if isinstance(vals,Iterable): values=list(vals)
		elif isinstance(vals,Callable): values=[vals(i) for i in range(seq_length)]
		else: values=[vals]
	values=values+[values[-1]]*(seq_length-len(values))
	return values

def read_geojson(geojson_file_path,):
	with open(geojson_file_path,'r') as gjf:
		data=geojson.load(gjf)
	return data

def main():
	pass

if __name__=='__main__':
	main()
