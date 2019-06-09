# -*- coding: utf-8 -*-
from collections import OrderedDict
import os
from io import IOBase

import h5py
import yaml
import numpy as np
import pandas as pd

from .settings import *
from .io.file import flex_open, flex_out
from .core.get_gadgets import *
from .core.exceptions import *
from .core.verify import prompt_user, make_cli_function,\
                         check_experiment_list_in_ribo_handle
from ._version import (__format_version__,
                      __version__) 

###########################################################


class NORNASEQ(Exception):
    pass

###########################################################

@check_experiment_list_in_ribo_handle
def set_rnaseq(ribo_handle, name, rnaseq_df):
    """
    Set the rna-seq data

    Parameters
    ----------
    ribo_handle: h5py.File
        Open ribo file handle

    name: str
        Name of the experiment

    rnaseq_df: pd.DataFrame
        Index is the transcript names
        The first (and only) column has transcript expression values.

    Returns
    -------
    actual_rnaseq_df[0]: np.array
       Transcript expression array
    """

    rnaseq_datagroup  = ribo_handle[EXPERIMENTS_name][name]\
                           .require_group(RNASEQ_name)

    t_names = get_reference_names(ribo_handle)                       

    actual_rnaseq_df  = pd.DataFrame(np.zeros( len(t_names), 
                                               dtype = RNASEQ_DT ), 
                                      index = t_names )

    for transcript in rnaseq_df.index:
        actual_rnaseq_df.loc[transcript, 0] = rnaseq_df.loc[transcript, 0]

    rnaseq_dataset = rnaseq_datagroup.get(RNASEQ_name, None)

    if rnaseq_dataset:
        rnaseq_dataset[...] = actual_rnaseq_df.loc[: , 0]
    else:
        rnaseq_datagroup.create_dataset(
                                RNASEQ_name, 
                                shape       = (len(t_names),),
                                data        = actual_rnaseq_df[0],
                                dtype       = RNASEQ_DT,
                                compression = DEFAULT_COMPRESSION, 
                                fletcher32  = DEFAULT_FLETCHER32)
                                     
    return actual_rnaseq_df[0]

@make_cli_function
def set_rnaseq_wrapper(ribo_file, name, rnaseq_file, 
                       sep = "\t", force = True):
    """
    Wrapper for set_metadata.

    It makes sure that the provided transcript names
    are actually in the reference transcripts.

    See set_rnaseq for details,
    """
 
    with flex_open(rnaseq_file, "rt") as input_stream,\
         h5py.File(ribo_file, "r+") as ribo_handle:

        experiment_handle = ribo_handle[EXPERIMENTS_name][name]
        prompt_message    = "This will overwrite existing RNA-Seq data." 
        attr_exists       = \
           experiment_handle.get(RNASEQ_name , None) \
              and \
           experiment_handle[RNASEQ_name].get(RNASEQ_name, name)

        prompt_user( message     = prompt_message, 
                     attr_exists = attr_exists, 
                     force       = force)

        rnaseq_df = pd.read_csv(input_stream, 
                                    header    = None, 
                                    names     = [0], 
                                    index_col = 0, 
                                    sep       = sep )

        transcript_names = get_reference_names(ribo_handle)

        for t in rnaseq_df.index:
            if t not in transcript_names:
                print("Error: Invalid transcrpt name: {}".format(t))
                exit(1)

        set_rnaseq(ribo_handle = ribo_handle, 
                   name        = name, 
                   rnaseq_df   = rnaseq_df)
    



def _get_single_rna_seq(ribo_handle, name):
    """
    Helper function for get_rnaseq

    It return rnaseq data of a single experiment if exists
    """

    if not rnaseq_exists(ribo_handle, name):
        raise NORNASEQ("{} doesn't have RNA_seq data".format(name))

    rnaseq_np = ribo_handle[EXPERIMENTS_name]\
                    [name][RNASEQ_name][RNASEQ_name][...]
    ref_names = get_reference_names(ribo_handle)
    rnaseq_df = pd.DataFrame( rnaseq_np , 
                              index   = ref_names , 
                              columns = [name])

    return rnaseq_df


def _get_all_rna_seq(ribo_handle):
    """
    Helper function for get_rnaseq

    It return rnaseq data of a all experiments in the ribo file
    """

    has_rnaseq = False

    experiment_list = get_experiment_names(ribo_handle)
    rnaseq_df_list  = list()

    for experiment in experiment_list:
        if rnaseq_exists(ribo_handle, experiment):
            has_rnaseq = True
            rnaseq_df_list.append( _get_single_rna_seq(ribo_handle, experiment) )

    if not has_rnaseq:
        return None
    else:
        all_df = pd.concat(rnaseq_df_list, axis = 1)
        return all_df

@check_experiment_list_in_ribo_handle
def get_rnaseq(ribo_handle, name = None):
    """
    Returns rnaseq profile of the data if it exists

    Parameters
    ----------
    ribo_handle: h5py.File
        Open ribo file handle

    name: str
        Name of the experiment

    Returns
    -------
    rnaseq_df: pd.DataFrame 
        transcript expression table.
        Indices are transcript names
    """

    if not name:
        return _get_all_rna_seq(ribo_handle)
    else:
        return _get_single_rna_seq(ribo_handle, name)



@make_cli_function
def get_rnaseq_wrapper(ribo_file, name, output, sep = "\t"):
    """
    Wrapper for get_rnaseq
    """

    ribo_handle = h5py.File(ribo_file , "r")

    try:
        rnaseq_df = get_rnaseq(ribo_handle, name)
    except NORNASEQ as e:
        print(e)
        exit(1)

    out_str = rnaseq_df.to_csv(sep = sep, header = True)
 
    with flex_out(output) as output_stream:
        print(out_str, file = output_stream)
    
    ribo_handle.close()



@check_experiment_list_in_ribo_handle
def delete_rnaseq(ribo_handle, name):
    """
    Returns rnaseq profile of the data if it exists

    Parameters
    ----------
    ribo_handle: h5py.File
        Open ribo file handle

    name: str
        Name of the experiment

    Returns
    -------
    rnaseq_df: pd.DataFrame 
        transcript expression table.
        Indices are transcript names
    """

    if not rnaseq_exists(ribo_handle, name):
        raise NORNASEQ("{} doesn't have RNA_seq data".format(name))

    del ribo_handle[EXPERIMENTS_name][name][RNASEQ_name]


@make_cli_function
def delete_rnaseq_wrapper(ribo_file, name, force = True):
    """
    Wrapper for delete_rnaseq
    """

    prompt_message    = "This will delete existing RNA-Seq data."

    with h5py.File(ribo_file , "r+") as ribo_handle:
        attr_exists = rnaseq_exists(ribo_handle, name)
        prompt_user( message     = prompt_message, 
                     attr_exists = attr_exists, 
                     force       = force)
        delete_rnaseq(ribo_handle, name)





