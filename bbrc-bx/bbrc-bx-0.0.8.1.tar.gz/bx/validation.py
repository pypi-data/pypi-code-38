import logging as log
import os.path as op
from tqdm import tqdm

def collect_reports(xnat_instance, experiments,
        validator_name='ArchivingValidator', version=['toto']):
    import json
    url = '/data/experiments/%s/resources/BBRC_VALIDATOR/files/%s'
    reports = {}

    for e in tqdm(experiments):
        exp = xnat_instance.array.experiments(experiment_id=e,
                                             columns = ['ID',
                                                        'label',
                                                        'xsiType']
                                             ).data
        assert(len(exp)==1)
        uri = url%(exp[0]['ID'], '%s_%s.json'%(validator_name, exp[0]['label']))
        r = xnat_instance.select.experiment(e).resource('BBRC_VALIDATOR')
        if not r.exists(): continue
        f = r.file('%s_%s.json'%(validator_name, exp[0]['label']))
        if not f.exists(): continue

        j = json.loads(xnat_instance.get(f._uri).text)
        if 'version' not in j.keys():
            log.warning('Version not found in report %s'%j.keys())
            continue
        if j['version'] not in version: continue
        fields = list(j.keys())
        try:
            for each in ['version', 'generated', 'experiment_id']:
                fields.remove(each)
        except ValueError:
            msg = 'No valid report found (%s).'%e
            log.error(msg)
            raise Exception(msg)
        if j['version'] not in  version: continue
        reports[e] = j

    return reports

def validation_scores(x, validator, version,  experiment_id=None, project_id=None, max_rows=None):
    import traceback
    if project_id is None and experiment_id is None:
        log.error('project_id and experiment_id cannot be both None')
    elif not project_id is None and not experiment_id is None:
        log.error('project_id and experiment_id cannot be provided both')
    else:
        experiments = []
        if not experiment_id is None:
            experiments = [experiment_id]

        if not project_id is None:
            experiments = [e.id() for e in\
                list(x.select.project(project_id).experiments())]

        res = []
        fields = []
        log.info('Looking for experiments with %s report with versions %s.'%(validator, version))
        reports = dict(list(collect_reports(x, validator_name=validator, experiments=experiments, version=version).items())[:max_rows])
        print(reports)
        log.info('Now initiating download for %s experiment(s).'%len(reports.items()))

        for e, report in tqdm(reports.items()):
            fields = list(report.keys())
            for each in ['version', 'generated', 'experiment_id']:
                fields.remove(each)
            row = [e]
            row.extend([report[f]['has_passed'] for f in fields])
            res.append(row)

        import pandas as pd
        fields.insert(0, 'ID')
        df = pd.DataFrame(res, columns=fields).set_index('ID')
        return df
