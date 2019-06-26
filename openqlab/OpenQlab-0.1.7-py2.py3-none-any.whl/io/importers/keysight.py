from OpenQlab.io.data_container import DataContainer
from . import utils

try:
    import numpy as np
    import pandas as pd
    from OpenQlab.io.importers.OldImporters import agilent

    has_imports = True
except ImportError as e:
    print(e)
    has_imports = False


def get_importers():
    if has_imports:
        return {'KeysightBinary': keysight_binary}
    else:
        return {}


def get_auto_importers():
    return get_importers()


def keysight_binary(file):
    time, data = agilent.binary(file)

    with open(file) as f:
        ylabel = utils.get_file_basename(f.name)

    data = pd.DataFrame(np.array(data).T, index=time,
                        columns=[ylabel + '_{0}'.format(ii) for ii in range(1, len(data) + 1)])
    data.index.name = 'Time'
    output = DataContainer(data, type='osci')
    return output
