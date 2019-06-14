import pandas as pd

from cellphonedb.src.core.exceptions.ProcessMetaException import ProcessMetaException


def meta_preprocessor(meta_raw: pd.DataFrame) -> pd.DataFrame:
    meta_raw.columns = map(str.lower, meta_raw.columns)
    try:
        if 'cell' in meta_raw and 'cell_type' in meta_raw and 'group' in meta_raw:
            meta = meta_raw[['cell', 'cell_type', 'group']]
            meta.set_index('cell', inplace=True, drop=True)
            return meta

        meta = pd.DataFrame(data={'cell_type': meta_raw.iloc[:, 1], \
                                  'group': meta_raw.iloc[:, 2]})
        meta.set_index(meta_raw.iloc[:, 0], inplace=True)
        meta.index.name = 'cell'
        return meta

    except:
        raise ProcessMetaException
