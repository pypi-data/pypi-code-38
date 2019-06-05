import urllib
from typing import Dict, Any, Union, List, Tuple
from pymongo import uri_parser
from swimlane_platform.lib import SplitStreamLogger
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return


class PyMongoManager:

    def __init__(self, logger):
        # type: (SplitStreamLogger) -> None
        assert logger
        self.logger = logger

    @debug_function_return
    @debug_function_args
    def parse_mongo_uri(self, uri):
        # type: (str) -> Dict[str, Union[str, List[Tuple[str, str]], Dict[str, str]]]
        return uri_parser.parse_uri(uri, validate=False)

    @debug_function_return
    @debug_function_args
    def get_mongo_uri(self, mongo_settings):
        # type: (Union[None,Dict[str, Any]]) -> str
        """
        Returns formatted MongoDb Uri.
        :param mongo_settings: MongoDb settings.
        :return: MongoDb uri string.
        """
        url = 'mongodb://'
        if mongo_settings.get('username') and mongo_settings.get('password'):
            url += '{user}:{password}@'.format(
                user=mongo_settings['username'],
                password=self.escape_mongo_password(mongo_settings['password']))
        url += ','.join(['{host}:{port}'.format(host=node[0], port=node[1]) for node in mongo_settings['nodelist']])
        if mongo_settings.get('database'):
            url += '/{database}'.format(database=mongo_settings['database'])
        if mongo_settings.get('options'):
            url += '?'
            items = ['{key}={value}'.format(key=key, value=value) for key, value in mongo_settings['options'].items()]
            url += '&'.join(items)
        return url

    @debug_function_return
    @debug_function_args
    def escape_mongo_password(self, password):
        # type: (str) -> str
        """
        Escapes MongoDb password for use in connection string.
        :param password: The password.
        :return: The escaped password.
        """
        return urllib.quote(password)
