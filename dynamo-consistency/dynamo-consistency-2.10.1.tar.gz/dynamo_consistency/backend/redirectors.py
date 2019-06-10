"""
.. Warning::

   Must be used on a machine with xrdfs installed (for locate command).
"""

import os
import time
import subprocess
import logging

from cmstoolbox.siteinfo import get_domain

from .. import config

LOG = logging.getLogger(__name__)

def locate_file(file_name, redirs=None):
    """
    Find servers for a file.

    :param str file_name: Name of the file to locate
    :param list redirs: Global redirectors to start from.
                        If blank, gets them from the configuration file.
    :returns: List of hostnames that hold the file
    :rtype: list
    """

    # The final list of hosts. Only include Server ReadWrite
    output = []
    # This is where we store Manager ReadWrite responses.
    # Call these recursively to get the servers behind them.
    managers = []

    if redirs is None:
        redirs = config.config_dict()['GlobalRedirectors']

    for redir in redirs:
        LOG.debug('About to call: %s %s %s %s', 'xrdfs', redir, 'locate -h', file_name)
        proc = subprocess.Popen(['xrdfs', redir, 'locate', '-h', file_name],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()

        if stderr:
            LOG.error('Error in locate call:\n%s', stderr)

        LOG.debug('Stdout:\n%s', stdout)

        for line in [line for line in stdout.split('\n') if line.strip()]:
            explode = line.split()
            if explode[1] == 'Server':
                output.append(explode[0])
            else:
                managers.append(explode[0])

    # Recursively call managers
    if managers:
        output.extend(locate_file(file_name, managers))

    return output


def _xrd_locate(redirs, file_name, max_age):
    """
    Dump the redirectors from a xrdfs locate call into a file.
    Only makes the call if the cache is old, or non-existent.
    This is used by :py:func:`get_redirector`.

    :param list redirs: Is a list of redirectors to check for servers
    :param str file_name: Is the name of the file to output the redirector
    :param float max_age: The maximum age of a cached file, in seconds
    """

    # Update, if necessary (File doesn't exist or is too old)
    if not os.path.exists(file_name) or \
            (max_age and (time.time() - os.stat(file_name).st_mtime) > max_age):

        with open(file_name, 'w') as redir_file:

            for global_redir in redirs:
                # Get the locate from each redirector
                LOG.debug('About to call: %s %s %s', 'xrdfs', global_redir, 'locate -h /store/')
                proc = subprocess.Popen(['xrdfs', global_redir, 'locate', '-h', '/store/'],
                                        stdout=subprocess.PIPE)

                for line in proc.stdout:
                    redir_file.write(line.split()[0] + '\n')

                proc.communicate()

def get_redirector(site, banned_doors=None):
    """
    Get the redirector and xrootd door servers for a given site.
    An example valid site name is ``T2_US_MIT``.

    :param str site: The site we want to contact
    :param list banned_doors: Give a list of doors to not return.
                              These are usually ones that just timed out.
    :returns: Public hostname of the local redirector
              and a list of xrootd door servers
    :rtype: str, list
    """
    banned_doors = banned_doors or []

    LOG.debug('Getting doors for %s', site)
    config_dict = config.config_dict()
    max_age = config_dict.get('RedirectorAge', 0) * 24 * 3600

    # If the redirector is hardcoded, return it
    redirector = config_dict.get('Redirectors', {}).get(site, '')
    redirs = []

    domain = get_domain(site) or redirector

    if not domain:
        LOG.error('Could not get domain for %s', site)
        return '', []

    # If not hard-coded, get the redirector
    redir_directory = config.vardir('redirectors')
    if not redirector:
        # First check the cache
        file_name = os.path.join(redir_directory, 'redirector_list.txt')

        _xrd_locate(config_dict['GlobalRedirectors'],
                    file_name, max_age)

        # Parse for a correct redirector
        with open(file_name, 'r') as redir_file:
            for line in redir_file:
                if domain in line:
                    redirs.append(line.strip())

        if redirs:
            redirector = redirs[0]
    else:
        redirs.append(redirector)

    # Use that site redirector to get a list of doors
    list_name = os.path.join(redir_directory, '%s_redirector_list.txt' % site)
    _xrd_locate(redirs, list_name, max_age)
    LOG.debug('Door list cached at %s', list_name)

    # Get the list of doors
    with open(list_name, 'r') as list_file:
        local_list = [line.strip() for line in list_file \
                          if line.strip() not in banned_doors and domain in line]

    if not os.path.getsize(list_name):
        LOG.error('Redirector list %s is empty, removing', list_name)
        os.remove(list_name)

    LOG.info('From %s, got doors %s', redirector, local_list)
    LOG.info('Full list from global redirectors: %s', redirs)

    if len(redirs) > len(local_list):
        LOG.info('Using list from global redirectors')
        local_list = redirs

    # Return redirector and list of xrootd doors
    return (redirector, local_list)
