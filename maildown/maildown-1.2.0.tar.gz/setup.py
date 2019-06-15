# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['maildown', 'maildown.backends']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0',
 'cleo>=0.7.2,<0.8.0',
 'coverage>=4.5,<5.0',
 'flake8>=3.7,<4.0',
 'jinja2>=2.10,<3.0',
 'mistune>=0.8.4,<0.9.0',
 'mock>=3.0,<4.0',
 'mypy>=0.701.0,<0.702.0',
 'premailer>=3.4,<4.0',
 'pygments>=2.3,<3.0',
 'pytest-cov>=2.7,<3.0',
 'requests>=2.21,<3.0',
 'sendgrid>=6.0,<7.0',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['maildown = maildown:run']}

setup_kwargs = {
    'name': 'maildown',
    'version': '1.2.0',
    'description': 'A super simple CLI for sending emails',
    'long_description': '[![Netlify Status](https://api.netlify.com/api/v1/badges/9d67273a-a51d-417b-bbad-291c237e5d8a/deploy-status)](https://app.netlify.com/sites/adoring-newton-752f36/deploys)\n![MIT license](https://img.shields.io/github/license/chris104957/maildown.svg)\n[![Coverage Status](https://coveralls.io/repos/github/chris104957/maildown/badge.svg?branch=master)](https://coveralls.io/github/chris104957/maildown?branch=master)\n[![Build Status](https://travis-ci.org/chris104957/maildown.svg?branch=master)](https://travis-ci.org/chris104957/maildown)\n[![GitSpo Mentions](https://gitspo.com/badges/mentions/chris104957/maildown?style=flat-square)](https://gitspo.com/mentions/chris104957/maildown)\n\n# Maildown\n\nA super simple CLI for sending emails\n\n## Introduction\n\nMaildown is a command line interface that lets you send emails with a minimum of fuss. It currently supports the AWS SES (default)\nand Sendgrid as email backends. Support for more email providers will be added in the future\n\n### Why can\'t I just use `boto3`/the SendGrid API?\n\nMaildown makes it easier to add structure and style to your email content. It supports **Markdown syntax** out of the box, meaning that you can just send Markdown files as emails with no additional effort.\n\n### How much does it cost?\n\nMaildown is open source and therefore completely free. However, it relies on third party services (e.g. AWS, SendGrid) to actually send your emails - these services aren\'t free,\nalhough they do have free limits depending on the number of emails you need to send\n\n## Installation and usage\n\n### Pre requisites\n\nIn order to use Maildown, you first need to create an account with one of the supported backend email providers:\n\n- **[AWS](https://aws.amazon.com)**\n\n   For AWS, you\'ll also realistically need to [take your AWS SES account out of the sandbox](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html)\n   \n- **[SendGrid](https://sendgrid.com/)**\n\n\n### Install with `pip`\n\nYou can install maildown as follows:\n```bash\npip install maildown\n```\n\n### Authenticating Maildown\n\nMaildown stores your credentials locally for convenience. Before you can use Maildown\'s features, you should run the `maildown init` command. By default, \n`maildown` uses the AWS backend:\n\n```bash\nmaildown init access_key=AWS_ACCESS_KEY_ID secret_key=AWS_SECRET_ACCESS_KEY\n```\n\nTo use the SendGrid API, you\'ll need to pass the `--backend=sendgrid` option with all commands:\n```bash\nmaildown init api_key=SENDGRID_API_KEY --backend=sendgrid\n```\n\n> If you have previously used the `aws cli` and have already run `aws configure`, or if you have set the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in your environment, you can just use `maildown init` with no arguments to store your credentials\n\n### Verify email addresses\n\nAmazon only lets you send emails from verified email addresses - In other words, you need to verify that you own your email address before you can send mails from it. You can either do this from the [SES console](https://console.aws.amazon.com/ses/home), or by using Maildown:\n\n```bash\n$ maildown verify christopherdavies553@gmail.com\nEmail sent to christopherdavies553@gmail.com. You must click the link in this email to verify ownership before you can send any emails\n```\n\nWhen you use the above command, AWS will send an email to the email address you provided. You\'ll need to click on the link to verify your ownership of the account. Once you\'ve done this, you can repeat the previous command to check the status\n\n```bash\n$ maildown verify christopherdavies553@gmail.com\nThis email address has already been verified\n```\n\nYou are now ready to start sending emails!\n\n.. note:\n    This command is AWS-specific - The SendGrid backend does not implement this feature\n\n## Sending emails\n\nYou can now send emails with the following command\n```bash\nmaildown send christopherdavies553@gmail.com "my email subject" -f "email.md" recipient1@gmail.com recipient2@gmail.com\n```\nThe above arguments, in order, are:\n- The sending email address (which must have been verified)\n- The subject line of your email\n- A markdown file containing some content to send. Note that you can also use the `-c` flag to pass string content to be sent directly to the email, e.g. `-c "hello"`\n- A list of email addresses to send the content to\n\n## Styling emails\n\nBy default, Maildown bakes in its own default style sheet when sending emails. This looks something like this (the below email is the content of this readme):\n\n![screenshot](https://raw.githubusercontent.com/chris104957/maildown/master/Screen%20Shot%202019-05-08%20at%2023.26.45.png)\n\nYou can apply your own styles by simply using the `--theme` flag when sending mails, like this:\n\n```bash\nmaildown send christopherdavies553@gmail.com "my email subject" -f "email.md" --theme "my-style.css" recipient1@gmail.com recipient2@gmail.com\n```\n\n',
    'author': 'Christopher Davies',
    'author_email': 'christopherdavies553@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
