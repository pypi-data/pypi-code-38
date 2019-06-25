"""
    Runner
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import argparse
import functools

import tensorflow as tf

from tflibs.utils import log_parse_args


class Runner:
    """
    Initialize all the artifacts by resolving initializers

    :param initializers: Initializers
    :param default_job_dir: Default job directory
    """

    def __init__(self, initializers=[], default_job_dir='/tmp/job-dir', no_job_dir=False):
        self._initializers = initializers
        self._argparser = argparse.ArgumentParser()
        self._no_job_dir = no_job_dir

        if not no_job_dir:
            #################
            # Job Directory #
            #################
            self.argparser.add_argument('--job-dir',
                                        type=str,
                                        default=default_job_dir,
                                        help="""
                                            GCS or local dir for checkpoints, exports, and
                                            summaries. Use an existing directory to load a
                                            trained model, or a new directory to retrain""")
            self.argparser.add_argument('--run-name',
                                        required=True,
                                        type=str,
                                        help='The run name.')
        ##############
        # Run Config #
        ##############
        self.argparser.add_argument('--verbosity',
                                    choices=[
                                        'DEBUG',
                                        'ERROR',
                                        'FATAL',
                                        'INFO',
                                        'WARN',
                                    ],
                                    default='INFO',
                                    help='Set logging verbosity')

        for initializers in self._initializers:
            initializers.add_arguments(self.argparser)

    def run(self, main):
        """
        Run

        :param function main: main function to run
        """
        parse_args, unknown = self.argparser.parse_known_args()

        # Set python level verbosity
        tf.logging.set_verbosity(parse_args.verbosity)
        # Set C++ Graph Execution level verbosity
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(
            tf.logging.__dict__[parse_args.verbosity] / 10)
        del parse_args.verbosity

        log_parse_args(parse_args, 'Runner arguments')

        if not self._no_job_dir:
            # Set job directory
            job_dir = parse_args.job_dir
            run_name = parse_args.run_name

            handled = {
                'job_dir': os.path.join(job_dir, run_name)
            }
            del parse_args.job_dir
            del parse_args.run_name
        else:
            handled = {}

        handled.update(vars(parse_args))
        parse_args = argparse.Namespace(**handled)

        # Handle arguments with initializer
        def handle(reducing, initializer):
            parse_args, unknown = reducing
            handled, unknown = initializer.handle(parse_args, unknown)
            handled.update(vars(parse_args))
            return argparse.Namespace(**handled), unknown

        handled_args, unknown = functools.reduce(handle,
                                                 self._initializers,
                                                 (parse_args, unknown))

        if unknown:
            raise ValueError('Unknown arguments: {}'.format(unknown))

        log_parse_args(handled_args, 'Final arguments')

        main(**vars(handled_args))

    @property
    def argparser(self):
        return self._argparser
