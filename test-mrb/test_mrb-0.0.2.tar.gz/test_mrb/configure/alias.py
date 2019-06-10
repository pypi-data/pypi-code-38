import pathlib


def main():
    print('===== Setting up alias =====')
    path = pathlib.Path('~/file.txt').expanduser()
    open(path, 'w').write('Setting up alias')


