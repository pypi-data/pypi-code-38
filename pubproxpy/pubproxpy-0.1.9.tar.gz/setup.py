# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pubproxpy']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'pubproxpy',
    'version': '0.1.9',
    'description': 'An easy to use Python wrapper for pubproxy.com',
    'long_description': '# Pubproxpy\n\nAn easy to use Python wrapper for [pubproxy](http://pubproxy.com)\'s public proxy API.\n\n## Installation\n\nInstall the pybproxpy package using your standard Python package manager e.g.\n\n```bash\n$ pip install pubproxpy\n```\n\n## Keyless API Limitations\n\n### API Daily Limits\n\nAt the time of writing this, without an API key the pubproxy API limits users to 5 proxies per request and 50 requests per day. The maximum proxies per request is always used to minimize rate limiting along with getting the most proxies possible within the request limit.\n\n### API Rate Limiting\n\nWithout an API key pubproxy limits users to one request per second so a `ProxyFetcher` will try to ensure that at most only one request per second is done without an API key. This is synchronized between `ProxyFetcher`s, but this is not thread safe so make sure all `ProxyFetcher`s are on the same thread if you have no API key. The rate limiting is quite severe, upon being hit the API seems to deny requests for several minutes/hours.\n\n## Quickstart Example\n\n```python\nfrom pubproxpy import ProxyFetcher\n\n# ProxyFetcher for proxies that support https, are elite anonymity level,\n# and connected in 15 seconds or less\nhttp_pf = ProxyFetcher(protocol="http", https=True, level="elite",\n                       time_to_connect=15)\n\n# ProxyFetcher for proxies that use the socks5 protocol, are located in\n# the US or Canada and support POST requests\nsocks_pf = ProxyFetcher(protocol="socks5", countries=["US", "CA"], post=True)\n\n# Get and print 10 of each kind of proxy, even though there are multiple\n# `ProxyFetcher`s, the delays will be coordinated to prevent rate limiting\nfor _ in range(10):\n    https_proxy = http_pf.get_proxy()\n    socks_proxy = socks_pf.get_proxy()\n\n    # Do something with the proxies, like spawn worker threads that use them\n```\n\n### Advanced Example\n\n```python\nfrom pubproxpy import ProxyFetcher\n\n# Get a single elite proxy from France\npf = ProxyFetcher(level="elite", countries="FR")\nelite_proxy = pf.get_proxy()\n\n# Now get 20 elite proxies from anywhere except France and Ireland that support\n# post requests\n# NOTE: setting `not_countries` will remove `countries` since they\'re\n#       incompatible\npf.update_params(post=True, not_countries=["FR", "IE"])\nanon_proxies = pf.get_proxies(20)\n```\n\n## Documentation\n\nGetting proxies is fully handled by the `ProxyFetcher` class. There are several parameters you can pass on initialization, by using `set_params`, or by using `update_params` to narrow down the proxies to a suitable range. From there you can just call `get_proxy` to receive a proxy in the form of `{ip-address}:{port-number}` or call `get_proxies(amount)` to receive a list of `amount` proxies. Also there is an internal blacklist to ensure that the same proxy ip and port combo will not be used more than once per `ProxyFetcher`.\n\n### `ProxyFetcher` Parameters\n\n|Parameter|Type|Description|\n|:--|:--|:--|\n|`api_key`|`int`|API key for a paid account, you can also set `$PUBPROXY_API_KEY` to pass your key, passing the `api_key` parameter will override this|\n|`level`|`str`|[Options: anonymous, elite] Proxy anonymity level|\n|`protocol`|`str`|[Options: http, socks4, socks5] The proxy protocol|\n|`countries`|`str` or `list<str>`|locations of the proxy using the [ISO-3166 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code, **Incompatible with `not_countries`**|\n|`not_countries`|`str` or `list<str>`|blacklist locations of the proxy using the [ISO-3166 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code, **Incompatible with `countries`**|\n|`last_checked`|`int`|[Bounds: 1-1000] Minutes since the proxy was checked|\n|`port`|`int`|Proxies using a specific port|\n|`time_to_connect`|`int`|[Bounds: 1-60] How many seconds it took for the proxy to connect|\n|`cookies`|`bool`|Supports requests with cookies|\n|`google`|`bool`|Can connect to Google|\n|`https`|`bool`|Supports https requests|\n|`post`|`bool`|Supports post requests|\n|`referer`|`bool`|Supports referer requests|\n|`user_agent`|`bool`|Supports user-agent requests|\n',
    'author': 'LovecraftianHorror',
    'author_email': 'LovecraftianHorror@pm.me',
    'url': 'https://github.com/LovecraftianHorror/pubproxpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
