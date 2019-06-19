import yaml

""" YAML """

from microlab.io.files import file_exist


def create_yaml(data, path, verbose=False):
    if verbose:
        print('[  C  ]  {}'.format(path), end='.....')
    # file exists
    if file_exist(path=path, verbose=False):
        if verbose:
            print('[ OK ] replace the old yaml')

    # file not exists
    else:
        if verbose:
            print('[ OK ] create new file yaml')

    with open(path, 'w') as f:
        f.write(yaml.dump(data, default_flow_style=False))


def read_yaml(path, verbose=False):
    if verbose:
        print('[  R  ]  {}'.format(path), end='.....')
    if file_exist(path=path, verbose=verbose):
        with open(path, 'r') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        if verbose:
            print('[ OK ] load from exist yaml')
        return data
    else:
        return {}


def update_yaml(data, path, verbose=False):
    if verbose:
        print('[  U  ]  {}'.format(path), end='.....')
    if file_exist(path=path, verbose=False):
        old_data = read_yaml(path=path, verbose=False)
        old_data.update(data)
        create_yaml(data=old_data, path=path, verbose=False)
        print('[ OK ] replace the old yaml')
