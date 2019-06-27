from ..infrastructure import *
import seaborn
import pandas as pd

class heatmap(PlotFactory):
    def __init__(self, x: str, y: str, value: str, default: Any = 0, **kwargs):
        super(heatmap, self).__init__()
        self.x=x
        self.y=y
        self.value = value
        self.default = default
        self.kwargs = kwargs

    def draw(self, obj: pd.DataFrame, ax: Axes):
        map = obj.pivot_table(columns=self.x,index=self.y,values=self.value,aggfunc=lambda z: z)
        if self.default is not None:
            map = map.fillna(self.default)
        seaborn.heatmap(map,ax=ax,**self.kwargs)

