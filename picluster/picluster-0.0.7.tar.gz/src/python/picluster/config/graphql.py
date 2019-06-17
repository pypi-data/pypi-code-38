from .base import Config


class GraphQLConfig(Config):

    @staticmethod
    def insert_returning_parser(result):
        return result['data']['insert_backends']['returning'][0]['id']

