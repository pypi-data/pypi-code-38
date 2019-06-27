
import os
from numina.user.cli import main


def enter_directory():
    workdir = "/home/spr/devel/guaix/pyemir/img_tut"
    os.chdir(workdir)


def create_datamanager(reqfile, basedir, datadir):
    import yaml
    from numina.user.clirundal import process_format_version_1, process_format_version_2
    from numina.user.clirundal import DataManager

    loaded_obs = []

    with open(reqfile, 'r') as fd:
        loaded_data = yaml.load(fd)

    loaded_data_extra = None

    control_format = loaded_data.get('version', 1)

    if control_format == 1:
        _backend = process_format_version_1(loaded_obs, loaded_data)
        datamanager = DataManager(basedir, datadir, _backend)
        datamanager.workdir_tmpl = "obsid{obsid}_work"
        datamanager.resultdir_tmpl = "obsid{obsid}_results"
        datamanager.serial_format = 'yaml'
        datamanager.result_file = 'result.yaml'
        datamanager.task_file = 'task.yaml'
    elif control_format == 2:
        _backend = process_format_version_2(loaded_obs, loaded_data)
        datamanager = DataManager(basedir, datadir, _backend)
    else:
        print('Unsupported format', control_format, 'in', reqfile)
        raise ValueError
    return datamanager


def run_job(datamanager, obid):
    print('calling run job')
    from numina.user.clirundal import DEFAULT_RECIPE_LOGGER

    # Directories with relevant data
    request = 'reduce'
    request_params = {}

    request_params['oblock_id'] = obid
    request_params["pipeline"] = 'default' #  args.pipe_name
    request_params["instrument_configuration"] = 'default'  # args.insconf
    request_params["intermediate_results"] = True
    request_params["copy_files"] = True

    logger_control = dict(
        default=DEFAULT_RECIPE_LOGGER,
        logfile='processing.log',
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        enabled=True
    )
    request_params['logger_control'] = logger_control

    task = datamanager.backend.new_task(request, request_params)

    run_task_reduce(datamanager, task)


def run_task_reduce(datamanager, task):
    print('calling run task, obid=', task.request_params['oblock_id'], "taskid=", task.id)
    from numina.user.clirundal import run_recipe, fully_qualified_name, working_directory
    import numina.exceptions
    from numina import __version__

    task.request_runinfo['runner'] = 'numina'
    task.request_runinfo['runner_version'] = __version__

    workenv = datamanager.create_workenv(task)

    task.request_runinfo["results_dir"] = workenv.resultsdir_rel
    task.request_runinfo["work_dir"] = workenv.workdir_rel
    # Roll back to cwd after leaving the context
    with working_directory(workenv.datadir):

        obsres = datamanager.backend.obsres_from_oblock_id(
            task.request_params['oblock_id'],
            configuration=task.request_params["instrument_configuration"]
        )

        pipe_name = task.request_params["pipeline"]
        obsres.pipeline = pipe_name
        recipe = datamanager.backend.search_recipe_from_ob(obsres)

        # Enable intermediate results by default
        recipe.intermediate_results = task.request_params["intermediate_results"]

        # Update runinfo
        recipe.runinfo['runner'] = task.request_runinfo['runner']
        recipe.runinfo['runner_version'] = task.request_runinfo['runner_version']
        recipe.runinfo['task_id'] = task.id
        recipe.runinfo['data_dir'] = workenv.datadir
        recipe.runinfo['work_dir'] = workenv.workdir
        recipe.runinfo['results_dir'] = workenv.resultsdir
        recipe.runinfo['intermediate_results'] = task.request_params["intermediate_results"]

        try:
            rinput = recipe.build_recipe_input(obsres, datamanager.backend)
        except (ValueError, numina.exceptions.ValidationError) as err:
            raise

    # Load recipe control and recipe parameters from file
    task.request_runinfo['instrument'] = obsres.instrument
    task.request_runinfo['mode'] = obsres.mode
    task.request_runinfo['recipe_class'] = recipe.__class__.__name__
    task.request_runinfo['recipe_fqn'] = fully_qualified_name(recipe.__class__)
    task.request_runinfo['recipe_version'] = recipe.__version__

    # Copy files
    workenv.sane_work()
    if task.request_params["copy_files"]:
        workenv.copyfiles_stage1(obsres)
        workenv.copyfiles_stage2(rinput)
        workenv.adapt_obsres(obsres)

    logger_control = task.request_params['logger_control']
    completed_task = run_recipe(recipe=recipe, task=task, rinput=rinput,
                                workenv=workenv, logger_control=logger_control)

    print('completed')
    datamanager.store_task(completed_task)


def read_obs(obsresult_doc, session=False):
    import yaml

    loaded_obs = []
    sessions = []
    if session:
        for obfile in obsresult_doc:

            with open(obfile) as fd:
                sess = yaml.load(fd)
                sessions.append(sess['session'])
    else:
        for obfile in obsresult_doc:

            with open(obfile) as fd:
                sess = []
                for doc in yaml.load_all(fd):
                    enabled = doc.get('enabled', True)
                    docid = doc['id']
                    requirements = doc.get('requirements', {})
                    sess.append(dict(id=docid, enabled=enabled,
                                     requirements=requirements))

                    loaded_obs.append(doc)

            sessions.append(sess)

    return sessions, loaded_obs


if __name__ == '__main__':

    enter_directory()

    class Args:
        pass

    args1 = Args()
    args1.session = False
    args1.obsresult = ['obs1.yaml']
    args1.reqs = 'control2.yaml'
    args1.reqs = 'control_dump.yaml'
    args1.profilepath = None
    args1.dump_control = True
    args1.basedir = '.'
    args1.datadir = 'data'
    args1.pipe_name = 'default'
    args1.insconf = 'default'
    args1.copy_files = True

    datamanager = create_datamanager(args1.reqs, args1.basedir, args1.datadir)

    sessions, loaded_obs = read_obs(args1.obsresult, session=args1.session)

    datamanager.backend.add_obs(loaded_obs)

    #for obid in range(111, 118):
    #    run_job(datamanager, obid)

    #for obid in range(121, 128):
    #    run_job(datamanager, obid)

    run_job(datamanager, 10101)

    if args1.dump_control:
        with open('control_dump.yaml', 'w') as fp:
            datamanager.backend.dump(fp)

