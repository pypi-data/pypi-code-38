# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['chuck_says']

package_data = \
{'': ['*'], 'chuck_says': ['assets/*']}

install_requires = \
['click>=7.0,<8.0', 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['chuck = chuck_says.cli:main']}

setup_kwargs = {
    'name': 'chuck-says',
    'version': '0.1.1',
    'description': 'Cowsay Chuck Norris Facts',
    'long_description': '# Chuck Norris Facts... in your TERMINAL.\n\nBecause, who wouldn\'t want that? You better...\n\nGet your day started as soon you see that sweet Chuck Norris fact of the day in your terminal; there\'s more than 600+ facts here, baby!\nThey\'re all real... allegedly.\n\n_This package was completely made to write a blog post. It\'s not meant to be a \'real\' project. It\'s fun though._\n_You can check out the post at: https://codingdose.info/2019/06/08/create-a-project-page-for-your-repositories-easily-with-Jekyll/_\n\n# Installation and Usage\n\nInstall this package right now before Chuck installs his foot on your face.\n```bash\n$ pip install --user chuck-says\n```\n\nWorried about how to execute it before Chuck executes you? Just call **Chuck**!\n\n```\n# Automatically add Cowsay\n$ chuck\n  ________________________________________\n/ Chuck Norris doesn\'t need a debugger, he \\\n| just stares down the bug until the code  |\n\\ confesses.                               /\n  ----------------------------------------\n         \\   ^__^\n          \\  (oo)\\_______\n             (__)\\       )\\/\\\n                 ||----w |\n                 ||     ||\n\n# Output fact only if you want to integrate it with another \'cow\'\n$ chuck -n | cowsay -f eyes\n _______________________________________\n/ Chuck Norris has never won an Academy \\\n| Award for acting... because he\'s not  |\n\\ acting.                               /\n ---------------------------------------\n    \\\n     \\\n                                   .::!!!!!!!:.\n  .!!!!!:.                        .:!!!!!!!!!!!!\n  ~~~~!!!!!!.                 .:!!!!!!!!!UWWW$$$\n      :$$NWX!!:           .:!!!!!!XUWW$$$$$$$$$P\n      $$$$$##WX!:      .<!!!!UW$$$$"  $$$$$$$$#\n      $$$$$  $$$UX   :!!UW$$$$$$$$$   4$$$$$*\n      ^$$$B  $$$$\\     $$$$$$$$$$$$   d$$R"\n        "*$bd$$$$      \'*$$$$$$$$$$$o+#"\n             """"          """""""\n```\n\nTo have a fun fact whenever you open your terminal just edit your shell configuration file.\nFor Bash:\n```bash\necho chuck >> ~/.bashrc\n```\n\nFor Fish:\n```fish\n# Edit your fish_greeting function\n~ function fish_greeting\n             chuck\n  end\n\n# And save it\n~ funcsave fish_greeting\n```\n\n# Collaboration\n\nWant to add a fact? Are you a first timer and want to make your first pull request? Is my coding style a piece of garbage that makes your eyes bleed? Fear not!\n1. Get that fork going, boy.\n2. Make your changes in the **develop** branch.\n3. Make a pull request including your changes.\n\nBoom, your done, get that approved pull request into your CV right now goddammit.\n\n# How it works\n\nWho the hell knows? I just made this yesterday.\n',
    'author': 'Franccesco Orozco',
    'author_email': 'franccesco@codingdose.info',
    'url': 'https://franccesco.github.io/chuck-says',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
