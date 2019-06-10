#!/usr/bin/env python3

# Peripheral python modules
from pathlib import Path
import pickle

# External python modules
import pandas as pd
import goenrich


BASE_DIR = Path(__file__).parent

def _get_pickled_ontology(path="db/go-basic.pkl"):

	ontology_path = BASE_DIR / path

	if ontology_path.exists():
		print("Loading ontology from pickled file...")
		return pickle.load(open(ontology_path, 'rb'))

	else: 
		print("Converting ontology to pickled file...")
		O = goenrich.obo.ontology(str(BASE_DIR / 'db/go-basic.obo'))
		# Save as pickle
		pickle.dump(O, open(ontology_path, 'wb'))
		return O


def _get_pickled_symbol2go(path="db/symbol2go.pkl"):
	
	symbol2go_path = BASE_DIR / path

	if symbol2go_path.exists(): 
		print("Loading symbol2go from pickled file...")
		return pickle.load(open(symbol2go_path, 'rb'))

	else: 
		print("Converting gene2go to symbol2go file...")
		gene2go = goenrich.read.gene2go(str(BASE_DIR / "db/gene2go.gz"))
		# Download mapping from entrez ID to gene symbols
		import mygene
		mg = mygene.MyGeneInfo()
		entrez2symbol =  mg.getgenes(gene2go.GeneID.unique(), fields="symbol", as_dataframe=True)
		entrez2symbol.index = entrez2symbol.index.astype(int)
		# Add column for gene symbols
		symbol2go = gene2go.assign(symbol=entrez2symbol.symbol.reindex(gene2go.GeneID).values)
		# Save as pickle
		pickle.dump(symbol2go, open(symbol2go_path, 'wb'))
		return symbol2go

def node_attributes_as_df(nxgraph): 
	"""Returns node attributes on networkx graph as dataframe."""
	return pd.DataFrame.from_dict(dict(nxgraph.nodes(data=True)), orient='index')


O = _get_pickled_ontology()
symbol2go = _get_pickled_symbol2go()

class GO: 

	def __init__(self, bg): 

		self.O = O.copy()
		self.symbol2go = symbol2go.copy()
		self.bg = bg

		self._propogate_background()

		self.O_attribs = node_attributes_as_df(self.O)

	def _propogate_background(self): 
		# Filter GO database for genes in background
		symbol2go_bg = self.symbol2go[self.symbol2go.symbol.isin(self.bg)]
		# Create GO to gene mapping
		bg_GO_gene_map = { k: set(v) for k,v in symbol2go_bg.groupby("GO_ID")["symbol"] }
		# Assign terms to Ontology as background node attribute
		goenrich.enrich.propagate(self.O, bg_GO_gene_map, "background")
		
	def enrich(self, fg, **options): 
		# Run enrichment
		results = goenrich.enrich.analyze(self.O, fg, 'background', **options).dropna().sort_values('q').set_index("term")
		# Calculate enrichment score
		results["ES"] = (results.x / results.N) / (results.n / results.M)
		results = results[["name", "q", "ES", "namespace", "p", "x", "n", "M", "N"]]
		return results

	def get_genes_in_GO(self, goid, input=None): 
		"""Returns all genes in a GO category"""
		goid = "GO:{}".format(goid.lstrip("GO:"))
		go_genes = self.O.nodes("background")[goid]
		if input is None: 
			return go_genes
		else: 
			return set(go_genes) & set(input)