
import os
import shutil
from appdirs import user_data_dir

CONFIG_APPNAME = u'itt_general'
CONFIG_DATABASE_PATH = user_data_dir(appname=CONFIG_APPNAME)


def remove_config_db():
    if os.path.exists(CONFIG_DATABASE_PATH):
        shutil.rmtree(CONFIG_DATABASE_PATH)


if __name__ == u'__main__':
    remove_config_db()
