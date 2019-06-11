"""Utility functions for common tasks"""
from fussy import install, nbio
import os, glob, logging
from optparse import OptionParser
log = logging.getLogger( __name__ )

MIGRATION_PATTERN = '????_*.py'

def find_reverse_upgrades( final_target, relative_path, migration_pattern=MIGRATION_PATTERN ):
    """Find reverse upgrades that must be run before final_target is installed
    
    final_target -- final target of the installation
    relative_path -- path from final target to Django/South migrations
    
    returns ID/number of the migration to run (if any)
    """
    new = glob.glob( os.path.join( final_target, relative_path, migration_pattern ) )
    old = glob.glob( os.path.join( final_target, '..', install.CURRENT_LINK, relative_path, migration_pattern ) )
    new = sorted([os.path.basename( x ) for x in new ])
    old = sorted([os.path.basename( x ) for x in old ])
    # we want the last migration in both old and new
    common = [ old_item for (new_item,old_item) in zip( new,old ) if new_item == old_item ]
    if common == old:
        # forward migration only 
        log.info( 'No reverse migration required' )
        return None
    elif common:
        # there is a common set, but it is *not* the same as old, so roll back current 
        # until it is at the common branching point...
        log.warning(
            "Extra migrations in current versus target: %s",
            ", ".join( old[len(common):] ),
        )
        return os.path.splitext( common[-1] )[0]
    else:
        # I can't think of a legitimate use case for wanting to roll back to having no data...
        raise RuntimeError( "No common migrations found" )
def get_options():
    """Creates the OptionParser used in :func:`main` """
    parser = OptionParser()
    parser.add_option(
        '-f', '--final_target',
        dest = 'final_target',
        help = "Path to the new firmware installation",
    )
    parser.add_option(
        '-d','--django-admin',
        dest = 'django_admin',
        default = 'django-admin.py',
        help="Path to the django-admin.py script with which to run migrations",
    )
    parser.add_option(
        '-p', '--path',
        dest = 'path',
        help = "Relative path from current to migration directory...",
    )
    parser.add_option(
        '-a', '--app',
        dest = 'app',
        help = "Application name to migrate",
    )
    return parser

def main():
    """Finds last common migration and reverts current Django db to that 
    
    Must be run with DJANGO_SETTINGS_MODULE set in the environment
    """
    logging.basicConfig( level=logging.INFO )
    options,args = get_options().parse_args()
    migration = find_reverse_upgrades( 
        options.final_target,
        options.path,
    )
    if migration:
        pipe = nbio.Process([
            options.django_admin,
            'migrate',
            '--noinput',
            options.app,
            migration,
        ],stderr=-1)
        print(pipe())
