from airflow import configuration
from airflow.exceptions import AirflowConfigException


def conf_get_default (section, key, default):
    try:
        return configuration.get(section, key)
    except AirflowConfigException:
        return default