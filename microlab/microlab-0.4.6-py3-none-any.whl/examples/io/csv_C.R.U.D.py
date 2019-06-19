from microlab.io.csv import create_csv, update_csv, read_csv
from microlab.io.files import delete_file

import os

dir = os.getcwd()
file = os.path.join(dir, 'DataFrame.csv')

if __name__ == "__main__":
    print('\n~ TEST CSV')
    """ DATA """


    """ CREATE """
    create_csv(path=file, data={'Name': {'Alex': 10}}, verbose=True)


    """ READ """
    data = read_csv(path=file, verbose=True)


    """ UPDATE """
    update_csv(path=file, data={'Name': {'Alex': 20}}, verbose=True)


    """ DELETE """
    delete_file(path=file, verbose=True)

