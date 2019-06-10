"""
Copyright 2018 IDRsolutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Main class used to interact with the buildvu web app
For detailed usage instructions, see the GitHub repository:
    https://github.com/idrsolutions/buildvu-python-client
"""
import json
import os
import time

try:
    import requests
except ImportError:
    raise Exception("Missing dependency: 'requests'. Install it using 'pip install requests'.")


class BuildVu:

    DOWNLOAD = "download"
    UPLOAD = "upload"

    def __init__(self, url, timeout_length=(10, 30), conversion_timeout=30):
        """
        Constructor, setup the converter details

            Args:
                url (str): The URL of the converter
                timeout_length (int, int): (Optional) A tuple of ints representing the request and
                    response timeouts in seconds respectively
                conversion_timeout (int): (Optional) The maximum length of time (in seconds) to
                    wait for the file to convert before aborting
        """
        self.base_endpoint = url
        self.endpoint = url + '/buildvu'
        self.request_timeout = timeout_length
        self.convert_timeout = conversion_timeout

    def convert(self, **params):
        """
        Converts the given file and returns a dictionary with the conversion results. Requires the 'input' 
        and either 'url' or 'file' parameters to run. You can then use the values from the returned
        dictionary, or use methods like downloadResult().

        Args:
            input (str): The method of inputting a file. Examples are BuildVu.DOWNLOAD or BuildVu.UPLOAD
            file (str): (Optional) Location of the PDF to convert, i.e 'path/to/input.pdf'
            url (str): (Optional) The url for the server to download a PDF from

        Returns:
            dict [ of str: str ], The results of the conversion
        """
        if not self.base_endpoint:
            raise Exception('Error: Converter has not been setup. Please create an instance of the BuildVu'
                            ' class first.')

        try:
            uuid = self.__upload(params)
        except requests.exceptions.RequestException as error:
            raise Exception('Error uploading file: ' + str(error))

        # Check the conversion status once every second until complete or error / timeout
        count = 0
        while True:
            time.sleep(1)

            try:
                r = self.__poll_status(uuid)
            except requests.exceptions.RequestException as error:
                raise Exception('Error checking conversion status: ' + str(error))

            response = json.loads(r.text)

            if response['state'] == 'processed':
                break

            if response['state'] == 'error':
                raise Exception('The server ran into an error converting file, see server logs for '
                                'details.')
            if params.get('callbackUrl') is not None:
                break

            if count > self.convert_timeout:
                raise Exception('Failed: File took longer than ' + str(self.convert_timeout) +
                                ' seconds to convert')

            count += 1

        return response
        
    def downloadResult(self, results, output_file_path, file_name=None):
        """
        Downloads the zip file produced by the microservice. Provide '.' as the output_file_path
        if you wish to use the current directory. Will use the filename of the zip on the server
        if none is specified.

        Args:
            output_file_path (str): The output location to save the zip file to
            file_name (str): (Optional) The custom name for the zip file - Should not include .zip
        """
        download_url = results['downloadUrl']
        if file_name is not None:
            output_file_path += '/' + file_name + '.zip'
        else:
            output_file_path += '/' + download_url.split('/').pop()
        try:
            self.__download(download_url, output_file_path)
        except requests.exceptions.RequestException as error:
            raise Exception('Error downloading conversion output: ' + str(error))

    def __upload(self, params):
        # Private method for internal use
        # Upload the given file to be converted
        # Return the UUID string associated with conversion
        if 'input' in params and params['input'] == self.UPLOAD and 'file' in params:
            files = {'file': open(params['file'], 'rb')}
            del params['file']
        else:
            files = {}
        
        try:
            r = requests.post(self.endpoint, files=files, data=params, timeout=self.request_timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise Exception(error)

        response = json.loads(r.text)

        if response['uuid'] is None:
            raise Exception('The server ran into an error uploading file, see server logs for details')

        return response['uuid']

    def __poll_status(self, uuid):
        # Private method for internal use
        # Poll converter for status of conversion with given UUID
        # Returns response object
        try:
            r = requests.get(self.endpoint, params={'uuid': uuid}, timeout=self.request_timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise Exception(error)

        return r

    def __download(self, download_url, output_file_path):
        # Private method for internal use
        # Download the given resource to the given location
        try:
            r = requests.get(download_url, timeout=self.request_timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise Exception(error)

        if not r.ok:
            raise Exception('Failed: Status code ' + str(r.status_code) + ' for ' + download_url)

        with open(output_file_path, 'wb') as output_file:
            for chunk in r.iter_content(chunk_size=1024):
                output_file.write(chunk)
