"""
View-Controller class for OnePanel API
"""
import json

from prettytable import PrettyTable


class APIViewController:
    conn = None  # Connection from onepanel.cli
    endpoint = str

    def __init__(self, conn):
        self.conn = conn
        self.endpoint = conn.URL

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    # Wrappers for HTTP requests
    def get(self, uid='', field_path='', params=None, endpoint=None):
        """Get a JSON object from the endpoint"""

        if endpoint is None:
            endpoint = self.endpoint

        r = self.conn.get(
            '{endpoint}{uid}{field_path}{params}'.format(endpoint=endpoint, uid=uid, field_path=field_path,
                                                          params=params or ''))

        c = r.status_code
        if c == 200:
            if r.headers['Content-Type'] == 'text/plain':
                item = r.text
            else:
                item = r.json()
        else:
            item = None

        response_data = {
                'data':item,
                'status_code':c
            }
        return response_data

    def put(self, uid='', field_path='', params=None, post_object=None, endpoint=None):
        """Put a JSON object to the endpoint"""

        if endpoint is None:
            endpoint = self.endpoint

        url = '{endpoint}{uid}{field_path}{params}'.format(endpoint=endpoint, uid=uid, field_path=field_path,
                                                         params=params or '')
        r = self.conn.put(url, data=json.dumps(post_object))

        c = r.status_code
        if c == 200:
            if r.headers['Content-Type'] == 'text/plain':
                item = r.text
            else:
                item = r.json()
        else:
            item = None

        response_data = {
            'data': item,
            'status_code': c
        }
        return response_data

    def head(self, uid='', field_path='', params=None):
        """Make a head request to the endpoint"""

        url = '{endpoint}{uid}{field_path}{params}'.format(endpoint=self.endpoint, uid=uid, field_path=field_path,
                                                           params=params or '')
        r = self.conn.head(url)

        c = r.status_code
        if c == 200:
            if r.headers['Content-Type'] == 'text/plain':
                item = r.text
            else:
                item = r.json()
        else:
            item = None

        response_data = {
            'data': item,
            'status_code': c
        }
        return response_data

    def list(self, params=None, endpoint=None):
        """Get a JSON list from the endpoint"""

        if endpoint is None:
            endpoint = self.endpoint

        r = self.conn.get('{endpoint}{params}'.format(endpoint=endpoint, params=params or ''))

        c = r.status_code
        if c == 200:
            items = r.json()
        else:
            return None

        return items

    def post(self,post_object,params=None, json_encoder=None):
        """POST an object and return the newly created resource"""

        url = '{endpoint}{params}'.format(endpoint=self.endpoint, params=params or '')

        r = self.conn.post(url, data=json.dumps(post_object, cls=json_encoder))

        c = r.status_code
        if c == 200:
            created_object = r.json()
        else:
            try:
                created_object = "An error occurred: {}".format(r.json())
            except ValueError:
                created_object = "An error occurred: {}".format(r.text)

        return {
            'data': created_object,
            'status_code': c
        }

    def delete(self, uid, field_path='', message_on_success='Resource deleted',
               message_on_failure='Resource not found'):
        r = self.conn.delete('{}/{}{}'.format(self.endpoint, uid, field_path))

        c = r.status_code
        if c == 200:
            print('{message}: {id}'.format(message=message_on_success, id=uid))
            return True
        elif c == 404:
            print('{message}: {id}'.format(message=message_on_failure, id=uid))
        else:
            print('Error: {}'.format(c))

        return False

    def delete_v2(self, uid='', field_path='', params=None, endpoint=None):
        """Delete an object from the endpoint"""

        if endpoint is None:
            endpoint = self.endpoint

        r = self.conn.delete(
            '{endpoint}/{uid}{field_path}{params}'.format(endpoint=endpoint, uid=uid, field_path=field_path,
                                                          params=params or ''))

        c = r.status_code
        if c == 200:
            if r.headers['Content-Type'] == 'text/plain':
                item = r.text
            else:
                item = r.json()
        else:
            item = None

        response_data = {
                'data':item,
                'status_code':c
            }
        return response_data

    # Support functions

    @staticmethod
    def print_items(
            items,
            fields=None,
            field_names=None,
            empty_message='No items found'
    ):
        """A standard table for showing response to GET requests"""

        if fields is None:
            fields = ['uid', 'name']
        if field_names is None:
            field_names = ['ID', 'NAME']

        if len(items) == 0:
            print(empty_message)
            return items

        summary = PrettyTable(border=False)
        summary.field_names = field_names
        summary.align = 'l'
        for item in items:
            summary.add_row([item[field] for field in fields])
        print(summary)
