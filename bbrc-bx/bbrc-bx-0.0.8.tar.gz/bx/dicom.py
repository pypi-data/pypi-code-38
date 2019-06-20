import pydicom
import logging as log
import tempfile
from tqdm import tqdm
import pandas as pd
import os.path as op
import os


def get_scandate(experiment_id, x, t1_scan_label='T1_ALFA1'):

    columns = ['xsiType', 'xnat:imagescandata/type', 'xnat:imagescandata/ID']
    scans = x.array.scans(experiment_id=experiment_id, columns=columns).data
    t1_scans = {e['xnat:imagescandata/id']:e for e in scans \
        if e['xnat:imagescandata/type'] == t1_scan_label}

    if len(t1_scans.items()) == 0:
        msg = 'No T1 found for %s: %s. Trying with all of them.'\
            %(experiment_id, [e['xnat:imagescandata/id'] for e in scans])
        log.warning(msg)
        t1_scans = {e['xnat:imagescandata/id']:e for e in scans \
            if not e['xnat:imagescandata/id'].startswith('OT-')\
            and not e['xnat:imagescandata/id'].startswith('O-')}


    max_nb = sorted(t1_scans.keys())[-1]
    log.debug('Found scan: %s'%max_nb)
    scan = x.select.experiment(experiment_id).scan(max_nb)

    f = list(scan.resource('DICOM').files())[0]
    fp = op.join(tempfile.gettempdir(), 'test.dcm')
    f.get(dest=fp)
    d = pydicom.read_file(fp)

    if hasattr(d, 'AcquisitionDate'):
        acquisition_date = d.AcquisitionDate
    else:
        acquisition_date = d.AcquisitionDateTime[:8]
    os.remove(fp)
    return acquisition_date

def collect_mrdates(x, project_id=None, experiment_id=None, max_rows=None,
        overwrite=False):

    def __create_table__(data):
        df = pd.DataFrame(data, columns=('ID', 'label', 'subject_label', 'scandate'))
        df['scandate'] = pd.to_datetime(df['scandate'])
        df = df.set_index('ID').sort_index()
        return df

    if project_id is None and experiment_id is None:
        log.error('project_id and experiment_id cannot be both None')
    elif not project_id is None and not experiment_id is None:
        log.error('project_id and experiment_id cannot be provided both')
    elif not experiment_id is None:
        res = get_scandate(experiment_id, x)
        return res

    elif not project_id is None:
        data = []
        columns = ['label', 'subject_ID', 'subject_label']
        for e in tqdm(x.array.experiments(project_id=project_id, columns=columns).data[:max_rows]):
            try:
                log.debug('Experiment ID: %s Subject label: %s'%(e['ID'], e['subject_label']))
                row = [e['ID'], e['label'], e['subject_label']]
                d = get_scandate(e['ID'], x)
                row.append(d)
                data.append(row)
            except KeyboardInterrupt:
                return __create_table__(data)
            except Exception as exc:
                log.error('Failed with %s. Skipping it. (%s)'%(e['ID'], exc))
                continue
        return __create_table__(data)
