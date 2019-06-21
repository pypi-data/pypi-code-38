#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Aug 13:43:21 2015
#


from __future__ import print_function

import sys
import argparse
import os.path

import logging

logger = logging.getLogger("bob.pad.base")

from bob.pad.base import tools
import bob.bio.base.tools as biotools


# from bob.bio.base.tools import grid

def parse_arguments(command_line_parameters, exclude_resources_from=[]):
    """This function parses the given options (which by default are the command line options).
    If exclude_resources_from is specified (as a list), the resources from the given packages are
    not listed in the help message."""
    # set up command line parser
    parsers = tools.command_line_parser(exclude_resources_from=exclude_resources_from)

    # Add sub-tasks that can be executed by this script
    parser = parsers['main']
    parser.add_argument('--sub-task',
                        choices=('preprocess', 'train-extractor', 'extract', 'train-projector', 'project',
                                 'compute-scores'),
                        help=argparse.SUPPRESS)  # 'Executes a subtask (FOR INTERNAL USE ONLY!!!)'
    parser.add_argument('--group',
                        help=argparse.SUPPRESS)  # 'The group for which the current action should be performed'

    # now that we have set up everything, get the command line arguments
    return tools.initialize(parsers, command_line_parameters,
                            skips=['preprocessing', 'extractor-training', 'extraction', 'projector-training',
                                   'projection', 'score-computation'])


def add_jobs(args, submitter):
    """Adds all (desired) jobs of the tool chain to the grid, or to the local list to be executed."""

    # collect the job ids
    job_ids = {}

    # if there are any external dependencies, we need to respect them
    deps = args.external_dependencies[:]

    jobs_to_execute = []

    # preprocessing
    if not args.skip_preprocessing:
        if args.grid is None:
            jobs_to_execute.append(('preprocess',))
        else:
            job_ids['preprocessing'] = submitter.submit(
                '--sub-task preprocess',
                number_of_parallel_jobs=args.grid.number_of_preprocessing_jobs,
                dependencies=deps,
                **args.grid.preprocessing_queue)
            deps.append(job_ids['preprocessing'])

    # feature extraction training
    if not args.skip_extractor_training and args.extractor.requires_training:
        if args.grid is None:
            jobs_to_execute.append(('train-extractor',))
        else:
            job_ids['extractor-training'] = submitter.submit(
                '--sub-task train-extractor',
                name='train-f',
                dependencies=deps,
                **args.grid.training_queue)
            deps.append(job_ids['extractor-training'])

    # feature extraction
    if not args.skip_extraction:
        if args.grid is None:
            jobs_to_execute.append(('extract',))
        else:
            job_ids['extraction'] = submitter.submit(
                '--sub-task extract',
                number_of_parallel_jobs=args.grid.number_of_extraction_jobs,
                dependencies=deps,
                **args.grid.extraction_queue)
            deps.append(job_ids['extraction'])

    # feature projection training
    if not args.skip_projector_training and args.algorithm.requires_projector_training:
        if args.grid is None:
            jobs_to_execute.append(('train-projector',))
        else:
            job_ids['projector-training'] = submitter.submit(
                '--sub-task train-projector',
                name="train-p",
                dependencies=deps,
                **args.grid.training_queue)
            deps.append(job_ids['projector-training'])

    # feature projection
    if not args.skip_projection and args.algorithm.performs_projection:
        if args.grid is None:
            jobs_to_execute.append(('project',))
        else:
            job_ids['projection'] = submitter.submit(
                '--sub-task project',
                number_of_parallel_jobs=args.grid.number_of_projection_jobs,
                dependencies=deps,
                **args.grid.projection_queue)
            deps.append(job_ids['projection'])

    for group in args.groups:
        # compute scores
        if not args.skip_score_computation:
            if args.grid is None:
                jobs_to_execute.append(('compute-scores', group, None, 'A'))
            else:
                job_ids['score-%s' % group] = submitter.submit(
                    '--sub-task compute-scores --group %s' % group,
                    name="score-%s" % group,
                    dependencies=deps,
                    **args.grid.scoring_queue)

    if args.grid is None:
        # return the list of jobs that need to be executed in series
        return jobs_to_execute
    else:
        # return the job ids, in case anyone wants to know them
        return job_ids


def execute(args):
    """Run the desired job of the tool chain that is specified on command line.
    This job might be executed either in the grid, or locally."""
    # the file selector object
    fs = tools.FileSelector.instance()

    if args.dry_run:
        # Don't actually run the experiment, but just print out, what we would have done
        parameters = ""
        if args.group is not None: parameters += "group='%s' " % args.group
        if args.model_type is not None: parameters += "and model-type='%s' " % args.model_type
        if args.score_type is not None: parameters += "and score-type='%s' " % args.score_type
        print("Would have executed task '%s' with %s" % (args.sub_task, parameters if parameters else "no parameters"))
        # return True as we pretend to have executed the task
        return True

    # preprocess the data
    if args.sub_task == 'preprocess':
        tools.preprocess(
            args.preprocessor,
            groups=tools.groups(args),
            indices=biotools.indices(fs.original_data_list(groups=tools.groups(args)),
                                     None if args.grid is None else args.grid.number_of_preprocessing_jobs),
            allow_missing_files=args.allow_missing_files,
            force=args.force)

    # train the feature extractor
    elif args.sub_task == 'train-extractor':
        tools.train_extractor(
            args.extractor,
            args.preprocessor,
            allow_missing_files=args.allow_missing_files,
            force=args.force)

    # extract the features
    elif args.sub_task == 'extract':
        tools.extract(
            args.extractor,
            args.preprocessor,
            groups=tools.groups(args),
            indices=biotools.indices(fs.preprocessed_data_list(groups=tools.groups(args)),
                                     None if args.grid is None else args.grid.number_of_extraction_jobs),
            allow_missing_files=args.allow_missing_files,
            force=args.force)

    # train the feature projector
    elif args.sub_task == 'train-projector':
        tools.train_projector(
            args.algorithm,
            args.extractor,
            allow_missing_files=args.allow_missing_files,
            force=args.force)

    # project the features
    elif args.sub_task == 'project':
        tools.project(
            args.algorithm,
            args.extractor,
            groups=tools.groups(args),
            indices=biotools.indices(fs.preprocessed_data_list(groups=tools.groups(args)),
                                     None if args.grid is None else args.grid.number_of_projection_jobs),
            allow_missing_files=args.allow_missing_files,
            force=args.force)

    # compute scores
    elif args.sub_task == 'compute-scores':
        tools.compute_scores(
            args.algorithm,
            args.extractor,
            groups=[args.group],
            allow_missing_files=args.allow_missing_files,
            force=args.force,
            write_compressed=args.write_compressed_score_files)

    # Test if the keyword was processed
    else:
        return False
    return True


def detect_spoofing(args, command_line_parameters, external_fake_job_id=0):
    """This is the main entry point for computing anti-spoofing experiments.
    You just have to specify configurations for any of the steps of the toolchain, which are:
    -- the database
    -- the preprocessing
    -- feature extraction
    -- the anti-spoofing algorithm
    -- and the grid configuration (in case, the function should be executed in the grid).
    Additionally, you can skip parts of the toolchain by selecting proper --skip-... parameters.
    If your probe files are not too big, you can also specify the --preload-probes switch to speed up the score computation.
    If files should be re-generated, please specify the --force option (might be combined with the --skip-... options)."""

    # as the main entry point, check whether the sub-task is specified
    if args.sub_task is not None:
        # execute the desired sub-task
        if not execute(args):
            raise ValueError("The specified --sub-task '%s' is not known to the system" % args.sub_task)
        return {}
    else:
        # add jobs, path the first argument as the script to execute
        submitter = biotools.GridSubmission(args, command_line_parameters,
                                            executable='spoof.py',
                                            first_fake_job_id=external_fake_job_id)
        retval = add_jobs(args, submitter)
        tools.write_info(args, command_line_parameters, submitter.executable)

        if args.grid is not None:
            if args.grid.is_local() and args.run_local_scheduler:
                if args.dry_run:
                    print("Would have started the local scheduler to run the experiments with parallel jobs")
                else:
                    # start the jman local deamon
                    submitter.execute_local()
                return {}

            else:
                # return job ids as a dictionary
                return retval
        else:
            # not in a grid, execute tool chain sequentially
            if args.timer:
                logger.info("- Timer: Starting timer")
                start_time = os.times()
            # execute the list of jobs that we have added before
            for job in retval:
                # set comamnd line arguments
                args.sub_task = job[0]
                args.group = None if len(job) <= 1 else job[1]
                args.model_type = None if len(job) <= 2 else job[2]
                args.score_type = None if len(job) <= 3 else job[3]
                if not execute(args):
                    raise ValueError("The current --sub-task '%s' is not known to the system" % args.sub_task)

            if args.timer:
                end_time = os.times()
                logger.info("- Timer: Stopped timer")

                for t in args.timer:
                    index = {'real': 4, 'system': 1, 'user': 0}[t]
                    print("Elapsed", t, "time:", end_time[index] - start_time[index], "seconds")

            return {}


def main(command_line_parameters=None):
    """Executes the main function"""
    try:
        # do the command line parsing
        args = parse_arguments(command_line_parameters)
        # it's a hack to allow interpreting a commandline parameters passed as
        # a string, e.g., using form --groups=['dev', 'eval']
        # it is interpreted as a list of lists, so we remove the outer list wrapper
        if args.groups and isinstance(args.groups, list) and isinstance(args.groups[0], list):
            args.groups = args.groups[0]

        # perform anti-spoofing test
        detect_spoofing(args, command_line_parameters)
    except Exception as e:
        # track any exceptions as error logs (i.e., to get a time stamp)
        logger.error("During the execution, an exception was raised: %s" % e)
        raise


if __name__ == "__main__":
    main()
