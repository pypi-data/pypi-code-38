import os
import shutil

""" FOLDERS """


def folder_exist(path, verbose=False):
    if os.path.isdir(path):
        return True
    else:
        if verbose:
            print('[ !! ] folder not found')
        return False


def create_folder(path, verbose=False):
    if verbose:
        print('[  C  ]  {}'.format(path), end='.....')
    # folder exists
    if folder_exist(path=path, verbose=False):
        if verbose:
            print('[ OK ] folder exists')

    # folder not exists
    else:
        if verbose:
            print('[ OK ] create new folder')
        os.mkdir(path=path)


def delete_folder(path, verbose=False):
    if verbose:
        print('[  D  ]  {}'.format(path), end='.....')
    if folder_exist(path=path, verbose=False):
        shutil.rmtree(path=path)
        if verbose:
            print('[ OK ] delete the folder')
