"""Link all files in a distribution from relative location on the hard disk"""
import os, logging, shutil
from optparse import OptionParser

log = logging.getLogger( __name__ )

def link_tree( distribution_dir, target_dir='/', symbolic=True, copy=False ):
    """(Sym)link all files under distribution_dir from target_dir 
    """
    if symbolic:
        link = os.symlink 
    else:
        link = os.link
    for path, subdirs, filenames in os.walk( distribution_dir ):
        dir_relative = os.path.relpath( path, distribution_dir )
        dir_source = os.path.normpath( os.path.abspath( path ) )
        dir_final = os.path.normpath( os.path.join( target_dir, dir_relative ))
        if not os.path.exists( dir_final ):
            log.info( 'Creating directory: %s', dir_final )
            try:
                os.makedirs( dir_final )
            except Exception as err:
                err.args += (dir_final,)
                raise 
        for filename in filenames + subdirs:
            file_source = os.path.join( dir_source, filename )
            file_final = os.path.join( dir_final, filename )
            if os.path.islink( file_source ):
                
                target = os.readlink( file_source )
                final_target = os.path.join( dir_final,target)
                log.info('Recreating link in %s to %s',file_final, final_target )
                create_link( final_target, file_final, os.symlink )
            elif os.path.isfile(file_source):
                if os.path.lexists( file_final ):
                    if (
                        symbolic and 
                        os.path.islink( file_final ) and 
                        os.readlink( file_final ) == file_source
                    ):
                        log.info( 'Up to date: %s', file_final )
                        continue
                    log.info( 'Replacing: %s', file_final )
                    create_link( file_source, file_final, link, copy=copy )
                else:
                    log.info( 'Linking: %s', file_final )
                    create_link( file_source, file_final, link, copy=copy )

def create_link( file_source, file_final, link, copy=False ):
    try:
        temp = file_final + '~'
        if os.path.exists( temp ) or os.path.lexists( temp ):
            try:
                os.remove( temp )
            except Exception as err:
                err.args += (temp, )
                raise 
        try:
            if copy:
                shutil.copy2( file_source, temp )
            else:
                link( file_source, temp )
        except OSError as err:
            if link is os.link:
                shutil.copy2( file_source, temp )
            else:
                raise
        os.rename( temp, file_final )
    except Exception as err:
        log.error( "Error linking %s: %s", file_final, err )
        raise err
    
def get_options():
    """Creates the OptionParser used in :func:`main` """
    parser = OptionParser()
    parser.add_option(
        '-d','--directory',
        dest = 'directory',
        default = None,
        help="Directory to which to link",
    )
    parser.add_option(
        '-t','--target',
        dest = 'target',
        default = None,
        help="Directory in which to create the links",
    )
    parser.add_option(
        '-v','--verbose',
        dest = 'verbose',
        action="store_true",
        default = False,
        help="Perform verbose logging (INFO level), default: False",
    )
    parser.add_option(
        '-H','--hard',
        dest = 'hardlink',
        action="store_true",
        default = False,
        help="Use hard-links instead of symlinks, default: False",
    )
    parser.add_option(
        '-c','--copy',
        dest = 'copy',
        action="store_true",
        default = False,
        help="Copy the inode rather than linking, default: False",
    )
    return parser

def main():
    options,args = get_options().parse_args()
    if options.verbose:
        logging.basicConfig( level=logging.INFO )
    else:
        logging.basicConfig( level=logging.WARNING )
    if args:
        if not options.directory:
            options.directory = args[0]
            args = args[1:]
        if args and not options.target:
            options.target = args[0]
            args = args[1:]
    link_tree( options.directory, options.target, symbolic = (not options.hardlink), copy=options.copy )
    return 0
