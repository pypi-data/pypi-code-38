from ..infrastructure import *
import pandas as pd

class _GrpbyPlot(PlotFactory):
    def __init__(self, x: str, y: str, method: Callable):
        super(_GrpbyPlot, self).__init__()
        self.x = x
        self.y = y
        self.method = method

    def draw(self, obj: Any, ax: Axes):
        for group, data in obj:
            self.method(ax, data[self.x], data[self.y], label=group)
        ax.set_xlabel(str(self.x))
        ax.set_ylabel(str(self.y))

def line(x: str, y: str):
    return _GrpbyPlot(x,y,Axes.plot)

def scatter(x: str, y:str):
    return _GrpbyPlot(x,y,Axes.scatter)

class bars(PlotFactory):
    def __init__(self, x: str, y: str, format: Optional[str]='%.2f'):
        super(bars, self).__init__()
        self.x=x
        self.y=y
        self.format = format

    def draw(self, obj: Any, ax: Axes):
        columns = [self.x, self.y]
        value_column = self.y
        bar_column = self.x
        result = []
        for group, df in obj:
            tdf = df[columns]
            tdf = tdf.assign(group=tdf.apply(lambda z: group, axis=1))
            result.append(tdf)
        data = pd.concat(result)

        plot_bars(data, ax, value_column, 'group', bar_column, value_format=self.format)

