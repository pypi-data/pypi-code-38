from goza import Chart


class Bar(Chart):
    """
    Plot bar chart using x and y data points.
    """
    def __init__(self, x, y, title=None, xlabel=None, ylabel=None, figsize=None,
                 orientation='vertical'):

        self.x = x
        self.y = y
        self.orientation = orientation

        # Initiate chart
        Chart.__init__(self, title, xlabel, ylabel, figsize)

        # Plot scatter plot
        self.plot_bar()

    def plot_bar(self, color="#d32323"):

        self.ax.bar(x=self.x, height=self.y, color=color, orientation=self.orientation)
