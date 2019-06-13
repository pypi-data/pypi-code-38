"""Create dataframe with messages required to run local position tests.

Store topics required for local position tests.
Add missing messages to the dataframe which are required for local position tests.

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

parser = argparse.ArgumentParser(description="Script to process attitude")
parser.add_argument("filename", metavar="file.ulg", help="ulog file")


def print_pdf(df, pdf, topic_1, topic_2, title, y_label, iterator):
    """Create a plot in a pdf with the information passed as arguments.

    Arguments:
    df -- dataframe containing messages from the required topics
    pdf -- pdf file
    topic_1 -- name of one of the messages whose data will be plotted
    topic_2 -- name of one of the messages whose data will be plotted
    title -- title of the plot
    y_label -- label for the y axis
    iterator -- number of the plot in the pdf

    """
    # desired and measured x position
    plt.figure(iterator, figsize=(20, 13))
    df_tmp = df[["timestamp", topic_1, topic_2]].copy()
    df_tmp.plot(x="timestamp", linewidth=0.8)
    plot_time_series(df_tmp, plt)
    plt.title(title)
    plt.ylabel(y_label)
    pdf.savefig()
    plt.close(iterator)


def add_horizontal_distance(df):
    """Compute the horizontal distance between the aircraft and the home point.

    Arguments:
    df -- dataframe containing messages from the required topics

    """
    abs_horizontal_dist = pd.Series(
        np.zeros(df.shape[0]),
        index=df["timestamp"],
        name="T_vehicle_local_position_0__NF_abs_horizontal_dist",
    )

    abs_horizontal_dist = mpd.series_norm_2d(
        df["T_vehicle_local_position_0__F_x"],
        df["T_vehicle_local_position_0__F_y"],
    )
    df[
        "T_vehicle_local_position_0__NF_abs_horizontal_dist"
    ] = abs_horizontal_dist.values


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
    # create dataframe-ulog class for Position/Position-setpoint topic
    pos = DfUlg.create(
        args.filename,
        topics=["vehicle_local_position", "vehicle_local_position_setpoint"],
        # nan_topic_msgs_list=[
        #    TopicMsgs("vehicle_local_position_setpoint", ["x", "y", "z"])
        # ],
    )

    with PdfPages("position.pdf") as pdf:

        add_horizontal_distance(pos.df)

        # TODO: make print_pdf adapt to different numbers of messages
        # desired and measured x position
        print_pdf(
            pos.df,
            pdf,
            "T_vehicle_local_position_0__F_x",
            "T_vehicle_local_position_setpoint_0__F_x",
            "x position",
            "meters",
            0,
        )

        # desired and measured y position
        print_pdf(
            pos.df,
            pdf,
            "T_vehicle_local_position_0__F_y",
            "T_vehicle_local_position_setpoint_0__F_y",
            "y position",
            "meters",
            1,
        )

        # desired and measured z position
        print_pdf(
            pos.df,
            pdf,
            "T_vehicle_local_position_0__F_z",
            "T_vehicle_local_position_setpoint_0__F_z",
            "z position",
            "meters",
            2,
        )

        print("position.pdf was created")


if __name__ == "__main__":
    main()
