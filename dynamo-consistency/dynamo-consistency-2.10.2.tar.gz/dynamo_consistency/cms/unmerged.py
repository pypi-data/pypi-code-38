"""
A module for handling the listing and cleaning of /store/unmerged
"""

import os
import sqlite3
import shutil
import logging

from cmstoolbox.unmergedcleaner import listdeletable

from .. import config
from .. import datatypes
from .. import history
from .. import opts
from .. import remotelister
from .. import summary
from ..backend import registry
from ..backend import listers
from ..emptyremover import EmptyRemover


LOG = logging.getLogger(__name__)


def report_contents(timestamp, site, files):
    """
    Creates a SQLite3 database that contains all of the files and directories in a list.
    This database is then copied to the **WebDir** with the name
    ``SITE_unmerged.db``.

    :param int timestamp: Time that the listing was done
    :param str site: Used mostly for naming the database
    :param list files: List of files to put in the database
    """

    db_name = os.path.join(config.vardir('work'),
                           '%s_protected.db' % site)

    if os.path.exists(db_name):
        os.remove(db_name)

    # dump undeleted unmerged files into an SQL database
    conn = sqlite3.connect(db_name)
    curs = conn.cursor()
    currdir = 'fake_start'
    dirid = 1
    currcontents = []
    curs.execute('CREATE TABLE timestamp (timestamp DATETIME);')
    curs.execute('CREATE TABLE directories (id INT PRIMARY KEY, dirname VARCHAR(511));')
    curs.execute("""
                 CREATE TABLE files (dir INT, file CHAR(63),
                                     FOREIGN KEY(dir) REFERENCES directories(id));
                 """)
    curs.execute("""
                 INSERT INTO timestamp (`timestamp`) VALUES (DATETIME({0}, 'unixepoch'));
                 """.format(timestamp))

    for fname in files:
        if fname.startswith(currdir):
            currcontents.append(os.path.basename(fname))
        else:
            if currcontents:
                curs.execute('INSERT INTO directories (`id`, `dirname`) VALUES (?, ?);',
                             (dirid, currdir))
                curs.executemany('INSERT INTO files (`dir`, `file`) VALUES (?, ?);',
                                 [(dirid, f) for f in currcontents])
                dirid += 1

            currdir = os.path.dirname(fname)
            currcontents = [os.path.basename(fname)]

    if currcontents:
        curs.execute('INSERT INTO directories (`id`, `dirname`) VALUES (?, ?);',
                     (dirid, currdir))
        curs.executemany('INSERT INTO files (`dir`, `file`) VALUES (?, ?);',
                         [(dirid, f) for f in currcontents])

    conn.commit()
    conn.close()

    webdir = summary.webdir()

    db_dest = os.path.join(webdir, os.path.basename(db_name))
    if os.path.exists(db_dest):
        os.remove(db_dest)

    # Move this over to the web directory
    shutil.move(db_name, webdir)


def clean_unmerged(site):  # pylint: disable=too-complex
    """
    Lists the /store/unmerged area of a site, and then uses
    :py:mod:`cmstoolbox.unmergedcleaner.listdeletable`
    to list files to delete and adds them to the registry.

    .. Warning::

      This function has a number of side effects to various module configurations.
      Definitely call this after running the main site consistency.

    :param str site: The site to run the check over
    :returns: The number of files entered into the register and the number that are log files
    :rtype: int, int
    """

    # First, we do a bunch of hacky configuration changes for /store/unmerged
    listdeletable.set_config(config.LOCATION, 'ListDeletable')

    # Set the directory list to unmerged only
    config.DIRECTORYLIST = ['unmerged']
    logsdirs = ['unmerged/logs']
    if opts.MORELOGS:
        morelogs = config.CONFIG.get('AdditionalLogDeletions', {}).get(site, [])

        LOG.debug('Adding more log directories: %s', morelogs)

        config.DIRECTORYLIST.extend(morelogs)
        logsdirs.extend(morelogs)

    # Set the IgnoreAge for directories to match the listdeletable config
    datatypes.DirectoryInfo.ignore_age = listdeletable.config.MIN_AGE/(24 * 3600)

    # Get the list of protected directories
    try:
        listdeletable.PROTECTED_LIST = listdeletable.get_protected()
    except listdeletable.SuspiciousConditions:
        LOG.error('Problem with protected list, returning nothing')
        return 0, 0

    # If list is empty, exit because something is wrong
    if not listdeletable.PROTECTED_LIST:
        LOG.error('No protected list was found... Not cleaning /store/unmerged')
        return 0, 0

    listdeletable.PROTECTED_LIST.sort()

    with open(os.path.join(config.vardir('cache/%s' % site),
                           'protectedLFNs.txt'), 'w') as protected:
        protected.write('\n'.join(listdeletable.PROTECTED_LIST) + '\n')

    # Create a tree structure that will hold the protected directories
    protected_tree = datatypes.DirectoryInfo()

    for directory in listdeletable.PROTECTED_LIST:
        protected_tree.get_node(directory)

    def check_protected(path):
        """
        Determine if the path should be protected or not

        :param str path: full path of directory
        :returns: If the path should be protected
        :rtype: bool
        """

        # If the directory is explicitly protected, of course don't delete it
        if bool(protected_tree.get_node(path, make_new=False)):
            LOG.debug('%s is protected', path)
            return True

        for protected in listdeletable.PROTECTED_LIST:
            # If a subdirectory, don't delete
            if path.startswith(protected):
                LOG.debug('%s is protected', path)
                return True
            # We sorted the protected list, so we don't have to check all of them
            if path < protected:
                break

        LOG.debug('%s is NOT protected', path)
        return False


    # Turn on the filtering of ignored directories
    listers.FILTER_IGNORED = True

    # And do a listing of unmerged
    site_tree = remotelister.listing(    # pylint: disable=unexpected-keyword-arg
        site, cache='unmerged',          # cache keyword comes from cache decorator
        callback=EmptyRemover(site, check_protected))

    # Setup the config a bit more
    deletion_file = os.path.join(config.vardir('work'),
                                 '%s_unmerged.txt' % site)
    listdeletable.config.DELETION_FILE = deletion_file

    # Reset the protected list in case the listing took a long time
    try:
        listdeletable.PROTECTED_LIST = listdeletable.get_protected()
    except listdeletable.SuspiciousConditions:
        LOG.error('Problem with protected list, returning nothing')
        return 0, 0

    listdeletable.PROTECTED_LIST.sort()

    # Only consider things older than four weeks
    # Only look inside unmerged for the cleaning

    rootpath = config.CONFIG['RootPath']
    listdeletable.get_unmerged_files = lambda: [
        os.path.join(rootpath, fil) for fil in
        site_tree.get_node('unmerged').get_files(listdeletable.config.MIN_AGE)
    ]

    # Do the cleaning
    listdeletable.main()

    config_dict = config.config_dict()

    # Delete the contents of the deletion file and the contents of the log directory that are old
    with open(deletion_file, 'a') as d_file:
        for logs in logsdirs:
            node = site_tree.get_node(logs, make_new=False)
            if node:
                d_file.write('\n' + '\n'.join(
                    node.get_files(
                        min_age=(int(config_dict['UnmergedLogsAge']) * 24 * 3600),
                        path=os.path.join(rootpath,
                                          os.path.dirname(logs))
                    )))

    to_delete = set()
    with open(deletion_file, 'r') as d_file:
        to_delete.update([l.strip() for l in d_file if l.strip()])

    report_contents(site_tree.timestamp, site,
                    [f for f in site_tree.get_files() if f not in to_delete])

    history.report_unmerged([(name, site_tree.get_file(name)) for name in to_delete])

    return registry.delete(site, to_delete), len(
        [f for f in to_delete if f.strip().endswith('.tar.gz')])
