import sys
import logging
import json
import click
import collections

from alfa_sdk.common.stores import ConfigStore
from alfa_cli.common.exceptions import AlfaCliError


class Logger:
    def __init__(self, *, verbose=None, pretty=None):
        if verbose is None:
            verbose = ConfigStore.get_value("verbose", False, is_boolean=True)

        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(format="%(message)s", level=log_level, stream=sys.stdout)

        self.verbose = verbose
        self.pretty = pretty

    def result(self, res):
        try:
            res = json.loads(str(res))
        except:
            pass

        if self.pretty:
            res = json.dumps(res, indent=4)
        else:
            res = json.dumps(res)

        click.echo(res)
        sys.exit(0)

    @classmethod
    def error(cls, err):
        verbose = logging.getLogger().isEnabledFor(logging.DEBUG)

        # Parse Error Object

        message = str(err)
        data = None
        if hasattr(err, "kwargs") and "error" in err.kwargs:
            try:
                data = json.loads(err.kwargs.get("error"))

                if isinstance(data, collections.Mapping):
                    if "error" in data:
                        data = data.get("error")

                    if "stack" in data and not verbose:
                        data.pop("stack")

                message = message.replace(err.kwargs.get("error"), "")
                if message.endswith(": "):
                    message = message[:-2]

            except:
                pass

        error = {
            "name": type(err).__name__,
            "message": message
        }

        if data is not None:
            error["error"] = data

        # Print

        error = json.dumps({"error": error}, indent=4)
        click.secho(error, err=True, fg="red")

        if verbose:
            raise err
        sys.exit(1)
