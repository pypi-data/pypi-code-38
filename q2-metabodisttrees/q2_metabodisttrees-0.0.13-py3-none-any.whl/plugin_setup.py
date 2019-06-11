# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (Plugin, Str, Properties, Choices, Int, Bool, Range,
                           Float, Set, Visualization, Metadata, MetadataColumn,
                           Categorical, Numeric, Citations)

import q2_metabodisttrees
from q2_metabodisttrees import getNewick
from q2_metabodisttrees import get_motiftrees
from q2_metabodisttrees import get_classytrees
from q2_types.feature_table import FeatureTable, Frequency, RelativeFrequency
from q2_types.distance_matrix import DistanceMatrix
from q2_types.sample_data import AlphaDiversity, SampleData
from q2_types.tree import Phylogeny, Rooted
from q2_types.ordination import PCoAResults

citations = Citations.load('citations.bib', package='q2_metabodisttrees')

plugin = Plugin(
    name='metabodisttrees',
    version=q2_metabodisttrees.__version__,
    website='https://qiime2.org',
    package='q2_metabodisttrees',
    description=('This QIIME 2 plugin supports metrics for calculating '
                 'chemically informed distance trees through '
                 'unsupervised substructure discovery and '
                 'chemical class information.'),
    short_description='Plugin for calculating chemically-informed trees.',
) 


plugin.methods.register_function(
    function=q2_metabodisttrees.get_motiftrees,
    inputs={'motifs': FeatureTable[Frequency],
            'buckettable': FeatureTable[Frequency]},
    parameters={'method': Str % Choices(['single', 'complete', 'average', 'weighted', 'centroid'
    									, 'median', 'ward']),
                'metric': Str% Choices(['braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation'
    									, 'cosine', 'dice', 'euclidean','hamming', 'jaccard', 'jensenshannon',
    									'kulsinski', 'mahalanobis', 'matching', 'mikowski', 'rogerstanimoto', 'russellrao',
    									'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean'])},
    outputs=[('metabodist_tree', Phylogeny[Rooted])],
    input_descriptions={
        'motifs': ('A table containing presence/absence of substrucutres ',
        			'per feature. '),
        'buckettable': ('The feature table containing the samples for which a '
                      'chemically informed tree should be computed. ')
    },
    parameter_descriptions={
        'method': 'The clustering method to be used for hierarchical cluster analysis.',
        'metric': 'The metric to be used for hierarchical cluster analysis.'
    },
    output_descriptions={'meatbodist_tree': 'Phylogeny[Rooted]. This is the chemical tree output'
                      'in the .qza format. Extracted it is in the Newick format.'},
    name='Metabodisttrees substructures',
    description=("Computes chemically informed distance tree through"
                 " unsupervised substructure discovery."),
    citations=[
        citations['vanderHooft2016'],
        citations['Ernst2019']]
)

plugin.methods.register_function(
    function=q2_metabodisttrees.get_classytrees,
    inputs={'cf': FeatureTable[Frequency],
            'buckettable': FeatureTable[Frequency]},
    parameters={'method': Str % Choices(['single', 'complete', 'average', 'weighted', 'centroid'
    									, 'median', 'ward']),
                'metric': Str% Choices(['braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation'
    									, 'cosine', 'dice', 'euclidean','hamming', 'jaccard', 'jensenshannon',
    									'kulsinski', 'mahalanobis', 'matching', 'mikowski', 'rogerstanimoto', 'russellrao',
    									'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean'])},
    outputs=[('metabodist_tree', Phylogeny[Rooted])],
    input_descriptions={
        'cf': ('A table containing presence/absence of chemical classes ',
        			'per feature. '),
        'buckettable': ('The feature table containing the samples for which a '
                      'chemically informed tree should be computed. ')
    },
    parameter_descriptions={
        'lev': ('Level of the chemical class onotology from where ',
        	'tree should be computed.'),
        'method': 'The clustering method to be used for hierarchical cluster analysis.',
        'metric': 'The metric to be used for hierarchical cluster analysis.'
    },
    output_descriptions={'meatbodist_tree': 'Phylogeny[Rooted]. This is the chemical tree output'
                      'in the .qza format. Extracted it is in the Newick format.'},
    name='Metabodisttrees chemical classes',
    description=("Computes chemically informed distance tree through "
                 "unsupervised substructure discovery."),
    citations=[
        citations['DjoumbouFeunang2016'],
        citations['Ernst2019']]
)
