# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dscan']

package_data = \
{'': ['*']}

install_requires = \
['dnslib>=0.9.10,<0.10.0', 'requests>=2.22,<3.0', 'toml>=0.9,<0.10']

entry_points = \
{'console_scripts': ['dscan = dscan.cli:main']}

setup_kwargs = {
    'name': 'dscan',
    'version': '0.1.5',
    'description': 'dscan makes scanning a list of domains for DNS records easy!',
    'long_description': '# dscan\n\ndscan makes scanning a list of domains for DNS records easy!\n\n## Installation\n\nSimply run:\n\n    $ pip install dscan\n\n## Command Reference\n\n\tusage: dscan [-h] [--input INPUT] [--output OUTPUT] [--rrtype RRTYPE]\n\t\t\t\t[--single]\n\t\t\t\t[--provider {adguard,appliedprivacy,cleanbrowsing-family,cloudflare,commons.host,dnswarden,dnswarden-adblock,google,powerdns,quad9}]\n\t\t\t\t[--verbose]\n\t\t\t\t[domain]\n\n\tpositional arguments:\n\tdomain                domain name (single mode only)\n\n\toptional arguments:\n\t-h, --help            show this help message and exit\n\t--input INPUT, -i INPUT\n\t\t\t\t\t\t\tpath to list of domains (in plain text)\n\t--output OUTPUT, -o OUTPUT\n\t\t\t\t\t\t\tpath to output\n\t--rrtype RRTYPE, -r RRTYPE\n\t\t\t\t\t\t\trrtype to collate\n\t--single, -s          single domain mode\n\t--provider {adguard,appliedprivacy,cleanbrowsing-family,cloudflare,commons.host,dnswarden,dnswarden-adblock,google,powerdns,quad9}, -p {adguard,appliedprivacy,cleanbrowsing-family,cloudflare,commons.host,dnswarden,dnswarden-adblock,google,powerdns,quad9}\n\t\t\t\t\t\t\tdns provider to use\n\t--verbose, -v         increase output verbosity\n\n## License\n\nThis project has been developed by Matthew Gall. This project is hereby released under the terms of the MIT License, and is included below\n\n\tMIT License\n\n\tCopyright (c) 2019 Matthew Gall\n\n\tPermission is hereby granted, free of charge, to any person obtaining a copy\n\tof this software and associated documentation files (the "Software"), to deal\n\tin the Software without restriction, including without limitation the rights\n\tto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n\tcopies of the Software, and to permit persons to whom the Software is\n\tfurnished to do so, subject to the following conditions:\n\n\tThe above copyright notice and this permission notice shall be included in all\n\tcopies or substantial portions of the Software.\n\n\tTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n\tIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n\tFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n\tAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\tLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n\tOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n\tSOFTWARE.\n\n## Support\n\nHave a question? Need assistance? Don\'t stay stuck! If you do use this project or have any feedback we would love to hear from you, drop me an [e-mail](mailto:hello@matthewgall.com)',
    'author': 'Matthew Gall',
    'author_email': 'me@matthewgall.com',
    'url': 'https://codedin.wales/matthew/dscan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
}


setup(**setup_kwargs)
