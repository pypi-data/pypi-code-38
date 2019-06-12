# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['googledrivefs']

package_data = \
{'': ['*']}

install_requires = \
['fs>=2.0.7', 'google-api-python-client>=1.6.3', 'google-auth>=1.5.1']

entry_points = \
{'fs.opener': ['googledrive = fs.googledrivefs.opener:GoogleDriveFSOpener']}

setup_kwargs = {
    'name': 'fs.googledrivefs',
    'version': '1.0.3',
    'description': 'Pyfilesystem2 implementation for Google Drive',
    'long_description': 'fs.googledrivefs\n================\n\n.. image:: https://travis-ci.org/rkhwaja/fs.googledrivefs.svg?branch=master\n    :target: https://travis-ci.org/rkhwaja/fs.googledrivefs \n\n.. image:: https://coveralls.io/repos/github/rkhwaja/fs.googledrivefs/badge.svg?branch=master\n    :target: https://coveralls.io/github/rkhwaja/fs.googledrivefs?branch=master\n\n\nImplementation of pyfilesystem2 file system for Google Drive\n\nUsage\n=====\n\n.. code-block:: python\n\n  fs = GoogleDriveFS(credentials=<google-auth credentials>)\n\n  # fs is now a standard pyfilesystem2 file system\n\n  fs2 = open_fs("googledrive:///?access_token=<oauth2 access token>&refresh_token=<oauth2 refresh token>&client_id=<oauth2 client id>&client_secret=<oauth2 client_secret>")\n\n  # fs2 is now a standard pyfilesystem2 file system\n\nRunning tests\n=============\n\nTo run the tests, set the following environment variables:\n\nGOOGLEDRIVEFS_TEST_CREDENTIALS_PATH - path to a json file which will contain the credentials\nGOOGLEDRIVEFS_TEST_CLIENT_ID - your client id (see Google Developer Console)\nGOOGLEDRIVEFS_TEST_CLIENT_SECRET - your client secret (see Google Developer Console)\n\nThen generate the credentials json file by running\n\n.. code-block:: bash\n\n  python generate-credentials.py\n\nThen run the tests by executing\n\n.. code-block:: bash\n\n  pytest\n\nin the root directory. The tests may take an hour or two to complete. They create and destroy many, many files and directories exclusively under the /test-googledrivefs directory in the user\'s Google Drive\n',
    'author': 'Rehan Khwaja',
    'author_email': 'rehan@khwaja.name',
    'url': 'https://github.com/rkhwaja/fs.googledrivefs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
