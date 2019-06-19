from microlab.io.files import file_exist
import patoolib
import zipfile
import os
import sys

""" ZIP """


def create_zip(source, destination, verbose=False):
    # cd to Repos directory
    parrent_folder = '\\'.join(source.split('/')[:-1])
    # input(parrent_folder)
    # os.chdir(parrent_folder)

    # zip_file = '{}.zip'.format(source)

    # if zip found, delete it
    if file_exist(path=destination, verbose=False):
        os.remove(destination)

    # create zip file
    if verbose:
        print('[  Z  ]  {}'.format(source), end='...')
    patoolib.create_archive(destination, (source,), verbosity=-1)

    # cd back to root
    if sys.platform == 'win32':
        os.chdir(os.getcwd())

    # move the zip from repos to zips
    zip_file_in_repos = ''.format(destination)
    # zip_file_in_zips = 'Zips/{}.zip'.format(path)
    # shutil.move(zip_file_in_repos, zip_file_in_zips)
    if verbose:
        print('[ OK ] create zip file ')


def extract_zip(source, destination, verbose=False):
    if verbose:
        print('[  E  ]  {}'.format(destination), end='.....')
    if file_exist(path=source, verbose=verbose):
        zip_ref = zipfile.ZipFile(source, 'r')
        zip_ref.extractall(destination)
        zip_ref.close()
        if verbose:
            print('[ OK ] zip  extracted ')
