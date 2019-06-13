from .infrastructure import PlotFactory
import copy

class gen_plot(PlotFactory):
    def __init__(self, ax_method: Callable, *args, **kwargs):
        super(gen_plot, self).__init__()
        self._ax_method = ax_method
        self._args = args
        self._kwargs = kwargs
        self._iterate = False
        self._iterate_df_columns = False

    def iterate(self, iterate=True):
        self._iterate = iterate
        return self

    def iterate_df_columns(self, iterate_df_columns=True):
        self._iterate_df_columns = iterate_df_columns
        return self


    def _make_args(self, obj):
        args = [a(obj) if callable(a) else a for a in self._args]
        return args

    def _make_kwargs(self, obj):
        kwargs = {key: (value(obj) if callable(value) else value) for key, value in self._kwargs.items()}
        return kwargs

    def draw(self, obj, ax):
        method = self._ax_method(ax)
        if self._iterate:
            for item in obj:
                method(*self._make_args(item), **self._make_kwargs(item))
        elif self._iterate_df_columns:
            if not isinstance(obj,pd.DataFrame):
                raise ValueError('Value expect to be pd.Dataframe to do iterate over its columns')
            for c in obj.columns:
                item = obj[c]
                method(*self._make_args(item), **self._make_kwargs(item))
        else:
            method(*self._make_args(obj), **self._make_kwargs(obj))


