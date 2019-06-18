import requests
import urllib
import urllib.parse
from ms_sdk.Lib.Http.Response import Response


class Request:

    def __init__(self, client, resource):
        """
        RequestHandler initializer.
        :param client:
        :param resource:
        """
        self.client = client
        self.resource = resource

    def handle(self, method: str, body: bool = False, uriAppend: bool = False, queryParams: dict = {}):
        """
        :param method:
        :param body:
        :param uriAppend:
        :param queryParams:
        :return: Promise|Response
        """
        _async = self.client.getAsync()
        options = {}

        # TODO: Set user authorization

        # Generate request URL
        url = self.client.getGatewayUrl() + '/' + self.client.getVersion() + \
            '/' + self.resource.getURI()

        # Base url should end without slash
        url = url.replace('?', '')
        url = url.rstrip('/')

        # Append additional data to url
        if uriAppend:
            url += '/' + str(uriAppend)

        # Add query params
        if queryParams and method.lower() != 'post':
            url += '?' + \
                urllib.parse.unquote(urllib.parse.urlencode(queryParams))

        if body:
            if method.lower() == 'put':
                options['body'] = urllib.parse.urlencode(queryParams)
            elif method.lower() == 'post':
                options['content-type'] = 'application/x-www-form-urlencoded'
                # options['form_params'] = body
            elif method.lower() == 'delete':
                options['body'] = urllib.parse.urlencode(queryParams)

        self.client.setCallStatistic(
            {'method': method, 'url': url, 'options': options})

        if _async:
            return {'method': method, 'url': url, 'options': options}

        headers = {'user-agent': 'PythonAPI'}

        if method.lower() == 'get':
            return Response(requests.get(url, options, headers=headers))
        elif method.lower() == 'delete':
            return Response(requests.delete(url, data=options, headers=headers))
        elif method.lower() == 'put':
            return Response(requests.put(url, options, headers=headers))
        elif method.lower() == 'post':
            return Response(requests.post(url, data=queryParams, headers=headers))
