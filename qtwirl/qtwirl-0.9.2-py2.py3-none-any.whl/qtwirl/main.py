# Tai Sakuma <tai.sakuma@gmail.com>
import functools

import alphatwirl

from ._parser.inputs import parse_data
from ._parser.readerconfig import expand_reader_config
from ._builder.func import build_reader, create_file_loaders, let_reader_read

##__________________________________________________________________||
__all__ = ['qtwirl']

##__________________________________________________________________||
def qtwirl(data, reader_cfg,
           tree_name=None,
           parallel_mode='multiprocessing',
           dispatcher_options=None,
           process=4, quiet=False,
           user_modules=None,
           max_events=-1, max_files=-1,
           max_events_per_process=-1, max_files_per_process=1,
           skip_error_files=True):
    """qtwirl (quick-twirl), one-function interface to alphatwirl

    Summarize event data in ``file`` in the way specified by
    ``reader_cfg`` and return the results.

    Parameters
    ----------
    data : str or list of str
        Input file path(s)
    reader_cfg : dict or list of dict
        Reader configuration
    parallel_mode : str, optional
        "multiprocessing" (default) or "htcondor"
    dispatcher_options : dict, optional
        Options to dispatcher
    process : int, optional
        The number of processes when ``parallel_mode`` is
        "multiprocessing"
    quiet : bool, optional
    user_modules : list, optional
        The names of modules to be sent to worker nodes when
        parallel_mode is "htcondor"
    max_events : int, optional
    max_files : int, optional
    max_events_per_process : int, optional
    max_files_per_process : int, optional
    skip_error_files, bool, default True

    Returns
    -------
    DataFrame or list of DataFrame
        Summary of event data

    """

    ##
    files = parse_data(data)

    ##
    reader_cfg = expand_reader_config(reader_cfg)
    reader = build_reader(reader_cfg)

    ##
    if dispatcher_options is None:
        dispatcher_options=dict()


    ##
    default_user_modules = ('qtwirl', 'alphatwirl')
    if user_modules is None:
        user_modules = ()
    user_modules = set(user_modules)
    user_modules.update(default_user_modules)

    ##
    parallel = alphatwirl.parallel.build_parallel(
        parallel_mode=parallel_mode, quiet=quiet,
        processes=process,
        user_modules=user_modules,
        dispatcher_options=dispatcher_options)
    func_create_file_loaders = functools.partial(
        create_file_loaders,
        tree_name=tree_name,
        max_events=max_events, max_events_per_run=max_events_per_process,
        max_files=max_files, max_files_per_run=max_files_per_process,
        check_files=True, skip_error_files=skip_error_files)
    read_files = functools.partial(
        let_reader_read, reader=reader, parallel=parallel,
        func_create_file_loaders=func_create_file_loaders)

    parallel.begin()
    ret = read_files(files=files)
    parallel.end()

    if isinstance(reader, alphatwirl.loop.ReaderComposite):
        ret = [r for r in ret if r is not None]
    return ret

##__________________________________________________________________||
