# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['beedumper']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'click>=7.0,<8.0',
 'pathos>=0.2.3,<0.3.0',
 'requests>=2.21,<3.0']

entry_points = \
{'console_scripts': ['beedumper = beedumper.cli:cli']}

setup_kwargs = {
    'name': 'beedumper',
    'version': '0.1.4',
    'description': 'Exporting SupportBee data for better integration with other ticketing tools',
    'long_description': '# beedumper: backup your SupportBee data\n\nA tool to backup all your data from [SupportBee](https://supportbee.com) ticketing tool\n\n## Install\n\nThe package is published at PyPi as [beedumper](https://pypi.org/project/beedumper) so you can run `pip install beedumper` on your Python 3.6 environment to install the main command line interface. Alternatively you can also import  `beedumper.export.Exporter` class and work directly with the different methods outside the implemented [`cli`](https://github.com/CartoDB/beedumper/blob/master/beedumper/cli.py) logic.\n\n**Note**: This tool requires python 3.6 or later to run.\n\n## `beedumper` CLI command\n\n```txt\n$ beedumper -h\nUsage: beedumper [OPTIONS] COMMAND [ARGS]...\n\n  This command line tool helps you export your SupportBee account data.\n\nOptions:\n  -l, --loglevel [error|warn|info|debug]\n  -c, --config PATH               Defaults to current folder "config.yaml"\n  -v, --version                   Show the version and exit.\n  -h, --help                      Show this message and exit.\n\nCommands:\n  all                 Export all account info, both metadata and tickets\n  all-metadata        Export all metadata\n  all-tickets         Export all ticket info: tickets, replies, comments\n                      and...\n  emails              Exports the forwarding addresses\n  export-attachments  Exports all attachments from the tickets stored\n  export-comments     Exports all comments from the tickets stored\n  export-replies      Exports all replies from the tickets stored\n  export-tickets      Exports all tickets in a folder structure\n  labels              Exports the labels\n  snippets            Exports the snippets\n  teams               Exports the teams\n  users               Exports the users\n```\n\nCheck the [example configuration](https://github.com/CartoDB/beedumper/blob/master/config.template.yaml) to set up your `config.yaml` file with SupportBee credentials and other settings.\n\nSome subcommands may have further options, use `-h` to find out more about them.\n\n## Tickets storage\n\nThe tickets are stored under a folder `tickets` below your defined output directory. For each ticket a folder is created with its `id` under an intermediate folder that is the modulus of the id by `99`. That is, under tickets you\'ll eventually have folders running from `00` to `98` spreading the tickets approximately evenly over them.\n\nUnder each ticket folder you\'ll eventually end with this structure:\n\n* `ticket.json`: main information\n* `replies.json`: array of replies made to the requester\n* `comments.json`: comments made by agents\n* `attachments`: folder with attachment files by the original requester\n* `attachments_replies`: folder with attachments coming from the replies\n\n## Recommended usage\n\nIt\'s recommended to first run the simple subcommands like `users` or `labels` to test things work as expected. Then you can start with `export-tickets --since-date` passing a recent date to download only a few tickets. Then you can do the same with `export-replies`, `export-comments`, and `export-attachments` sequentially, as replies and comments are based on existing tickets, and attachments use both tickets and replies JSON files.\n\nIf there are no issues on downloading those recent assets, you can then run `all` to download the full dump of tickets information and in subsequent executions use the `--since-date` parameter to only download tickets with `last_activity_at` metadata older than the passed timestamp to keep your dump updated with recent changes.',
    'author': 'Jorge Sanz',
    'author_email': 'jsanz@carto.com',
    'url': 'https://github.com/CartoDB/beedumper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
