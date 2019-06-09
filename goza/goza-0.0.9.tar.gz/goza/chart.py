import matplotlib.pyplot as plt


class Chart:
    """
    Chart class to create and format a basic pyplot figure
    """
    def __init__(self, title=None, xlabel=None, ylabel=None, figsize=None):

        self.title = title if title else "Unnamed Chart"
        self.xlabel = xlabel if xlabel else "X-Axis"
        self.ylabel = ylabel if ylabel else "Y-Axis"
        self.figsize = figsize if figsize else (10, 8)

        # Create figure
        self.figure, self.ax = self.create_figure(self.figsize)

        # Format
        self.format_title()
        self.format_axes()

    def create_figure(self, figsize):
        """
        Create plplot figure and axes objects and assign to Chart
        :param figsize:
        :return:
        """
        self.figure, self.ax = plt.subplots(1, 1, figsize=figsize)

        return self.figure, self.ax

    def format_title(self, color="black", fontsize=14):
        """
        Format title, x label, and y label
        :return:
        """
        self.ax.set_title(self.title, color=color, fontsize=fontsize)

    def format_axes(self, color="#605770", fontsize=12):
        """
        Format axes to my preference.  Remove top/right spines and set colors on
        left/bottom spines, ticks, and tick labels
        :param color:
        :return:
        """

        # Turn off top / right spines
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        # Format left / bottom spines
        self.ax.spines["left"].set_color(color)
        self.ax.spines["bottom"].set_color(color)

        # Format ticks
        self.ax.tick_params(axis="x", colors=color)
        self.ax.tick_params(axis="y", colors=color)

        # Format labels
        self.ax.set_xlabel(self.xlabel, fontsize=fontsize)
        self.ax.set_ylabel(self.ylabel, fontsize=fontsize)

    @staticmethod
    def show():
        """
        Show chart
        :return:
        """
        plt.show()

    # TODO: save_figure method saving blank image.
    @staticmethod
    def save_figure(*args, **kwargs):
        """
        Save figure to file
        :param args:
        :param kwargs:
        :return:
        """
        plt.savefig(*args, **kwargs)
