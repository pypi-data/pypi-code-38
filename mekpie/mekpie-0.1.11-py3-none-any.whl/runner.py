from sys        import stdout, stderr
from shutil     import which
from subprocess import run, PIPE

import mekpie.messages as messages

from .cli  import panic, log

def lrun(args, quiet=False, error=True, runset=[], **kwargs):
    log('Running...\n' + serialize_command(args))
    try:
        if quiet:
            if run(args, stdout=PIPE, stderr=PIPE, **kwargs).returncode != 0:
                raise OSError
        else:
            if run(args, **kwargs).returncode != 0:
                raise OSError
        runset.append(True)
    except KeyboardInterrupt:
        exit(1)
    except OSError:
        if error:
            panic(messages.failed_program_call.format(serialize_command(args)))
        else:
            runset.append(False)

def serialize_command(args):
    return '$ ' + ' '.join(args)

def autodetect(options, default=None):
    for option in options:
        if which(option) is not None:
            return option
    return default