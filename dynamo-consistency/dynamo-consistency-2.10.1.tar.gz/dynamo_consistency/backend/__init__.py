"""
The "backend" handles all of the connections to dynamo objects and databases
as well as connections for performing listings of remote or local filesystems.

A complete list and description of the modules and functions that should be
accessible through this module is the following.

.. contents::
   :local:
"""

import sys

from .. import opts


# A dictionary of modules and functions that should
# be accessible through the backend.
# Values end up in the module docstring

_PROVIDE = {
    'inventory': """
.. py:module:: inventory

A module that access contents of sites and other information
from Dynamo's internal inventory.

.. py:function:: dynamo_consistency.backend.inventory.protected_datasets(site)

   :param str site: Site to query
   :returns: The datasets that are protected by Dynamo
   :rtype: set

.. py:function::  dynamo_consistency.backend.inventory.list_files(site)

   :param str site: Site to query
   :returns: List of files at the site.
             Each element of the list is a tuple with
             (file name, size in bytes, datetime object)
   :rtype: list
""",
    'registry': """
.. py:module:: registry

Module that handles transfers and deletions

.. py:function::  dynamo_consistency.backend.registry.delete(site, files)

   Requests deletion of files from a site

   :param str site: The site to remove files from
   :param list files: List of LFNs of files (and directories) to remove

.. py:function::  dynamo_consistency.backend.registry.transfer(site, files)

   Requests transfer of files to a site

   :param str site: The site to transfer files to
   :param list files: List of LFNs of files to transfer
""",
    'siteinfo': """
.. py:module:: siteinfo

Site information from inventory

.. py:function::  dynamo_consistency.backend.siteinfo.site_list()

   :returns: List of sites known by Dynamo
   :rtype: list

.. py:function::  dynamo_consistency.backend.siteinfo.ready_sites()

   :returns: Sites that are ready to run on
   :rtype: set
""",

    'get_listers': """
.. py:function:: get_listers(site)

   :param str site: The name of the site that we want listers for
   :returns: A tuple containing a constructor (or function) and
             object creation parameters (or None) for passing to
             :py:func:`dynamo_consistency.create.create_dirinfo`.

             Optionally, the first parameter of the tuple can be a fully constructed
             :py:class:`dynamo_consistency.datatypes.DirectoryInfo`.
             In that case, the second returned value is ignored by
             :py:func:`dynamo_consistency.remotelister.listing`.
   :rtype: tuple
""",
    'check_site': """
.. py:function:: check_site(site)

   :param str site: Site to check status of
   :returns: True, if site is ready to run on
   :rtype: bool
""",
    'deletion_requests': """
.. py:function:: deletion_requests(site)

   :param str site: The site that we want the deletion requests for
   :returns: A set of datasets that have pending deletion requests
   :rtype: set
""",
    'filelist_to_blocklist': """
.. py:function:: filelist_to_blocklist(site, infile, outfile)

   Converts a file of list of files to a summary of blocks and owning groups.

   :param str site: Name of the site to get group names for.
   :param str infile: Location of the file that contains the list of files
   :param str outfile: Location of the file to output blocks summary
""",
    'DatasetFilter': """
.. py:class:: DatasetFilter(datasets)

   :param set datasets: A set of datasets that are protected by dynamo.

   .. py:method:: protected(filename)

      :param str filename: Name of a file that is checked for filtering
      :returns: True if the file is protected
      :rtype: bool
"""
}


if opts.TEST:
    from . import test as mod

else:
    from . import prod as mod


_THIS = sys.modules[__name__]

for thing in _PROVIDE:
    setattr(_THIS, thing, getattr(mod, thing))

__doc__ += '\n'.join( # pylint: disable=redefined-builtin
    ["""
{head}
{under}
{description}""".format(head=key, under='-' * len(key), description=value)
     for key, value in sorted(_PROVIDE.items())]
)
