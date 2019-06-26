PACKAGE_NAME = "pyvss"

__version__ = '0.9.34'

API_ENDPOINT_BASE = 'https://cloud-api.eis.utoronto.ca'
VSKEY_STOR_ENDPOINT = 'https://vskey-stor.eis.utoronto.ca'
DATETIME_FMT = '%Y-%m-%d %H:%M'
VALID_VM_USAGE = [
    ('Production', 'Prod'),
    ('Testing', 'Test'),
    ('Development', 'Dev'),
    ('QA', 'QA'),
]
VALID_VM_BUILD_PROCESS = ['clone', 'template', 'image', 'os_install']
