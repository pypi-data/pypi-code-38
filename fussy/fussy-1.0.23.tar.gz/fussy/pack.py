#! /usr/bin/env python
"""Bundle a package as a signed firmware for installation/redistribution
"""
import tempfile, subprocess, os
from optparse import OptionParser

DEFAULT_EXCLUDES = [
    '.svn',
    '.bzr',
    '.git',
]

def pack( root_dir, excludes=None, tar_name=None ):
    """Bundle directory into a firmware file...
    
    * root_dir -- directory to be packed into the firmware, the 
        :func:`os.path.basename` of this directory will be the name used 
        in the created bundle filename and the directory installed into 
        the target on client machines
    * excludes -- patterns to exclude from the firmware image (passed to
        :command:`tar` during packing)
    
    returns absolute filename for generated .tar.gz firmware 
    (created in a temporary directory)
    """
    temp_dir = tempfile.mkdtemp(prefix='fussy-',suffix='-pack')
    firmware_name = os.path.basename( root_dir )
    if firmware_name == 'current':
        raise RuntimeError( 'Cannot create a firmware named "current"')
    if tar_name is None:
        tar_name = firmware_name+ '.tar.gz'
    tar_file = os.path.join( temp_dir, tar_name )
    command = [
        'tar','-zcf',
        tar_file,
    ] + [
        '--exclude=%s'%(x,) 
        for x in ((excludes or []) + DEFAULT_EXCLUDES)
    ] + [os.path.basename(root_dir)]
    subprocess.check_call( command, cwd=os.path.dirname( os.path.abspath(root_dir) ) )
    return tar_file

def sign( tar_file, key=None,encrypt_for=None ):
    """Sign an existing tar.gz-file with the default key
    
    * tar_file -- tar.gz file to sign (and/or encrypt)
    * encrypt_for -- if non-null, string identifier for which to encrypt
    """
    gpg_file = tar_file + '.gpg'
    command = [ 'gpg' ]
    if encrypt_for:
        command += ['-se', '-r', encrypt_for]
    else:
        command += ['--sign']
    if key:
        command += ['-u',key]
    command.append( tar_file )
    subprocess.check_call( command )
    assert os.path.exists( gpg_file )
    os.remove( tar_file )
    return gpg_file
    

def get_options():
    """Produces the OptionParser for :func:main"""
    parser = OptionParser()
    parser.add_option( 
        '-x','--exclude', 
        dest='exclude', 
        action="append",
        type="string",
        help="Paths/patterns to exclude from the archive",
    )
    parser.add_option(
        '-r','--root',
        dest = 'root',
        default='firmware',
        type="string",
        help="The directory to be packed for distribution, should be a versioned/unique name, for instance including a human-readable timestamp",
    )
    parser.add_option(
        '-u','--unsigned',
        dest='signed',
        action="store_false",
        default=True,
        help="If specified, do not do signing, just produced an unsigned tar.gz file (intended to allow for signing on a separate workstation)",
    )
    parser.add_option(
        '-t','--tarname',
        dest='tar_name',
        default=None,
        type="string",
        help="If specified, override the calculation of the .tar.gz filename (defaults to target directory basename + .tar.gz)",
    )
    add_encryption_options( parser )
    return parser
def add_encryption_options( parser ):
    parser.add_option(
        '-k','--key',
        dest='key',
        default = None,
        help = 'If specified, use this key id to perform the signing (passed to :cmd:gpg -u option), otherwise uses default identity',
    )
    parser.add_option(
        '-e','--encrypt-for',
        dest = 'encrypt',
        action="store",
        type="string",
        help="The name of the key for which to encrypt (otherwise just sign)",
    )
    return parser
    
def main():
    """Main function for the packing script"""
    options,args = get_options().parse_args()
    tar_file = pack( options.root, options.exclude, options.tar_name )
    if options.signed:
        gpg_file = sign( tar_file, key=options.key, encrypt_for=options.encrypt )
        print(gpg_file) 
    else:
        print(tar_file)
    return 0

def get_sign_options():
    parser = OptionParser()
    parser.add_option(
        '-f','--filename',
        dest='filename',
        default = None,
        help = 'The full path to the tar.gz file we will sign',
    )
    add_encryption_options( parser )
    return parser

def sign_main():
    """Main function that *just* signs a tar-file"""
    options,args = get_sign_options().parse_args()
    if not options.filename and args:
        options.filename = args[0]
    gpg_file = sign( options.filename, key=options.key, encrypt_for=options.encrypt )
    print(gpg_file)
    return 0
    
