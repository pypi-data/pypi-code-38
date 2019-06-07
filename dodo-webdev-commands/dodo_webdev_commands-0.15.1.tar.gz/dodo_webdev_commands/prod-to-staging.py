from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from plumbum.cmd import dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    org_layer = dodo('layer', 'django')[:-1]

    Dodo.run(['dodo', 'layer', 'django', 'prod'], cwd='.')
    Dodo.run(['dodo', 'django-manage', 'dump-db'], cwd='.')
    Dodo.run(['dodo', 'layer', 'django', 'staging'], cwd='.')
    Dodo.run(['dodo', 'django-manage', 'restore-db'], cwd='.')
    Dodo.run(['dodo', 'django-manage', 'anonymize_db'], cwd='.')
    Dodo.run(['dodo', 'django-manage', 'dump-db'], cwd='.')
    Dodo.run(['dodo', 'layer', 'django', org_layer], cwd='.')
