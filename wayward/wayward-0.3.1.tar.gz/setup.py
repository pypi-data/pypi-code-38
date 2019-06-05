# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wayward']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.15,<2.0']

setup_kwargs = {
    'name': 'wayward',
    'version': '0.3.1',
    'description': 'Wayward is a Python package that helps to identify characteristic terms from single documents or groups of documents.',
    'long_description': 'Wayward\n=======\n\n**Wayward** is a Python package that helps to identify characteristic terms from\nsingle documents or groups of documents. It can be used to create word clouds.\n\nRather than use simple term frequency, it weighs terms by statistical models\nknown as *parsimonious language models*. These models are good at picking up\nthe terms that distinguish a text document from other documents in a\ncollection.\n\nFor this to work, a preferably large amount of documents are needed\nto serve as a background collection, to compare the documents of interest to.\nThis could be a random sample of newspaper articles, for instance, but for many\napplications it works better to take a natural collection, such as a periodical\npublication, and to fit the model for separate parts (e.g. individual issues,\nor yearly groups of issues).\n\nSee the `References`_ section for more information about parsimonious\nlanguage models and their applications.\n\nWayward does not do visualization of word clouds. For that, you can paste\nits output into a tool like http://wordle.net or the `IBM Word-Cloud Generator\n<http://www.alphaworks.ibm.com/tech/wordcloud>`_.\n\n\nInstallation\n------------\n\nEither install the latest release from PyPI::\n\n    pip install wayward\n\nor clone the git repository, and use `Poetry <https://poetry.eustace.io/docs/>`_\nto install the package in editable mode::\n\n    git clone https://github.com/aolieman/wayward.git\n    cd wayward/\n    poetry install\n\nUsage\n-----\n>>> quotes = [\n...     "Love all, trust a few, Do wrong to none",\n...     ...\n...     "A lover\'s eyes will gaze an eagle blind. "\n...     "A lover\'s ear will hear the lowest sound.",\n... ]\n>>> doc_tokens = [\n...     re.sub(r"[.,:;!?\\"‘’]|\'s\\b", " ", quote).lower().split()\n...     for quote in quotes\n... ]\n\nThe ``ParsimoniousLM`` is initialized with all document tokens as a\nbackground corpus, and subsequently takes a single document\'s tokens\nas input. Its ``top`` method returns the top terms and their probabilities:\n\n>>> from wayward import ParsimoniousLM\n>>> plm = ParsimoniousLM(doc_tokens, w=.1)\n>>> plm.top(10, doc_tokens[-1])\n[(\'lover\', 0.1538461408077277),\n (\'will\', 0.1538461408077277),\n (\'eyes\', 0.0769230704038643),\n (\'gaze\', 0.0769230704038643),\n (\'an\', 0.0769230704038643),\n (\'eagle\', 0.0769230704038643),\n (\'blind\', 0.0769230704038643),\n (\'ear\', 0.0769230704038643),\n (\'hear\', 0.0769230704038643),\n (\'lowest\', 0.0769230704038643)]\n\nThe ``SignificantWordsLM`` is similarly initialized with a background corpus,\nbut subsequently takes a group of document tokens as input. Its ``group_top``\nmethod returns the top terms and their probabilities:\n\n>>> from wayward import SignificantWordsLM\n>>> swlm = SignificantWordsLM(doc_tokens, lambdas=(.7, .1, .2))\n>>> swlm.group_top(10, doc_tokens[-3:])\n[(\'in\', 0.37875318027881),\n (\'is\', 0.07195732361699828),\n (\'mortal\', 0.07195732361699828),\n (\'nature\', 0.07195732361699828),\n (\'all\', 0.07110584778711342),\n (\'we\', 0.03597866180849914),\n (\'true\', 0.03597866180849914),\n (\'lovers\', 0.03597866180849914),\n (\'strange\', 0.03597866180849914),\n (\'capers\', 0.03597866180849914)]\n\nSee ``example/dickens.py`` for a running example with more realistic data.\n\nBackground\n----------\nThis package started out as `WeighWords <https://github.com/larsmans/weighwords/>`_,\nwritten by Lars Buitinck at the University of Amsterdam. It provides an efficient\nparsimonious LM implementation, and a very accessible API.\n\nA recent innovation in language modeling, Significant Words Language\nModels, led to the addition of a two-way parsimonious language model to this package.\nThis new version targets python\xa03.x, and after a long slumber deserved a fresh name.\nThe name "Wayward" was chosen because it is a near-homophone of WeighWords, and as\na nod to parsimonious language modeling: it uncovers which terms "depart" most from\nthe background collection. The parsimonization algorithm discounts terms that are\nalready well explained by the background model, until the most wayward terms come\nout on top.\n\nReferences\n----------\nD. Hiemstra, S. Robertson, and H. Zaragoza (2004). `Parsimonious Language Models\nfor Information Retrieval\n<http://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.4.5806>`_.\nProc. SIGIR\'04.\n\nR. Kaptein, D. Hiemstra, and J. Kamps (2010). `How different are Language Models\nand word clouds? <http://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.189.822>`_.\nProc. ECIR\'10.\n\nM. Dehghani, H. Azarbonyad, J. Kamps, D. Hiemstra, and M. Marx (2016).\n`Luhn Revisited: Significant Words Language Models\n<https://djoerdhiemstra.com/wp-content/uploads/cikm2016.pdf>`_.\nProc. CKIM\'16.\n',
    'author': 'Alex Olieman',
    'author_email': 'alex@olieman.net',
    'url': 'https://github.com/aolieman/weighwords',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
