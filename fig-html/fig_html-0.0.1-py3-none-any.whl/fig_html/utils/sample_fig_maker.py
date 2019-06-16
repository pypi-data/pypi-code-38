import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class SampleFiguresMaker(object):
    """
    Example
    -------
    >>> from fig_html.utils import SampleFiguresMaker
    >>> root_dir = "./tests/outputs"
    >>> SampleFiguresMaker().make(root_dir)
    """
    def make(self, outputs_path: str) -> None:
        """
        outputs_path : str
            i.e. outputs_path = "./outputs"
        """
        os.makedirs(outputs_path, exist_ok=True)

        df = self._get_sample_data()
        self._make_corr_fig(outputs_path, df)
        self._make_corr_fig(os.path.join(outputs_path, "correlation"), df, color="red")
        self.make_histogram_fig(outputs_path, df)

    def _get_sample_data(self) -> pd.DataFrame:
        x1 = np.random.randn(100)
        x2 = 3.*x1 + np.random.randn(100) / 2.
        y = 4.*x1 + 5.*x2

        df = pd.DataFrame({"x1": x1, "x2": x2, "y": y})
        return df

    def _make_corr_fig(self, outputs_path: str, df: pd.DataFrame, color: str="blue") -> None:
        fig_path = os.path.join(outputs_path, "correlation")
        os.makedirs(fig_path, exist_ok=True)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(df["x1"], df["x2"], color=color)
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        savename = os.path.join(fig_path, "fig1.png")
        fig.savefig(savename)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(df["x1"], df["y"], color=color)
        ax.set_xlabel("x1")
        ax.set_ylabel("xy")
        savename = os.path.join(fig_path, "fig2.png")
        fig.savefig(savename)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(df["x2"], df["y"], color=color)
        ax.set_xlabel("x2")
        ax.set_ylabel("y")
        savename = os.path.join(fig_path, "fig3.png")
        fig.savefig(savename)

        plt.close("all")

    def make_histogram_fig(self, outputs_path: str, df: pd.DataFrame) -> None:
        fig_path = os.path.join(outputs_path, "histogram")
        os.makedirs(fig_path, exist_ok=True)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(df["x1"])
        ax.set_xlabel("x1")
        savename = os.path.join(fig_path, "histogram1.png")
        fig.savefig(savename)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(df["x2"])
        ax.set_xlabel("x2")
        savename = os.path.join(fig_path, "histogram2.png")
        fig.savefig(savename)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(df["y"])
        ax.set_xlabel("y")
        savename = os.path.join(fig_path, "histogram3.png")
        fig.savefig(savename)

        plt.close("all")