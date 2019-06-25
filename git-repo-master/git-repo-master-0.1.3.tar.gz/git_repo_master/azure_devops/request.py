import base64
import json
from http import client
from urllib.parse import quote


class AzureGitRequest:
    __VERSION = '5.0'
    __ENDPOINT = 'dev.azure.com'
    __REQUEST_FORMAT = '/{}/{}/_apis/git/repositories/{}/{}{}'
    __query = []

    def __init__(self):
        self.clean_query()
        self.__token = ''
        self.__organization = ''
        self.__project = ''
        self.__repository = ''
        self.__resource = ''
        self.__method = ''
        self.__body = ''
        pass

    def clean_query(self):
        self.__query = []
        self.__query.append('api-version={}'.format(self.__VERSION))
        return self

    def __validate_parameters(self):
        if (self.__organization == '' or
                self.__project == '' or
                self.__repository == '' or
                self.__method == '' or
                self.__resource == '' or
                self.__token == ''):
            return False
        return True

    def __build_query(self):
        if len(self.__query) == 0:
            return ''
        return '?{}'.format('&'.join(self.__query))

    def __build_request(self):
        return self.__REQUEST_FORMAT.format(
            self.__organization,
            self.__project,
            self.__repository,
            self.__resource,
            self.__build_query()
        )

    def __build_headers(self):
        return {
            'Authorization': 'Basic {}'.format(self.__token),
            'Content-Type': 'application/json'
        }

    def __execute_request(self):
        print('Making request to endpoint:')
        print('https://{}{}'.format(self.__ENDPOINT, self.__build_request()))
        conn = client.HTTPSConnection(self.__ENDPOINT, 443)
        conn.request(
            method=self.__method,
            url=self.__build_request(),
            headers=self.__build_headers(),
            body=json.dumps(self.__body).encode()
        )
        response = conn.getresponse()
        if response.status not in [200, 201]:
            print("Error during request. Response status: {}".format(response.status))
            print("Error during request. Response body: {}".format(response.read()))
        else:
            response_json = json.loads(response.read().decode())
            print(json.dumps(response_json, indent=4, sort_keys=True))
            return response_json

    def with_organization(self, organization):
        self.__organization = quote(organization)
        return self

    def with_project(self, project):
        self.__project = quote(project)
        return self

    def with_repository(self, repository):
        self.__repository = quote(repository)
        return self

    def with_method(self, method):
        self.__method = method
        return self

    def with_resource(self, resource):
        self.__resource = resource
        return self

    def with_query(self, query):
        self.__query.append(query)
        return self

    def with_token(self, token):
        self.__token = base64.b64encode(':{}'.format(token).encode()).decode()
        return self

    def with_body(self, body):
        self.__body = body
        return self

    def execute(self):
        if self.__validate_parameters():
            self.__execute_request()
        else:
            print("There is problem with request parameters. Check configuration.")
