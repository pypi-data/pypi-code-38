import json
import logging
from pathlib import Path
from .things import Collection, Metadata

logger = logging.getLogger(__name__)


def inspect(thing):
    '''Prints out contents of a Bebanjo object for debugging purposes. Ideal for interactive
    sessions. User guide:

    > from bebanjo import inspect
    > inspect(thing)
    '''

    def str_meta(d):
        for k, v in d.items():
            if not k.startswith('_'):
                v = str(v)
                if len(v) > 77:
                    v = v[:80] + '...'
                lines.append(f' > {k}: {v.__repr__()}')

    def append_formatted(k, v):
        if v is None:
            v = 'Unknown'
        lines.append(f'{k + ":":18} {v:>15}')

    if thing is None:
        print('NoneType object')
        return

    lines = []
    lines.append(f'Instance of {thing.__class__.__name__} ({thing.summary_url})')

    if isinstance(thing, Metadata):
        str_meta(thing)
    elif isinstance(thing, Collection):
        # we are inherited class and may have much detail to return
        append_formatted('members held', len(thing.members))
        append_formatted('members available', thing.items_available)
        append_formatted('per page', thing.per_page)
        append_formatted('pages available', thing.count_pages)
        append_formatted('next page', thing.next_page or 'None or Unknown')
    # primary metadata
    str_meta(getattr(thing, '_meta1', {}))
    # extended metadata
    mdata = getattr(thing, 'metadata', {})
    if mdata:
        lines.append('Metadata:')
        str_meta(mdata)
    # links are trickier to pick out since they are top level properties
    links = thing.child_getters()
    if links:
        lines.append('Getters:')
        for k in links:
            lines.append(' > ' + k)
    print('\n' + ('\n'.join(lines)) + '\n')


def read_local_config(fullpath=f'{Path.home()}/.bebanjo.json'):
    'Reads local config ({fullpath}) and returns as a json object'
    result = {}
    try:
        with open(fullpath, 'r') as f:
            bconfig = json.load(f)
        auth = bconfig['auth']
        for env, creds in auth.items():
            if env not in ['staging', 'preproduction', 'production']:
                raise KeyError
            for k in creds.keys():
                if k not in ['name', 'password']:
                    raise KeyError
            result[env] = creds
        return result
    except FileNotFoundError:
        err_str = f'Config file not found: {fullpath}'
    except AssertionError:
        raise KeyError
    except KeyError:
        err_str = f'Config file {fullpath} contents are invalid'
    logger.error(err_str)
    exit(err_str)


def rm_csv_tag(csv: str, rm_value: str):
    '''Given a csv string, returns the string with matching value removed.
    '''
    tags = csv.split(',')
    return ','.join(filter(lambda x: x != rm_value, tags))


def add_csv_tag(csv: str, new):
    tags = set(csv.split(','))
    tags.add(str(new))
    return ','.join(tags)
