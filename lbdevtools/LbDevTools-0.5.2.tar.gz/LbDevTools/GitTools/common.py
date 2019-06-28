###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
__author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'

PROTOCOLS_URLS = {
    'ssh': 'ssh://git@gitlab.cern.ch:7999/',
    'krb5': 'https://:@gitlab.cern.ch:8443/',
    'https': 'https://gitlab.cern.ch/',
}
DEFAULT_PROTOCOL = 'krb5'


def gitlab_url(group, name, protocol):
    '''
    Return the URL of a _project_ in a group for a given protocol.
    '''
    return '{}{}/{}.git'.format(PROTOCOLS_URLS[protocol], group, name)


def project_url(project, protocol):
    '''
    Return the url to the Git repository of the project for a given protocol.
    '''
    from LbEnv import fixProjectCase
    # FIXME: get source uri from SoftConfDB
    uri = 'gitlab-cern:{}/{}'.format('lhcb' if project.lower() != 'gaudi' else
                                     'gaudi', fixProjectCase(project))
    group, name = uri.split(':', 1)[-1].split('/', 1)
    return gitlab_url(group, name, protocol)


def package_url(name, protocol):
    '''
    Return the url to the Git repository of the package for a given protocol.
    '''
    return gitlab_url('lhcb-datapkg', name, protocol)


def get_default_protocol(repo=None):
    '''
    Return the protocol to use by default (from configuration or hardcoded
    default).
    '''
    # FIXME: GitPython does not provide direct access to global configuration
    from os.path import normpath, expanduser, join
    from git import GitConfigParser
    conf_reader = (repo.config_reader() if repo else GitConfigParser(
        [normpath(expanduser(join('~', '.gitconfig')))], read_only=True))
    with conf_reader as conf:
        return conf.get_value('lb-use', 'protocol', DEFAULT_PROTOCOL)


def add_protocol_argument(parser):
    '''
    Helper to share the definiton of the --protocol argument
    '''
    parser.add_argument(
        '-p',
        '--protocol',
        choices=PROTOCOLS_URLS,
        help='which protocol to use to connect to gitlab; '
        'the default is defined by the config option '
        'lb-use.protocol, or {} if not set'.format(DEFAULT_PROTOCOL))
    return parser


def handle_protocol_argument(args, repo=None):
    if not args.protocol:
        args.protocol = get_default_protocol(repo)


def add_verbosity_argument(parser):
    import logging
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        dest='log_level',
        const=logging.ERROR,
        help='be more quiet')
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        dest='log_level',
        const=logging.INFO,
        help='be more verbose')
    parser.add_argument(
        '-d',
        '--debug',
        action='store_const',
        dest='log_level',
        const=logging.DEBUG,
        help='be very verbose')
    parser.set_defaults(log_level=logging.WARNING)
    return parser


def handle_verbosity_argument(args):
    import logging
    logging.basicConfig(level=args.log_level)


def add_version_argument(parser):
    from LbDevTools import __version__
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__))
    return parser
