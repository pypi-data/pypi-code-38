# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import os

from .._utils import ui


def load_feather(file_path=None, columns=None):
    """Load a Dataset from a feather format file (experimental).

    Parameters
    ----------
    file_path : None | str
        Path to a feather file. If None (default), a system file dialog will be
        shown. If the user cancels the file dialog, a RuntimeError is raised.
    columns : sequence of str
        Only import a subset of columns (optional).

    Returns
    -------
    data : Dataset
        Data read from the file.
    """
    from .feather_reader import Reader

    if file_path is None:
        filetypes = [("Feather (*.feather)", '*.feather'), ("All files", '*')]
        file_path = ui.ask_file("Select Feather format file to load", "", filetypes)
        if file_path is False:
            raise RuntimeError("User canceled")
        else:
            print("load %r" % (file_path,))
    else:
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            new_path = os.extsep.join((file_path, 'arrow'))
            if os.path.exists(new_path):
                file_path = new_path

    reader = Reader(file_path)
    return reader.read(columns)
