from microlab.io.zip import create_zip, extract_zip
from microlab.io.folders import create_folder, delete_folder
from microlab.io.json import create_json
from microlab.io.files import delete_file

import os

dir = os.getcwd()

if __name__ == "__main__":
    print('\n~ TEST ZIP')

    #  create a folder
    folder = os.path.join(dir, 'Test')
    create_folder(path=folder, verbose=True)

    #  create a file inside of the folder
    json = os.path.join(folder, 'test.json')
    create_json(data={'hello': 'wolrd'}, path=json, verbose=True)

    # create a zip of the folder
    zip_file = os.path.join(dir, 'aaa.zip')
    create_zip(source=folder, destination=zip_file, verbose=True)

    # extract a zip to destination
    folder_2 = os.path.join(dir, 'Output')
    create_folder(path=folder_2, verbose=True)
    extract_zip(source=zip_file,destination=folder_2, verbose=True)


    # delete output
    delete_file(path=zip_file, verbose=True)
    delete_folder(path=folder_2, verbose=True)
    delete_folder(path=folder, verbose=True)
