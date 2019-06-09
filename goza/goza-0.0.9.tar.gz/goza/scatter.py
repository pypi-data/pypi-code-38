from goza import Chart


class Scatter(Chart):
    """
    Plot scatter chart using x and y data points.
    """
    def __init__(self, x, y, title=None, xlabel=None, ylabel=None, figsize=None):

        self.x = x
        self.y = y

        # Initiate chart
        Chart.__init__(self, title, xlabel, ylabel, figsize)

        # Plot scatter plot
        self.plot_scatter()

    def plot_scatter(self, color="#d32323", size=3):

        self.ax.scatter(self.x, self.y, color=color, s=size)
