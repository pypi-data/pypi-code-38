# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# Revised BSD License, included in this distribution as LICENSE

"""

"""

from rowgenerators.appurl.file.file import FileUrl


class JupyterNotebookUrl(FileUrl):
    """IPYthon Notebook URL"""

    match_priority = FileUrl.match_priority - 10

    def __init__(self, url=None, **kwargs):
        kwargs['proto'] = 'ipynb'
        super().__init__(url, **kwargs)

    @classmethod
    def _match(cls, url, **kwargs):
        return url.resource_format == 'ipynb'

    def get_target(self):
        return self

    def target_dataframe(self):
        return self.target_file


