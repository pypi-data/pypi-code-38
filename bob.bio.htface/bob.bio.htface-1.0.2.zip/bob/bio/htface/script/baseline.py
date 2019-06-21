#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
A script to run HETEROGENEOUS FACE RECOGNITION baselines
"""


from bob.bio.base import load_resource
import os
from bob.bio.base.baseline import get_available_databases, search_preprocessor
from bob.extension.scripts.click_helper import ResourceOption, verbosity_option
import click
from bob.bio.base.script.verify import main as verify
from bob.extension import rc
import tensorflow as tf
import tempfile
import bob.io.base

@click.command(context_settings={'ignore_unknown_options': True,
                                 'allow_extra_args': True})
@click.argument('baseline', required=True)
@click.argument('database', required=True)
@click.option('--preprocess-training-data', default=False, help='If set, the preprocessed data from the training set (world) will be extracted', required=False, is_flag=True)
@click.option('--result-directory', default=rc["bob.bio.htface.experiment-directory"], help='Directory where the experiments will be executed', required=True)
@click.option('--protocols', default=None, help='If set, it will replace the set of predifined protocols. It\'s used when you want to run an experiment in a protocol that is not covered in this package', required=False)
@verbosity_option(cls=ResourceOption)
@click.pass_context
def htface_baseline(ctx, baseline, database, preprocess_training_data, result_directory, protocols, **kwargs):
    """Run a biometric recognition baseline.

    \b
    Example:
        $ bob bio htface_baseline eigenface cufs -vvv

    which will run the eigenface baseline (from bob.bio.face) on the 5 splits of CUHK_CUFS
    database.

    \b
    Check out all baselines available by running:
    `resource.py --types baseline`
    and all available databases by running:
    `resource.py --types database`

    This script accepts parameters accepted by verify.py as well.
    See `verify.py --help` for the extra options that you can pass.

    Hint: pass `--grid demanding` to run the baseline on the SGE grid.

    Hint: pass `--temp-directory <dir>` to set the directory for temporary files

    Hint: pass `--result-directory <dir>` to set the directory for resulting score files
 
    """
    # Triggering training for each baseline/database
    loaded_baseline = load_resource(
        baseline, 'baseline', package_prefix="bob.bio.")

    # this is the default sub-directory that is used
    base_sub_directory = os.path.join(database, baseline)

    # find the compatible preprocessor for this database
    db = load_resource(database, 'database', package_prefix="bob.bio.")
    db_preprocessor = search_preprocessor(database, loaded_baseline.preprocessors.keys())
    preprocessor = loaded_baseline.preprocessors[db_preprocessor]

    # Iterating over the protocols
    if protocols is None:
        # If the protocols were not set, take the ones preset in the database
        if hasattr(db, "reproducible_protocols"):
            protocols = db.reproducible_protocols
        else:
            # if doesn't have any defined, will take the default one
            protocols = [None]
    else:
        protocols = [protocols]
    for p, i in zip(protocols, range(len(protocols))):
        temp_config_file = generate_temp_config_file(result_directory,
                                                     db.name,
                                                     p,
                                                     baseline)
        # call verify with all parameters
        parameters = [
            temp_config_file,
            loaded_baseline.extractor,
            '-p', preprocessor,
            '-d', database] + ['-v'] * ctx.meta['verbosity']

        parameters += ['--groups', "dev"]

        # Special treatment for the protocol
        if p is None:
            parameters += ['--sub-directory', base_sub_directory]
        else:
            sub_directory = os.path.join(base_sub_directory, p)
            parameters += ['--sub-directory', sub_directory]
            parameters += ['--protocol', p]

        # Reusing the preprocessed directory to save space
        if i==0:
            preprocessed_directory = os.path.join(result_directory, sub_directory, "preprocessed")

            directories = ["-T", result_directory, "-R", result_directory]
            directories += ["--preprocessed-directory", preprocessed_directory]
            if hasattr(loaded_baseline, "reuse_extractor") and loaded_baseline.reuse_extractor:
                extracted_directory = os.path.join(result_directory, sub_directory, "extracted")
                directories += ["--extracted-directory", extracted_directory]

        verify(parameters + ['-a', loaded_baseline.algorithm] + directories + ctx.args)

        # CASE WE NEED TO EXTRACT THE TRAINING DATA
        tf.reset_default_graph()
        if preprocess_training_data:
            training_data_params = ['-a', 'pca']
            training_data_params += ['-o', 'preprocessing', 'extraction']
            verify(parameters + training_data_params + directories + ctx.args)
            tf.reset_default_graph()


def generate_temp_config_file(result_directory, database_name, protocol, baseline):

    config = '''
temp_dir      = '{temp_dir}'
database_name = '{database_name}'
protocol      = '{protocol}'
'''.format(temp_dir=result_directory,
                        database_name=database_name,
                        protocol=protocol)

    directory = os.path.join(result_directory, "temp")
    bob.io.base.create_directories_safe(directory)

    with tempfile.NamedTemporaryFile(mode='w+t', prefix='{}_'.format(baseline),                                      suffix='.py', delete=False, dir=directory)as f:
        f.write(config)
        f.flush()
        f.seek(0)
        return f.name
