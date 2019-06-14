# NOTE(Brian): This file was lifted from the tusclient package (https://github.com/tus/tus-py-client)
# @ 9f00aa2b187fc29c2b66d465df56efae2187d5e5. The only modifications include revising import statements
# and comments to account for new package name.  This code was imported into the code base (in lieu
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
from tus_client.uploader import Uploader


class TusClient(object):
    """
    Object representation of Tus client.

    :Attributes:
        - url (str):
            represents the tus server's create extension url. On instantiation this argument
            must be passed to the constructor.
        - headers (dict):
            This can be used to set the server specific headers. These headers would be sent
            along with every request made by the cleint to the server. This may be used to set
            authentication headers. These headers should not include headers required by tus
            protocol. If not set this defaults to an empty dictionary.

    :Constructor Args:
        - url (str)
        - headers (Optiional[dict])
    """

    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}

    # you can set authentication headers with this.
    def set_headers(self, headers):
        """
        Set tus client headers.

        Update and/or set new headers that would be sent along with every request made
        to the server.

        :Args:
            - headers (dict):
                key, value pairs of the headers to be set. This argument is required.
        """
        self.headers.update(headers)

    def uploader(self, *args, **kwargs):
        """
        Return uploader instance pointing at current client instance.

        Return uplaoder instance with which you can control the upload of a specific
        file. The current instance of the tus client is passed to the uploader on creation.

        :Args:
            see tus_client.uploader.Uploader for required and optional arguments.
        """
        kwargs['client'] = self
        return Uploader(*args, **kwargs)
