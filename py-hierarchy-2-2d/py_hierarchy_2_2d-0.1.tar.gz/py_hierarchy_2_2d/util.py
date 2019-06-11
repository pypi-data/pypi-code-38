import hashlib
from os import path

# from os import makedirs
from subprocess import getoutput


def if_string_remove_crnl(cell, delim=r"\x01"):
    if not isinstance(cell, str):
        return cell
    for crnl in [
        r"\x00",  # nulls
        delim,  # remove our delim
        "\n",  # unix new lines
        "\r",  # windows carriage returns
    ]:
        cell = cell.replace(crnl, " ")
    return cell


def md5sum(s):
    """take inbound string 's' and return unicode md5 hash (for data uniqueness)

    >>> md5sum('hello world')
    '5eb63bbbe01eeed093cb22bb8f5acdc3'
    """
    m = hashlib.md5()
    m.update(str(s).encode("utf-8"))
    return m.hexdigest()


def spit(f_path, content, fq=False):
    with open(f_path, "w") as i:
        return i.write(content)


def slurp(f_path, fq=False):
    with open(f_path, "r") as i:
        return i.read()


def get_project_dir():
    """Python makes it difficult to yeld our project root... not sure how this
    will work as a python site package; it won't work in service fabric where
    git might not be on the path. For testing only."""
    try:
        return path.abspath(getoutput("git rev-parse --show-toplevel"))
    except FileNotFoundError:
        raise FileNotFoundError("This is not a git repo; Can't find our project dir?")


def prefix_project_dir(relative_path):
    return path.join(get_project_dir(), relative_path)
