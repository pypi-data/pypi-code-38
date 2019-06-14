from __future__ import (absolute_import, division, print_function, unicode_literals)

import logging
import os
import sys
import time
import traceback

import click

from .klass_convert import Convert
from .klass_date import Date
from .klass_operator import Operator
from .klass_path import Path
from .klass_queue import Pipeline
from .klass_str import Str
from .klass_yaml_config import YamlConfig


def __execute(logger, config, path, ctx):
    full_path = Path.find_file_path(path, config)
    if not os.path.isfile(full_path):
        assert os.path.isfile(full_path), "The file [%s] not found" % full_path
    try:
        exec(open(full_path).read(), ctx)
    except:
        logger.error(traceback.format_exc())
        logger.error('path: %s', full_path)
        sys.exit(-1)


def __load_connectors(logger, config, yaml, _params, context):
    connectors = yaml.get_data()['connectors']
    for name, klass_path in connectors.items():
        params = yaml.get_data().get('params', {}).get(name, {})
        params.update(_params.get(name, {}))
        if params.get('path'):
            param_path = Path.find_file_path(params['path'], config)
            params.update(dict(path=param_path))
        path, klass = klass_path.split('::')
        _ctx = context.copy()
        __execute(logger, config, path, _ctx)
        ctx_params = context.copy()
        ctx_params.update(params)
        ctx_params.update(dict(params=params))
        try:
            context[name] = _ctx[klass](**ctx_params).get
            _ctx[klass](**ctx_params).get()
        except:
            logger.error(traceback.format_exc())
            logger.error('can not open the stream [path=%s][class=%s]', path, klass)
            sys.exit(-1)


def __get_jobs_priorities(logger, config, yaml, _params, context, select, start, stop, tags):
    select = [int(x) for x in Operator.split_and_flat(',', select)]
    tags = Operator.split_and_flat(',', tags) if tags else []
    jobs = yaml.get_data()['jobs']
    result = {}
    priorities = {}
    for job in jobs:
        if tags and job.get('tag', None) not in tags:
            logger.warning('skip the job with tag=%s', job.get('tag', None))
            continue
        if not job.get('active', True):
            logger.warning('skip the job with active=%s', job.get('active'))
            continue
        priority = job.get('priority', 1)
        if select and priority not in select:
            continue
        if start and priority < start:
            continue
        if stop and priority > stop:
            continue
        threads = job.get('threads', 1)
        priorities.setdefault(priority, 0)
        priorities[priority] += threads
        result.setdefault(priority, [])
        get_klass_method = job.pop('extract')
        load_klass_method = job.pop('load')
        transform_klass_method = job.pop('transform')
        error_klass_method = job.pop('error')
        [e_path, e_klass], e_method = get_klass_method.split('::'), 'extract'
        [l_path, l_klass], l_method = load_klass_method.split('::'), 'load'
        [t_path, t_klass], t_method = transform_klass_method.split('::'), 'transform'
        [r_path, r_klass], r_method = error_klass_method.split('::'), 'error'
        limit = job.get('limit', 0)
        offset = job.get('offset', 0)
        domain = job.get('domain', [])
        ctx = context.copy()
        __execute(logger, config, e_path, ctx)
        __execute(logger, config, l_path, ctx)
        __execute(logger, config, t_path, ctx)
        __execute(logger, config, r_path, ctx)
        job_ctx = context.copy()
        job_ctx.update(_params)
        job_ctx.update(job)
        job_ctx.update(dict(domain=domain, offset=0, limit=0))
        if limit:
            step = limit
            try:
                count = ctx[e_klass](**job_ctx).count()
                logger.info('receiver: the count from [%s] is [%s] item(s)', e_klass, count)
            except:
                logger.error(traceback.format_exc())
                logger.error('path: %s', e_path)
                sys.exit(-1)
            while offset < count:
                job_ctx.update(dict(domain=domain, offset=offset, limit=limit))
                offset += step
                extract_method = getattr(ctx[e_klass](**job_ctx), e_method)
                transform_method = getattr(ctx[t_klass](**job_ctx), t_method)
                load_method = getattr(ctx[l_klass](**job_ctx), l_method)
                error_method = getattr(ctx[r_klass](**job_ctx), r_method)
                result[priority].append([extract_method, transform_method, load_method, error_method])
        else:
            extract_method = getattr(ctx[e_klass](**job_ctx), e_method)
            transform_method = getattr(ctx[t_klass](**job_ctx), t_method)
            load_method = getattr(ctx[l_klass](**job_ctx), l_method)
            error_method = getattr(ctx[r_klass](**job_ctx), r_method)
            result[priority].append([extract_method, transform_method, load_method, error_method])
    return result, priorities


@click.command()
@click.option('--logfile', '-l',
              type=click.Path(file_okay=True, dir_okay=False, writable=True, readable=True, resolve_path=True,
                              allow_dash=True), required=False, help='Logfile')
@click.option('--config', '-c',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True, readable=True,
                              resolve_path=True,
                              allow_dash=True), required=True, help='Configuration file to use')
@click.option('--params', '-p',
              type=click.Path(file_okay=True, dir_okay=False, writable=True, readable=True,
                              resolve_path=True,
                              allow_dash=True), required=False,
              help='Yaml file, keys are connector names and values are a mapping of parameters', )
@click.option('--log-level', type=click.Choice(['debug', 'info', 'warning', 'error']), default='info', required=True, )
@click.option('--start', type=click.INT, default=False, help='Start with which priority', )
@click.option('--stop', type=click.INT, default=False, help='Stop with which priority', )
@click.option('--select', '-s', type=click.STRING, nargs=1, multiple=True,
              help='Select priorities to process like 2,3,4', )
@click.option('--tags', '-t', type=click.STRING, default=False, help='Select tags to process like tag1,tag2,tag3', )
def cli_etl(logfile, config, params, log_level, start, stop, select, tags):
    """Command line Interface for ETL\n
    The yaml file of connector parameters contains the same information
    that can be given in the configuration file section 'params'
    """
    time_start = time.time()
    root_path = os.path.dirname(config)
    error_path = Path.create_dir(os.path.join(root_path, 'output', Date(fmt=Date.DATETIME_HASH_FORMAT).to_str()))
    os.chdir(root_path)
    if params:
        params = Path.find_file_path(params, config, raise_if_not_found=True)
        params = YamlConfig(params).get_data()
    else:
        params = {}
    yaml = YamlConfig(config)
    logger = logging.getLogger()
    logger.setLevel(log_level.upper())
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    context = {
        'logfile': logfile,
        'logger': logger,
        'config': config,
        'yaml': yaml,
        'error_path': error_path,
    }
    __load_connectors(logger, config, yaml, params, context)
    jobs, priorities = __get_jobs_priorities(logger, config, yaml, params, context, select, start, stop, tags)
    pipeline = Pipeline()
    pipeline.add_worker(name='Extract', maxsize=4)
    pipeline.add_worker(name='Transform', maxsize=4)
    pipeline.add_worker(name='Load', maxsize=4)
    pipeline.add_worker(name='Error', maxsize=1)
    pipeline.start()
    len_priorities = len(priorities)
    for i, (queue_priority, queue_threads) in enumerate(priorities.items(), 1):
        logger.info('receiver: global priorities progression %s/%s', i, len_priorities)
        len_queue_priority = len(jobs[queue_priority])
        queue_threads = min([queue_threads, len_queue_priority])
        index = 0
        while index < len_queue_priority:
            logger.info('receiver: stage priority=%s threads=%s %s-%s/%s', queue_priority, queue_threads, index,
                        queue_threads + index,
                        len_queue_priority)
            queue_data = []
            for i in range(queue_threads):
                queue_data.append((jobs[queue_priority][index], True))
                index += 1
            pipeline.put(queue_data)
            queue_threads = min([queue_threads, len(jobs[queue_priority][index:])])
    pipeline.stop()
    logger.info('all: migration completed [time=%s] [time=%s]',
                Str(Convert.time(time.time() - time_start, r=2), suffix='seconds'),
                Str(Convert.time(time.time() - time_start, to='M', r=2), suffix='minutes'))
    Path.clean_empty_dirs(root_path)
    if os.path.isdir(root_path):
        logger.info('all: output [%s]', root_path)
