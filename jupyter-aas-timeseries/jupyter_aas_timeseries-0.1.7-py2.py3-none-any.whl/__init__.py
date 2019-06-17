from ._version import version_info, __version__  # noqa

from .figure import TimeSeriesWidget


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-aas-timeseries',
        'require': 'jupyter-aas-timeseries/extension'
    }]
