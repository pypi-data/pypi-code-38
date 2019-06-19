import sys
import subprocess
from pathlib import Path
from iapsync.config import config
from iapsync.handlers import all_handlers
from iapsync.utils.transporter import transporter_path


def run(params, opts, data_to_upload):
    username = params['username']
    password = params['password']
    BUNDLE_ID = params['itc_conf']['BUNDLE_ID']
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    tmp_dir = Path(config.TMP_DIR).joinpath(BUNDLE_ID + '-' + params['target_env'])
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)

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

    has_update = params.get('force_update', False)
    has_update = has_update or check_update(data_to_upload)

    if has_update and not params['dry_run']:
        # 初始化etree
        itms = params['itms'] if params['itms'] else  transporter_path
        try:
            subprocess.check_call([
                itms,
                '-v', params['log_level'],
                '-m', 'upload',
                '-u', username,
                '-p', password,
                '-f', p.as_posix()])
        except:
            print('上传失败：%s.' % sys.exc_info()[0])
            raise
        all_handlers.handle(data_to_upload, params)
    else:
        print('Not updates or --dry-run, will upload nothing.')
    return data_to_upload
