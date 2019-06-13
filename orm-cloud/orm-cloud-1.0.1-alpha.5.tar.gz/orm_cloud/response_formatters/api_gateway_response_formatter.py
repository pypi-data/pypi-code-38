import logging


class ApiGatewayResponseFormatter:
    log = logging.getLogger(__name__)

    def __init__(self):
        self.log.debug('Creating ApiGatewayResponseFormatter response formatter...')

    def format_response(self, response_code, body, headers):
        headers['Content-Type'] = 'application/json'

        response = {
            'statusCode': response_code,
            'headers': headers
        }

        if body:
            response['body'] = body

        return response
