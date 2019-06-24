"""Utility functions."""

import errno
import glob
import logging
import os


def mkdir_p(path):
    """Python equivalent of bash mkdir -p.

    Parameters
    ----------
    path : str
        Directory path to create.

    Raises
    ------
    OSError if the directory does not already exist and cannot be created
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def which(executable):
    """Search the PATH for the specified executable file.

    Parameters
    ----------
    executable : str
        Name of executable

    Returns
    -------
    path : str, or None
        Path to the executable or None if not found on the PATH.
        If the excutable is available at more than one location,
        Only the first path is returned.
    """
    path = os.environ.get('PATH', "")

    for p in path.split(os.pathsep):
        p = os.path.join(p, executable)
        if os.access(p, os.X_OK):  # Can the file be executed?
            return p

    return None


def basename_no_ext(path):
    """Strip the directory and extension from a file path, returning the file name without extension.

    Only one level of extension is removed (the last).

    Parameters
    ----------
    path : str
        File path.

    Returns
    -------
    basename : str
        Filename without the extension.

    Examples
    --------
    >>> basename_no_ext("aaa/bbb")
    'bbb'
    >>> basename_no_ext("aaa/bbb.ccc")
    'bbb'
    >>> basename_no_ext("aaa/bbb.ccc.ddd")
    'bbb.ccc'
    """
    # Remove directory
    base_file_name = os.path.basename(path)

    # Remove extension
    base_file_name, _ = os.path.splitext(base_file_name)

    return base_file_name


def fasta_basename(fasta_path):
    """Strip the directory and extension from a fasta path, returning the basename.

    Parameters
    ----------
    fasta_path : str
        Fasta file path.

    Returns
    -------
    basename : str
        Fasta filename without the extension(s).

    Examples
    --------
    >>> fasta_basename("aaa/bbb.fa")
    'bbb'
    >>> fasta_basename("aaa/bbb.fas")
    'bbb'
    >>> fasta_basename("aaa/bbb.fasta")
    'bbb'
    >>> fasta_basename("aaa/bbb.fna")
    'bbb'
    >>> fasta_basename("aaa/bbb.gz")
    'bbb'
    >>> fasta_basename("aaa/bbb.fasta.gz")
    'bbb'
    """
    # Remove directory
    base_file_name = os.path.basename(fasta_path)

    # Remove .gz
    _, extension = os.path.splitext(base_file_name)
    if extension == ".gz":
        base_file_name = base_file_name[0: -3]

    # Remove .fa .fas .fasta .fna
    _, extension = os.path.splitext(base_file_name)
    for ext in [".fa", ".fas", ".fasta", ".fna"]:
        if extension == ext:
            base_file_name = base_file_name[0: -len(ext)]
            break

    return base_file_name


def get_file_list(container):
    """Given a directory containing files, or a file containing paths to other files,
    return a list of paths to the files.

    Parameters
    ----------
    container : str
        Directory containing files, or a file containing paths to other files.

    Returns
    -------
    paths : list of str
        List of paths to files
    """
    paths = []

    if os.path.isfile(container):
        with open(container) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                glob_paths = glob.glob(line)
                for path in glob_paths:
                    paths.append(path)
        return sorted(paths)

    if os.path.isdir(container):
        paths = os.listdir(container)
        paths = [os.path.join(container, file) for file in paths]
        return sorted(paths)

    logging.error("%s is neither a directory, nor a file containing paths to other files." % container)
    return paths
