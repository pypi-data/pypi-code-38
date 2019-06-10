'''usage:
  bf [options] [<command>] [<args>...]

Available commands:
  use               Set your current working dataset
  init              Initialize a new dataset
  search            Search across your datasets
  datasets          List your datasets
  organizations     List the organizations you belong to

  collaborators     List the collaborators of the current working dataset
  share             Share a dataset with users, teams, or your organization
  unshare           Revoke access to the a dataset from users, teams, or your organization

  props             Add/remove/modify a package or collection's properties
  move              Move a package or collection
  where             Show path to package or collection
  append            Append data to a package
  rename            Rename a package or collection
  delete            Delete a package or collection
  create            Create a collection
  get               Get the contents of a package, collection, or dataset

  upload            Upload file(s) or directory

  status            Display connection status
  cache             Perform cache operations
  profile           Profile management


global options:
  -h --help                 Show help
  --dataset=<dataset>       Use specified dataset (instead of your current working dataset)
  --profile=<name>          Use specified profile (instead of default)
'''
from __future__ import absolute_import, division, print_function

import os

from docopt import docopt

import blackfynn
from blackfynn import Blackfynn, Settings

from .working_dataset import set_working_dataset


DEPRECATION = """
+---------------------------------------------------+
| WARNING: The Python CLI is deprecated and will be |
| removed in a future release.                      |
|                                                   |
| Please install and use the new Blackfynn CLI:     |
| https://developer.blackfynn.io/agent              |
+---------------------------------------------------+
"""

def blackfynn_cli():
    args = docopt(__doc__,
                  version='bf version {}'.format(blackfynn.__version__),
                  options_first=True)

    # Test for these two commands first as they
    # do not require a Blackfynn client
    if args['<command>'] in ['help',None]:
        print(__doc__.strip('\n'))
        print(DEPRECATION)
        return

    print(DEPRECATION)

    if args['<command>'] == 'profile':
        from . import bf_profile
        bf_profile.main()
        return

    # Display warning message if config.ini is not found
    settings = Settings() # create a dummy settings object to load environment variables and defaults only
    if not os.path.exists(settings.config_file):
        print("\033[31m* Warning: No config file found, run 'bf profile' to start the setup assistant\033[0m")

    # Try to use profile specified by --profile, exit if invalid
    try:
        bf = Blackfynn(args['--profile'])
    except Exception as e:
        exit(e)

    #Try to use dataset specified by --dataset, exit if invalid
    try:
        if args['--dataset'] is not None:
            dataset = bf.get_dataset(args['--dataset'])
            set_working_dataset(dataset.id)
    except Exception as e:
        exit(e)

    if args['<command>'] == 'status':
        from . import bf_status
        bf_status.main(bf)
    elif args['<command>'] == 'use':
        from . import bf_use
        bf_use.main(bf)
    elif args['<command>'] == 'init':
        from . import bf_init
        bf_init.main(bf)
    elif args['<command>'] in ['datasets', 'ds']:
        from . import bf_datasets
        bf_datasets.main(bf)
    elif args['<command>'] in ['organizations', 'orgs']:
        from . import bf_organizations
        bf_organizations.main(bf)
    elif args['<command>'] in ['share', 'unshare', 'collaborators']:
        from . import bf_share
        bf_share.main(bf)
    elif args['<command>'] == 'cache':
        from . import bf_cache
        bf_cache.main(bf)
    elif args['<command>'] == 'create':
        from . import bf_create
        bf_create.main(bf)
    elif args['<command>'] == 'delete':
        from . import bf_delete
        bf_delete.main(bf)
    elif args['<command>'] == 'move':
        from . import bf_move
        bf_move.main(bf)
    elif args['<command>'] == 'rename':
        from . import bf_rename
        bf_rename.main(bf)
    elif args['<command>'] == 'props':
        from . import bf_props
        bf_props.main(bf)
    elif args['<command>'] == 'get':
        from . import bf_get
        bf_get.main(bf)
    elif args['<command>'] == 'where':
        from . import bf_where
        bf_where.main(bf)
    elif args['<command>'] == 'upload':
        from . import bf_upload
        bf_upload.main(bf)
    elif args['<command>'] == 'append':
        from . import bf_append
        bf_append.main(bf)
    elif args['<command>'] == 'search':
        from . import bf_search
        bf_search.main(bf)
    else:
        exit("Invalid command: '{}'\nSee 'bf help' for available commands".format(args['<command>']))
