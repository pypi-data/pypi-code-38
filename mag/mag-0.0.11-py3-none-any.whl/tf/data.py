import os, random
def partition_iterable(
    iterable:list,
    train:float=1, valid:float=0, test:float=0,
    shuffle:bool=True
):
    '''Randomly assigns a list of indicies to train, valid and test datasets

    Note: train + valid + test should be 1

    Args:
        iterable (list): an iterable (line numbers of a file, file names, etc).
        train (float): a float in [0, 1] specifying the percent of the files
            should be allocated to the training dataset
        valid (float): a float in [0, 1] specifying the percent of the files
            should be allocated to the training valid
        test (float): a float in [0, 1] specifying the percent of the files
            should be allocated to the training test
        shuffle (boolean): whether or not to shuffle the iterable prior to
            partitioning. Defaults to true.

    Returns:
        datasets (dict): a dictionary with three keys - train, valid, test -
            each of which correpond to a list of elements from iterable.
    '''
    n = len(iterable)

    if shuffle:
        random.shuffle(iterable)

    a = int(n * (train))
    b = int(n * (train + valid))
    c = int(n * (train + valid + test))

    partitioned = {
        'train': set(iterable[:a]),
        'valid': set(iterable[a:b]),
        'test' : set(iterable[b:])
    }
    return partitioned


from mag.py.files import filelines, streamlines
def downsample(
    files:list,
    write_to_disk:bool = False,
    write_dir:str=None,
    prefix:str='',
    suffix:str=None,
) -> list:
    '''Randomly downsamples the provided files so that they contain the same
    number of lines.

    Args:
        files (list): a list of files where it is assumed that each line is a
            record.
        write_to_disk (boolean): whether to write the downsampled lines to disk.
        write_dir (str): where to write the downsampled file. Defaults to same
            directory as the current file being processed in the files list.
        prefix (str): a string to be preprended to each downsampled file.
            Defaults to ''.
        suffix (str): a string to be appened to each downsampled file. Defaults
            to '_downsampled_to_N', where N is the number of lines in the file.

    Returns:
        result (list): if write_to_disk is true, returns the list of output
            filenames, otherwise returns a list of indicies corresponding to the
            randomly downsampled lines for each file.
    '''
    # how many lines per file
    records_per_file = {file: filelines(file) for file in files}
    # minimum lines of all files
    to = min([records for file, records in records_per_file.items()])
    # indicies of all lines per file
    ranges = [list(range(records)) for file, records in records_per_file.items()]
    # mix up lines
    [random.shuffle(rng) for rng in ranges]
    # take minimum lines for each range
    ranges = [set(rng[:to]) for rng in ranges]
    if not write_to_disk:
        return ranges

    filenames = []
    if suffix is None: suffix = '_downsampled_to_{}'.format(to)
    if write_dir is not None: out_dir = write_dir

    for (i, file) in enumerate(files):
        if write_dir is None: out_dir = os.path.dirname(file)
        fname = streamlines(file, ranges[i], out_dir, prefix, suffix)
        filenames.append(fname)

    return filenames




def paritition_class_text_files(
    files:list,
    train:float=1, valid:float=0, test:float=0,
    shuffle:bool=True,
    write_dir:str=None,
)->dict:
    '''Splits each file into train, validation and test sets at the specified
    ratios.

    Args:
        files (list): a list of files where it is assumed that each line is a
            record.
        train (float): a float in [0, 1] specifying the percent of the files
            should be allocated to the training dataset
        valid (float): a float in [0, 1] specifying the percent of the files
            should be allocated to the training valid
        test (float): a float in [0, 1] specifying the percent of the files
            should be allocated to the training test
        shuffle (boolean): whether or not to shuffle the iterable prior to
            partitioning. Defaults to true.
        write_dir (str): the directory where the split files should be written.
            Defaults to the same directory of the original file.

    '''
    filenames = {}
    for file in files:
        n_lines = filelines(file)
        datasets = partition_iterable(list(range(n_lines)), train, valid, test, shuffle)

        bname, ext = os.path.splitext(os.path.basename(file))
        for (ds, keep) in datasets.items():
            fname = streamlines(file, keep, write_dir, '', '_{}'.format(ds))
            if file not in filenames: filenames[file] = {}
            filenames[file][ds] = fname
    return filenames
