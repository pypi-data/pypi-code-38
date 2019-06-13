"""Create dataframe with messages required to run global position tests.

Store topics required for global position tests.
Add missing messages to the dataframe which are required for global position tests.

"""
import pandas as pd
import numpy as np
import argparse
import os
import pyulog
from pyulgresample import ulogconv as conv
from pyulgresample import mathpandas as mpd
from pyulgresample import loginfo
from pyulgresample.ulogdataframe import DfUlg, TopicMsgs

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

parser = argparse.ArgumentParser(
    description="Script to process global position"
)
parser.add_argument("filename", metavar="file.ulg", help="ulog file")


def apply_UTM_constraints(df):
    """Only keep entries that fulfill UTM constraints.

    Arguments:
    df -- dataframe containing messages from the required topics

    """
    # only consider dataframe where global reference is provided
    # xy_global is True if xy_global == 1, False if xy_global == 0
    df = df[  # xy_global needs to be true
        (df["T_vehicle_local_position_0__F_xy_global"] > 0.1)
        & (  # z_global needs to be true
            df["T_vehicle_local_position_0__F_z_global"] > 0.1
        )
        & (  # lat needs to be larger than -80  TODO is that correct?
            df["T_vehicle_global_position_0__F_lat"] >= -80
        )
        & (  # lat needs to be smaller than 84 TODO is that correct?
            df["T_vehicle_global_position_0__F_lat"] <= 80
        )
        & (  # lon needs to be larger than -180
            df["T_vehicle_global_position_0__F_lon"] >= -180
        )
        & (  # lon needs to be smaller than 180
            df["T_vehicle_global_position_0__F_lon"] <= 180
        )
        & (  # lat needs to be larger than -80
            df["T_position_setpoint_triplet_0__F_current_lat"] >= -80
        )
        & (  # lat needs to be smaller than 84
            df["T_position_setpoint_triplet_0__F_current_lat"] <= 80
        )
        & (  # lon needs to be larger than -180
            df["T_position_setpoint_triplet_0__F_current_lon"] >= -180
        )
        & (  # lon needs to be smaller than 180
            df["T_position_setpoint_triplet_0__F_current_lon"] <= 180
        )
    ]
    return df


def add_UTM_from_global_target_setpoin(df):
    """Convert data from global target setpoint to UTM and add that to the dataframe.

    Arguments:
    df -- dataframe containing messages from the required topics

    """
    easting, northing, zone = mpd.series_utm(
        df["T_position_setpoint_triplet_0__F_current_lat"],
        df["T_position_setpoint_triplet_0__F_current_lon"],
    )

    df["T_position_setpoint_triplet_0__NF_current_easting"] = easting.values
    df["T_position_setpoint_triplet_0__NF_current_northing"] = northing.values
    df["T_position_setpoint_triplet_0__NF_current_zone"] = zone.values


def add_UTM_from_reference(df):
    """Convert data from reference to UTM and add that to the dataframe.

    Arguments:
    df -- dataframe containing messages from the required topics

    """
    easting, northing, zone = mpd.series_utm(
        df["T_vehicle_local_position_0__F_ref_lat"],
        df["T_vehicle_local_position_0__F_ref_lon"],
    )

    df["T_vehicle_local_position_0__NF_ref_easting"] = easting.values
    df["T_vehicle_local_position_0__NF_ref_northing"] = northing.values
    df["T_vehicle_local_position_0__NF_ref_zone"] = zone.values


def add_UTM_setpoint_relative_to_reference(df):
    """Add missing easting messages to dataframe, absolute and relative.

    Arguments:
    df -- dataframe containing messages from the required topics

    """
    if "T_position_setpoint_triplet_0__NF_current_easting" not in df:
        add_UTM_from_global_target_setpoin(df)

    if "T_vehicle_local_position_0__NF_ref_easting" not in df:
        add_UTM_from_reference(df)

    df["T_position_setpoint_triplet_0__NF_current_easting_relative"] = (
        df["T_position_setpoint_triplet_0__NF_current_easting"].values
        - df["T_vehicle_local_position_0__NF_ref_easting"]
    )
    df["T_position_setpoint_triplet_0__NF_current_northing_relative"] = (
        df["T_position_setpoint_triplet_0__NF_current_northing"].values
        - df["T_vehicle_local_position_0__NF_ref_northing"]
    )


def add_UTM_from_global_position(df):
    """Convert data from global position to UTM and add that to the dataframe.

    Arguments:
    df -- dataframe containing messages from the required topics

    """
    easting, northing, zone = mpd.series_utm(
        df["T_vehicle_global_position_0__F_lat"],
        df["T_vehicle_global_position_0__F_lon"],
    )

    df["T_vehicle_global_position_0__NF_easting"] = easting.values
    df["T_vehicle_global_position_0__NF_northing"] = northing.values
    df["T_vehicle_global_position_0__NF_zone"] = zone.values
    # df["T_vehicle_global_position_0__NF_letter"] = letter.values


def add_UTM_position_relative_to_reference(df):
    """Add missing easting data and global position relative easting data.

    Arguments:
    df -- dataframe containing messages from the required topics

    """
    if "T_vehicle_global_position_0__NF_easting" not in df:
        add_UTM_from_global_position(df)

    df["T_vehicle_global_position_0__NF_easting_relative"] = (
        df["T_vehicle_global_position_0__NF_easting"].values
        - df["T_vehicle_local_position_0__NF_ref_easting"]
    )
    df["T_vehicle_global_position_0__NF_northing_relative"] = (
        df["T_vehicle_global_position_0__NF_northing"].values
        - df["T_vehicle_local_position_0__NF_ref_northing"]
    )


def plot_time_series(df, plt):
    """Plot a time series.

    Arguments:
    df -- dataframe containing messages from the required topics
    plt -- plot

    """
    # Remove the plot frame lines
    delta = (df["timestamp"].max() - df["timestamp"].min()) / 10
    plt.xticks(
        np.arange(
            df["timestamp"].min(),
            df["timestamp"].max(),
            step=np.around(delta, decimals=1),
        )
    )
    plt.grid()


def main():
    """Call methods and create pdf with plots showing relevant data."""
    args = parser.parse_args()
    # create dataframe-ulog class for Attitude/Attiutde-setpoint topic
    posg = DfUlg.create(
        args.filename,
        topics=[
            "vehicle_global_position",
            "vehicle_local_position",
            "position_setpoint_triplet",
            "vehicle_status",
        ],
        zoh_topic_msgs_list=[
            TopicMsgs("position_setpoint_triplet", []),
            TopicMsgs("vehicle_status", []),
        ],
    )
    posg.df = apply_UTM_constraints(posg.df)  # apply UTM constraints

    # store the values for all auto navigation states in a list
    NAVIGATION_STATE_AUTO = list(range(3, 9))

    with PdfPages("global_to_local.pdf") as pdf:

        add_UTM_from_global_target_setpoin(posg.df)
        add_UTM_from_reference(posg.df)
        add_UTM_setpoint_relative_to_reference(posg.df)
        add_UTM_from_global_position(posg.df)
        add_UTM_position_relative_to_reference(posg.df)

        # give all rows with an auto navigation state the same number
        auto_state_group_number = -1
        df_manipulate = posg.df.copy()
        for i in NAVIGATION_STATE_AUTO:
            df_manipulate.loc[
                posg.df["T_vehicle_status_0__F_nav_state"] == i,
                ["T_vehicle_status_0__F_nav_state"],
            ] = auto_state_group_number

        # group the rows by the status value they contain
        df_manipulate["T_vehicle_status_0__F_nav_state_group2"] = (
            df_manipulate.T_vehicle_status_0__F_nav_state
            != df_manipulate.T_vehicle_status_0__F_nav_state.shift()
        ).cumsum()
        state_group = df_manipulate.groupby(
            ["T_vehicle_status_0__F_nav_state_group2"]
        )

        # for each time the drone went into an auto mode with setpoints, create a new plot!
        figure_number = 0
        for g, d in state_group:
            if (
                d["T_vehicle_status_0__F_nav_state"][0]
                == auto_state_group_number
            ):
                # global path with setpoint in UTM
                plt.figure(figure_number, figsize=(20, 13))
                df_tmp = d[
                    [
                        "T_vehicle_global_position_0__NF_easting_relative",
                        "T_vehicle_global_position_0__NF_northing_relative",
                    ]
                ].copy()

                plt.plot(
                    d[
                        "T_position_setpoint_triplet_0__NF_current_easting_relative"
                    ],
                    d[
                        "T_position_setpoint_triplet_0__NF_current_northing_relative"
                    ],
                    "rD--",
                    label="Waypoint",
                )
                plt.plot(
                    d["T_vehicle_global_position_0__NF_easting_relative"],
                    d["T_vehicle_global_position_0__NF_northing_relative"],
                    "g",
                    label="Estimation",
                )

                group_easting = d.groupby(
                    [
                        "T_position_setpoint_triplet_0__NF_current_easting_relative"
                    ]
                )
                waypoints = {"time": [], "east": [], "north": []}
                for g, d in group_easting:
                    waypoints["east"].append(g)
                    waypoints["time"].append(d["timestamp"][0])
                    waypoints["north"].append(
                        d[
                            "T_position_setpoint_triplet_0__NF_current_northing_relative"
                        ][0]
                    )

                waypoints = pd.DataFrame(data=waypoints)
                waypoints = waypoints.sort_values(by="time")
                waypoints = waypoints.reset_index(drop=True)
                plt.text(
                    waypoints["east"].iloc[0] + 0.4,
                    waypoints["north"].iloc[0],
                    "Start",
                    color="black",
                    fontsize=18,
                )
                plt.legend()
                plt.title("UTM trajectories")
                plt.ylabel("local position x")
                plt.xlabel("local position y")
                plt.axis("equal")
                plt.grid()
                pdf.savefig()
                plt.close(0)

                figure_number = figure_number + 1

        # easting and northing setpoints and state
        plt.figure(figure_number, figsize=(20, 13))
        df_tmp = posg.df[
            [
                "timestamp",
                "T_position_setpoint_triplet_0__NF_current_easting_relative",
                "T_position_setpoint_triplet_0__NF_current_northing_relative",
                "T_vehicle_global_position_0__NF_easting_relative",
                "T_vehicle_global_position_0__NF_northing_relative",
            ]
        ].copy()
        df_tmp.plot(x="timestamp", linewidth=0.8)
        plot_time_series(df_tmp, plt)
        plt.title("UTM setpoint/state-trajectory")
        plt.ylabel("meters")
        plt.xlabel("meters")
        pdf.savefig()
        plt.close(1)

        figure_number = figure_number + 1

        # vehicle status
        plt.figure(figure_number, figsize=(20, 13))
        df_tmp = posg.df[
            ["timestamp", "T_vehicle_status_0__F_nav_state"]
        ].copy()
        df_tmp.plot(x="timestamp", linewidth=0.8)
        plot_time_series(df_tmp, plt)
        plt.title("vehicle status")
        plt.ylabel("meters")
        plt.xlabel("meters")
        pdf.savefig()
        plt.close(1)

        figure_number = figure_number + 1

        print("global_to_local.pdf was created")


if __name__ == "__main__":
    main()
