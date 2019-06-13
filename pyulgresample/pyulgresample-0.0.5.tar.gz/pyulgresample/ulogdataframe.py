"""Create dataframe from .ulg file and convert it to other structures.

Read required topics.
Create ulog structure from .ulg file.
Create pandas dataframe

"""
import os
from pyulgresample import loginfo
from pyulgresample import ulogconv as conv
import numpy as np


class TopicMsgs:
    """Store topic messages."""

    def __init__(self, topic, msgs):
        """Initialization.

        Arguments:
        topic -- topic that is used to generate dataframe and ulog
        msgs -- list of messages from the corresponding topic

        """
        self.topic = topic
        self.msgs = msgs


class DfUlg:
    """Class that contains ulog-structure and pandas-dataframe for a set of topics.

    Check .ulg file.
    Read required topics.
    Create new data structures.

    """

    def __init__(self, df, ulog, topics):
        """Initialization.

        Arguments:
        df -- pandas dataframe with uORB msgs from topics (resampled)
        ulog -- pyulog struct of uORB msgs (without resampling)
        topics -- list of topics that are used to generate df and ulog

        """
        self.df = df  # pandas dataframe
        self.ulog = ulog  # ulog
        self.topics = topics  # uorb topics

    @classmethod
    def _check_file(self, filepath):
        """Check if file is a .ulg file.

        Arguments:
            filepath -- path to .ulg-file

        """
        if os.path.isfile(filepath):
            base, ext = os.path.splitext(filepath)
            if ext.lower() not in (".ulg"):
                raise Exception("File is not .ulg file")
        else:
            raise Exception("File does not exist")

    @classmethod
    def create(
        cls,
        filepath,
        topics=None,
        zoh_topic_msgs_list=None,
        nan_topic_msgs_list=None,
    ):
        """Factory method. Create a DfUlg object.

        By default, the merge-method uses linear interpolation for resampling.
        Dataframe (df) is a pandas-dataframe with index equal to the merged timestamps. Each column represents a message-field.
        For instance, the thrust-field of the message vehicle_local_position_setpoint message would be named as follow:
            T_vehicle_local_position_setpoint_0__F_thrust_x
        if the field x of vehicle_local_position_setpoint is a scalar or
            T_vehicle_local_position_setpoint_0__F_x_0
        if the field x is an array, where the 0 represents the index of the array.
        The T stands for topic, which indicates the beginning of the topic. In this example, the topcic name is vehicle_local_position_setpoint.
        The topic name is followed by a number, which indicates the topic instance. If there is only one instance of a specific topic, then this number will be 0.
        The instance number is followed by two underlines and a capital letter F, which stands for field. In the example above, the field in question is x.

        Arguments:
        filepath -- path to .ulg file

        Keyword arguments:
        nan_topic_msgs_list -- list of TopicMsgs which contain Nan-values
        zoh_topic_msgs_list -- list of TopicMsgs on which zero-order-hold interpolation is used

        """
        # check if valid file is provided
        cls._check_file(filepath)

        ulog = loginfo.get_ulog(filepath, topics)

        if ulog is None:
            raise Exception("Ulog is empty")

        # replace nan with inf
        # this is needed because inf-values are considered as numerical values and therefore are not interpolated below
        if nan_topic_msgs_list:
            conv.replace_nan_with_inf(ulog, nan_topic_msgs_list)

        # create pandadict
        pandadict = conv.create_pandadict(ulog)

        # merge pandadict to a complete pandaframe
        df = conv.merge_pandadict(pandadict)

        # apply zero order hold
        if zoh_topic_msgs_list:
            conv.apply_zoh(df, zoh_topic_msgs_list)

        # we also apply zoh for msgs, which contain nan
        # TODO: this is just for the time being until a better solution is found
        if nan_topic_msgs_list:
            conv.apply_zoh(df, nan_topic_msgs_list)

        # linearly interpolate
        # only NaN values get interpolated, and therefore the zero order hold values from before do not get overwritten
        df.interpolate(mehtod="linear", inplace=True)

        # after interpolation, we can replace the inf-values back to nan-values
        df.replace(np.inf, np.nan, inplace=True)

        # add seconds
        df["timestamp_s"] = (df.timestamp - df.timestamp[0]) * 1e-6
        return cls(df, ulog, topics)
