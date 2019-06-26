import os
from datetime import datetime

from pytz import timezone

from news2play.common.configuration import storage_conf, storage_data, storage_log

US_NOW_YMD = datetime.now().astimezone(timezone('US/Eastern')).strftime('%Y%m%d')

folder_data_ymd = os.path.join(storage_data, US_NOW_YMD)

file_meta_data = os.path.join(folder_data_ymd, 'meta_data.json')
file_config = os.path.join(storage_conf, 'news2play.yml')
file_log = os.path.join(storage_log, f'car2play.{US_NOW_YMD}.logs')
