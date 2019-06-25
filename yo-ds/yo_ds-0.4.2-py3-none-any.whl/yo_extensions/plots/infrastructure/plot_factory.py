from .common import *
from typing import *

class PlotFactory(Callable[[Any],Axes]):
    def __init__(self):
        self._default_ax = None # type: Optional[Axes]
        self._default_fig_size = None # type: Optional[Tuple[float,float]]
        self._post_processing = [] # type: List[Callable[[Axes],Any]]

        self._title = None # type: Optional[str]
        self._xlabel = None # type: Optional[str]
        self._ylabel = None # type: Optional[str]
        self._with_legend = False # type: bool

    def draw(self, obj: Any, ax: Axes) -> None:
        raise NotImplementedError() #pragma: no cover

    def __call__(self, obj: Any)->Axes:
        if self._default_ax is not None:
            ax = self._default_ax
        elif self._default_fig_size is not None:
            _, ax = plt.subplots(1, 1, figsize = self._default_fig_size)
        else:
            _, ax = plt.subplots(1,1, figsize=(12,6))

        self.draw(obj,ax)

        if self._title is not None:
            ax.set_title(self._title)
        if self._xlabel is not None:
            ax.set_xlabel(self._xlabel)
        if self._ylabel is not None:
            ax.set_ylabel(self._ylabel)
        if self._with_legend:
            ax.legend()

        for post_proc in self._post_processing:
            post_proc(ax)

        return ax

    def on(self, ax: Axes) -> 'PlotFactory':
        self._default_ax = ax
        return self

    def size(self, width, height):
        self._default_fig_size=(width, height)
        return self

    def labels(self, title: Optional[str]=None, xlabel: Optional[str]=None, ylabel : Optional[str] = None) -> 'PlotFactory':
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        return self

    def with_legend(self) -> 'PlotFactory':
        self._with_legend = True
        return self

    def tune(self, method: Callable[[Axes],Any])->'PlotFactory':
        self._post_processing.append(method)
        return self






