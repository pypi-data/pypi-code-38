# Keys of this dict hold available os implementations.
# Values of this dict hold available subplugin implementations for each os.
__available_plugins__ = {
    'linux' : [ 'ftp', 'scp', 'sftp', 'curl.tftp' ],
    'darwin' : [ 'ftp', 'scp', 'sftp', 'curl.tftp' ],
}
