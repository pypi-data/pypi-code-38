import pandas as pd
import random
import numpy as np
import pickle

letters = ['a', 'b', 'c', 'd', 'e']
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
strings = ['now', 'is', 'the', 'time']
empties = ['']
nulls = [None, np.NaN]
data = letters + numbers + strings


def create_dataframe(num_rows, num_columns, data=data, include_empties=False, include_nulls=False):
    '''
    Creates a pandas dataframe with given number of rows and columns from a list of data.
    
    Parameters
    ----------
    num_rows : int
        Number of rows in the returned dataframe
    num_columns : int 
        Number of rows in the returned dataframe
    data : list
        List of elements to be used in the dataframe. 
        Default is a variety of letters, numbers and words
    include_empties : bool
        Whether to include at least one empty cell (the empty string '')
        Default False
    include_nulls : bool
        Whether to include at least one cell with a numpy NaN value or python None
        Default False

    Returns
    -------
    dataframe
    
    Examples
    --------
    >>> from random_word import RandomWords
    >>> data = RandomWords().get_random_words()
    >>> create_dataframe(4, 3, data=data, include_empties=True, include_nulls=True)
            col1         col2         col3
    row1  lupine         file-leader  NaN
    row2  skitters       skitters     lupine
    row3  contrat                     thermosetting
    row4  thermosetting  sauces       contrat
    
    
    >>> create_dataframe(2, 5, include_empties=True)
          col1   col2   col3   col4   col5
    row1  the    b      2      time   a
    row2         good   12            2
    
    '''
    rows = []
    cols = []
    for i in range(num_rows):
        rows.append('row' + str(i+1))
    for j in range(num_columns):
        cols.append('col' + str(j+1))
    df = pd.DataFrame(index=rows, columns=cols)
    if include_empties:
        data = data + empties
    if include_nulls:
        data = data + nulls
    for i in range(num_rows):
        for j in range(num_columns):
            df.iloc[i, j] = random.choice(data)
    if include_empties:
        empty_cell_row = random.choice(range(num_rows))
        empty_cell_col = random.choice(range(num_columns))
        df.iloc[empty_cell_row, empty_cell_col] = ''
    if include_nulls:
        null_cell_row = random.choice(range(num_rows))
        null_cell_col = random.choice(range(num_columns))
        while null_cell_row == empty_cell_row & null_cell_col == empty_cell_col:
            null_cell_row = random.choice(range(num_rows))
            null_cell_col = random.choice(range(num_columns))
        df.iloc[null_cell_row, null_cell_col] = random.choice(nulls)
    return df


def count_blanks(column):
    '''
    Counts the blank cells in a column in a pandas dataframe. 
    This is DIFFERENT than counting the null values.
    However, this WILL count cells that contain None.
    
    Parameters
    ----------
    column: a dataframe column or any iterable object
        column on which you want to count the blanks
    
    Returns
    -------
    int
        number of cells in the column that contain blanks
    
    Examples
    --------
    >>> my_df = create_dataframe(6, 4, include_empties=True, include_nulls=True)
    >>> my_df
          col1    col2    col3    col4
    row1  10      is      12      f
    row2  9       time            the
    row3  h       the     Nan     2
    row4  4       is      7       for
    row5  the     4               6
    row6  12      6       None    9
    
    >>> count_blanks(my_df['col3'])
    3
    '''
    count = 0
    for thing in column:
        if not thing:
            count += 1
    return count


def pickle_it(structure, filename):
    '''
    Save the data structure into the filename
    
    Parameters
    ----------
    structure : any
        some data
    filename : str
        the name you want the file to be
    '''
    outfile = open(filename,'wb')
    pickle.dump(structure, outfile)
    outfile.close()
    print(f'the data has been pickled as {filename}.')


def un_pickle_it(filename):
    '''
    Retrieve the data from a file
    
    Parameters
    ----------
    filename : str
        the name of your file
        
    Returns
    -------
    data of type that was saved
    
    '''
    infile = open(filename,'rb')
    returned_structure = pickle.load(infile)
    infile.close()
    return returned_structure
