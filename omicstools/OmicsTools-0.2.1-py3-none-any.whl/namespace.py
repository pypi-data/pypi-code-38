#!/usr/bin/env python3

import pandas as pd
import mygene


mg = mygene.MyGeneInfo()


class SymbolMapping: 

	def __init__(self, symbols, symbol_type): 

		self.symbols = symbols
		self.symbol_type = symbol_type # uniprot, ensemblgene

		self.mapping = self._get_namespace_mapping()
		self.unique_mapping = self._get_unique_mapping()


	def _get_namespace_mapping(self): 
		"""Returns namespace mapping following a gene symbol prioritization procedure for duplicate mappings."""

		mapping = mg.querymany(self.symbols, scopes=self.symbol_type, as_dataframe=True, returnall=True)["out"]
		# Queries with duplicated gene symbols may be returned in any order, so we prioritize certain gene symbols 
		# such that gene fusions do not appear first and protein subunits are sorted alphabetically. 
		mapping["is_fusion"] = mapping.symbol.str.contains('-')
		mapping = mapping.sort_values(by=["is_fusion", "symbol"]).loc[self.symbols, "symbol"]

		return mapping


	def _get_unique_mapping(self, input_symbols=None):
		"""Convert the full mapping results into a one-to-one mapping."""
		
		if input_symbols is None: input_symbols = self.symbols

		# Get reduced space of mappings.
		mapping = self.mapping.loc[ input_symbols & self.mapping.index ].dropna()
		# Handle many-to-one issues by keeping only first index that appears for duplicated symbols.
		mapping = mapping[ ~mapping.index.duplicated() ]
		# Handle one-to-many issues by keeping only first term that appears for duplicated values.
		mapping = mapping.drop_duplicates(keep='first')

		return mapping


	def convert(self, df, use_current_ordering=True): 
		"""Converts input dataframe index to gene symbols."""
		if use_current_ordering: 
			# Use ordering of df index to get the unique mapping.
			mapping = self._get_unique_mapping(input_symbols=df.index)
		else: 
			# Use default unique mapping. 
			mapping = self.mapping

		return df.merge(mapping, left_index=True, right_index=True, how="inner").set_index("symbol")
