import shutil
import os
import os.path as op
import tempfile
import logging as log
from tqdm import tqdm


def download_spm12(x, project_id=None, experiment_id=None,
        destdir=tempfile.gettempdir(), max_rows=5,
        overwrite=False, report_only=False):
    if project_id is None and experiment_id is None:
        log.error('project_id and experiment_id cannot be both None')
    elif not project_id is None and not experiment_id is None:
        log.error('project_id and experiment_id cannot be provided both')
    else:
        experiments = []
        if not experiment_id is None:
            experiments = [experiment_id]

        if not project_id is None:
            experiments = []
            for e in x.array.experiments(project_id=project_id, columns=['label']).data[:max_rows]:
                experiments.append(e['ID'])

        log.info('Now initiating download for %s experiments.'%len(experiments))
        for e in tqdm(experiments):
            log.debug(e)
            r = x.select.experiment(e).resource('SPM12_SEGMENT')
            if not r.exists():
                log.error('%s has no SPM12_SEGMENT resource'%e)
                continue
            dd = op.join(destdir, e)
            if op.isdir(dd) and not overwrite and not report_only:
                msg = '%s already exists. Skipping %s.'%(dd, e)
                log.error(msg)
            else:
                if op.isdir(dd) and overwrite and not report_only:
                    msg = '%s already exists. Overwriting %s.'%(dd, e)
                    log.warning(msg)
                    shutil.rmtree(dd)

                if not report_only:
                    os.mkdir(dd)
                    r.get(dest_dir=dd)

                r = x.select.experiment(e).resource('BBRC_VALIDATOR')
                pdf = {each.label():each for each in list(r.files()) \
                    if 'SPM12SegmentValidator' in each.label() and \
                    each.label().endswith('.pdf')}

                if not r.exists():
                    log.error('%s has no BBRC_VALIDATOR resource'%e)
                    continue
                if len(pdf.items()) == 0:
                    log.error('%s has no SPM12 Validation Report'%e)
                    continue

                assert(len(list(pdf.keys())) == 1)
                f = pdf[list(pdf.keys())[0]]
                fp = op.join(destdir, f.label()) if report_only \
                    else op.join(dd, f.label())
                if report_only:
                    log.debug('Saving it in %s.'%fp)
                f.get(dest=fp)

def download_freesurfer6(x, project_id=None, experiment_id=None,
        destdir=tempfile.gettempdir(), max_rows=5, overwrite=False, suffix=None):
    suffix2 = 'Hires' if suffix == '_HIRES' else ''

    if project_id is None and experiment_id is None:
        log.error('project_id and experiment_id cannot be both None')
    elif not project_id is None and not experiment_id is None:
        log.error('project_id and experiment_id cannot be provided both')
    else:
        experiments = []
        if not experiment_id is None:
            experiments = [experiment_id]

        if not project_id is None:
            experiments = []
            for e in x.array.experiments(project_id=project_id, columns=['label']).data[:max_rows]:
                experiments.append(e['ID'])

        log.info('Now initiating download for %s experiments.'%len(experiments))
        for e in tqdm(experiments):
            log.debug(e)
            r = x.select.experiment(e).resource('FREESURFER6%s'%suffix)
            if not r.exists():
                log.error('%s has no FREESURFER6%s resource'%(e, suffix))
                continue
            dd = op.join(destdir, e)
            if op.isdir(dd) and not overwrite:
                msg = '%s already exists. Skipping %s.'%(dd, e)
                log.error(msg)
            else:
                if op.isdir(dd) and overwrite:
                    msg = '%s already exists. Overwriting %s.'%(dd, e)
                    log.warning(msg)

                os.mkdir(dd)

                r.get(dest_dir=dd)
                r = x.select.experiment(e).resource('BBRC_VALIDATOR')
                pdf = {each.label():each for each in list(r.files()) \
                    if 'FreeSurfer%sValidator'%suffix2 in each.label() and \
                    each.label().endswith('.pdf')}

                if not r.exists():
                    log.error('%s has no BBRC_VALIDATOR resource'%e)
                    continue
                if len(pdf.items()) == 0:
                    log.error('%s has no FreeSurfer Validation Report'%e)
                    continue
                f = pdf[sorted(pdf.keys())[-1]]
                od = op.join(dd, f.label())
                f.get(dest=od)


def download_qmenta(x, project_id=None, experiment_id=None,
        destdir=tempfile.gettempdir(), max_rows=5, overwrite=False):

    if project_id is None and experiment_id is None:
        log.error('project_id and experiment_id cannot be both None')
    elif not project_id is None and not experiment_id is None:
        log.error('project_id and experiment_id cannot be provided both')
    else:
        experiments = []
        if not experiment_id is None:
            experiments = [experiment_id]

        if not project_id is None:
            experiments = []
            for e in x.array.experiments(project_id=project_id, columns=['label']).data[:max_rows]:
                experiments.append(e['ID'])

        log.info('Now initiating download for %s experiments.'%len(experiments))
        for e in tqdm(experiments):
            log.debug(e)
            r = x.select.experiment(e).resource('QMENTA_RESULTS')
            if not r.exists():
                log.error('%s has no QMENTA_RESULTS resource'%e)
                continue
            dd = op.join(destdir, e)
            if op.isdir(dd) and not overwrite:
                msg = '%s already exists. Skipping %s.'%(dd, e)
                log.error(msg)
            else:
                if op.isdir(dd) and overwrite:
                    msg = '%s already exists. Overwriting %s.'%(dd, e)
                    log.warning(msg)

                os.mkdir(dd)

                r.get(dest_dir=dd)
                r = x.select.experiment(e).resource('BBRC_VALIDATOR')
                pdf = {each.label():each for each in list(r.files()) \
                    if 'QMENTA' in each.label() and \
                    each.label().endswith('.pdf')}

                if not r.exists():
                    log.error('%s has no BBRC_VALIDATOR resource'%e)
                    continue
                if len(pdf.items()) == 0:
                    log.error('%s has no QMENTA Validation Report'%e)
                    continue
                f = pdf[sorted(pdf.keys())[-1]]
                od = op.join(dd, f.label())
                f.get(dest=od)
