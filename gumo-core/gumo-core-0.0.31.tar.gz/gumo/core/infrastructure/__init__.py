import os
import yaml

from logging import getLogger

logger = getLogger(__name__)


class MockAppEngineEnvironment:
    @classmethod
    def load_app_yaml(cls, app_yaml_path):
        with open(app_yaml_path, 'r+') as f:
            app_yaml = yaml.load(f, Loader=yaml.CLoader)

        if 'env_variables' in app_yaml:
            for key, value in app_yaml['env_variables'].items():
                os.environ[key] = str(value)
