"""Convert ulog file to different data structure."""
import pyulog
import pandas as pd
import re
import numpy as np


def create_pandadict(ULog):
    """Convert ulog to dictionary of topic based panda-dataframes.

    Rename topic-name such that each topic starts with `T_` and ends with instance ID.
    i.e. vehicle_local_position and instance 0 -> T_vehicle_local_position_0
    rename topic-fields such that vector indicices are replaced with underline and each field starts
    with letter F for denoting fields
    i.e.: fieldmsg[0] -> F_fieldmsg_0; fieldmsg[1] -> F_fieldmsg_1

    Arguments:
    ULog -- ulog object

    """
    # column replacement
    col_rename = {"[": "_", "]": "", ".": "_"}
    col_rename_pattern = re.compile(
        r"(" + "|".join([re.escape(key) for key in col_rename.keys()]) + r")"
    )

    pandadict = {}
    for msg in ULog.data_list:
        msg_data = pd.DataFrame.from_dict(msg.data)
        msg_data.columns = [
            col_rename_pattern.sub(lambda x: col_rename[x.group()], col)
            for col in msg_data.columns
        ]

        ncol = {}
        for col in msg_data.columns:
            if col == "timestamp":
                ncol[col] = col
            else:
                ncol[col] = "F_" + col
        msg_data.rename(columns=ncol, inplace=True)
        msg_data.index = pd.TimedeltaIndex(
            msg_data["timestamp"] * 1e3, unit="ns"
        )
        pandadict["T_{:s}_{:d}".format(msg.name, msg.multi_id)] = msg_data

    return pandadict


def replace_nan_with_inf(ulog, topic_msgs_list):
    """Replace nan-values with inf-values.

    Arguments:
    pandadict -- a dictionary of pandas dataframe with keys equal to topics
    topic_msgs_list -- list of topicMsgs on which zero-order-hold interpolation is used

    """
    for topic_msgs in topic_msgs_list:
        for ulogtopic in ulog.data_list:
            if ulogtopic.name == topic_msgs.topic:
                if topic_msgs.msgs:
                    for msg in topic_msgs.msgs:
                        nan_ind = np.isnan(ulogtopic.data[msg])
                        ulogtopic.data[msg][nan_ind] = np.inf
                else:
                    for msg in ulogtopic.data.keys():
                        nan_ind = np.isnan(ulogtopic.data[msg])
                        ulogtopic.data[msg][nan_ind] = np.inf


def merge_pandadict(pandadict):
    """Merge all dataframes within dictionanry.

    Arguments:
    pandadict -- a dictionary of pandas dataframe

    """
    combine_topic_fieldname(pandadict)
    skip = True
    for topic in pandadict:
        if skip:
            m = pandadict[topic]
            skip = False
        else:
            m = pd.merge_ordered(
                m, pandadict[topic], on="timestamp", how="outer"
            )
    m.index = pd.TimedeltaIndex(m.timestamp * 1e3, unit="ns")
    return m


def apply_zoh(df, topic_msgs_list):
    """Apply zero-order-hold to msgs.

    Arguments:
    df -- dataframe of all msgs
    topic_msgs_list -- list of topicMsgs on which zoh is going to be applied
    """
    for topicMsgs in topic_msgs_list:
        regex = topicMsgs.topic + ".+"
        if topicMsgs.msgs:
            regex = regex + "["
            for msg in topicMsgs.msgs:
                regex = "{0}({1})".format(regex, msg)
            regex = regex + "]"
        df[list(df.filter(regex=regex).columns)] = df[
            list(df.filter(regex=regex).columns)
        ].fillna(method="ffill")


def combine_topic_fieldname(pandadict):
    """Add topic name to field-name except for timestamp field.

    Arguments:
    pandadict -- a dictionary of pandas dataframe

    """
    for topic in pandadict.keys():
        ncol = {}
        for col in pandadict[topic].columns:
            if col == "timestamp":
                ncol[col] = col
            else:
                ncol[col] = topic + "__" + col
        pandadict[topic].rename(columns=ncol, inplace=True)
    return
