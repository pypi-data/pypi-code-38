# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pydantic_requests']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=0.25.0', 'requests>=2.21']

setup_kwargs = {
    'name': 'pydantic-requests',
    'version': '0.1.2',
    'description': 'A pydantic integration with requests.',
    'long_description': '# Marriage of Pydantic and Requests\n\nA helper that integrates Pydantic with requests library for seamless access to defined Models.\n\n## Example\n\n```python\nfrom enum import Enum\nfrom pydantic import BaseModel\nfrom pydantic_requests import PydanticSession\n\n\nclass DNSStatus(Enum):\n    """DNS OP response codes.\n    ref: https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-6\n    """\n\n    # No Error = 0\n    NoError = 0\n\n    # Format Error = 1\n    FormErr = 1\n\n    # Server Failure\n    ServFail = 2\n\n    # Non-Existent Domain\n    NXDomain = 3\n\n\nclass DNSQuery(BaseModel):\n    Status: DNSStatus\n\n    class Config:\n        """Configure DNS query."""\n\n        allow_mutation = False\n        arbitrary_types_allowed = True\n\n\nwith PydanticSession(\n    {200: DNSQuery}, headers={"accept": "application/dns-json"}\n) as session:\n    domain = "dz0ny.xyz"\n    res = session.get(\n        "https://cloudflare-dns.com/dns-query", params={"name": domain, "type": "NS"}\n    )\n    res.raise_for_status()\n    query: DNSQuery = res.model\n    if query.Status != DNSStatus.NXDomain:\n        print("Domain is registered.")\n    else:\n        print("Domain is registered.")\n\n```',
    'author': 'Janez Troha',
    'author_email': 'dz0ny@ubuntu.si',
    'url': 'https://github.com/dz0ny/pydantic-requests',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
