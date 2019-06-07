# Tai Sakuma <tai.sakuma@gmail.com>
import os
import functools
import alphatwirl

from .expander import _apply_default_for_one_key

##__________________________________________________________________||
def expand_table_cfg(cfg, shared):
    cfg = _apply_default_for_one_key('table_cfg', cfg, shared)
    cfg = complete_table_cfg(cfg)
    cfg = dict(table_cfg=cfg)
    return cfg

##__________________________________________________________________||
def complete_table_cfg(cfg):
    """complete a table config.

    Parameters
    ----------
    cfg : dict
        A table config

    Returns
    -------
    dict
        A completed table config

    """

    default_agg_class = alphatwirl.summary.Count
    default_agg_name_for_default_agg_class = ('n', 'nvar')

    default_weight = alphatwirl.summary.WeightCalculatorOne()

    default_cfg = dict(
        key_name=( ),
        key_index=None,
        key_binning=None,
        val_name=None,
        val_index=None,
        agg_class=default_agg_class,
        weight=default_weight,
        sort=True,
        nevents=None,
        store_file=False,
    )

    func_compose_tbl_filename = functools.partial(
        compose_tbl_filename_from_config,
        default=dict(file_name_prefix='tbl_n'))

    ret = default_cfg
    ret.update(cfg)

    ret['key_out_name'] = ret.get('key_out_name', ret['key_name'])

    if isinstance(ret['key_name'], str):
        ret['key_name'] = (ret['key_name'], )
        ret['key_out_name'] = (ret['key_out_name'], )
        if ret['key_index'] is not None:
            ret['key_index'] = (ret['key_index'], )
        if ret['key_binning'] is not None:
            ret['key_binning'] = (ret['key_binning'], )

    if isinstance(ret['val_name'], str):
        ret['val_name'] = (ret['val_name'], )
        if ret['val_index'] is not None:
            ret['val_index'] = (ret['val_index'], )

    use_default_agg_class = 'agg_class' not in cfg
    if 'agg_name' not in ret:
        if use_default_agg_class:
            ret['agg_name'] = default_agg_name_for_default_agg_class
        else:
            ret['agg_name'] = ret['val_name'] if ret['val_name'] is not None else ()

    if isinstance(ret['agg_name'], str):
        ret['agg_name'] = (ret['agg_name'], )

    if ret['store_file']:
        if 'file_path' not in ret:
            file_dir = ret.get('file_dir', '')
            file_name = ret.get('file_name', func_compose_tbl_filename(ret))
            ret['file_path'] = os.path.join(file_dir, file_name)

    return ret

##__________________________________________________________________||
def compose_tbl_filename_from_config(table_cfg, default=None):

    """compose a file name based on a table config.

    This function calls ``compose_tbl_filename()``.

    Parameters
    ----------
    table_cfg : dict
        A table config
    default : dict, optional
        A default config

    Returns
    -------
    str
        A file name

    """

    default_base = dict(
        file_name_prefix='tbl',
        file_name_suffix='txt',
        file_name_var_separator='.',
        file_name_idx_separator='-',
    )

    if default is None:
        default = default_base
    else:
        default_base.update(default)
        default = default_base

    cfg = default.copy()
    cfg.update(table_cfg)

    ret = compose_tbl_filename(
        cfg['key_out_name'],
        key_indices=cfg.get('key_index', None),
        prefix=cfg['file_name_prefix'],
        suffix=cfg['file_name_suffix'],
        var_separator=cfg['file_name_var_separator'],
        idx_separator=cfg['file_name_idx_separator']
    )

    return ret

##__________________________________________________________________||
def compose_tbl_filename(
        key_names, key_indices=None,
        prefix='tbl', suffix='txt',
        var_separator='.', idx_separator='-'):
    """compose a file name based on key names

    Parameters
    ----------
    key_names : list of str
        A list of key names
    key_indices : list of str
        A list of key indices, which can be a number, ``None``, a
        wildcard ``*``, a wildcards in parentheses ``(*)``, a back
        reference ``\\n`` (``n`` is a number),
        e.g., ``(1, None, '*', '(*)', '\\1')``
    prefix : str, default ``tbl``
        A prefix of a file name
    suffix : str, default ``txt``
        A suffix of a file name (filename extension)
    var_separator : str, default '.'
        A separator between key names
    idx_separator : str, default '-'
        A separator between a key name and a key index

    Returns
    -------
    str
        A file name

    """

    if not key_names:
        return prefix + '.' + suffix # e.g. "tbl.txt"

    if key_indices is None:
        colidxs = key_names
        # e.g., ('var1', 'var2', 'var3'),

        middle = var_separator.join(colidxs)
        # e.g., 'var1.var2.var3'

        ret = prefix + var_separator + middle + '.' + suffix
        # e.g., 'tbl.var1.var2.var3.txt'

        return ret

    # e.g.,
    # key_names = ('var1', 'var2', 'var3', 'var4', 'var5'),
    # key_indices = (1, None, '*', '(*)', '\\1')

    idx_str = key_indices
    # e.g., (1, None, '*', '(*)', '\\1')

    idx_str = ['w' if i == '*' else i for i in idx_str]
    # e..g, [1, None, 'w', '(*)', '\\1']

    idx_str = ['wp' if i == '(*)' else i for i in idx_str]
    # e.g., [1, None, 'w', 'wp', '\\1']

    idx_str = ['b{}'.format(i[1:]) if isinstance(i, str) and i.startswith('\\') else i for i in idx_str]
    # e.g., [1, None, 'w', 'wp', 'b1']

    idx_str = ['' if i is None else '{}{}'.format(idx_separator, i) for i in idx_str]
    # e.g., ['-1', '', '-w', '-wp', '-b1']

    colidxs = [n + i for n, i in zip(key_names, idx_str)]
    # e.g., ['var1-1', 'var2', 'var3-w', 'var4-wp', 'var5-b1']

    middle = var_separator.join(colidxs)
    # e.g., 'var1-1.var2.var3-w.var4-wp.var5-b1'

    ret =  prefix + var_separator + middle + '.' + suffix
    # e.g., tbl.var1-1.var2.var3-w.var4-wp.var5-b1.txt

    return ret

##__________________________________________________________________||
