from django.apps import AppConfig
import os


def get_current_app_name(_file):
    return os.path.split(os.path.dirname(_file))[-1]


app_name = get_current_app_name(__file__)


class PrimaryConfig(AppConfig):
    name = app_name
    verbose_name = '系统管理'


default_app_config = '%s.PrimaryConfig' % app_name
