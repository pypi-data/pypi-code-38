#!/usr/bin/env python3

import pandas as pd
import numpy as np


class Counts(pd.DataFrame): 
	
	@property
	def _constructor(self):
		return Counts
	
	## NORMALIZATIONS

	def sample_norm(self, scale=1e8):
		"""Normalize by sum of sample abundances values."""

		return self.div(self.sum(), axis=1) * scale
	
	def log(self, base=2, pseudocount=1): 
		"""Log-transform data."""

		return np.log(self + pseudocount) / np.log(base)
	
	def zscore(self): 
		"""Normalize across features by z-score."""

		return self.sub(self.mean(axis=1), axis=0).div(self.std(ddof=0, axis=1), axis=0)
	
	
	## GROUPING OPERATIONS
	
	def group_samples(self): 
		"""Groups samples by mean after removing replicate suffixes."""

		return Counts(self.rename(columns={ col: col.rsplit('_', 1)[0] for col in self.columns }).mean(axis=1, level=0))

	def group_indices(self, method="mean", min_features=0): 
		"""Collapse data with duplicate indices (such as peptide data)."""

		# Filter features based on number of missing values
		df = self[self.index.value_counts() >= min_features]

		if method == "mean": 
			return Counts(df.groupby(level=df.index.names).mean())
		
		elif method == "median": 
			return Counts(df.groupby(level=df.index.names).median())

		else: 
			print("`method` attribute must be 'mean' or 'median'.")
	   
	
	## FILTERING
	
	def remove_na(self, min_features=None, frac=None): 
		"""Filter rows based on number of missing values."""

		if min_features is not None: 
			return self[self.index.value_counts() >= min_features]

		elif frac is not None: 
			return self.dropna(thresh=int(self.shape[1] * frac))

		else: 
			print("No nan filter provided. Returning original dataframe.")
			return self