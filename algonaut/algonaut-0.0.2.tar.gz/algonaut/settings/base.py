from algonaut.utils.settings import Settings, load_settings
import os

settings_filenames = []

# finally we load custom settings...
_algonaut_settings_d =  os.environ.get('ALGONAUT_SETTINGS_D', '').split(':')
if _algonaut_settings_d:
    for s in _algonaut_settings_d:
        settings_directory = os.path.abspath(s)
        if not os.path.exists(settings_directory):
            continue
        settings_filenames += [os.path.join(settings_directory,fn)
            for fn in sorted(os.listdir(settings_directory)) if fn.endswith('.yml') and not fn.startswith('.')]

settings = Settings(load_settings(settings_filenames))
