"""
Subpackage containing algorithms for 5C data analysis.

Subpackage structure:

* :mod:`lib5c.algorithms.clustering` - algorithms for clustering together 5C
  interactions
* :mod:`lib5c.algorithms.distributions` - statistical modeling of 5C contact
  frequencies
* :mod:`lib5c.algorithms.filtering` - binning, smoothing, etc.
* :mod:`lib5c.algorithms.correlation` - pairwise correlations between replicates
* :mod:`lib5c.algorithms.determine_bins` - computing bins to tile 5C regions
* :mod:`lib5c.algorithms.donut_filters` - "donut" expected model correction
* :mod:`lib5c.algorithms.enrichment` - computing enrichments for genomic
  annotations between different 5C interaction classes
* :mod:`lib5c.algorithms.expected` - building expected models for 5C data
* :mod:`lib5c.algorithms.express` - "Express" normalization algorithms
* :mod:`lib5c.algorithms.knight_ruiz` - Knight-Ruiz matrix balancing
* :mod:`lib5c.algorithms.outliers` - finding and removing high spatial outliers
  in 5C contact matrices
* :mod:`lib5c.algorithms.qnorm` - quantile normalization standardize
  distributions between replicates
* :mod:`lib5c.algorithms.spline_normalization` - spline-based bias factor
  normalization
* :mod:`lib5c.algorithms.trimming` - removing "dead" or low-count primers from
  5C datasets

"""
