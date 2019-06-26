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
    output_dir = params['output_dir']
    tmp_dir = Path(output_dir + config.TMP_DIR).joinpath(BUNDLE_ID + '-' + params['target_env'])
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)
    # 初始化etree
    def check_update(data):
        if not data:
            return False
        for data_item in data:
            result = data_item.get('result', None)
            if not result:
                continue
            if result.get('updated', []) or result.get('added', []):
                return True
        return False
    has_update = check_update(agg_ret)
    # 数据没更改，不需要验证
    if not has_update and params['mode'] != 'verify':
        return agg_ret

    if params['skip_mode'] == 'verify':
        return agg_ret
    itms = params['itms'] if params['itms'] else  transporter_path
    try:
        subprocess.check_call([
            itms,
            '-v', params['log_level'],
            '-m', 'verify', '-u', username, '-p', password, '-f', p.as_posix()])
    except:
        print('验证失败：%s.' % sys.exc_info()[0])
        raise
    return agg_ret
