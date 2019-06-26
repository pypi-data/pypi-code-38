import requests
from iapsync.config.config import APP_VER

def check_new_version():
    try:
        app_json = requests.get('https://pypi.python.org/pypi/iapsync/json').json()
        info = app_json.get('info', {})
        latest = info.get('version', None)
        if not latest:
            print('Failed to get latest app version, maybe pypi web api changed.')
            return
        latest_parts = latest.split('.')
        now = APP_VER.split('.')
        for idx, part in enumerate(latest_parts):
            if int(part) > int(now[idx]):
                return latest
    except Exception as e:
        print('Non fatal error: %s' % e)
    return None
