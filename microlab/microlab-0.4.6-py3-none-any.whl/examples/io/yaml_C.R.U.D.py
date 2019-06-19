from microlab.io.yaml import create_yaml, read_yaml, update_yaml
from microlab.io.files import delete_file
import os

if __name__ == "__main__":
    print('\n~ TEST YAML')
    dummy_filename = 'test.yaml'
    folder_path = os.getcwd()
    filename = os.path.join(folder_path, dummy_filename)

    # Data
    data = {'name': 'Test', 'id': 10}

    #  Create
    create_yaml(data=data, path=filename, verbose=True)

    #  Read
    data = read_yaml(path=filename, verbose=True)

    # Update
    new_data = {'name': 'new name',
                'telephones': {'mobile': 00000000,
                               'home': 1111111,
                               'office': 22222222}}
    update_yaml(data=new_data, path=filename, verbose=True)

    # Delete
    delete_file(path=filename, verbose=True)

