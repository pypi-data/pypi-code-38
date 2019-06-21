#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
A script that runs the Domain SPECIFIC UNITS approach for
Heterogeneous Face Recognition
"""


from bob.bio.base import load_resource
import os
from bob.bio.base.baseline import get_available_databases, search_preprocessor
from bob.extension.scripts.click_helper import verbosity_option, ResourceOption
import click
from bob.bio.base.script.verify import main as verify
from bob.extension import rc
from bob.bio.htface.configs.domain_specific_units.utils import get_dsu_training_setup
import tensorflow as tf
from tensorflow.python import debug as tf_debug


@click.command(context_settings={'ignore_unknown_options': True,
                                 'allow_extra_args': True})
@click.argument('baseline', required=True)
@click.argument('database', required=True)
@click.option('--result-directory', default=rc["bob.bio.htface.experiment-directory"], help='Directory where the experiments will be executed', required=True)
@click.option('--protocol', default=None, help='Protocol name. If not set, the script will iterate over all protocols of a given database', required=False)
@verbosity_option(cls=ResourceOption)
@click.pass_context
def htface_train_dsu(ctx, baseline, database, result_directory, protocol, **kwargs):
    """Trains a CNN using the domain specific units approach

    \b
    Example:
        $ bob bio htface_domain_specific_units xxx cufs -vvv

 
    """
    # STANDARD DSU TRAINING SETUP
    training_setup = get_dsu_training_setup()

    # Triggering training for each baseline/database
    loaded_baseline = load_resource(
        baseline, 'baseline', package_prefix="bob.bio.")

    # find the compatible preprocessor for this database
    db = load_resource(database, 'database', package_prefix="bob.bio.")
    #db_preprocessor = search_preprocessor(database, loaded_baseline.preprocessors.keys())
    #preprocessor = loaded_baseline.preprocessors[db_preprocessor]

    # Iterating over the protocols
    if protocol is None:
        if hasattr(db, "reproducible_protocols"):
            protocols = db.reproducible_protocols
        else:
            raise NotImplemented("The method `reproducible_protocols` was not"
                                 "defined in the database {0}".format(database))
    else:
        protocols=[protocol]

    for p in protocols:
        # Computing the number of samples per epoch from the dataset
        samples_per_epoch = (len(db.objects(protocol=p, groups="world"))//2)*5

        # load the estimator
        estimator, train_input_fn, hooks, preprocessed_relative_dir = \
                                                          loaded_baseline.estimator(result_directory, \
                                                          db, p, samples_per_epoch=samples_per_epoch,\
                                                          training_setup=training_setup)

        # Replacing 
        preprocessed_directory = os.path.join(result_directory, database, \
                                              preprocessed_relative_dir, \
                                              db.reproducible_protocols[0] , \
                                              "preprocessed")
        # Changing the database path
        db.original_directory = preprocessed_directory
        db.original_extension = ".hdf5"

        # debug        
        #hooks.append(tf_debug.LocalCLIDebugHook())

        # Triggering the estimator
        estimator.train(input_fn=train_input_fn, hooks=hooks,
                    steps=200000)
 
