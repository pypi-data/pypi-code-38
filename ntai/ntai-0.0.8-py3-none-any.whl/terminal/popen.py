import subprocess
POPEN_DEFAULTS = {
    'bufsize'            : 1,
    'executable'         : None,
    'stdin'              : subprocess.PIPE,
    'stdout'             : subprocess.PIPE,
    'stderr'             : subprocess.PIPE,
    'preexec_fn'         : None,
    'close_fds'          : False,
    'shell'              : False,
    'cwd'                : None,
    'env'                : None,
    'universal_newlines' : False,
    'startupinfo'        : None,
    'creationflags'      : 0
}
