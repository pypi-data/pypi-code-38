# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.cli.core.util import CLIError


class MlCliError(CLIError):
    def __init__(self, error, headers=None, content=None, status_code=None):
        self.error = error
        self.headers = dict(headers) if headers else None
        self.content = content
        self.status_code = status_code
        super(MlCliError, self).__init__(self.to_json())

    def to_json(self):
        result = {'Error': self.error}
        if self.headers:
            result['Response Headers'] = self.headers
        if self.content:
            result['Response Content'] = self.content
        if self.status_code:
            result['Response Code'] = self.status_code
        return result
