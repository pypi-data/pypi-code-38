import json
import ipywidgets as widgets
from traitlets import Unicode, Integer

__all__ = ['TimeSeriesWidget']


@widgets.register
class TimeSeriesWidget(widgets.DOMWidget):

    """A widget for interactive time series."""

    _view_name = Unicode('TimeSeriesView').tag(sync=True)
    _model_name = Unicode('TimeSeriesModel').tag(sync=True)
    _view_module = Unicode('jupyter-aas-timeseries').tag(sync=True)
    _model_module = Unicode('jupyter-aas-timeseries').tag(sync=True)
    _view_module_version = Unicode('^0.1.7').tag(sync=True)
    _model_module_version = Unicode('^0.1.7').tag(sync=True)

    width = Integer(600).tag(sync=True)
    height = Integer(480).tag(sync=True)
    vega_json = Unicode().tag(sync=True)

    def __init__(self, filename):
        super(TimeSeriesWidget, self).__init__()
        self.load_vega(filename)

    def load_vega(self, filename):
        with open(filename, 'r') as f:
            self.vega_json = f.read()
