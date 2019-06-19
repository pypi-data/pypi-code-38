import urllib.parse
from asnake.client import ASnakeClient


class ArchivesSpace(object):
    UPDATE_STATUS_FAILED = 'failed'
    UPDATE_STATUS_SUCCESS = 'success'

    def __init__(self, config={}):
        self.client = ASnakeClient()
        self.config = config
        self.containers = {}
        self.locations = {}
        self.repositories = {}
        self.results = []

    def handle(self, line_count, repo_code, con_barcode, loc_barcode):
        status = self.UPDATE_STATUS_FAILED  # default
        repo_uri = self.repo_uri_from_code(repo_code)
        con_uri = self.con_uri_from_barcode(repo_uri, con_barcode)
        loc_uri = self.loc_uri_from_barcode(loc_barcode)

        if repo_uri and con_uri and loc_uri:
            print(f'Shelving: {repo_uri}, {con_uri}, {loc_uri} [{line_count}]')
            try:
                uri = f'{repo_uri}/top_containers/bulk/locations'
                data = {con_uri: loc_uri}
                self.client.post(uri, json=data)
                status = self.UPDATE_STATUS_SUCCESS
            except Exception:
                print(f'Failed: {repo_code}, {con_barcode}, {loc_barcode}')

        self.results.append({
          'row': line_count,
          'con_barcode': con_barcode,
          'con_uri': con_uri,
          'loc_barcode': loc_barcode,
          'loc_uri': loc_uri,
          'repo_code': repo_code,
          'repo_uri': repo_uri,
          'status': status,
        })

    def ping(self):
        try:
            self.reset_client()
            self.client.authorize()
            print('Login OK!')
        except Exception as ex:
            print(ex)

    def reset_client(self):
        self.client = ASnakeClient(
            baseurl=self.config['baseurl'],
            username=self.config['username'],
            password=self.config['password'],
        )

    def con_uri_from_barcode(self, repo_uri, barcode):
        try:
            if barcode not in self.containers:
                path = f'{repo_uri}/top_containers/by_barcode/{self.quote(barcode)}'  # noqa
                uri = self.client.get(path).json()['uri']
                self.containers[barcode] = uri
        except Exception:
            print(f'Container not found: {barcode}')
        return self.containers.get(barcode, None)

    def loc_uri_from_barcode(self, barcode):
        try:
            if barcode not in self.locations:
                path = f'/locations/by_barcode/{self.quote(barcode)}'
                uri = self.client.get(path).json()['uri']
                self.locations[barcode] = uri
        except Exception:
            print(f'Location not found: {barcode}')
        return self.locations.get(barcode, None)

    def quote(self, parameter):
        return urllib.parse.quote(parameter)

    def repo_uri_from_code(self, repo_code):
        try:
            if repo_code not in self.repositories:
                path = f'/repositories/by_repo_code/{self.quote(repo_code)}'
                uri = self.client.get(path).json()['uri']
                self.repositories[repo_code] = uri
        except Exception:
            print(f'Repository not found: {repo_code}')
        return self.repositories.get(repo_code, None)
