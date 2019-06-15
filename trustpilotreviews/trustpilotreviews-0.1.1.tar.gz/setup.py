# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['trustpilotreviews']

package_data = \
{'': ['*']}

install_requires = \
['dataset>=1.1,<2.0',
 'numpy>=1.15,<2.0',
 'pandas>=0.23.0,<0.24.0',
 'requests>=2.20,<3.0',
 'stuf>=0.9.16,<0.10.0']

setup_kwargs = {
    'name': 'trustpilotreviews',
    'version': '0.1.1',
    'description': 'Unoffice TrustPilot API to download reviews scores and contents',
    'long_description': "# TrustPilotReader\nUnofficial TrustPilot reviews collector. For Academic Use Only. READ: [TrustPilot Terms of Use](https://legal.trustpilot.com/end-user-terms-and-conditions)\n\n# Disclamer:\nYou, and you alone, are responsible for following TrustPilot terms and using this tool to gather their data. Respect\ntheir servers and be thoughtful when gathering large amount of data. \n\n\n# Unmatured Documetation :)\n\nThis code implements basic data scraping of TrustPilot [default:Danish] Reviews .\n\nIt is a prototype to be used for academic reasons only.\nTrustPilot offers APIs to gather their data\n \n# Get it from PyPI\n```bash\npip install trustpilotreviews\n```\n\n\n# How to use it:\n\nImport package\n\n```python\nfrom trustpilotreviews import GetReviews\n```\n\n# 1. Initiat Class \n\nInitiate the class with either (a) passing a dictionary of companies as keys\nand companies TrustPilot id as items or (b) adding them with dictionary syntax.\n\ne.g.\n```python\n# way a\nid_dict = {'Skat':'470bce96000064000501e32d','DR':'4690598c00006400050003ee'}\nd = GetReviews(id_dict)\n\n# ids dictionary can be loaded from text files e.g.\nlines = np.genfromtxt('companies_ids.csv', delimiter=',',\n                            dtype=str,skip_header=1) #skipped header\ncsv_dict = {key:item for key, item in lines}\nd = GetReviews(csv_dict)\n\n# way b \nd = GetReviews()\nd['Skat'] = '470bce96000064000501e32d'\n```\n        \nNo business ids, no problem:\n```python\nfrom trustpilotreviews import GetReviews\nt = GetReviews()\nmate_id = t.get_id('www.mate.bike')\nif mate_id.ok:\n    print(mate.business_id)\n\ndata = t.get_reviews() \n    \n ```\n \n Having multiple websites, well, no problem:\n \n ```python\nfrom trustpilotreviews import GetReviews\nt = GetReviews()\nids = t.get_ids(['www.ford.dk','www.mate.bike'])\nprint(ids) # same as print(t) as ids are added to que\n\ndata = t.get_reviews() # mine data for those ids    \n ```\n\nWant to save it on a database instead of Pandas, done:\n\n ```python\nfrom trustpilotreviews import GetReviews\nt = GetReviews()\nids = t.get_ids(['www.ford.dk','www.mate.bike'])\n\n# mine data for those ids \nt.get_reviews()\n\n# send them to in memory database\nt.send_db('../data/','reviews')   \n ```\n \n \n## 2. Reading Data\n\n\n```python\ndf = pd.DataFrame(t.dictData)\n```\nor from stored source\n\n```python\ndf = pd.read_pickle('TrustPilotData.pkl')\n```\n# A full example:\n\n```python\nimport numpy as np\nfrom trustpilotreviews import GetReviews\n\n\n# Dictionary from Data \nlines = np.genfromtxt('companies_ids.csv', delimiter=',',\n                      dtype=str, skip_header=1)\ncsv_dict = {key: item for key, item in lines}\n\nd = GetReviews(csv_dict) # Select no for Norwegian Reviews\nd.gather_data() \nd.save_data(file_name='NoTrustPilotData')\n```\n\n# TODOs:\n   * Allow different saving formats e.g. df.to_XXX\n   * Split page_review funciton into connection and data parsing (better way to handler bad requests)\n   * Add more features\n   * Write a better documetation\n\n## [TrustPilot Terms of Use](https://legal.trustpilot.com/end-user-terms-and-conditions)\n\n![c091684c-879c-4d6e-90c6-92fbc53cb676](https://user-images.githubusercontent.com/14926709/43354373-980e2882-924b-11e8-8b85-237f3e4b1dde.jpeg)\n",
    'author': 'Prayson Wilfred Daniel',
    'author_email': 'praysonwilfred@gmail.com',
    'url': 'https://github.com/Proteusiq/TrustPilotReader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
