import nibabel as nib
import logging as log
import tempfile
import numpy as np
from tqdm import tqdm
import pandas as pd
import os


def spm12_volumes(x, project_id=None, experiment_id=None, max_rows=None,
        overwrite=False):

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
        table = []
        for e in tqdm(experiments[:max_rows]):
            log.debug(e)
            try:
                r = x.select.experiment(e).resource('SPM12_SEGMENT')
                if not r.exists():
                    log.error('%s has no SPM12_SEGMENT resource'%e)
                    continue
                vols = [e]
                for kls in ['c1', 'c2', 'c3']:
                    f = [each for each in r.files() if each.id().startswith(kls)][0]
                    fp = tempfile.mkstemp('.nii.gz')[1]
                    f.get(fp)
                    d = nib.load(fp)
                    size = np.prod(d.header['pixdim'].tolist()[:4])
                    v = np.sum(d.dataobj) * size
                    os.remove(fp)
                    vols.append(v)
                table.append(vols)
            except KeyboardInterrupt:
                return pd.DataFrame(table, columns=['ID', 'c1', 'c2', 'c3']).set_index('ID').sort_index()
            except Exception as exc:
                log.error('Failed for %s. Skipping it.'%e)
                log.error(exc)
                continue
        df = pd.DataFrame(table, columns=['ID', 'c1', 'c2', 'c3']).set_index('ID').sort_index()
        return df


def freesurfer6_measurements(x, func, project_id=None, experiment_id=None,
        max_rows=None, overwrite=False, suffix=None):

    if project_id is None and experiment_id is None:
        log.error('project_id and experiment_id cannot be both None')
    elif not project_id is None and not experiment_id is None:
        log.error('project_id and experiment_id cannot be provided both')
    else:
        experiments = []
        columns = ['label', 'subject_ID', 'subject_label']

        if not experiment_id is None:
            experiments = [x.array.experiments(experiment_id=experiment_id,
                columns=columns).data[0]]

        if not project_id is None:
            experiments = []
            for e in x.array.experiments(project_id=project_id,
                    columns=columns).data[:max_rows]:
                experiments.append(e)
        table = []
        for e in tqdm(experiments[:max_rows]):
            log.debug(e)
            try:
                s = e['subject_label']
                r = x.select.experiment(e['ID']).resource('FREESURFER6%s'%suffix)
                if not r.exists():
                    log.error('%s has no FREESURFER6%s resource'%(e, suffix))
                    continue
                if func == 'aparc':
                    volumes = r.aparc()
                elif func == 'aseg':
                    volumes = r.aseg()
                elif func == 'hippoSfVolumes':
                    volumes = r.hippoSfVolumes(mode='T1')
                volumes['subject'] = s
                volumes['ID'] = e['ID']
                table.append(volumes)
            except KeyboardInterrupt:
                return pd.concat(table).set_index('ID').sort_index()
            except Exception as exc:
                log.error('Failed for %s. Skipping it.'%e)
                log.error(exc)
                continue
        hippoSfVolumes = pd.concat(table).set_index('ID').sort_index()
        return hippoSfVolumes
