from __future__ import print_function
from __future__ import division

import os
import six
import pkg_resources
import platform
import pytest
from civis.compat import TemporaryDirectory

if (six.PY2 or pkg_resources.parse_version(
        '.'.join(platform.python_version_tuple()[0:2]))
        == pkg_resources.parse_version('3.4')):
    import mock
else:
    from unittest import mock


@pytest.fixture
def client():
    client_mock = mock.MagicMock()
    client_mock.username = 'a'
    client_mock.credentials.list.return_value = [
        {'owner': 'a', 'id': 0},
        {'owner': 'b', 'id': 1}]

    return client_mock


@pytest.fixture()
def cleandir():
    cwd = os.getcwd()
    with TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(cwd)


@pytest.fixture()
def example_notebook():
    return r"""{
"cells": [
{
"cell_type": "code",
"execution_count": null,
"metadata": {
"collapsed": true
},
"outputs": [],
"source": [
"import sys\n",
"\n",
"%matplotlib inline\n",
"    %matplotlib notebook"
]
}
],
"metadata": {
"kernelspec": {
"display_name": "Python 3",
"language": "python",
"name": "python3"
},
"language_info": {
"codemirror_mode": {
"name": "ipython",
"version": 3
},
"file_extension": ".py",
"mimetype": "text/x-python",
"name": "python",
"nbconvert_exporter": "python",
"pygments_lexer": "ipython3",
"version": "3.6.1"
}
},
"nbformat": 4,
"nbformat_minor": 2
}
"""
