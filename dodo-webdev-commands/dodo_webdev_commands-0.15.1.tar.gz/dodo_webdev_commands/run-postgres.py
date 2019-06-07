from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    args.pg_version = Dodo.get_config('/SERVER/pg_version', '9.5')
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run([
        "sudo",
        "-u",
        "postgres",
        "/usr/lib/postgresql/%s/bin/postgres" % args.pg_version,
        "-D"
        "/var/lib/postgresql/%s/main" % args.pg_version,
        "-c",
        "config_file=/etc/postgresql/%s/main/postgresql.conf" %
        args.pg_version,
    ],
             cwd="/")  # noqa
