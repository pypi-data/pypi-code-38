# encoding: utf-8

# Variables for setup (these must be string only!)
__module_name__ = u'PyDNServer'
__description__ = u'Provides a very simple DNS server.'

__version__ = u'2.3.1'

__author__ = u'Oli Davis & Hywel Thomas'
__authorshort__ = u'OWBD_HT'
__authoremail__ = u'oli.davis@me.com, hywel.thomas@mac.com'

__license__ = u'MIT'

__githost__ = u'bitbucket.org'
__gituser__ = u'davisowb'
__gitrepo__ = u'pydnserver.git'


# Additional variables
__copyright__ = u'Copyright (C) 2016 {author}'.format(author=__author__)

__url__ = u'https://{host}/{user}/{repo}'.format(host=__githost__,
                                                 user=__gituser__,
                                                 repo=__gitrepo__)
__downloadurl__ = u'{url}/get/{version}.tar'.format(url=__url__,
                                                    version=__version__)
