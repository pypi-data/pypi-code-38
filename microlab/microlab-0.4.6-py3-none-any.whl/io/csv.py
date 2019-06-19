from microlab.io.files import delete_file
import pandas

""" CSV """


# Create
def create_csv(data, path, verbose=False):
    if verbose:
        print('[  C  ]  {}'.format(path), end='.....')
    df = pandas.DataFrame.from_dict(data)
    df.to_csv(path_or_buf=path, header=True)
    if verbose:
        print('[ OK ] create new csv file')


# Read
def read_csv(path, verbose=False):
    if verbose:
        print('[  R  ]  {}'.format(path), end='.....')
    pandas.read_csv(filepath_or_buffer=path)
    if verbose:
        print('[ OK ] read from csv file')



# Update
def update_csv(data, path, verbose=False):
    if verbose:
        print('[  U  ]  {}'.format(path), end='.....')
    new_df = pandas.DataFrame.from_dict(data)
    df = pandas.read_csv(filepath_or_buffer=path)
    df.update(new_df)
    create_csv(data=df, path=path, verbose=False)
    if verbose:
        print('[ OK ] update csv file')


