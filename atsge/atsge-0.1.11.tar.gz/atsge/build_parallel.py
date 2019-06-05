import sys
import logging

from atpbar import atpbar
from alphatwirl import concurrently
from alphatwirl.misc.deprecation import _deprecated

from alphatwirl.parallel import Parallel
from .SGEJobSubmitter import SGEJobSubmitter

##__________________________________________________________________||
def build_parallel(parallel_mode, quiet=True, processes=4, user_modules=[ ],
                   dispatcher_options={}, dropbox_options={}):

    dispatchers = ('subprocess', 'htcondor', 'sge')
    parallel_modes = ('multiprocessing', ) + dispatchers
    default_parallel_mode = 'multiprocessing'

    if not parallel_mode in parallel_modes:
        logger = logging.getLogger(__name__)
        logger.warning('unknown parallel_mode "{}", use default "{}"'.format(
            parallel_mode, default_parallel_mode
        ))
        parallel_mode = default_parallel_mode

    if parallel_mode == 'multiprocessing':
        return _build_parallel_multiprocessing(quiet=quiet, processes=processes)

    return build_parallel_dropbox(
        parallel_mode=parallel_mode,
        user_modules=user_modules,
        dispatcher_options=dispatcher_options,
        dropbox_options=dropbox_options,
    )

##__________________________________________________________________||
def build_parallel_dropbox(parallel_mode, user_modules,
                           dispatcher_options={},
                           dropbox_options={}):
    workingarea_topdir = '_ccsp_temp'
    python_modules = set(user_modules)
    python_modules.add('alphatwirl')
    python_modules.add('atpbar')
    workingarea_options = dict(topdir=workingarea_topdir, python_modules=python_modules)

    if parallel_mode == 'htcondor':
        dispatcher_class = concurrently.HTCondorJobSubmitter
    elif parallel_mode == 'sge':
        dispatcher_class = SGEJobSubmitter
    else:
        dispatcher_class = concurrently.SubprocessRunner

    return _build_parallel_dropbox_(
        workingarea_options, dropbox_options, dispatcher_class, dispatcher_options
    )

def _build_parallel_dropbox_(workingarea_options, dropbox_options,
                             dispatcher_class, dispatcher_options):

    workingarea = concurrently.WorkingArea(**workingarea_options)

    dispatcher = dispatcher_class(**dispatcher_options)

    dropbox_options.update(dict(workingArea=workingarea, dispatcher=dispatcher))
    dropbox = concurrently.TaskPackageDropbox(**dropbox_options)
    communicationChannel = concurrently.CommunicationChannel(dropbox=dropbox)

    return Parallel(None, communicationChannel, workingarea)

##__________________________________________________________________||
def _build_parallel_multiprocessing(quiet, processes):

    if processes is None or processes == 0:
        communicationChannel = concurrently.CommunicationChannel0(progressbar=not quiet)
    else:
        dropbox = concurrently.MultiprocessingDropbox(processes, progressbar=not quiet)
        communicationChannel = concurrently.CommunicationChannel(dropbox=dropbox)
    return Parallel(None, communicationChannel)

##__________________________________________________________________||

##__________________________________________________________________||
@_deprecated(msg='use alphatwirl.parallel.build.build_parallel() instead.')
def build_parallel_multiprocessing(quiet, processes):
    return build_parallel(
        parallel_mode='multiprocessing',
        quiet=quiet, processes=processes
    )

##__________________________________________________________________||
