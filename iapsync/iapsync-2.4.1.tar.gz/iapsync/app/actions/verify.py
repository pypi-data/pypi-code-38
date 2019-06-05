import sys
import subprocess
from pathlib import Path
from iapsync.config import config
from iapsync.utils.transporter import transporter_path


def run(params, opts, agg_ret):
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    username = params['username']
    password = params['password']
    BUNDLE_ID = params['itc_conf']['BUNDLE_ID']
    tmp_dir = Path(config.TMP_DIR).joinpath(BUNDLE_ID + '-' + params['env'])
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)
    # 初始化etree
    itms = params['itms'] if params['itms'] else transporter_path
    try:
        subprocess.run([
            itms,
            '-m', 'verify', '-u', username, '-p', password, '-f', p.as_posix()])
    except:
        print('验证失败：%s.' % sys.exc_info()[0])
        raise
    return agg_ret
