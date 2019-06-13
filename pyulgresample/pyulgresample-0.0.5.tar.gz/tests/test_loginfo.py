"""test_loginfo."""
from context import loginfo
from context import DfUlg
import pytest
import warnings
from numpy.testing import assert_almost_equal


def test_get_ulog_wrong_topic():
    """test for get_ulog.

    If a topic is provided which does not exist, then raise a user warning.
    """
    file = "testlgs/position.ulg"
    topics = ["vehicle_local_position", "vv"]

    warnings.simplefilter("error")  # turn warning into exception

    with pytest.raises(Exception):
        loginfo.get_ulog(file, topics)


def test_no_topic_present():
    """test if no topic is present."""
    file = "testlogs/position.ulg"
    topics = ["vv"]
    warnings.simplefilter("error")  # turn warning into exception

    with pytest.raises(Exception):
        loginfo.get_ulog(file, topics)


def test_get_ulog():
    """test get_ulog as expected."""
    file = "testlogs/position.ulg"
    topics = ["vehicle_local_position"]
    # should have valid topics
    ulog = loginfo.get_ulog(file, topics)
    assert ulog.data_list is not None
    # should have valid topics
    ulog = loginfo.get_ulog(file)
    assert ulog.data_list is not None


def test_ulog_getters():
    """test simple getters."""
    file = "testlogs/position.ulg"
    ulog = loginfo.get_ulog(file)
    starttime = loginfo.get_starttime(ulog)
    assert starttime == "0:00:01"

    duration = loginfo.get_duration(ulog)
    assert duration == "0:01:01"

    mpc_xy_p = loginfo.get_param(ulog, "MPC_XY_P", 0)
    assert_almost_equal(mpc_xy_p, 0.8)


def test_add_parameter():
    """test add parameter to dataframe."""
    file = "testlogs/parameterchange.ulg"
    lm = DfUlg.create(
        filepath=file,
        topics=["vehicle_local_position", "vehicle_local_position_setpoint"],
    )

    # we should have three different groups
    loginfo.add_param(lm, "MPC_YAW_MODE")
    group = lm.df.groupby("MPC_YAW_MODE")
    assert group.ngroups == 3

    # should have two values of MPC_YAW_EXPO
    loginfo.add_param(lm, "MPC_YAW_EXPO")
    group = lm.df.groupby("MPC_YAW_EXPO")
    assert group.ngroups == 2

    # should have only one value for MPC_XY_P
    loginfo.add_param(lm, "MPC_XY_P")
    group = lm.df.groupby("MPC_XY_P")
    assert group.ngroups == 1

    # you can find the parameter changes from ulog: lm.ulog.changed_parameters
    # between 34 and 48.5 seconds, we should have MPC_YAW_MODE 1
    assert all(
        lm.df[
            (lm.df["timestamp"] * 1e-6 > 34.0)
            & (lm.df["timestamp"] * 1e-6 < 48.0)
        ]["MPC_YAW_MODE"]
        == 1
    )

    # between 49 and 53.5 seconds, MPC_YAW_MODE should be 3
    assert all(
        lm.df[
            (lm.df["timestamp"] * 1e-6 > 49)
            & (lm.df["timestamp"] * 1e-6 < 53.5)
        ]["MPC_YAW_MODE"]
        == 3
    )

    # between 54 to then end, MPC_YAW_MODE equal 0
    assert all(lm.df[(lm.df["timestamp"] * 1e-6 > 54.1)]["MPC_YAW_MODE"] == 0)
