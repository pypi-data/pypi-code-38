from __future__ import print_function

from aitools.core import k_means
from aitools.utils import util

# Caution: Do not go crazy with the function
global_input = util.create_random_cluster(10, 1000, 3, 2000)

# Printing the global input
print_function(global_input)

# Creating 4 clusters with KMeans
clusters = k_means.KMeans(4)
clusters.build(global_input)

# Printing Cluster Means
print_function(clusters.means)

# Use to find the most relevant numbers of clusters
k_means.plot_k_with_squared_clustering_error(global_input, 30)
