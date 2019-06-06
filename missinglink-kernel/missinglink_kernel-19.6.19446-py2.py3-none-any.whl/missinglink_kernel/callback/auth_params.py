# -*- coding: utf-8 -*-


class AuthParams(object):
    def __init__(self, config_prefix=None, config_file=None):
        self._config_prefix = config_prefix
        self._config_file = config_file
        self._config = None

    @property
    def config(self):
        if self._config is None:
            from missinglink.core.config import Config

            self._config = Config(self._config_prefix, self._config_file)

        return self._config

    @property
    def api_host(self):
        return self.config.api_host

    def get_user_id(self):
        return self.config.user_id

    def select_volume_id(self):
        from .api_get_resources import select_volume_id
        from ..data_management.http_session import create_http_session

        session = create_http_session()

        data_volume = select_volume_id(self.config, session)

        return data_volume['id']

    def get_project_token(self, project_id):
        from missinglink.core import ApiCaller
        from .api_get_resources import select_project
        from ..data_management.http_session import create_http_session

        session = create_http_session()

        if project_id is not None:
            project = ApiCaller.call(self.config, session, 'get', 'projects/{project_id}'.format(project_id=project_id))
        else:
            project = select_project(self.config, session)

        return project['token'] if project else None
