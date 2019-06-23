from .functions import getfasta
from ..terminal.tools import process

function_map = {
    'getfasta': getfasta
}


def bedtools(
    subfunction:str,
    stdin:str,
    encoding:str='utf-8',
    **kwargs
):
    '''
    Arguments:
        stdin (str): the stringified bedfile to be passed to `process`
            called with `subfunction`

        **kwargs (dict): the configurable options for `subfunction`.

    Returns:
        stdout (str): the stringified output bedfile.

    '''
    command = function_map[subfunction](**kwargs)
    encoded = stdin.encode(encoding)
    stdout, stderr = process(command, stdin=encoded)
    decoded = stdout.decode(encoding)
    return decoded
