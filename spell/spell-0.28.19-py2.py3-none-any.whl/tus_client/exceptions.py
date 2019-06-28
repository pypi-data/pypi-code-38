# NOTE(Brian): This file was lifted from the tusclient package (https://github.com/tus/tus-py-client)
# @ 9f00aa2b187fc29c2b66d465df56efae2187d5e5.  This code was imported into the code base (in lieu
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
"""
Global Tusclient exception and warning classes.
"""


class TusCommunicationError(Exception):
    """
    Should be raised when communications with tus-server behaves
    unexpectedly.

    :Attributes:
        - message (str):
            Main message of the exception
        - status_code (int):
            Status code of response indicating an error
        - response_content (str):
            Content of response indicating an error
    :Constructor Args:
        - message (Optional[str])
        - status_code (Optional[int])
        - response_content (Optional[str])
    """
    def __init__(self, message, status_code=None, response_content=None):
        default_message = 'Communication with tus sever failed with status {}'.format(status_code)
        message = message or default_message
        super(TusCommunicationError, self).__init__(message)
        self.status_code = status_code
        self.response_content = response_content


class TusUploadFailed(TusCommunicationError):
    """Should be raised when an attempted upload fails"""
    pass
