# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aws_utilities']

package_data = \
{'': ['*']}

install_requires = \
['ansiwrap>=0.8.4,<0.9.0',
 'boto3>=1.9,<2.0',
 'colorama>=0.4.1,<0.5.0',
 'docopt>=0.6.2,<0.7.0',
 'ec2-metadata>=2.0,<3.0',
 'eventlet>=0.24.1,<0.25.0',
 'tenacity>=5.0,<6.0',
 'urllib3>=1.24,<1.25']

entry_points = \
{'console_scripts': ['pending_stack_resources = '
                     'aws_utilities.pending_stack_resources:main',
                     'tail_cloudwatch_logs = '
                     'aws_utilities.tail_cloudwatch_logs:main',
                     'tail_stack_events = aws_utilities.tail_stack_events:main',
                     'wait_for_stack_complete = '
                     'aws_utilities.wait_for_stack_complete:main',
                     'watch_resource = aws_utilities.watch_resource:main']}

setup_kwargs = {
    'name': 'aws-utilities',
    'version': '1.3.1',
    'description': 'Utilities for use with aws.',
    'long_description': "# aws-utilities\n\nThis package includes various command-line utilities for use with aws.\n\n## Installation\n### pip\n```\npip install aws-utilities\n```\n\n### pipx\n```\npipx install aws-utilities\n```\n\n### git\nTo set up a local checkout with [pyenv](https://github.com/pyenv/pyenv) run these commands:\n```\ngit clone https://github.com/reversefold/aws-utilities.git\ncd aws-utilities\npyenv virtualenv 3.6.5 aws-utilities\npyenv local aws-utilities\npip install -r dev-requirements.txt\n./sync-requirements.sh\n```\n\n## Scripts\n### tail_cloudwatch_logs.py\n\nGet the last `n` lines of a cloudwatch log group and follow the output in realtime as it is written to CloudWatch Logs. Has the ability to use any profile set up in your `~/.aws/credentials` so working across multiple accounts is easy.\n\nInspired by [cw](https://github.com/lucagrulla/cw).\n\n\n### tail_stack_events.py\n\nGet the last `n` events for a CloudFormation stack and all of its nested stacks and follow the events in realtime. This utility can give you a view into all of the events happening in any size CloudFormation stack, even if it has multiple levels of nested stacks. When this script is started up it finds all nested stacks and follows their events as well if the stack is in any status which includes IN_PROGRESS. When following stack events, nested stacks will be dynamically added to and removed from the set of stacks being queried for events as nested stacks go into the various `IN_PROGRESS` and `COMPLETE` states. This lets you get a complete picture of what is going on while also making the minimum number of API calls.\n\nIn postmortem mode this script will find the events that caused the last stack update to fail. It will follow nested stack failures until it finds the specific resource that caused the failure.\n\nOriginally inspired by [tail-stack-events](https://github.com/tmont/tail-stack-events) and [cfn-tail](https://github.com/taimos/cfn-tail).\n\n\n### aws_switch.py\n\nA quick and dirty script to make any one of your configured aws profiles the default profile. Useful when you're using tools which don't support profiles or when you work in distinct profiles at distinct times.\n\n\n### wait_for_stack_complete.py\n\nA simple script for running on an ec2 instance. No parameters are taken. Finds the CloudFormation stack that the instance resides in and polls until the stack is in a `COMPLETE` state. If the stack has a parent stack it will watch that one instead. Has retries with exponential backoff (up to 5m) for all API calls so as to not overload the AWS APIs when used in a large environment. This script is particularly useful for UserData or cfn-init scripts which need to wait for other resources to be created and attached, such as EBS volumes not included in the instance's BlockDeviceMapping.\n",
    'author': 'Justin Patrin',
    'author_email': 'papercrane@reversefold.com',
    'url': 'https://github.com/reversefold/aws-utilities',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
