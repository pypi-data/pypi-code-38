from typing import List  # NOQA

from .chart import Chart
from .singletons import get_backend


class Frame:
    def __init__(self, *, height_px=500, width_px=500):
        self._backend = get_backend()

        self.height_px = height_px
        self.width_px = width_px
        self.nrows = 1
        self.ncols = 1
        self._charts: List[Chart] = []

    def create_chart(self):
        chart = Chart(self._backend)
        self._charts.append(chart)
        return chart

    def layout(self, nrows: int, ncols: int):
        self.nrows = nrows
        self.ncols = ncols

    def show(self):
        if self.nrows * self.ncols != len(self._charts):
            raise ValueError(f'Number of rows ({self.nrows}) and columns ({self.ncols}) do not add upto the number of charts ({len(self._charts)})!')
        self._backend.set_frame(self)
        for chart in self._charts:
            self._backend.add_chart(chart)
            for plot in chart._plots:
                plot.draw()
        self._backend.show()
