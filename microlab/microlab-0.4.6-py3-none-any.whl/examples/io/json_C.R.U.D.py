from microlab.io.json import create_json, read_json, update_json
from microlab.io.files import delete_file
import os

if __name__ == "__main__":
    print('\n~ TEST JSON')
    dummy_filename = 'test.json'
    folder_path = os.getcwd()
    filename = os.path.join(folder_path, dummy_filename)

    # Data
    data = {'name': 'Test', 'id': 10}

    #  Create
    create_json(data=data, path=filename, verbose=True)

    #  Read
    data = read_json(path=filename, verbose=True)

    # Update
    new_data = {'name': 'new name'}
    update_json(data=new_data, path=filename, verbose=True)

    # Delete
    delete_file(path=filename, verbose=True)

