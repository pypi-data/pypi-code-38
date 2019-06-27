try:
    from tronald import cli
except ImportError:
    from . import cli

cli.run_cli()
