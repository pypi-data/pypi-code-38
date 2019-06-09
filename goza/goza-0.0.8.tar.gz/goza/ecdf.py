from goza import Chart
import numpy as np


class ECDF(Chart):
    """
    Empirical Cumulative Distribution Function plot
    """
    def __init__(self, x, title=None, xlabel=None, ylabel=None, figsize=None):
        """
        Compose data (x) into ECDF and plot as a scatter plot
        :param x:
        :param title:
        :param xlabel:
        :param ylabel:
        :param figsize:
        """
        self.x, self.y, self.n = self._compose_ecdf(x)

        # Initiate chart
        Chart.__init__(self, title, xlabel, ylabel, figsize)

        # Plot scatter plot
        self.plot_ecdf()

    def _compose_ecdf(self, x):
        """
        Compute ECDF data structure for a one-dimensional array
        :param x:
        :return:
        """
        # Number of data points
        n = len(x)

        # Sort x
        x = np.sort(x)

        # Generate y
        y = np.arange(1, n + 1) / n

        return x, y, n

    def plot_ecdf(self, color="#d32323", size=3):
        """
        Plot ECDF diagram
        :param color:
        :param size:
        :return:
        """

        self.ax.scatter(self.x, self.y, color=color, s=size)
