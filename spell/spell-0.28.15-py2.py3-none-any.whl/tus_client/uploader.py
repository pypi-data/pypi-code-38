# NOTE(Brian): This file was lifted from the tusclient package (https://github.com/tus/tus-py-client)
# @ 9f00aa2b187fc29c2b66d465df56efae2187d5e5. The only modifications include:
#   - revising import statements and comments to account for new package name
#   - removing the store_url, url_storage, and fingerprinter parameters from the
#     Uploader class and revising the constructor and get_url methods to account
#     for their removal. These parameters were removed since the tusclient.url_storage and
#     tusclient.fingerprint packages are not used in our code base and thus not imported.
# This code was imported into the code base (in lieu of specifying tusclient as a dependency)
# because the tusclient package has very strict dependencies specified in the setup.py that precluded
# installing spell on many systems with more recent versions of common packages.
#
# Copyright (c) 2016 Ifedapo .A. Olarewaju
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
from __future__ import print_function
import os
import re
from base64 import b64encode
import time

from six import iteritems, b, wraps
from six.moves.urllib.parse import urljoin
import requests

from tus_client.exceptions import TusUploadFailed, TusCommunicationError
from tus_client.request import TusRequest


# Catches requests exceptions and throws custom tuspy errors.
def _catch_requests_error(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as error:
            raise TusCommunicationError(error)

    return _wrapper


class Uploader(object):
    """
    Object to control upload related functions.

    :Attributes:
        - file_path (str):
            This is the path(absolute/relative) to the file that is intended for upload
            to the tus server. On instantiation this attribute is required.
        - file_stream (file):
            As an alternative to the `file_path`, an instance of the file to be uploaded
            can be passed to the constructor as `file_stream`. Do note that either the
            `file_stream` or the `file_path` must be passed on instantiation.
        -  url (str):
            If the upload url for the file is known, it can be passed to the constructor.
            This may happen when you resume an upload.
        - client (<tus_client.client.TusClient>):
            An instance of `tus_client.client.TusClient`. This would tell the uploader instance
            what client it is operating with. Although this argument is optional, it is only
            optional if the 'url' argument is specified.
        - chunk_size (int):
            This tells the uploader what chunk size(in bytes) should be uploaded when the
            method `upload_chunk` is called. This defaults to 2 * 1024 * 1024 i.e 2mb if not
            specified.
        - metadata (dict):
            A dictionary containing the upload-metadata. This would be encoded internally
            by the method `encode_metadata` to conform with the tus protocol.
        - offset (int):
            The offset value of the upload indicates the current position of the file upload.
        - stop_at (int):
            At what offset value the upload should stop.
        - request (<tus_client.request.TusRequest>):
            A http Request instance of the last chunk uploaded.
        - retries (int):
            The number of attempts the uploader should make in the case of a failed upload.
            If not specified, it defaults to 0.
        - retry_delay (int):
            How long (in seconds) the uploader should wait before retrying a failed upload attempt.
            If not specified, it defaults to 30.
        - log_func (<function>):
            A logging function to be passed diagnostic messages during file uploads

    :Constructor Args:
        - file_path (str)
        - file_stream (Optional[file])
        - url (Optional[str])
        - client (Optional [<tus_client.client.TusClient>])
        - chunk_size (Optional[int])
        - metadata (Optional[dict])
        - retries (Optional[int])
        - retry_delay (Optional[int])
        - log_func (Optional [<function>])
    """
    DEFAULT_HEADERS = {"Tus-Resumable": "1.0.0"}
    DEFAULT_CHUNK_SIZE = 2 * 1024 * 1024  # 2MB

    def __init__(self, file_path=None, file_stream=None, url=None, client=None,
                 chunk_size=None, metadata=None, retries=0, retry_delay=30,
                 log_func=None):
        if file_path is None and file_stream is None:
            raise ValueError("Either 'file_path' or 'file_stream' cannot be None.")

        if url is None and client is None:
            raise ValueError("Either 'url' or 'client' cannot be None.")

        self.file_path = file_path
        self.file_stream = file_stream
        self.stop_at = self.file_size
        self.client = client
        self.metadata = metadata or {}
        self.url = url or self.get_url()
        self.offset = self.get_offset()
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.request = None
        self.retries = retries
        self._retried = 0
        self.retry_delay = retry_delay
        self.log_func = log_func

    # it is important to have this as a @property so it gets
    # updated client headers.
    @property
    def headers(self):
        """
        Return headers of the uploader instance. This would include the headers of the
        client instance.
        """
        client_headers = getattr(self.client, 'headers', {})
        return dict(self.DEFAULT_HEADERS, **client_headers)

    @property
    def headers_as_list(self):
        """
        Does the same as 'headers' except it is returned as a list.
        """
        headers = self.headers
        headers_list = ['{}: {}'.format(key, value) for key, value in iteritems(headers)]
        return headers_list

    @_catch_requests_error
    def get_offset(self):
        """
        Return offset from tus server.

        This is different from the instance attribute 'offset' because this makes an
        http request to the tus server to retrieve the offset.
        """
        resp = requests.head(self.url, headers=self.headers)
        offset = resp.headers.get('upload-offset')
        if offset is None:
            msg = 'Attempt to retrieve offset fails with status {}'.format(resp.status_code)
            raise TusCommunicationError(msg, resp.status_code, resp.content)
        return int(offset)

    def encode_metadata(self):
        """
        Return list of encoded metadata as defined by the Tus protocol.
        """
        encoded_list = []
        for key, value in iteritems(self.metadata):
            key_str = str(key)  # dict keys may be of any object type.

            # confirm that the key does not contain unwanted characters.
            if re.search(r'^$|[\s,]+', key_str):
                msg = 'Upload-metadata key "{}" cannot be empty nor contain spaces or commas.'
                raise ValueError(msg.format(key_str))

            value_bytes = b(value)  # python 3 only encodes bytes
            encoded_list.append('{} {}'.format(key_str, b64encode(value_bytes).decode('ascii')))
        return encoded_list

    def get_url(self):
        """
        Request a new upload url from the tus server.
        """
        return self.create_url()

    @_catch_requests_error
    def create_url(self):
        """
        Return upload url.

        Makes request to tus server to create a new upload url for the required file upload.
        """
        headers = self.headers
        headers['upload-length'] = str(self.file_size)
        headers['upload-metadata'] = ','.join(self.encode_metadata())
        resp = requests.post(self.client.url, headers=headers)
        url = resp.headers.get("location")
        if url is None:
            msg = 'Attempt to retrieve create file url with status {}'.format(resp.status_code)
            raise TusCommunicationError(msg, resp.status_code, resp.content)
        return urljoin(self.client.url, url)

    @property
    def request_length(self):
        """
        Return length of next chunk upload.
        """
        remainder = self.stop_at - self.offset
        return self.chunk_size if remainder > self.chunk_size else remainder

    def verify_upload(self):
        """
        Confirm that the last upload was sucessful.
        Raises TusUploadFailed exception if the upload was not sucessful.
        """
        if self.request.status_code == 204:
            return True
        else:
            raise TusUploadFailed('', self.request.status_code, self.request.response_content)

    def get_file_stream(self):
        """
        Return a file stream instance of the upload.
        """
        if self.file_stream:
            self.file_stream.seek(0)
            return self.file_stream
        elif os.path.isfile(self.file_path):
            return open(self.file_path, 'rb')
        else:
            raise ValueError("invalid file {}".format(self.file_path))

    @property
    def file_size(self):
        """
        Return size of the file.
        """
        stream = self.get_file_stream()
        stream.seek(0, os.SEEK_END)
        return stream.tell()

    def upload(self, stop_at=None):
        """
        Perform file upload.

        Performs continous upload of chunks of the file. The size uploaded at each cycle is
        the value of the attribute 'chunk_size'.

        :Args:
            - stop_at (Optional[int]):
                Determines at what offset value the upload should stop. If not specified this
                defaults to the file size.
        """
        self.stop_at = stop_at or self.file_size

        while self.offset < self.stop_at:
            self.upload_chunk()
        else:
            if self.log_func:
                self.log_func("maximum upload specified({} bytes) has been reached".format(self.stop_at))

    def upload_chunk(self):
        """
        Upload chunk of file.
        """
        self._retried = 0
        self._do_request()
        self.offset = int(self.request.response_headers.get('upload-offset'))
        if self.log_func:
            msg = '{} bytes uploaded ...'.format(self.offset)
            self.log_func(msg)

    def _do_request(self):
        # TODO: Maybe the request should not be re-created everytime.
        #      The request handle could be left open until upload is done instead.
        self.request = TusRequest(self)
        try:
            self.request.perform()
            self.verify_upload()
        except TusUploadFailed as error:
            self.request.close()
            self._retry_or_cry(error)
        finally:
            self.request.close()

    def _retry_or_cry(self, error):
        if self.retries > self._retried:
            time.sleep(self.retry_delay)

            self._retried += 1
            try:
                self.offset = self.get_offset()
            except TusCommunicationError as e:
                self._retry_or_cry(e)
            else:
                self._do_request()
        else:
            raise error
