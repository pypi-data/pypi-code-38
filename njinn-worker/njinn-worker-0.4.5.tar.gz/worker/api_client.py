import os
import tempfile

import requests
from requests_jwt import JWTAuth


class NjinnAPI():
    """
    Class provides access to the Njinn API by adding the
    base URL and authentication (JWT) to each request.
    """

    def __init__(self, api, token, worker_name, execution_id=None):
        """
        Prepare Njinn base URL and token for authentication
        """

        self.auth = JWTAuth(token, header_format=u'JWT %s')
        self.auth.expire(30)
        self.auth.add_field('worker', worker_name)

        self.njinn_api = api
        self.execution_id = execution_id

    def get_url(self, path):
        """
        Add the Njinn API base url in front of the path.
        """

        path = path[1:] if path.startswith('/') else path
        url = f"{self.njinn_api}/{path}"
        return url

    def get(self, path, params=None, **kwargs):
        """
        Run GET request to the Njinn API.
        """

        url = self.get_url(path)
        return requests.get(url, params=params, auth=self.auth, **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        """
        Run POST request to the Njinn API.
        """

        url = self.get_url(path)
        return requests.post(url, data=data, json=json, auth=self.auth, **kwargs)

    def put(self, path, data=None, **kwargs):
        """
        Run PUT request to the Njinn API.
        """

        url = self.get_url(path)
        return requests.put(url, data=data, auth=self.auth, **kwargs)

    def patch(self, path, data=None, **kwargs):
        """
        Run PATCH request to the Njinn API.
        """

        url = self.get_url(path)
        return requests.patch(url, data=data, auth=self.auth, **kwargs)

    def delete(self, path, **kwargs):
        """
        Run DELETE request to the Njinn API.
        """

        url = self.get_url(path)
        return requests.delete(url, auth=self.auth, **kwargs)

    def upload_file(self, file_path, **kwargs):
        """
        Creates Storage object and then uploads a file to this object.
        """

        url = '/api/v1/storages'
        data = {
            "execution_id": self.execution_id
        }
        response = self.post(url, json=data)
        if response.status_code != requests.codes.created:
            raise Exception(f"Could not create Storage object. \
                            API status code: {response.status_code}")

        storage_id = response.json()['id']

        url += f'/{storage_id}/data'
        files = {"data": open(file_path, 'rb')}
        response = self.put(url, files=files)
        if response.status_code != requests.codes.ok:
            raise Exception(f"Could not upload the file: {file_path}. \
                            API status code: {response.status_code}")

        print(f"File was successfully uploaded: {file_path.split('/')[-1]}")

        return f"FILE({storage_id})"

    def download_file(self, storage_id, target_folder, log, **kwargs):
        """
        Download the file from the Njinn API with ``storage_id`` ID and
        save it into the action working directory.
        """
        
        url = f'/api/v1/storages/{storage_id}'
        response = self.get(url)
        if response.status_code != requests.codes.ok:
            raise Exception(f"Could not download the file metadata with ID: {storage_id}. \
                            API status code: {response.status_code}")

        file_name = response.json()['name']
        file_path = os.path.join(target_folder, file_name)

        url += '/data'
        response = self.get(url)
        if response.status_code != requests.codes.ok:
            raise Exception(f"Could not download the file with ID: {storage_id} \
                            API status code: {response.status_code}")

        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"Successfully downloaded a file: {file_name}", file=log)

        return file_path
