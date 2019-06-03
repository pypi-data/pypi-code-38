from lifelib.commands import create
from os import path

here = path.abspath(path.dirname(__file__))

if __name__ == '__main__':
    create.main([
        "--template",
        "solvency2",
        here + "\\temp\\solvency2"
    ])
