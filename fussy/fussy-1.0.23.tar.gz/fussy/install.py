#! /usr/bin/env python
"""Install a given firmware package onto the file system (commands fussy-install and fussy-clean)

Major TODO items:

* TODO: error handling for all of the big issues (disk-space, memory, script failures)
"""
import subprocess, os, shutil, glob, logging, traceback
from optparse import OptionParser
from fussy import unpack, errors, nbio
log = logging.getLogger( __name__ )
from ._shims import bytes, unicode

CURRENT_LINK = 'current'
FAILSAFE_NAME = 'failsafe'
PROTECTED = [CURRENT_LINK,FAILSAFE_NAME]
DEFAULT_FIRMWARE_DIRECTORY = '/opt/firmware'
LOG_FORMAT = '%(levelname)- 7s %(name)-30s %(asctime)s  %(message)s'

def clean( target=DEFAULT_FIRMWARE_DIRECTORY, protected = None ):
    """Naive cleaning implementation
    
    Removes all names in target which are not in protected,
    paths in protected must be *full* path names, as returned 
    by glob.  The target of the current link is protected.
    """
    if protected is None:
        protected = [
            os.path.join( target, p ) 
            for p in PROTECTED
        ]
    # current target is always protected...
    target = final_path(target)
    current = os.path.join( target, CURRENT_LINK)
    assert os.path.exists( current ), "Current link appears to be missing, corrupt installation  (e.g. run install)?"
    current_target = final_path( current )
    assert os.path.exists( current_target ), "Current link appears to be broken, fix before cleaning (e.g. run install)"
    protected.append( current_target )
    for path in glob.glob( os.path.join( target, '*' )):
        if path not in protected:
            log.warning( 'Removing unused firmware: %s', path )
            shutil.rmtree( path, True )
    return current_target

def final_path( link ):
    """Get the final path of the given link
    
    raises IOError if link target does not exist, or the target is not a directory 
    
    returns normalized real target path of the link
    """
    real = os.path.normpath( os.path.realpath( link ) )
    if not os.path.exists( real ):
        raise IOError( "Target of link %(link)r (%(real)s) does not exist"%locals())
    if not os.path.isdir( real ):
        raise IOError( "Target of link %(link)r is not a directory"%locals())
    return real 

def swap_link( final_target, current ):
    """Swap current link to point to final_target
    
    Steps taken:
    
        * if there is an existing tmp link, remove it 
        * create a tmp link to the final target 
        * rename tmp link to `current`
    
    returns None
    """
    tmp = current + '~'
    try:
        os.remove( tmp )
        # TODO: address race condition, you should have the while upgrade 
        # cron-locked, but that's not obvious here...
    except (OSError,IOError):
        pass
    os.symlink( os.path.basename(final_target), tmp )
    os.rename( tmp, current )

def install_bytes( filename, keyring='/etc/fussy/keys', target='/opt/firmware' ):
    """Install the packaged bytes into a final target directory
    
    Steps taken:
    
        * unpack firmware using :func:`fussy.unpack.unpack`
        * rsync new_firmware into /opt/firmware (`target`)
            * if `CURRENT_LINK` (current) is present in `target`, 
              will hard-link shared files between the new firmware and `current` 
              to reduce disk use (using :command:`rsync` parameter --link-dest)
        * removes the temporary directory where unpacking was performed
    
    returns full path to sub-directory of target where new firmware was installed
    
    raises Errors on most failures, including disk-full, failed commands, missing 
    executables, etc
    """
    temp_dir = unpack.unpack( filename, keyring )
    assert os.path.exists( temp_dir )
    base_name = os.path.basename( temp_dir )
    try:
        final_target = os.path.join( os.path.normpath( target ), base_name )
        i=0
        while os.path.exists( final_target ):
            i+= 1
            final_target = os.path.join( os.path.normpath( target ), base_name + '-%i'%(i,) )
        current = os.path.join( os.path.normpath( target ), 'current' )
        command = [
            'rsync', '-aq',
        ]
        if os.path.exists( current ):
            log.info( 'Reducing firmware size with hard-link compression' )
            command.append( '--link-dest=%s'%( current,),)
        # TODO: figure out some way to configure rsync to not create a second 
        # level directory when told `rsync -a a b`
        command.extend([
            os.path.join( temp_dir, x )
            for x in os.listdir( temp_dir )
        ])
        command.extend([
            final_target,
        ])
        log.info( 'Fixating firmware' )
        subprocess.check_call( command )
        return final_target
    finally:
        shutil.rmtree( temp_dir, True )

def enable( final_target, current, recovery=False ):
    """Attempt to enable final_target as the current release
    
    Steps taken:
    
        * runs `final_target/.pre-install final_target recovery` 
          (iff .pre-install is present)
        * (atomically) swaps the link `current` 
          for a link that points to `final_target`
        * runs `final_target/.post-install final_target recovery` 
          (iff .post-install is present)
        * if a failure occurs before swap-link completes,
          deletes final_target 
        * if a failure occurs after swap-link, raises an error
    
    returns None 
    raises Exceptions on lots of failure cases
    """
    pre_install = os.path.join( final_target, '.pre-install' )
    post_install = os.path.join( final_target, '.post-install' )
    
    try:
        if os.path.exists( pre_install ):
            log.info( 'Running pre-install script' )
            def report_progress( line ):
                log.info( 'pre-install: %s', line )
            pipe = nbio.Process( [
                pre_install,
                final_target,
                unicode(recovery).encode('utf-8'),
            ], by_line=True, stderr=-1) | report_progress
            pipe()
        log.info( 'Setting firmware current' )
        swap_link( final_target, current )
    except Exception:
        # we failed in either pre-setup or swapping
        if not recovery:
            log.warning( 'Failed during pre-install or swap, aborting' )
            shutil.rmtree( final_target, True )
            raise
        else:
            log.exception( 'Failure attempting to re-initialize previous installation, likely reboot required' )
            # Note, we will attempt to run post-install, as it is often able to perform 
            # cleanups that the pre-install cannot...
    
    if os.path.exists( post_install ):
        log.info( 'Running post-install script' )
        def report_progress( line ):
            log.info( 'post-install: %s', line )
        pipe = nbio.Process([
            post_install,
            final_target,
            unicode(recovery).encode('utf-8'),
        ], by_line=True, stderr=-1) | report_progress
        pipe()

def ensure_current_link( current, failsafe ):
    """Ensure that current is a link (not a directory)"""
    if (
        os.path.isdir( current ) and 
        not os.path.islink( current)
    ):
        if not os.path.exists(failsafe):
            # this is the initial install case, where we want failsafe to be 
            # created from the initial installation image...
            os.rename( current, failsafe )
            os.symlink( os.path.basename(failsafe), current )
        else:
            raise RuntimeError(
                """%(current)r is a directory, it should be a link.  Failsafe already exists."""%locals()
            )

def install( filename, keyring='/etc/fussy/keys', target='/opt/firmware', unpacked=False ):
    """Install given firmware <filename> into given target directory
    
    Steps taken:

        * unpack firmware (using :func:`fussy.install.install_bytes`)
        * enable firmware (using :func:`fussy.install.enable`)
        * if :func:enable fails, enable `previous` 
          (or `failsafe` if there was no previous)
    
    returns (error_code (0 is success), path name of the installed package)
    """
    current = os.path.join( os.path.normpath( target ), CURRENT_LINK )
    failsafe = os.path.join( os.path.normpath( target ), FAILSAFE_NAME )
    
    ensure_current_link( current, failsafe )
    
    previous = None
    try:
        previous = final_path( current )
    except IOError as err:
        log.warning( "Target of current does not appear to exist: %s", err )
    if not previous and os.path.exists( failsafe ):
        previous = failsafe
    log.info( 'Previous installation: %s', previous )
    log.info( 'Unpacking firmware to disk' )
    if not unpacked:
        final_target = install_bytes( filename, keyring, target )
    else:
        final_target = os.path.normpath(os.path.abspath(filename))
        if not final_target.startswith(target):
            raise RuntimeError("Firmware is not unpacked into the target directory")
        if os.path.basename(final_target) == 'current':
            raise RuntimeError("Firmware is named 'current', cannot activate")
    log.info( 'New installation: %s', final_target )
    assert os.path.exists( final_target )
    try:
        enable( final_target, current )
    except Exception as err:
        log.error( "Failure installing %s: %s", final_target, err )
        log.error( "Traceback: %s", traceback.format_exc())
        if previous:
            log.warning( "Attempting to restore previous: %s", previous )
            enable( previous, current, recovery=True )
            raise errors.RevertedFailure( previous )
        log.error( "Unable to recover, contact support!" )
        raise errors.UnrecoverableError( unicode(err) )
        # TODO: need lots more logic in the back-off code...
    else:
        log.info( "Successfully installed %s", final_target )
        return final_target

def get_options():
    """Creates the OptionParser used in :func:`main` """
    parser = OptionParser()
    parser.add_option(
        '-f','--file',
        dest = 'file',
        default = None,
        action="store",
        type="string",
        help="The firmware archive to unpack, must be a .tar.gz.gpg or a .tar.gz.asc",
    )
    parser.add_option(
        '-k','--keyring',
        dest = 'keyring',
        default = unpack.DEFAULT_KEYRING,
        action="store",
        type="string",
        help="GPG keyring to use for verification/decryption (default /etc/fussy/keys)",
    )
    parser.add_option(
        '-t','--target',
        dest = 'target',
        default = DEFAULT_FIRMWARE_DIRECTORY,
        action="store",
        type="string",
        help="Directory into which to rsync the firmware (default /opt/firmware)",
    )
    parser.add_option(
        '-u','--unpacked',
        dest = 'unpacked',
        default = False,
        action="store_true",
        help="Target is pre-unpacked image directory (fussy-install-bytes)",
    )
    parser.add_option(
        '-l', '--logfile',
        dest='logfile',
        default='/tmp/fussy-install.log',
        help = "File into which to write the fussy installation log (default /tmp/fussy-install.log)",
    )
    return parser

def configure_log( logfile ):
    if logfile:
        logging.basicConfig(filename=logfile,level=logging.INFO, format=LOG_FORMAT,datefmt='%Y-%m-%d %H:%M:%S')
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    return logfile

def main():
    """Main entry-point for the fussy-install script
    
    Steps taken:
    
        * parses arguments 
        * launches :func:`install`
    """
    parser = get_options()
    options,args = parser.parse_args()
    if not options.file:
        if args:
            options.file = args[0]
        else:
            parser.error( "Need a file to install" )
    configure_log( options.logfile )
    try:
        install( options.file, options.keyring, options.target )
        return 0
    except Exception as err:
        log.error(
            "Failure during installation: %s", err,
        )
        log.error(
            "Traceback: %s", traceback.format_exc(),
        )
        raise

def clean_main():
    """Main entry-point for fussy-clean script 
    
    Steps taken:
    
        * parses arguments 
        * launches :func:`clean`
    """
    parser = OptionParser()
    parser.add_option(
        '-t','--target',
        dest = 'target',
        default = DEFAULT_FIRMWARE_DIRECTORY,
        action="store",
        type="string",
        help="Directory into which to rsync the firmware (default /opt/firmware)",
    )
    parser.add_option(
        '-l', '--logfile',
        dest='logfile',
        default='/tmp/fussy-install.log',
        help = "File into which to write the fussy installation log (default /tmp/fussy-install.log)",
    )
    options,args = parser.parse_args()
    configure_log( options.logfile )
    clean( options.target )
    return 0

def install_bytes_main_options():
    """Creates the OptionParser used in :func:`unpack_main` """
    parser = OptionParser("Unpacks a firmware onto disk without activating it")
    parser.add_option(
        '-f','--file',
        dest = 'file',
        default = None,
        action="store",
        type="string",
        help="The firmware archive to unpack, must be a .tar.gz.gpg or a .tar.gz.asc",
    )
    parser.add_option(
        '-k','--keyring',
        dest = 'keyring',
        default = unpack.DEFAULT_KEYRING,
        action="store",
        type="string",
        help="GPG keyring to use for verification/decryption (default /etc/fussy/keys)",
    )
    parser.add_option(
        '-t','--target',
        dest = 'target',
        default = DEFAULT_FIRMWARE_DIRECTORY,
        action="store",
        type="string",
        help="Directory into which to rsync the firmware (default /opt/firmware)",
    )
    parser.add_option(
        '-l', '--logfile',
        dest='logfile',
        default='/tmp/fussy-install.log',
        help = "File into which to write the fussy installation log (default /tmp/fussy-install.log)",
    )
    return parser
def install_bytes_main():
    parser = install_bytes_main_options()
    options, args = parser.parse_args()
    if not options.file:
        if args:
            options.file = args[0]
        else:
            parser.error( "Need a file to install" )
    configure_log( options.logfile )
    try:
        final_target = install_bytes_main( options.file, options.keyring, options.target )
        print(final_target)
        return 0
    except Exception as err:
        log.error(
            "Failure during unpacking: %s", err,
        )
        log.error(
            "Traceback: %s", traceback.format_exc(),
        )
        raise
    
