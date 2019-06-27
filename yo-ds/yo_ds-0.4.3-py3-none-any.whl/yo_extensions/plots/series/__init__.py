from ..infrastructure import *
from ...alg import trimmer as Trimmer
import pandas as pd
from matplotlib import cm
from yo_core import Query

class hist(PlotFactory):
    def __init__(self,
                 bins: int = 10,
                 trimmer: Trimmer = Trimmer(),
                 **kwargs):
        super(hist, self).__init__()
        self.bins = bins
        self.trimmer = trimmer
        self.kwargs = kwargs

    def draw(self, obj: pd.Series, ax: Axes):
        series = self.trimmer(obj)
        ax.hist(series, self.bins, **self.kwargs)

class pie(PlotFactory):
    def __init__(self,
                 explode: float = 0.1,
                 with_abs_values: bool = False):
        super(pie, self).__init__()
        self.explode = explode
        self.with_abs_values = with_abs_values

    def draw(self, series: pd.Series, ax: Axes):
        def pcnt(p, total):
            cnt = round(p * total / 100)
            return "{0:.0f} ({1:.2f}%)".format(cnt, p)

        values = series.name or 'values'
        ind = series.index.name or 'index'
        dt = series.to_frame(values).reset_index().assign(explode=self.explode)


        total = dt[values].sum()
        pcnter = '%1.2f%%'
        if self.with_abs_values:
            pcnter = lambda p: pcnt(p, total)

        ax.pie(
            dt[values],
            labels=dt[ind],
            explode=dt['explode'],
            shadow=True,
            startangle=90,
            autopct=pcnter
        )

class funnel(PlotFactory):
    def __init__(self, cmap: Callable[[int],Any] = cm.Pastel2):
        super(funnel, self).__init__()
        self.cmap = cmap

    def draw(self, funnel_data: pd.Series, ax: Axes):
        funnel_data = funnel_data.to_frame('').reset_index()
        funnel_data.columns = ['name', 'value']

        funnel_data = funnel_data.assign(ycoo=range(funnel_data.shape[0]))
        funnel_data = funnel_data.assign(ycoo=-funnel_data.ycoo)
        funnel_data = funnel_data.assign(color=[self.cmap(i) for i in range(funnel_data.shape[0])])
        ax.barh(
            funnel_data.ycoo,
            2 * funnel_data.value,
            height=1,
            left=-funnel_data.value,
            label=funnel_data.name,
            color=funnel_data.color,
            tick_label=funnel_data.name
        )

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_xaxis().set_ticks([])

        for row in Query.df(funnel_data):
            ax.text(0, row.ycoo, str(row.value), va='center', ha='center')

class default(PlotFactory):
    def __init__(self, kind: Optional[str]=None):
        super(default, self).__init__()
        self.kind = kind
    def draw(self, obj: pd.Series, ax: Axes):
        kwargs = {}
        if self.kind is not None:
            kwargs['kind']=self.kind
        kwargs['ax']=ax

        obj.plot(**kwargs)

