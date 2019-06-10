# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json

from azure.cli.core.util import CLIError

# When az CLI releases publically then from azure.cli.core.extensions import get_extension
# will replace from azure.cli.core.extension import get_extension
try:
    from azure.cli.core.extension import get_extension
except Exception as e:
    from azure.cli.core.extensions import get_extension

from azureml._cli_common.ml_cli_error import MlCliError


def _handle_exceptions(exc):
    """
    :param exc: Exception thrown by AML CLI
    :raises CLIError
    """

    ml_cli_version = None
    try:
        ml_cli_version = get_extension('azure-cli-ml').version
        if isinstance(exc, MlCliError):
            response = exc.to_json()
            response['Azure-cli-ml Version'] = ml_cli_version
            raise CLIError(json.dumps(response, indent=4, sort_keys=True))
        elif isinstance(exc, CLIError):
            response = {'Error': exc.args[0]}
            response['Azure-cli-ml Version'] = ml_cli_version
            raise CLIError(json.dumps(response, indent=4, sort_keys=True))
    except CLIError:
        raise
    except:  # noqa: E722
        pass

    response = {'Azure-cli-ml Version': ml_cli_version,
                'Error': exc}
    raise CLIError(response)
