import os


dir = os.getcwd()


""" FILES """


def file_exist(path, verbose=False):
    if os.path.isfile(path):
        return True
    else:
        if verbose:
            print('[ !! ] filenot found')
        return False


def create_file(path,data, verbose=False):
    if verbose:
        print('[  C  ]  {}'.format(path), end='.....')
    if type(data) == str:
        string = data
    elif type(data) == bytes:
        string = data.decode('utf-8')
    # wite io to dile
    with open(path, mode='w', encoding='utf-8') as f:
        f.write(string)
    if verbose:
        print('[ OK ] create file')


def read_file(path, verbose=False):
    if verbose:
        print('[  R  ]  {}'.format(path), end='.....')
    data = ''
    if file_exist(path=path, verbose=False):
        with open(path, 'r') as f:
            data = f.read()
        print('[ OK ] read file')
    return data


def update_file(path, data, verbose=False):
    if verbose:
        print('[  U  ]  {}'.format(path), end='.....')
    if file_exist(path=path, verbose=False):
        create_file(path=path, data=data, verbose=False)
        if verbose:
            print('[ OK ] update file')


def delete_file(path, verbose=False):
    if verbose:
        print('[  D  ]  {}'.format(path), end='.....')
    if file_exist(path=path, verbose=verbose):
        os.remove(path)
        if verbose:
            print('[ OK ] delete file')
    else:
        if verbose:
            print('[ !! ] delete file that not exist')
