# NOTE(Brian): This file was lifted from the tusclient package (https://github.com/tus/tus-py-client)
# @ 9f00aa2b187fc29c2b66d465df56efae2187d5e5. The only modifications include revising import statements
# and comments to account for new package name. This code was imported into the code base (in lieu
# of specifying tusclient as a dependency) because the tusclient package has very strict dependencies
# specified in the setup.py that precluded installing spell on many systems with more recent
# versions of common packages.
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
import http.client
import errno
from future.moves.urllib.parse import urlparse

from tus_client.exceptions import TusUploadFailed


class TusRequest(object):
    """
    Http Request Abstraction.

    Sets up tus custom http request on instantiation.

    requires argument 'uploader' an instance of tus_client.uploader.Uploader
    on instantiation.

    :Attributes:
        - handle (<http.client.HTTPConnection>)
        - response_headers (dict)
        - file (file):
            The file that is being uploaded.
    """

    def __init__(self, uploader):
        url = urlparse(uploader.url)
        if url.scheme == 'https':
            self.handle = http.client.HTTPSConnection(url.hostname, url.port)
        else:
            self.handle = http.client.HTTPConnection(url.hostname, url.port)
        self._url = url

        self.response_headers = {}
        self.status_code = None
        self.file = uploader.get_file_stream()
        self.file.seek(uploader.offset)

        self._request_headers = {
            'upload-offset': uploader.offset,
            'Content-Type': 'application/offset+octet-stream'
        }
        self._request_headers.update(uploader.headers)
        self._content_length = uploader.request_length
        self._response = None

    @property
    def response_content(self):
        """
        Return response data
        """
        return self._response.read()

    def perform(self):
        """
        Perform actual request.
        """
        try:
            host = '{}://{}'.format(self._url.scheme, self._url.netloc)
            path = self._url.geturl().replace(host, '', 1)

            self.handle.request("PATCH", path, self.file.read(self._content_length), self._request_headers)
            self._response = self.handle.getresponse()
            self.status_code = self._response.status
            self.response_headers = {k.lower(): v for k, v in self._response.getheaders()}
        except http.client.HTTPException as e:
            raise TusUploadFailed(e)
        # wrap connection related errors not raised by the http.client.HTTP(S)Connection
        # as TusUploadFailed exceptions to enable retries
        except OSError as e:
            if e.errno in (errno.EPIPE, errno.ESHUTDOWN, errno.ECONNABORTED, errno.ECONNREFUSED, errno.ECONNRESET):
                raise TusUploadFailed(e)
            raise e

    def close(self):
        """
        close request handle and end request session
        """
        self.handle.close()
