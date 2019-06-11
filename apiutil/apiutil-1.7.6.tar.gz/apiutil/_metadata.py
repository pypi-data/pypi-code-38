# encoding: utf-8

# Variables for setup (these must be string only!)
__module_name__ = u'apiutil'
__description__ = u'Boiler plate for coding against APIs.'

__version__ = u'1.7.6'

__author__ = u'Oli Davis'
__authorshort__ = u'OWBD'
__authoremail__ = u'oli.davis@me.com'

__license__ = u'MIT'

__githost__ = u'bitbucket.org'
__gituser__ = u'davisowb'
__gitrepo__ = u'apiutil.git'


# Additional variables
__copyright__ = u'Copyright (C) 2018 {author}'.format(author=__author__)

__url__ = u'https://{host}/{user}/{repo}'.format(host=__githost__,
                                                 user=__gituser__,
                                                 repo=__gitrepo__)
__downloadurl__ = u'{url}/get/{version}.tar'.format(url=__url__,
                                                    version=__version__)
