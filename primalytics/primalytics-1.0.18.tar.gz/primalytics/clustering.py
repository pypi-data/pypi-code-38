import pandas
import numpy
import seaborn

from matplotlib import pyplot as plt
from itertools import groupby
from sklearn.cluster import SpectralClustering


def norm_cov_matrix(df):
	"""
	:param df: pandas dataframe to use
	:return: normalized covariance matrix of a pandas dataframe
	"""
	var = numpy.sqrt(df.var())
	return (df.loc[:, var.index]/var).cov()


def cluster_variables(df: pandas.DataFrame, n_clusters: int, sigma: float, selected_variables: list=None, target: list=None, return_results: bool=False, **kwargs):
	"""
	:param df: pandas dataframe
	:param n_clusters: number of cluster to create
	:param sigma: decay constant for affinity matrix
	:param selected_variables: varaibles to use in clustering
	:param target: optional target variable to spot correlations
	:param return_results: return full clusters description
	:param kwargs: kwargs for seaborn heatmap
	:return: full clusters description
	"""
	# Affinity ------------------------------------------------------------------------------
	if selected_variables is None:
		cov_matrix = numpy.abs(norm_cov_matrix(df))
	else:
		if target[0] is not None:
			columns = selected_variables
			for tgt in target:
				if tgt not in selected_variables:
					columns = columns + [tgt]
		else:
			columns = selected_variables

		cov_matrix = numpy.abs(norm_cov_matrix(df[columns]))

	columns = list(cov_matrix.columns)
	selected_variables = columns

	for tgt in target:
		if tgt in selected_variables:
			selected_variables.remove(tgt)

	dist_matrix = 1. - cov_matrix

	affinity_matrix = numpy.exp(- dist_matrix ** 2 / (2. * sigma ** 2))

	# Clusters ------------------------------------------------------------------------------
	cluster = SpectralClustering(affinity='precomputed', n_clusters=n_clusters)
	clusters_tags = cluster.fit_predict(affinity_matrix.loc[selected_variables, :].loc[:, selected_variables])
	ordered_variables = [x for _, x in sorted(zip(clusters_tags, selected_variables))]

	clusters = {}
	for key, value in sorted(dict(zip(selected_variables, clusters_tags)).items()):
		clusters.setdefault(value, []).append(key)

	clusters_dim = [len(list(group)) for key, group in groupby(sorted(clusters_tags))]

	if target[0] is not None:
		columns = ordered_variables + target
	else:
		columns = ordered_variables

	sorted_cov_matrix = cov_matrix.loc[columns, :].loc[:, columns]
	sorted_affinity_matrix = affinity_matrix.loc[columns, :].loc[:, columns]

	# Plots ------------------------------------------------------------------------------
	plt.rcParams['figure.figsize'] = (18, max(10, len(cov_matrix.columns)//5))

	titles = ['sorted_cov_matrix', 'sorted_affinity_matrix']
	for i, matrix in enumerate([sorted_cov_matrix, sorted_affinity_matrix]):
		g = seaborn.heatmap(matrix, cmap='viridis', linecolor='black', linewidths=0.1, **kwargs)
		g.axes.hlines(numpy.cumsum(clusters_dim)[:-1], *g.axes.get_xlim(), colors='white', )
		g.axes.vlines(numpy.cumsum(clusters_dim)[:-1], *g.axes.get_xlim(), colors='white')

		if target is not None:
			g.axes.hlines(numpy.cumsum(clusters_dim)[-1], *g.axes.get_xlim(), colors='red', )
			g.axes.vlines(numpy.cumsum(clusters_dim)[-1], *g.axes.get_xlim(), colors='red')

		g.set_title(titles[i])
		plt.show()

	if return_results:
		return {
			'clusters': clusters,
			'cov_matrix': cov_matrix,
			'affinity_matrix': affinity_matrix,
			'sorted_cov_matrix': sorted_cov_matrix,
			'sorted_affinity_matrix': sorted_affinity_matrix}
