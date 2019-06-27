# pylint: disable=W0622
"""cubicweb-seda application packaging information"""

modname = 'seda'
distname = 'cubicweb-seda'

numversion = (0, 17, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Data Exchange Standard for Archival'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.25.4, < 3.27',
    'six': '>= 1.4.0',
    'cubicweb-eac': None,
    'cubicweb-skos': '>= 1.3.0',
    'cubicweb-compound': '>= 0.7',
    'cubicweb-relationwidget': '>= 0.4',
    'cubicweb-squareui': None,
    'pyxst': '>= 0.2',
    'rdflib': '>= 4.1',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
