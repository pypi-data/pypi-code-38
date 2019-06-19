from microlab.io.files import create_file, delete_file, update_file, read_file
import os

dir = os.getcwd()
file = os.path.join(dir, 'aa.txt')

if __name__ == '__main__':
    print('\n~ TEST FILE {}'.format(file))
    """ DATA """
    string_data ='helo,world string'
    bytes_data = b'helo,world bytes'

    """ CREATE """
    create_file(path=file, data=string_data, verbose=True)


    """ READ """
    data = read_file(path=file, verbose=True)


    """ UPDATE """
    update_file(path=file, data=bytes_data, verbose=True)


    """ DELETE """
    delete_file(path=file, verbose=True)

