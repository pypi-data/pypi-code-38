# # # # # # # # # # # # # # # # # # # # # # # # # #
# Cloudpickle-based dumper class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import cloudpickle
import shutil
from ..utils import traverse
from ..report import generate

def mkdir (directory, fresh=0):
    if fresh and os.path.exists (directory):
        shutil.rmtree (directory)
    if not os.path.exists (directory):
        os.makedirs (directory)

# generate file name using the format 'pwd_name'
def prefixname (name=None):
    """Generate file name using the format 'pwd_name'."""

    runpath, rundir = os.path.split (os.getcwd ())
    if name is not None:
        return rundir + "_" + name
    else:
        return rundir

def dump (obj, name="dump.dat", directory="output", verbose=0, prefix=False):
    """
    Writes *obj* as Python cloudpickle to given file with name *name* and directory *directory*.
    Creates target directory if this does not exist yet.
    If the file already exists, it is deleted before writing to prevent any corruption.

    returns: string describing the size of the dumped file.
    """

    mkdir (directory)
    if prefix:
        name = prefixname (name)
    path = os.path.join (directory, name)
    if os.path.exists (path):
        os.remove (path)
    if verbose:
        print ('DUMP:', path)
    with open (path, "wb") as f:
        cloudpickle.dump (obj, f)

    return '%.1f GB' % (os.path.getsize (path) / (1024 ** 3))

def text (string, name="dump.txt", directory="output", verbose=0, prefix=False):
    """
    Writes *string* to given file with name *name* and directory *directory*.
    Creates target directory if this does not exist yet.
    If the file already exists, it is deleted before writing to prevent any corruption.

    returns: None
    """

    if directory is not None:
        mkdir (directory)
    if prefix:
        name = prefixname (name)
    if directory is not None:
        path = os.path.join (directory, name)
    else:
        path = name
    if os.path.exists (path):
        os.remove (path)
    if verbose:
        print ('TEXT:', path)
    with open (path, "w") as f:
        f.write (string)

def report (directory, name, obj, title, entries, headers = None, align = 'l', formatters = {}, widths = None, math = False, columns = None, verbose = True, prefix = True):
    """Generate a report file in multiple formats (.dat, .txt, .tex)."""

    dump (obj, name + '.dat', directory, prefix = prefix)
    table = generate.txt_table (entries, headers, title, align, formatters, widths)
    if verbose:
        print (table)
    text (table, name + '.txt', directory, prefix = prefix)
    text (generate.tex_table (entries, headers, align, formatters, math, columns), name + '.tex', directory, prefix = prefix)
    text (title + '.', name + '.cap', directory, prefix = prefix)

def config (component, verbose = False, directory = 'report'):
    """
    Dump the traversed configuration for a specified SPUX component.
    """

    entries = traverse.components (component)
    headers = ['Component', 'Class', 'Options']
    title = 'SPUX components configuration'
    align = ['l', 'l', r'L{0.6\linewidth}']
    report (directory, 'config', component, title, entries, headers, align, verbose = verbose)

def infos (component, info, verbose = False, directory = 'report'):
    """
    Dump the traversed info structure.
    """

    infos = traverse.infos (info)
    if component is not None:
        components = traverse.components (component)
        entries = components [::-1] [:len (infos)]
        headers = ['Component', 'Class', 'Fields', 'Iterators for infos']
        for level in range (len (infos)):
            entries [level] .update (infos [level])
    else:
        entries = infos
        headers = ['Fields', 'Iterators for infos']
    title = 'SPUX infos structure'
    align = ['l', 'l', r'L{0.4\linewidth}', r'L{0.2\linewidth}']
    obj = components
    report (directory, 'infos', obj, title, entries, headers, align, verbose = verbose)