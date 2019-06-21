#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
Plot t-SNE clusted by modality

t-SNE is a tool to visualize high-dimensional data. 
It converts similarities between data points to joint probabilities and tries to minimize the Kullback-Leibler 
divergence between the joint probabilities of the low-dimensional embedding and the high-dimensional data.

WARNING: This is not a convex problem, so please try different seeds (`--seed` option).

More info in:
van der Maaten, L.J.P.; Hinton, G.E. Visualizing High-Dimensional Data Using t-SNE. Journal of Machine Learning Research 9:2579-2605, 2008.


For information about <database> parameter plese do:
  resources.py --type database


Usage:
  plot_tsne.py  <database> <database-original-directory>
               [--database-extension=<arg> --output-file=<arg> --protocol=<arg>]
               [--iterations=<arg> --learning-rate=<arg> --perplexity=<arg> --seed=<arg>]
  plot_tsne.py -h | --help

Options:
  --output-file=<arg>                   Output file [default: tsne.pdf]
  --iterations=<arg>                    Maximum number of iterations for the gradient descend [default: 5000]
  --learning-rate=<arg>                 Learning rate for the gradient descend [default: 200.0]
  --perplexity=<arg>                    Perplexity [default: 30]
  --seed=<arg>                          Seed for the pseudo random number generator [default: 0]
  --database-original-directory=<arg>   Database original directory
  --database-extension=<arg>            Database extension [default: .hdf5]
  -h --help                             Show this screen.
"""

from docopt import docopt
import logging
import bob.bio.base
import bob.core
import os
from bob.bio.base.tools import FileSelector
import bob.io.base
import bob.io.image
from sklearn.preprocessing import normalize


import numpy
import matplotlib
matplotlib.use('agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as mpl
from sklearn.manifold import TSNE

logger = logging.getLogger("bob.bio.base")
from matplotlib import colors as mcolors
import bob.core
import bob.bio.base
from mpl_toolkits.mplot3d import Axes3D
numpy.random.seed(10)
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D


def process_raw_data(raw_data):

    # If it is W x H x C 
    if raw_data.ndim == 3:
        raw_data = bob.io.image.to_bob(raw_data)
        return raw_data.flatten()
        #return numpy.reshape(raw_data, (raw_data.shape[0],raw_data.shape[1]*raw_data.shape[2]))

    elif raw_data.ndim == 2:
        return raw_data.flatten() 
    else:
        return raw_data


def main():
    """Executes the main function"""

    args = docopt(__doc__, version='Run experiment')
    bob.core.log.set_verbosity_level(logger, 3)
    preprocessor_resource_key = "preprocessor"
    database_resource_key = "database"

    database = args['<database>']
    protocol = args['--protocol']
    database_original_directory = args['<database-original-directory>']

    database_extension = args['--database-extension']
    output_file = args['--output-file']

    seed = int(args['--seed'])
    perplexity = int(args['--perplexity'])
    learning_rate = float(args['--learning-rate'])
    iterations = int(args['--iterations'])

    data = dict()
    indexes_modality = dict()
    MAX_CLIENTS = 100

    # Loading the database
    bob_db = bob.bio.base.utils.load_resource(database, database_resource_key,
                                              imports=['bob.bio.base'], package_prefix='bob.bio.',
                                              preferred_package=None)
                                                                                            
    if protocol is not  None:
        bob_db.protocol = protocol

    FileSelector.create(
            database=bob_db,            
            extractor_file="",
            projector_file="",
            enroller_file="",

            preprocessed_directory="",
            extracted_directory="",
            projected_directory="",
            model_directories="",
            score_directories="",
            zt_score_directories="",
            compressed_extension="",
            default_extension='.hdf5',
        )

    fs = FileSelector.instance()

    logger.debug("  >> Loading data ...")
    original_datalist = fs.original_data_list(groups="dev")
            
    # Keeping two lists for each modality. Will be useful to use the colors
    #indexes_modality = dict()
    #indexes_modality[bob_db.modalities[0]] = []
    #indexes_modality[bob_db.modalities[1]] = []

    data = None
    total_samples = len(original_datalist)


    color_index = 0
    colors = list(dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS).keys())

    client_colors = dict() # Stores the color per client
    sample_colors = [] # Stores the color/modality
    legend_elements = [Line2D([0], [0], marker="^", label="VIS"), Line2D([0], [0], marker="o", label="Sketch") ]

    for o, i in zip(original_datalist, range(total_samples)):

        if o.client_id not in client_colors:
            client_colors[o.client_id] = colors[color_index%len(colors)]
            color_index += 1
        
        marker = "^" if o.modality == bob_db.modality_separator else "o"
        sample_colors.append([client_colors[o.client_id], marker, o.modality])

        raw_data = bob.io.base.load(o.make_path(database_original_directory) + database_extension)
        raw_data = process_raw_data(raw_data)

        # Alocating numpy
        if data is None:
            # If it is W x H x C 
            if raw_data.ndim == 2:
                data = numpy.zeros(shape=(total_samples, raw_data.shape[0], raw_data.shape[1]))
            else:
                data = numpy.zeros(shape=(total_samples, 1, raw_data.shape[0]))

        for j in range(data.shape[1]):
            if raw_data.ndim == 1:
                data[i,j] = raw_data
            else:
                data[i,j] = raw_data[j]
 
    pp = PdfPages(output_file)
    # One TSNE per filter
    for i in range(data.shape[1]):


        logger.debug("  >> Training TSNE with {0} ...".format(data.shape))
        model = TSNE(n_components=2, random_state=seed, perplexity=perplexity,
                 learning_rate=learning_rate, n_iter=iterations, init='pca', metric='euclidean', method='exact')
        projected_data = model.fit_transform(data[:,i,:])
        # Ploting
        logger.debug("  >> Plotting projected data")
        fig = mpl.figure()
        #ax = mpl.subplot(111, projection='3d')
        ax = mpl.subplot(111)
    
        #mpl.title("T-SNE - '{0}'".format(database_name))
        mpl.title("".format(i))

        client_tracker = []
        for o, j in zip(original_datalist, range(projected_data.shape[0])):

            if o.client_id not in client_tracker and len(client_tracker) > MAX_CLIENTS:
                continue
            else: 
                client_tracker.append(o.client_id)


            mpl.plot(projected_data[j, 0], projected_data[j, 1], marker=sample_colors[j][1], color=sample_colors[j][0], label=sample_colors[j][2], markersize=5)

            #ax.scatter(projected_data[j, 0],
            #           projected_data[j, 1],
            #           c=sample_colors[j][0],
            #           marker=sample_colors[j][1],
            #           s=1)
   
        #mpl.legend(bob_db.modalities)
        mpl.legend(handles=legend_elements)
        pp.savefig(fig)

    pp.close()
    del pp

    logger.debug("  >> Plot saved in '{0}'".format(output_file))
    logger.debug("  >> Done !!!")


if __name__ == "__main__":
    main()
