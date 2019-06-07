# Tai Sakuma <tai.sakuma@gmail.com>
import os
import copy
import collections
import functools

import pandas as pd

import alphatwirl
from alphatwirl.roottree.inspect import get_entries_in_tree_in_file
from alphatwirl.loop.splitfuncs import create_files_start_length_list
from alphatwirl.loop.merge import merge_in_order

from .._misc import is_dict

##__________________________________________________________________||
def build_reader(cfg):
    """build a reader based on a configuration

    Parameters
    ----------
    cfg : dict or list of dicts
        Reader configuration (in its full form)

    Returns
    -------
    object
        A reader, which, for example, can be given to ``EventLoop`` of
        AlphaTwirl

    """
    if is_dict(cfg):
        return _build_single_reader(cfg)

    # cfg is a list
    readers = [_build_single_reader(c) for c in cfg]
    ret = alphatwirl.loop.ReaderComposite(readers=readers)
    return ret

def _build_single_reader(cfg):
    # cfg is a dict with one item
    key, val = list(cfg.items())[0]
    if key == 'table_cfg':
        return build_reader_for_table_config(val)
    elif key == 'selection_cfg':
        return build_reader_for_selection_config(val)
    elif key == 'reader':
        return val
    else:
        # TODO: produce warnings here
        return None

##__________________________________________________________________||
def build_reader_for_selection_config(cfg):
    if cfg['count'] is True:
        ret = alphatwirl.selection.build_selection(
            path_cfg=cfg['condition'],
            AllClass=alphatwirl.selection.modules.AllwCount,
            AnyClass=alphatwirl.selection.modules.AnywCount,
            NotClass=alphatwirl.selection.modules.NotwCount
        )
        ret.collector = build_collector_for_selection_config(cfg)
    else:
        ret = alphatwirl.selection.build_selection(path_cfg=cfg['condition'])
    return ret

def build_collector_for_selection_config(cfg):
    columns = ('depth', 'class', 'name', 'pass', 'total')
    if cfg['store_file'] is True:
        return functools.partial(
            to_dataframe_store_file,
            columns=columns, path=cfg['file_path'])
    else:
        return functools.partial(to_dataframe, columns=columns)

##__________________________________________________________________||
def build_reader_for_table_config(cfg):

    ## binnings: replace None with Echo with no next func
    ## TODO: this feature should be included in KeyValueComposer
    ## https://github.com/alphatwirl/alphatwirl/issues/49
    echo = alphatwirl.binning.Echo(nextFunc=None)
    binnings = cfg['key_binning']
    if binnings:
        binnings = tuple(b if b else echo for b in binnings)

    ##
    keyValComposer = alphatwirl.summary.KeyValueComposer(
        keyAttrNames=cfg['key_name'],
        binnings=binnings,
        keyIndices=cfg['key_index'],
        valAttrNames=cfg['val_name'],
        valIndices=cfg['val_index']
    )

    ##
    nextKeyComposer = alphatwirl.summary.NextKeyComposer(binnings) if binnings is not None else None

    ##
    summarizer = alphatwirl.summary.Summarizer(Summary=cfg['agg_class'])

    ##
    collector = build_collector_for_table_config(cfg)

    ##
    reader = alphatwirl.summary.Reader(
        keyValComposer=keyValComposer,
        summarizer=summarizer,
        collector=collector,
        nextKeyComposer=nextKeyComposer,
        weightCalculator=cfg['weight'],
        nevents=cfg['nevents']
    )
    return reader

##__________________________________________________________________||
def build_collector_for_table_config(cfg):
    columns = cfg['key_out_name'] + cfg['agg_name']
    if cfg['store_file'] is True:
        return functools.partial(
            to_dataframe_store_file,
            columns=columns, path=cfg['file_path'])
    else:
        return functools.partial(to_dataframe, columns=columns)

##__________________________________________________________________||
def to_dataframe_store_file(reader, columns, path):
    tuple_list = reader.results().to_tuple_list()

    if tuple_list is None:
        tuple_list = [ ]

    tuple_list_with_header = [columns] + tuple_list

    dir_ = os.path.dirname(path)
    alphatwirl.misc.mkdir_p(dir_)
    with open(path, 'w') as f:
        content = alphatwirl.misc.list_to_aligned_text(tuple_list_with_header)
        f.write(content)

    return pd.DataFrame(tuple_list, columns=columns)

def to_dataframe(reader, columns):
    tuple_list = reader.results().to_tuple_list()
    if tuple_list is None:
        tuple_list = [ ]
    return pd.DataFrame(tuple_list, columns=columns)

##__________________________________________________________________||
def create_file_loaders(
        files, tree_name,
        max_events=-1, max_events_per_run=-1,
        max_files=-1, max_files_per_run=1,
        check_files=True, skip_error_files=False):

        func_get_nevents_in_file = functools.partial(
            get_entries_in_tree_in_file,
            tree_name=tree_name,
            raises=not skip_error_files
        )

        files_start_length_list = create_files_start_length_list(
            files,
            func_get_nevents_in_file=func_get_nevents_in_file,
            max_events=max_events,
            max_events_per_run=max_events_per_run,
            max_files=max_files,
            max_files_per_run=max_files_per_run
        )
        # list of (files, start, length), e.g.,
        # [
        #     (['A.root'], 0, 80),
        #     (['A.root', 'B.root'], 80, 80),
        #     (['B.root'], 60, 80),
        #     (['B.root', 'C.root'], 140, 80),
        #     (['C.root'], 20, 10)
        # ]

        ret = [ ]
        for files, start, length in files_start_length_list:
            config = dict(
                events_class=alphatwirl.roottree.BEvents,
                file_paths=files,
                tree_name=tree_name,
                max_events=length,
                start=start,
                check_files=check_files,
                skip_error_files=skip_error_files,
            )
            ret.append(alphatwirl.roottree.BuildEvents(config))
        return ret

##__________________________________________________________________||
def let_reader_read(files, reader, parallel, func_create_file_loaders):
    eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(parallel.communicationChannel)
    eventLoopRunner.begin()

    file_loaders = func_create_file_loaders(files)
    njobs = len(file_loaders)
    eventLoops = [ ]
    for i, file_loader in enumerate(file_loaders):
        reader_copy = copy.deepcopy(reader)
        eventLoop = alphatwirl.loop.EventLoop(file_loader, reader_copy, '{} / {}'.format(i, njobs))
        eventLoops.append(eventLoop)
    runids = eventLoopRunner.run_multiple(eventLoops)
    # e.g., [0, 1, 2]

    runid_reader_map = collections.OrderedDict([(i, None) for i in runids])
    # e.g., OrderedDict([(0, None), (1, None), (2, None)])

    runids_towait = runids[:]
    while runids_towait:
        runid, reader_returned = eventLoopRunner.receive_one()
        merge_in_order(runid_reader_map, runid, reader_returned)
        runids_towait.remove(runid)

    if runid_reader_map:
        # assert 1 == len(runid_reader_map)
        reader = list(runid_reader_map.values())[0]
    return reader.collect()

##__________________________________________________________________||
