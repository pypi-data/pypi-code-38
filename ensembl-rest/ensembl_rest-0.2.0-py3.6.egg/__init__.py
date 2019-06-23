from .ensemblclient import EnsemblClient, _api_table
from .core import HTTPError, InvalidResponseError, _endpoint_docstring
from .assemblymapper import AssemblyMapper
from .utils import region_str

_default_client = EnsemblClient()

for endpoint_name, endpoint_data in _api_table['endpoints'].items():
    docstring = _endpoint_docstring(endpoint_data)
    exec(f"def {endpoint_name}(*args, **kwargs):                    \n"
         f"    '''                                                  \n"
         f"    {docstring}                                          \n"
         f"    '''                                                  \n"
         f"    return _default_client.{endpoint_name}(*args, **kwargs)"
    )