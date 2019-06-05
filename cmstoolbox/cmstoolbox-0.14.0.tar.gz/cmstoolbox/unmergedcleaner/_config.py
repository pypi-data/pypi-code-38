"""
The parameters in the configuration files can be
overwritten by matching keys in a JSON file.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


LFN_TO_CLEAN = '/store/unmerged'
"""
The Unmerged Cleaner tool cleans the directory matching this LFN. On most sites, this
will not need to be changed, but it is possible for a /store/dcachetests/unmerged
directory to exist, for example. The default is '/store/unmerged'.
"""


UNMERGED_DIR_LOCATION = LFN_TO_CLEAN
"""
The location, or PFN, of the unmerged directory. This can be
retrieved from Phedex (default) or given explicitly.
"""


WHICH_LIST = 'directories'
"""
Determines whether a list of directories or files will be generated.
These lists will be in PFN format. Possible values are
'directories' or 'files'. The default is 'directories'.
"""


DELETION_FILE = '/tmp/%s_to_delete.txt' % WHICH_LIST
"""
The list of directory or file PFNs to delete are placed this file.
The default is '/tmp/<WHICH_LIST>_to_delete.txt'.
"""


SLEEP_TIME = 0.5
"""
This is the number of seconds between each deletion of a directory or file.
The sleep avoids overloading the system and allows the operator to interrupt a deletion.
The default is 0.5.
"""


DIRS_TO_AVOID = ['SAM', 'logs']
"""
The directories in this list are left alone. Only the top level of directories within
the unmerged location is checked against this if WHICH_LIST is 'directories'.
The defaults are ['SAM', 'logs'].
"""


MIN_AGE = 1209600 * 2
"""
Directories with an age less than this, in seconds, will not be deleted.
"""


STORAGE_TYPE = 'posix'
"""
This defines the storage type of the site. This may be necessary for the script to run
correctly or optimally. Acceptable values are 'posix' and 'hadoop'.
The default is 'posix'.
"""
