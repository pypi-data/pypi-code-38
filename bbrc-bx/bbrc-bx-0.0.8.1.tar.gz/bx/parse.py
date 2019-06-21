import pandas as pd
import json
import os.path as op
import os
import tempfile
import argparse
from datetime import datetime

from .validation import validation_scores
from .download import *
from .measurements import *
from .dicom import *


class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            msg = "readable_dir:{0} is not a valid path".format(prospective_dir)
            raise argparse.ArgumentTypeError(msg)
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            msg = "readable_dir:{0} is not a readable dir".format(prospective_dir)
            raise argparse.ArgumentTypeError(msg)

def check_xnat_item(a, x):
    projects = [e.label() for e in list(x.select.projects())]
    experiments = []
    for p in projects:
        exp = x.array.experiments(project_id=p).data
        experiments.extend([e['ID'] for e in exp])

    if a in projects:
        return 0
    elif a in experiments:
        return 1
    else:
        return -1


def parse_args(command, args, x, destdir=tempfile.gettempdir(), overwrite=False,
        test=False):
    max_rows = 1 if test else None
    commands = ['nifti', 'mrdates', 'freesurfer6', 'spm12', 'freesurfer6_hires',
        'qmenta']
    if command not in commands:
        msg = '%s not found (valid commands: %s)'%(command, commands)
        log.info(msg)
        raise Exception(msg)
    log.debug('Command: %s'%command)

    if command == 'mrdates':
        if len(args) == 0:
            msg = 'display help message for %s'%command
            log.info(msg)
        elif len(args) == 1:
            a = args[0] #should be a project or an experiment_id
            t = check_xnat_item(a, x)
            if t == 0:
                log.debug('Project detected: %s'%a)
                df = collect_mrdates(x, project_id=a, max_rows=max_rows)
                if destdir == None:
                    destdir = tempfile.gettempdir()

                dt = datetime.today().strftime('%Y%m%d_%H%M%S')
                fn = 'bx_%s_%s_%s.xlsx'%(command, a, dt)
                fp = op.join(destdir, fn)
                log.info('Saving it in %s'%fp)
                df.to_excel(fp)

            elif t == 1:
                log.debug('Experiment detected: %s'%a)
                sd = collect_mrdates(x, experiment_id=a)
                print(sd)
                log.info('Scan date: %s'%sd)
            else:
                log.error('No project/experiment found: %s'%a)


    elif command.startswith('freesurfer6'):
        known_suffixes = ['_HIRES', '_SUBFIELDS']
        suffix = ''
        if '_' in command:
            suffix = '_%s'%command.split('_')[1].upper()
            if not suffix in known_suffixes:
                print('%s not known (known suffixes: %s)'
                    %(command, known_suffixes))

        if len(args) == 0:
            msg = 'display help message for %s'%command
            print(msg)
        elif len(args) == 1:
            # error: missing arguments (at least a project)
            msg = 'missing argument(s)'
            print(msg)
        elif len(args) == 2:
            subcommand = args[0]
            a = args[1] #should be a project or an experiment_id
            print(a)
            t = check_xnat_item(a, x)
            if subcommand in ['aparc', 'aseg', 'hippoSfVolumes']:
                max_rows = 25 if test else None

                if t == 0:
                    df = freesurfer6_measurements(x, subcommand, project_id=a,
                        max_rows=max_rows, suffix=suffix)
                elif t == 1:
                    df = freesurfer6_measurements(x, subcommand, experiment_id=a,
                        suffix=suffix)
                else:
                    log.error('No project/experiment found: %s'%a)

                if t != -1:
                    dt = datetime.today().strftime('%Y%m%d_%H%M%S')
                    fn = 'bx_%s_%s_%s_%s.xlsx'%(command, subcommand, a, dt)
                    fp = op.join(destdir, fn)
                    log.info('Saving it in %s'%fp)
                    df.to_excel(fp)

            elif subcommand == 'files':
                if t == 0:
                    log.debug('Project detected: %s'%a)
                    download_freesurfer6(x, project_id=a, destdir=destdir,
                        max_rows=max_rows, overwrite=overwrite, suffix=suffix)
                elif t == 1:
                    log.debug('Experiment detected: %s'%a)
                    download_freesurfer6(x, experiment_id=a, destdir=destdir,
                        overwrite=overwrite, suffix=suffix)
                else:
                    log.error('No project/experiment found: %s'%a)


    elif command == 'spm12':
        if len(args) == 0:
            msg = 'display help message for %s'%command
            log.info(msg)
        elif len(args) == 1:
            # error: missing arguments (at least a project)
            msg = 'missing argument(s)'
            log.info(msg)
        elif len(args) == 2:
            subcommand = args[0]
            a = args[1] #should be a project or an experiment_id
            log.info(a)
            t = check_xnat_item(a, x)
            if subcommand in ['files', 'report']:
                report_only = subcommand == 'report'
                if t == 0:
                    log.debug('Project detected: %s'%a)
                    download_spm12(x, project_id=a, destdir=destdir,
                        max_rows=max_rows, overwrite=overwrite,
                        report_only=report_only)
                elif t == 1:
                    log.debug('Experiment detected: %s'%a)
                    download_spm12(x, experiment_id=a, destdir=destdir,
                        overwrite=overwrite, report_only=report_only)
                else:
                    log.error('No project/experiment found: %s'%a)

            elif subcommand == 'volumes':
                if t == 0:
                    log.debug('Project detected: %s'%a)
                    df = spm12_volumes(x, project_id=a, max_rows=max_rows)
                elif t == 1:
                    log.debug('Experiment detected: %s'%a)
                    df = spm12_volumes(x, experiment_id=a)
                else:
                    log.error('No project/experiment found: %s'%a)
                if t != -1:

                    dt = datetime.today().strftime('%Y%m%d_%H%M%S')
                    fn = 'bx_%s_%s_%s_%s.xlsx'%(command, subcommand, a, dt)
                    fp = op.join(destdir, fn)
                    log.info('Saving it in %s'%fp)
                    df.to_excel(fp)

            elif subcommand == 'tests':
                if t == 0:
                    log.debug('Project detected: %s'%a)
                    df = validation_scores(x, validator='SPM12SegmentValidator',
                        project_id=a, version=['##0390c55f', '2bc4d861'], max_rows=max_rows)
                elif t == 1:
                    log.debug('Experiment detected: %s'%a)
                    df = validation_scores(x, validator='SPM12SegmentValidator',
                        experiment_id=a, version=['##0390c55f', '2bc4d861'])

                if t != -1:
                    dt = datetime.today().strftime('%Y%m%d_%H%M%S')
                    fn = 'bx_%s_%s_%s_%s.xlsx'%(command, subcommand, a, dt)
                    fp = op.join(destdir, fn)
                    log.info('Saving it in %s'%fp)
                    df.to_excel(fp)

    elif command.startswith('qmenta'):
        if len(args) == 0:
            msg = 'display help message for %s'%command
            print(msg)
        elif len(args) == 1:
            # error: missing arguments (at least a project)
            msg = 'missing argument(s)'
            print(msg)
        elif len(args) == 2:
            subcommand = args[0]
            a = args[1] #should be a project or an experiment_id
            print(a)
            t = check_xnat_item(a, x)
            if subcommand == 'files':
                if t == 0:
                    log.debug('Project detected: %s'%a)
                    download_qmenta(x, project_id=a, destdir=destdir,
                        max_rows=max_rows, overwrite=overwrite)
                elif t == 1:
                    log.debug('Experiment detected: %s'%a)
                    download_qmenta(x, experiment_id=a, destdir=destdir,
                        overwrite=overwrite)
                else:
                    log.error('No project/experiment found: %s'%a)

    elif command == 'nifti':
        if len(args) == 0:
            msg = 'display help message for %s'%command
            print(msg)
        elif len(args) == 1:
            # error: missing arguments (at least a project)
            msg = 'missing argument(s)'
            print(msg)
        elif len(args) == 2:
            _type = args[0]
            a = args[1] #should be a project or an experiment_id
            print(a)
            t = check_xnat_item(a, x)



def create_parser():
    import argparse
    cfgfile = op.join(op.expanduser('~'), '.xnat.cfg')
    parser = argparse.ArgumentParser(description='bx')
    parser.add_argument('command', help='BX command')
    parser.add_argument('args', help='BX command', nargs="*")
    parser.add_argument('--config', help='XNAT configuration file',
        required=False, type=argparse.FileType('r'), default=cfgfile)
    parser.add_argument('--dest', help='Destination folder',
        required=False, action=readable_dir)
    parser.add_argument('--verbose', '-V', action='store_true', default=False,
        help='Display verbosal information (optional)', required=False)
    parser.add_argument('--overwrite', '-O', action='store_true', default=False,
        help='Overwrite', required=False)
    return parser
