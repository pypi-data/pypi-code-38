import logging

from orm_cloud.database_adapters.database_adapter import DatabaseAdapter
from orm_cloud.request_parsers.api_gateway_request_parser import ApiGatewayRequestParser
from orm_cloud.response_formatters.api_gateway_response_formatter import ApiGatewayResponseFormatter


class RequestRouter:
    log = logging.getLogger(__name__)

    def __init__(self, entity):
        database_type = 'pymssql'
        self.log.debug('Database adapter type is {}.'.format(database_type))
        self._database_adapter = DatabaseAdapter(database_type)

        self._entity = entity

    def process_request(self, request):
        request_parser = ApiGatewayRequestParser()
        parsed_request = request_parser.parse(request)

        self.log.info('Processing request {} on resource {}...'.format(parsed_request['action'], parsed_request['resource']))
        self.log.debug('Variable parsed_request is {}.'.format(parsed_request))

        if parsed_request['action'] == 'GET':
            if parsed_request['resource'].endswith('}'):
                response = self.process_get_single(parsed_request)
            else:
                response = self.process_get(parsed_request)

        else:
            message = 'Operation {} is not yet implemented.'.format(parsed_request['resource'])
            self.log.error(message)
            raise NotImplementedError(message)

        self.log.debug('Response: {}'.format(response))

    def process_post(self):
        pass

    def process_get(self, parsed_request):
        where = parsed_request['query_string_params']['filter']

        sort_by = parsed_request['query_string_params']['sort_by'] if 'sort_by' in parsed_request[
            'query_string_params'] else None
        limit = parsed_request['query_string_params']['limit'] if 'limit' in parsed_request[
            'query_string_params'] else None
        offset = parsed_request['query_string_params']['offset'] if 'offset' in parsed_request[
            'query_string_params'] else None

        results = self._database_adapter.query('*', self._entity._table_name, where, sort_by, offset, limit)
        return self.format_response(results, {})

    def process_get_single(self, parsed_request):
        resource = parsed_request['resource']
        path = parsed_request['path']

        id = path.split('/')[-1]
        result = self._database_adapter.query('*', self._entity._table_name, '{}: {}'.format(self._entity._primary_key, id), one_result=True)
        return self.format_response(result, {})

    def format_response(self, results, headers):
        response_formatter = ApiGatewayResponseFormatter()
        headers['Version'] = self._entity._version

        if results:
            response_code = 200
            self.log.info('Returning response {}.'.format(response_code))
            self.log.debug('Returning data: {}'.format(results))
            self.log.debug('Returning headers: {}'.format(headers))
            response = response_formatter.format_response(response_code, results, headers)
        else:
            response_code = 404
            self.log.info('Returning response {}.'.format(response_code))
            self.log.debug('Returning headers: {}'.format(headers))
            response = response_formatter.format_response(response_code, None, headers)

        return response
