import os
def filelines(filename:str) -> int:
    '''Quickly returns the number of lines in a file.

    Args:
        filename (str): full path to file

    Returns:
        line_no (int): the number of lines if succsesful, None otherwise.
    '''
    with open(filename, 'r') as file:
        return sum(1 for line in file)
    return None



def slices(arr:list, slcs:list) -> list:
    '''Applies a list of slices to a list, joining the results.

    Args:
        arr (list): a list
        slcs (list): a list of slices

    Returns:
        filtered (list): The elements of arr which correspond to slcs
    '''
    return [col for slc in slcs for col in arr[slc]]


def linesplit(line:str, delim:str='\t', newline:str='\n') -> list:
    '''Convention for procesing deliminated lines of a file

    Args:
        line (str): a line of a file
        delim (str): what seperates elements in the line
        newline (str): the newline character

    Returns:
        elements (list): the list of elements of the line split by delim and
            with the newline removed.
    '''
    return line.rstrip(newline).split(delim)

def readsplit(file_object, delim:str='\t', newline:str='\n') -> list:
    '''Convention for procesing deliminated lines of a file

    Args:
        file_object: an opened file from which lines could be read
        delim (str): what seperates elements in the line
        newline (str): the newline character

    Returns:
        elements (list): the list of elements of next line of the file, split by
            delim and with the newline removed.
    '''
    return linesplit(file_object.readline(), delim, newline)


def lineslice(line:str, slcs:list, delim:str='\t', newline:str='\n', add_newline_q:bool=True) -> str:
    '''Convention for extracting elements of a deliminated lines of a file

    Args:
        line (str): a line of a file
        slcs (list): a list of slices of indicating what elements to extract
        delim (str): what seperates elements in the line
        newline (str): the newline character
        add_newline_q (bool): whether or not to add a newline after remerging
            the line.

    Returns:
        filtered_line (str): the string of delim seperated elements from the
            line after being filtered by lists of slcs.
    '''
    return delim.join(slices(linesplit(line, delim, newline), slcs)) \
    + (newline if add_newline_q else '')


def readslice(file_object, slcs:list, delim:str='\t', newline:str='\n', add_newline_q:bool=True) -> str:
        '''Convention for extracting elements of a deliminated lines of a file

        Args:
            file_object: an opened file from which lines could be read
            slcs (list): a list of slices of indicating what elements to extract
            delim (str): what seperates elements in the line
            newline (str): the newline character
            add_newline_q (bool): whether or not to add a newline after remerging
                the line.

        Returns:
            filtered_line (str): the string of delim seperated elements from the
                next line of the file_object after being filtered by lists of
                slcs.
        '''
    return lineslice(file_object.readline(), slcs, delim, newline, add_newline_q)




def multireplace(string:str, replacements:list):
    '''Apply as many replaces to string as specified by replacements

    Args:
        string (str): the string to transform
        replacements (list): a list of (find(str), replace(str)) tuples

    Returns:
        transformed (str): the provided string after sequentially updating
            by calling replace(find, replace) for all elements in replacements

    '''
    transformed = string
    for (find, replace) in replacements:
        transformed.replace(find, replace)
    return transformed


def streamlines(
    file:str,
    keep:list,
    write_dir:str=None,
    prefix:str='',
    suffix:str='',
):
    '''Write the lines specified in <keep> to specified output file.

    Args:
        file (str): full path of a file.
        keep (list): indicies of the lines to keep in the file.
        write_dir (str): directory to write the truncated file. Defaults to same
            directory as file.
        prefix (str): a string to add before the basename of the file in the
            write_dir. Defaults to ''.
        suffix (str): a string to add after the basename of the file in the
            write_dir. Defaults to ''.

    Returns:
        fname (str): the filename where the results were written.

    '''
    if write_dir is None: write_dir = os.path.dirname(file)
    bname, ext = os.path.splitext(os.path.basename(file))
    fname = os.path.join(write_dir, '{}{}{}.{}',format(prefix,bname,suffix,ext))

    with open(file, 'r') as ifile, open(fname, 'w') as ofile:
        for (i, line) in enumerate(ifile):
            if i in keep:
                ofile.write(line)
    return fname
