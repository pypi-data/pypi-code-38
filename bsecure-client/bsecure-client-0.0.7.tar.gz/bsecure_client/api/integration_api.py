from .base import API

start_integration_query = '''
  mutation startIntegration($endpoint: String!, $host: String!, $secret: String!) {
    startIntegration(input: {endpoint: $endpoint, host: $host, secret: $secret}) {
      token
    }
  }
'''

finish_integration_query = '''
  mutation finishIntegration($host: String!) {
    finishIntegration(input: {host: $host}) {
      jwt
    }
  }
'''


class IntegrationAPI(API):
    @API.expose_method
    def integrate(self, prepare_endpoint, endpoint, host, secret):
        response_data = self.perform_query(
            start_integration_query,
            {
                'endpoint': endpoint,
                'host': host,
                'secret': secret
            }
        )
        token = response_data['startIntegration']['token']
        prepare_endpoint(token)
        response_data = self.perform_query(
            finish_integration_query,
            {
                'host': host
            }
        )
        return response_data['finishIntegration']['jwt']
