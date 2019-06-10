import os
import json
import glob
import re
import math
import click
import asyncio
import aiofiles
import aiohttp
import functools
import logging
import sys

from multiprocessing import Pool
from datetime import datetime
from girder_client import GirderClient

from edp.composite.parser.exp import parse_exp
from edp.composite.parser.ana_rcp import parse_ana_rcp
from edp.composite.parser.rawlen import parse_rawlen
from edp.composite.parser.csv import parse_csv
from edp.composite.parser.sample import parse_sample

log = logging.getLogger('EDP')

scalars_to_extract = [
    'Emin.Vrhe',
    'Emax.Vrhe',
    'Jmin.mAcm2',
    'Jmax.mAcm2',
    'I.A_ave',
    'Eta.V_ave',
    'Eta(V)',
    'Ewe(V)',
    'Ach(V)',
    'I(A)',
    't(s)'
]

class AsyncGirderClient(object):

    def __init__(self, api_url, session):
        self._ratelimit_semaphore = asyncio.Semaphore(5)
        self._api_url = api_url.rstrip('/')
        self._session = session

    async def authenticate(self, api_key):
        params = [('key', api_key)]
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post('%s/api_key/token' % (self._api_url), params=params) as r:
                auth = await r.json()
            self._headers = {
                'Girder-Token': auth['authToken']['token']
                }

    async def post(self, path, json=None, *pargs, **kwargs):
        async with self._ratelimit_semaphore:
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                async with session.post('%s/%s' % (self._api_url, path),
                                        headers=self._headers, json=json) as r:
                    return await r.json()


    async def get(self, path, params=None, *pargs, **kwargs):
        async with self._ratelimit_semaphore:
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                async with session.post('%s/%s' % (self._api_url, path),
                                        headers=self._headers, json=json) as r:
                    return await r.json()


def _compute_run_parameters(parameters, techniques):
    vref_regex = re.compile(r'(.*)_vref')

    for technique in techniques:
        # compute is_dark
        tech_params = parameters['techniques'][technique]

        tech_params['is_dark'] = 'toggle_dark_time_init' not in tech_params or \
            tech_params['toggle_dark_time_init'] > 100.0

        reference_vrhe = parameters['reference_vrhe']
        # compute *_vrhe values
        new_params = {}
        for key, value in tech_params.items():
            match = vref_regex.match(key)
            if match:
                prefix = match.group(1)
                new_params['%s_vrhe' % prefix] = value - reference_vrhe

        tech_params.update(new_params)
        # Finally calculate min_potential_vref and min_potential_vref for all
        # CV* techniques
        if technique.startswith('CV'):
            potentials = []
            for k in ['init_potential_vrhe', 'first_potential_vrhe',
                      'second_potential_vrhe',  'final_potential_vrhe']:

                value = tech_params.get(k)
                if value is not None:
                    potentials.append(value)

            tech_params['min_potential_vref'] = min(potentials)
            tech_params['max_potential_vref'] = max(potentials)

    return parameters

def _coerce_values_to_float(d):
    converted = {}

    for key, value in d.items():
        try:
            converted[key] = float(value)
        except (TypeError, ValueError):
            converted[key] = value

    return converted

runint_regex = re.compile(r'run__(\d+)')
technique_file_regex = re.compile('files_technique__(.*)')
async def _ingest_run(gc, project, composite, rcp_files, experiment, run):
    # Extract out the techniques this run used
    rcp_file = run['rcp_file']
    for f in rcp_files:
        if f.endswith(rcp_file):
            run_file = f
            break

    technique_files = {}
    techniques = []
    for key, value in run.items():
        if key.startswith('files_technique__'):
            match = technique_file_regex.match(key)
            technique = match.group(1)
            techniques.append(technique)
            run_dir = os.path.dirname(run_file)
            technique_files[technique] = [os.path.join(run_dir, f) for f in value['pstat_files'].keys()]

    parameters = _coerce_values_to_float(run['parameters'])
    # Now extract the parameters for these techniques
    tech_parameters = parameters.setdefault('techniques', {})
    for technique in techniques:
        tech_param_key = 'echem_params__%s' % technique
        if tech_param_key in parameters:
            tech_parameters[technique] = _coerce_values_to_float(parameters[tech_param_key])

    # Now remove any used technique parameters
    parameters = {k: v for k, v in parameters.items() if not k.startswith('echem_params__')}

    _compute_run_parameters(parameters, techniques)

    # Extract the runint for sample matching
    match = runint_regex.match(run['run_key'])
    if match:
        run_int = int(match.group(1))
    else:
        raise click.ClickException('Unable to extract runint: %s' % run['run_key'])

    log.info('Ingesting run: %s' % run_file)

    run = {
        'runId': rcp_file,
        'name': run['name'],
        #'runPath': run['run_path'],
        'solutionPh': parameters['solution_ph'],
        'plateId': parameters['plate_id'],
        'electrolyte': parameters['electrolyte'],
        'parameters': parameters
    }
    run = await gc.post('edp/projects/%s/composites/%s/runs' % (project, composite), json=run)
    run['sampleFiles'] = technique_files
    experiment[run_int] = run

    log.info('Ingested run %s' % rcp_file)

async def _ingest_runs(gc, project, composite, dir):
    runint_regex = re.compile(r'run__(\d+)')
    # Find the exp file
    exp_paths = glob.glob('%s/**/*.exp' % dir, recursive=True)

    experiments = {}
    tasks = []
    for exp_path in exp_paths:
        async with aiofiles.open(exp_path, mode='r') as f:
            contents = await f.read()
        exp = parse_exp(contents)
        name = exp['name']
        experiment = experiments.setdefault(name, {})

        rcp_files = glob.glob( '%s/**/*.rcp' % dir, recursive=True)
        # for now only look at eche
        runs = [r for r in exp['runs'] if r['parameters']['experiment_type'] == 'eche']
        for run in runs:
            task = asyncio.create_task(_ingest_run(gc, project, composite, rcp_files, experiment, run))
            tasks.append(task)

    await asyncio.gather(*tasks)

    return experiments

async def _create_fom(gc, project, composite, name, value, sample_id, run_id, analysis):
    fom = {
        'name': name,
        'value': value,
        'sampleId': sample_id,
        'runId': run_id,
        'analysisId': analysis['_id']
    }

    await gc.post('edp/projects/%s/composites/%s/samples/%s/fom'
                  % (project, composite, sample_id), json=fom)

sample_regex = re.compile('.*ana__.*__run__(\d+)_.*_(.*)_rawlen.txt')
async def _process_rawlen_file(timeseries_data, sample_file):
    log.info('Ingesting %s' % sample_file)
    match = sample_regex.match(sample_file)
    technique = match.group(2)
    async with aiofiles.open(sample_file, mode='r') as f:
        contents = await f.read()
    timeseries = parse_rawlen(contents)
    timeseries_data.update(
        {key.replace('.', '\\u002e'):value for (key,value) in timeseries.items()}
    )


async def _process_rawlen_files(gc, project, composite, sample, run_id, sample_files):
    timeseries_data = {}
    tasks = []
    for sample_file in sample_files:
        tasks.append(asycio.create_task(_process_rawlen_file(timeseries_data, sample_file)))

    await asyncio.gather(*tasks)

    timeseries = {
        'data': timeseries_data,
        'runId': run_id,
        'technique': technique
    }
    timeseries = await gc.post(
        'edp/projects/%s/composites/%s/samples/%s/timeseries'
        % (project, composite, sample['_id']), json=timeseries)

async def _ingest_sample(gc, project, composite, runint, plate_id, sample_number,
                         platemaps, compositions, samples, runs, i):

    plate_id = int(plate_id)
    platemap = platemaps.setdefault(plate_id, {
        'plateId': plate_id,
        'elements': set()
    })
    run_id = runs[runint]['_id']
    log.info('Ingesting sample %s on plate %s' % (sample_number, plate_id))
    if sample_number not in samples.setdefault(plate_id, {}):
        sample_meta = samples.setdefault(plate_id, {}).setdefault(sample_number, {})
        sample_meta['sampleNum'] = sample_number
        sample_meta['plateId'] = plate_id

        comp = {
            'elements': [],
            'amounts': []
        }
        sample_meta['composition'] = comp
        nan_comp = False
        for key, value in compositions.items():
            comp_value = value['values'][i]

            # If we encounter a NAN then don't enforce the
            if math.isnan(comp_value):
                log.info('Encounter NAN for composition value.')
                nan_comp = True

            if comp_value > 0:
                element = value['element']
                comp['elements'].append(element)
                comp['amounts'].append(comp_value)
                platemap['elements'].add(element)

        if not nan_comp and sum(comp['amounts']) <  0.999:
            raise click.ClickException('Composite values don\'t add up to 1, for sample: %s' % sample_number)

        sample = await gc.post('edp/projects/%s/composites/%s/samples'
                               % (project, composite), json=sample_meta)

        samples.setdefault(plate_id, {})[sample_number] = sample

        # Now look up time series data
        glob_path = '%s/**/ana__*__Sample%d_*_*_rawlen.txt' % (dir, sample_number)
        sample_files = glob.glob(glob_path, recursive=True)

        if sample_files:
            await _process_rawlen_files(gc, project, composite, sample, run_id, sample_files)

    log.info('Ingested sample %d on plate %d' % (sample_number, plate_id))

async def _ingest_loading(gc, project, composite, dir, loading_file, platemaps, samples, runs):
    comp_regex = re.compile('([a-zA-Z]+)\.PM.AtFrac')
    sample_regex = re.compile('.*ana__.*__run__(\d+)__(.*)_rawlen.txt')

    [file_path] = glob.glob('%s/**/%s' % (dir, loading_file), recursive=True)
    log.info('Ingesting: %s' % file_path)

    async with aiofiles.open(file_path, mode='r') as f:
        contents = await f.read()
    loading = parse_csv(contents)

    sample_numbers = loading['sample_no']
    plate_ids = loading['plate_id']
    runints = loading['runint']
    compositions = {}
    for key, value in loading.items():
        match = comp_regex.match(key)
        if match:
            compositions[key] = {
                'element': match.group(1).lower(),
                'values': value
            }

    tasks = []
    for i, (runint, plate_id, sample_number) in enumerate(zip(runints, plate_ids, sample_numbers)):
        tasks.append(asyncio.create_task(_ingest_sample(gc, project, composite,
                                                       runint, plate_id,
                                                       sample_number, platemaps,
                                                       compositions, samples, runs, i)))

    await asyncio.gather(*tasks)

    return samples

async def _create_timeseries(gc, project, composite, timeseries_data, technique, sample_number, run, samples):
    timeseries = {
        'data': timeseries_data,
        'runId': run['_id'],
        'technique': technique
    }
    sample = samples[run['plateId']][sample_number]

    await gc.post(
            'edp/projects/%s/composites/%s/samples/%s/timeseries'
            % (project, composite, sample['_id']), json=timeseries)


async def _ingest_run_data(gc, project, composite, experiments, samples):
    # Now process the files associated with the runs in this experiment
    sample_regex = re.compile(r'Sample(\d+)_.*._(.*)\.txt')

    for _, experiment in experiments.items():
        for run in experiment.values():
            run_timeseries = {}
            for technique, technique_files  in run['sampleFiles'].items():
                technique_files = run['sampleFiles'][technique]
                for file_path in technique_files:
                    log.info('Ingesting: %s' % file_path)
                    match = sample_regex.match(os.path.basename(file_path))
                    if not match:
                        raise Exception('Unable to extract sample number.')
                    sample_number = int(match.group(1))

                    if sample_number not in samples[run['plateId']]:
                        log.info('Sample %s not in map.' % sample_number)
                        continue

                    timeseries_data = run_timeseries.setdefault(sample_number, {})
                    async with aiofiles.open(file_path, mode='rb') as f:
                        contents = await f.read()
                    s = parse_sample(contents.decode())
                    for key, value in s.items():
                        if key in scalars_to_extract:
                            key =  key.replace('.', '\\u002e')
                            timeseries_data[key] = value

            tasks = []
            for sample_number, timeseries_data in run_timeseries.items():
                tasks.append(asyncio.create_task(
                    _create_timeseries(gc, project, composite, timeseries_data, technique,
                                       sample_number, run, samples)))

            await asyncio.gather(*tasks)

async def _ingest_fom_file(gc, project, composite, fom_file, analysis, samples, runs):
    log.info('Ingesting %s' % fom_file)
    fom_excludes = ['sample_no', 'runint', 'plate_id', 'csv_version', 'plot_parameters']

    async with aiofiles.open(fom_file, mode='r') as f:
        contents = await f.read()

    fom = parse_csv(contents)

    plate_ids = fom['plate_id']
    sample_numbers = fom['sample_no']
    runints = fom['runint']

    for exclude in fom_excludes:
        if exclude in fom:
            del fom[exclude]

    for i, (runint, plate_id, sample_no) in enumerate(zip(runints, plate_ids, sample_numbers)):
        for fom_name in fom:
            sample = samples[plate_id][sample_no]
            await _create_fom(gc, project, composite, fom_name, float(fom[fom_name][i]),
                              sample['_id'], runs[runint]['_id'], analysis)

async def _create_analysis(gc, project, composite, timestamp, name, type, index, technique, plate_ids):
    analysis = {
        'timestamp': datetime.strptime(timestamp, '%Y%m%d.%H%M%S').isoformat(),
        'name': name,
        'type': type,
        'technique': technique,
        'index': index,
        'plateIds': plate_ids
    }

    return await gc.post('edp/projects/%s/composites/%s/analyses'
                         % (project, composite), json=analysis)

ana_regex = re.compile(r'ana__(\d+)')
async def _ingest_ana(gc, project, composite, dir, experiments, ana_file, platemaps, samples):
    ana_dir = os.path.dirname(ana_file)

    async with aiofiles.open(ana_file, mode='r') as f:
        contents = await f.read()

    ana = parse_ana_rcp(contents)

    experiment_name = ana['experiment_name']
    runs = experiments[experiment_name]
    loading_files_to_process = []
    fom_files_to_process = []
    ana_name = ana['name']
    plate_ids = ana['plate_ids']
    analysis_type = ana['analysis_type']

    for key, value in ana.items():
        match = ana_regex.match(key)
        if match:
            analysis_index = int(match.group(1))
            [file_path] = value['files_multi_run']['fom_files'].keys()
            technique = value.get('technique')
            analysis_name = value['name']
            analysis_name = analysis_name.partition('__')[2] if '__' in analysis_name else analysis_name

            analysis = await _create_analysis(gc, project, composite, ana_name,
                                              analysis_name, analysis_type, analysis_index,
                                              technique, plate_ids)

            if file_path.endswith('Loading.csv'):
                loading_files_to_process.append(file_path)
            else:
                [file_path] = glob.glob('%s/**/%s' % (ana_dir, file_path), recursive=True)
                fom_files_to_process.append((file_path, analysis))

    # Ingest the loading files to create the samples
    tasks = []
    for file_path in loading_files_to_process:
        tasks.append(
            asyncio.create_task(
                _ingest_loading(gc, project, composite, ana_dir,
                                file_path, platemaps, samples, runs)))
    await asyncio.gather(*tasks)

    # Now ingest the other FOM files
    tasks = []
    for (fom_file, analysis) in fom_files_to_process:
        if not fom_file.endswith('pc__1.csv'):
            tasks.append(
                asyncio.create_task(
                    _ingest_fom_file(gc, project, composite, fom_file,
                                     analysis, samples, runs)))
    await asyncio.gather(*tasks)

async def _ingest_samples(gc, project, composite, dir, experiments):
    ana_files = glob.glob('%s/**/*.ana' % dir, recursive=True)

    samples = {}
    platemaps = {}

    # We process these in order, as the Loading files might be duplicated
    # across analyses.
    for ana_file in ana_files:
        await _ingest_ana(gc, project, composite, dir,
                          experiments, ana_file, platemaps, samples)
        log.info('Ingested %s' % ana_file)

    tasks = []
    for platemap in platemaps.values():
        platemap['elements'] = list(platemap['elements'])
        tasks.append(
            asyncio.create_task(
                gc.post('edp/projects/%s/composites/%s/platemaps' % (project, composite),
                        json=platemap)))
    await asyncio.gather(*tasks)

    return samples

async def ingest(project, dir, api_url, api_key):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    dir  = os.path.abspath(dir)
    composite_name = os.path.basename(dir)
    composite = {
        'name': composite_name
    }

    async with aiohttp.ClientSession() as session:
        gc = AsyncGirderClient(api_url, session)
        await gc.authenticate(api_key)
        composite = await gc.post('edp/projects/%s/composites' % (project), json=composite)
        composite = composite['_id']
        experiments = await _ingest_runs(gc, project, composite, dir)

        samples = await _ingest_samples(gc, project, composite, dir, experiments)

        await _ingest_run_data(gc, project, composite, experiments, samples)
