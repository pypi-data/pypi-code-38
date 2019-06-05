import os
import importlib.util
from pathlib import Path
from ..config import config


def path_import(absolute_path):
    '''implementation taken from https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly'''
    spec = importlib.util.spec_from_file_location(absolute_path, absolute_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_params(parser):
    config_path = Path(parser.config_file)
    if config_path.is_absolute():
        config_full_path = config_path
    else:
        config_full_path = Path(os.getcwd()).joinpath(parser.config_file)

    config_md = path_import(config_full_path.as_posix())
    api_meta = config_md.api_meta
    itc_conf = config_md.itc_conf
    defaults = config_md.defaults if hasattr(config_md, 'defaults') else None
    excludes = itc_conf.get('excludes', {})
    fix_screenshots = True if parser.fix_screenshots else False
    force_update = True if parser.force_update else False

    limits = {}
    limits.update(config.ITC_CONF)
    for k in limits.keys():
        if itc_conf.get(k) is not None:
            limits[k] = itc_conf.get(k)
        else:
            limits[k] = config.ITC_CONF.get(k)

    APP_SKU = itc_conf.get('SKU', None)
    if itc_conf.get('APPLE_ID', None) is not None:
        APPSTORE_PACKAGE_NAME = '%s.itmsp' % itc_conf['APPLE_ID']
    else:
        APPSTORE_PACKAGE_NAME = '%s.itmsp' % APP_SKU

    return {
        'mode': parser.mode,
        'env': parser.env,
        'send_mail': parser.send_mail,
        'itms': parser.itms,
        'smtp_conf': config_md.smtp_conf if hasattr(config_md, 'smtp_conf') else {},
        'email_sender': config_md.email_sender if hasattr(config_md, 'email_sender') else None,
        'subscribers': config_md.subscribers if hasattr(config_md, 'subscribers') else [],
        'dry_run': parser.dry_run,
        'api_meta': api_meta,
        'itc_conf': itc_conf,
        'defaults': defaults,
        'excludes': excludes,
        'limits': limits,
        'APP_SKU': APP_SKU,
        'APPSTORE_PACKAGE_NAME': APPSTORE_PACKAGE_NAME,
        'username': itc_conf['username'],
        'password': itc_conf['password'],
        'skip_appstore': True if parser.skip_appstore else False,
        'price_only': True if not fix_screenshots and not force_update and parser.price_only else False,
        'fix_screenshots': fix_screenshots,
        'force_update': force_update,
        'verbose': True if parser.verbose else False
    }

