import pandas
import seaborn
import pydotplus
import numpy

from sklearn.externals.six import StringIO
from IPython.display import Image
from sklearn.tree import export_graphviz
from matplotlib import pyplot as plt
from matplotlib import gridspec


def plot_univariate(df: pandas.DataFrame, x_list: list, y_list: list, y_list_secondary: list = None, ylim: tuple = (None, None), mean_variables: list = None, order=None, hlines: list = None,
					grid: bool = False):
	"""
	:param df: pandas DataFrame to plot
	:param x_list: x variables to plot
	:param y_list: y variables to plot
	:param y_list_secondary: secondary y variables to plot
	:param ylim: y axis limit
	:param mean_variables: variables of which plot the mean
	:param order: sorting for x values, valid values are 'asc', 'desc', '<column_name>'
	:param hlines: list of float. plots horizontal lines
	:param grid: show grid
	:return: None
	"""
	plt.rcParams['figure.figsize'] = (18, 10)
	order_choices = ['desc', 'asc'] + list(df.columns)
	if y_list_secondary is None:
		y_list_secondary = []

	if len(x_list) > 1 and order is not None:
		if not isinstance(order, dict) and order not in order_choices:
			raise Exception('Error! order provided is invalid. Possible choices are: {} or a dict shaped as {{x: order for x in x_list}}'.format(order_choices))
		if isinstance(order, dict):
			if sum([x not in order.keys() for x in x_list]) > 0:
				raise Exception('Error! not all the variables specified in \'x_list\' are present in \'order\' dict')

	for x in x_list:
		n_uniques = len(df[x].unique())

		ax1 = plt.axes()
		ax1.tick_params('x', rotation=90)

		if order is None:
			plt_order = sorted(df[x].unique())
		elif order == 'desc':
			plt_order = df[x].value_counts().sort_values(ascending=False).index
		elif order == 'asc':
			plt_order = df[x].value_counts().sort_values(ascending=True).index
		elif isinstance(order, str):
			if order in df.columns:
				plt_order = list(df.pivot_table(index=x, aggfunc={order: 'mean'}).sort_values(order).index)
			else:
				raise Exception('Error! cannot order by variable \'{}\' as is not present in input dataset'.format(order))
		elif isinstance(order, dict):
			plt_order = order[x]
		elif isinstance(order, list):
			plt_order = order
			if len(x_list) == 1:
				missing_values = set(df[x].unique()).difference(order)
				if len(missing_values) != 0:
					raise Exception('Error! missing values \'{}\' in order list'.format(missing_values))
			else:
				raise Exception('Error! {} plotting variables specified but only one order list provided.'.format(len(x_list)))

		else:
			raise ValueError('{} invalid value for data ordering!'.format(order))

		seaborn.countplot(x=x, data=df, ax=ax1, alpha=0.7, order=plt_order)

		ax2 = ax1.twinx()
		if ylim[0] is not None and ylim[1] is not None:
			ax2.set_ylim(ylim)

		color = seaborn.color_palette("Set1", 8)
		color_index = 0

		for y in y_list:
			seaborn.pointplot(x=x, y=y, data=df, ax=ax2, color=color[color_index], order=plt_order)
			color_index += 1

		if len(y_list_secondary) > 0:
			ax3 = ax1.twinx()
			for y in y_list_secondary:
				seaborn.pointplot(x=x, y=y, data=df, ax=ax3, color=color[color_index], order=plt_order)
				color_index += 1

			ax3.spines['right'].set_position(('outward', 60))
			ax3.tick_params('y', labelsize=15)

		ax1.tick_params('x', labelsize=15)
		ax1.tick_params('y', labelsize=15)
		ax2.tick_params('y', labelsize=15)

		legend = y_list + y_list_secondary

		if hlines is not None:
			if not isinstance(hlines, list):
				hlines = [hlines]
			for hline in hlines:
				plt.hlines(y=hline, xmin=0, xmax=n_uniques, label=str(hline), colors=color[color_index], linestyles='--')
				color_index += 1

			legend += list(map(str, hlines))

		if mean_variables is not None:
			for mean_variable in mean_variables:
				y_mean = df[mean_variable].mean()
				ax2.plot([y_mean for _ in range(n_uniques)], c=color[color_index])
				color_index += 1
			legend += [mv + '_mean' for mv in mean_variables]

		ax2.legend(legend)

		leg = ax2.get_legend()
		color_index = 0
		for lgd in leg.legendHandles:
			lgd.set_color(color[color_index])
			color_index += 1

		ax2.grid(grid)
		plt.show()


def plot_tree(tree, class_names: list, feature_names: list, weighted_colors: float = None, palette_name: str = 'Accent'):
	"""
	Plots a decision tree with all its leaves
	:param tree: sklearn tree object
	:param class_names: names of the final classes
	:param feature_names: name of the features used in the decision tree
	:param weighted_colors: weight to apply to color scales
	:param palette_name: seaborn palette name
	:return: tree image
	"""
	palette = seaborn.color_palette(palette_name, n_colors=tree.n_classes_)
	colors = numpy.array(list(map(lambda x: 256 * numpy.array(x), palette)))

	dot_data = StringIO()
	export_graphviz(
		tree, out_file=dot_data,
		filled=True, rounded=True,
		special_characters=True,
		feature_names=feature_names,
		class_names=class_names)

	graph_string = dot_data.getvalue()

	for leaf_ID, leaf in enumerate(numpy.where(tree.tree_.children_left == -1)[0]):
		graph_string = graph_string.replace('\n{} [label=<'.format(leaf), '\n{} [label=<----- leaf {} -----<br/>'.format(leaf, leaf_ID))

	graph = pydotplus.graph_from_dot_data(graph_string)

	nodes = graph.get_node_list()

	for node in nodes:
		if node.get_label():
			values = numpy.array([int(ii) for ii in node.get_label().split('value = [')[1].split(']')[0].split(',')])

			if weighted_colors is None:
				color_weights = numpy.zeros(tree.n_classes_)
				color_weights[numpy.where(values == max(values))] = 1
			else:
				color_weights = values / sum(values)
				color_weights = numpy.power(color_weights, weighted_colors) / sum(numpy.power(color_weights, weighted_colors))

			color_rgb = numpy.dot(color_weights, colors)
			color_hex = '#%02x%02x%02x' % tuple(color_rgb.astype(int))
			node.set_fillcolor(color_hex)

	return Image(graph.create_png())


def plot_scatter_hist(df: pandas.DataFrame, x: str, y: str, fsize=(18, 8), width_ratios: tuple = (5, 1), height_ratios: tuple = (4, 1), hue: str = None, s=0.1, bins=100, alpha=0.5):
	"""
	Plots a scatter prlot rounded by an histogram for each axis
	:param df: pandas DataFrame to use
	:param x:
	:param y:
	:param fsize:
	:param width_ratios:
	:param height_ratios:
	:param hue:
	:param s:
	:param bins:
	:param alpha:
	:return:
	"""
	plt.rcParams['figure.figsize'] = fsize
	gs = gridspec.GridSpec(2, 2, width_ratios=list(width_ratios), height_ratios=list(height_ratios))

	ax0 = plt.subplot(gs[0])
	ax1 = plt.subplot(gs[1])
	ax2 = plt.subplot(gs[2])

	if hue is not None:
		legend = []
		for value in df[hue].value_counts().index.values:
			legend.append(value)
			ax0.scatter(df.loc[df[hue] == value, x], df.loc[df[hue] == value, y], s=s)
			ax1.hist(df.loc[df[hue] == value, y], orientation='horizontal', bins=bins, alpha=alpha)
			ax2.hist(df.loc[df[hue] == value, x], orientation='vertical', bins=bins, alpha=alpha)

		ax0.set(xlabel=x, ylabel=y)
		ax1.set(xlabel='count', ylabel=y)
		ax2.set(xlabel=x, ylabel='count')

		ax0.legend(legend, markerscale=6)

	else:
		ax0.scatter(df.loc[:, x], df.loc[:, y], s=s)
		plt.xlabel(x)
		plt.ylabel(y)
		ax1.hist(df.loc[:, y], orientation='horizontal', bins=bins, alpha=alpha)
		ax2.hist(df.loc[:, x], orientation='vertical', bins=bins, alpha=alpha)

	plt.tight_layout()
	plt.show()


def plot_heatmap(df: pandas.DataFrame, var_x: str, var_y: str, var_z: str, z_aggfunc, var_x_n_quantiles: int = 20, var_y_n_quantiles: int = 20, get_bins: bool = False, **kwargs):
	"""
	:param df: pandas DataFrame to use
	:param var_x: first variable for the heatmap
	:param var_y: second variable for the heatmap
	:param var_z: plotting variable for the heatmap
	:param z_aggfunc: aggregating function to use in the heatmap
	:param var_x_n_quantiles:
	:param var_y_n_quantiles:
	:param get_bins: return heatmap bins
	:return: heatmap_df dataframe
	"""
	cut_1, var_1_bins = pandas.qcut(df[var_x], q=var_x_n_quantiles, retbins=True)
	cut_2, var_2_bins = pandas.qcut(df[var_y], q=var_y_n_quantiles, retbins=True)

	heatmap_df = pandas.pivot_table(index=[cut_1, cut_2], aggfunc={var_z: z_aggfunc}).unstack()
	seaborn.heatmap(heatmap_df, **kwargs)

	if get_bins:
		return heatmap_df, var_1_bins, var_2_bins
	else:
		return heatmap_df
