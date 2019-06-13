"""test_ulogconv."""
from context import ulogconv
from context import TopicMsgs
import pyulog
import pandas as pd
import numpy as np
from numpy.testing import assert_almost_equal


def test_createPandaDict():
    """test create dictionary of panda-topics."""
    file = "testlogs/position.ulg"
    topics = ["vehicle_local_position", "vehicle_attitude"]
    ulog = pyulog.ULog(file, topics)

    dp = ulogconv.create_pandadict(ulog)

    expected_names = {
        "T_vehicle_local_position_0": "T_vehicle_local_position_0",
        "T_vehicle_attitude_0": "T_vehicle_attitude_0",
    }

    for key in dp:
        assert key == expected_names[key]

        for name in dp[key].columns:
            if name != "timestamp":
                assert name[:2] == "F_"


def test_apply_zoh():
    """test zoh."""
    # zoh to msg_2
    msg1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    msg2 = [0, np.nan, 2, np.nan, 4, np.nan, np.nan, 7, 8, np.nan]
    df = pd.DataFrame(
        {"T_topic_1_0__F_msg_1": msg1, "T_topic_1_0__F_msg_2": msg2}
    )
    topicMsgsList = [TopicMsgs("topic_1", ["msg_2"])]
    ulogconv.apply_zoh(df, topicMsgsList)
    msg_2_expected = [0, 0, 2, 2, 4, 4, 4, 7, 8, 8]
    assert_almost_equal(msg_2_expected, df.T_topic_1_0__F_msg_2)

    # zoh to msg_1
    df = pd.DataFrame(
        {"T_topic_1_0__F_msg_1": msg1, "T_topic_1_0__F_msg_2": msg2}
    )
    topicMsgsList = [TopicMsgs("topic_1", ["msg_1"])]
    ulogconv.apply_zoh(df, topicMsgsList)
    msg_1_expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert_almost_equal(msg_1_expected, df.T_topic_1_0__F_msg_1)

    # zoh to all msgs
    msg3 = [0, np.nan, np.nan, np.nan, 6, np.nan, np.nan, 7, np.nan, np.nan]
    msg_3_expected = [0, 0, 0, 0, 6, 6, 6, 7, 7, 7]
    df = pd.DataFrame(
        {
            "T_topic_1_0__F_msg_1": msg1,
            "T_topic_1_0__F_msg_2": msg2,
            "T_topic_1_0__F_msg_3": msg3,
        }
    )
    topicMsgsList = [TopicMsgs("topic_1", [])]
    ulogconv.apply_zoh(df, topicMsgsList)
    assert_almost_equal(msg_1_expected, df.T_topic_1_0__F_msg_1)
    assert_almost_equal(msg_2_expected, df.T_topic_1_0__F_msg_2)
    assert_almost_equal(msg_3_expected, df.T_topic_1_0__F_msg_3)

    # zoh if first is nan
    msg4 = [np.nan, np.nan, 2, 3, 4, 5, np.nan, np.nan, 8, 9]
    msg_4_expected = [np.nan, np.nan, 2, 3, 4, 5, 5, 5, 8, 9]
    df = pd.DataFrame(
        {
            "T_topic_1_0__F_msg_1": msg1,
            "T_topic_1_0__F_msg_2": msg2,
            "T_topic_1_0__F_msg_3": msg3,
            "T_topic_1_0__F_msg_4": msg4,
        }
    )
    topicMsgsList = [TopicMsgs("topic_1", ["msg_4"])]
    ulogconv.apply_zoh(df, topicMsgsList)
    assert_almost_equal(msg_4_expected, df.T_topic_1_0__F_msg_4)

    # zoh if inf is present
    msg5 = [np.inf, np.nan, 2, 3, 4, 5, np.inf, np.nan, 8, 9]
    msg_5_expected = [np.inf, np.inf, 2, 3, 4, 5, np.inf, np.inf, 8, 9]
    df = pd.DataFrame(
        {
            "T_topic_1_0__F_msg_1": msg1,
            "T_topic_1_0__F_msg_2": msg2,
            "T_topic_1_0__F_msg_3": msg3,
            "T_topic_1_0__F_msg_4": msg4,
            "T_topic_1_0__F_msg_5": msg5,
        }
    )
    topicMsgsList = [TopicMsgs("topic_1", ["msg_5"])]
    ulogconv.apply_zoh(df, topicMsgsList)
    assert_almost_equal(msg_5_expected, df.T_topic_1_0__F_msg_5)


def test_replace_nan_with_inf():
    """test replace nan with inf."""
    file = "testlogs/position.ulg"
    topics = ["vehicle_local_position", "vehicle_attitude"]
    nan_msg = [np.nan, 2, 4, np.nan, np.nan, 5]
    inf_msg = [np.inf, 2, 4, np.inf, np.inf, 5]
    ulog = pyulog.ULog(file, topics)
    ulog.data_list[0].data["fake_msg_0"] = np.array(nan_msg)
    ulog.data_list[1].data["fake_msg_0"] = np.array(nan_msg)

    topic_msgs_list = [
        TopicMsgs("vehicle_local_position", ["fake_msg_0"]),
        TopicMsgs("vehicle_attitude", ["fake_msg_0"]),
    ]

    ulogconv.replace_nan_with_inf(ulog, topic_msgs_list)
    assert_almost_equal(ulog.data_list[0].data["fake_msg_0"], inf_msg)
    assert_almost_equal(ulog.data_list[1].data["fake_msg_0"], inf_msg)
