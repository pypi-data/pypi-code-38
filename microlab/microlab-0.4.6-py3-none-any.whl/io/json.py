from microlab.io.files import file_exist
import json

""" JSON """


def create_json(data, path, verbose=False):
    if verbose:
        print('[  C  ]  {}'.format(path), end='.....')
    # file exists
    if file_exist(path=path, verbose=False):
        if verbose:
            print('[ OK ] replace the old json')

    # file not exists
    else:
        if verbose:
            print('[ OK ] create new file json')

    with open(path, 'w') as f:
        f.write(json.dumps(data))


def read_json(path, verbose=False):
    if verbose:
        print('[  R  ]  {}'.format(path), end='.....')
    if file_exist(path=path, verbose=verbose):
        with open(path, 'r') as f:
            data = json.load(f)
        if verbose:
            print('[ OK ] load from exist json')
        return data
    else:
        return {}


def update_json(data, path, verbose=False):
    if verbose:
        print('[  U  ]  {}'.format(path), end='.....')
    if file_exist(path=path, verbose=False):
        old_data = read_json(path=path, verbose=False)
        old_data.update(data)
        create_json(data=old_data, path=path, verbose=False)
        print('[ OK ] replace the old json')
