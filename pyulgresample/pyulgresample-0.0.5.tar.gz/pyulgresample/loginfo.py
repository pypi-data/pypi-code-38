"""Get general ulog info."""
import pyulog
import numpy as np
import datetime
import warnings


def get_ulog(filepath, topics=None):
    """Read a ulg file from the given filepath and return it as a ulog structure.

    It can be that sometimes, topics are missing.
    Thus, check if the required topic are available in the ulog file.

    Arguments:
    filepath -- absoulte path to the .ulg file
    topics -- list of required topics

    """
    if topics:
        ulog = pyulog.ULog(filepath, topics)

        tmp = topics.copy()

        for topic in ulog.data_list:
            if topic.name in tmp:
                idx = tmp.index(topic.name)
                tmp.pop(idx)

        if len(tmp) > 0:
            warnings.warn(
                "The following topics do not exist: \n {0}".format(tmp)
            )
    else:
        ulog = pyulog.ULog(filepath)

    if not ulog.data_list:
        warnings.warn("No topics present.")

    return ulog


def mu2hms(musecond):
    """convert microsecond to hours:min:second (string)."""
    m1, s1 = divmod(int(musecond / 1e6), 60)
    h1, m1 = divmod(m1, 60)
    return "{:d}:{:02d}:{:02d}".format(h1, m1, s1)


def get_starttime(ulog):
    """Recover the start time stored in the ulog structure.

    Arguments:
    ulog -- messages stored in ulog structure

    """
    return mu2hms(ulog.start_timestamp)


def get_duration(ulog):
    """Compute the duration for which data was logged.

    Arguments:
    ulog -- messages stored in ulog structure

    """
    return mu2hms(ulog.last_timestamp - ulog.start_timestamp)


def get_param(ulog, parameter_name, default):
    """Recover a parameter from the ulog structure.

    Arguments:
    ulog -- messages stored in ulog structure
    parameter_name -- name of the parameter that should be recovered
    default -- default value that will be returned if the parameter is not available

    """
    if parameter_name in ulog.initial_parameters.keys():
        return ulog.initial_parameters[parameter_name]
    else:
        return default


def add_param(dfUlg, parameter_name):
    """add a parameter from the ulog structure to the dataframe.

    If parameters have changed, update them in the dataframe.

    Arguments:
    ulog -- messages stored in ulog structure
    parameter_name -- name of the parameter that should be recovered
    dataframe -- pandas dataframe which contains all messages of the required topics

    """
    dfUlg.df[parameter_name] = get_param(dfUlg.ulog, parameter_name, 0)

    if len(dfUlg.ulog.changed_parameters) > 0 and (
        parameter_name in [x[1] for x in dfUlg.ulog.changed_parameters]
    ):
        for time, name, value in dfUlg.ulog.changed_parameters:
            if name == parameter_name:
                dfUlg.df.loc[
                    (dfUlg.df.timestamp >= time), parameter_name
                ] = value

        dfUlg.df[parameter_name].fillna(method="ffill", inplace=True)
