# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Execute notebook with papermill."""
import argparse
import json

import azureml.contrib.notebook._engines
from azureml.contrib.notebook._engines._utils import _update_kwargs, _log_scraps_from_notebook
import papermill as pm

try:
    import scrapbook as sb
    _sb = True
except ImportError:
    _sb = False


def execute_notebook(source_notebook, destination_notebook, infra_args, papermill_args, notebooks_args):
    """Execute notebook with papermill.

    :param source_notebook: Source notebook file name
    :type source_notebook: str
    :param destination_notebook: Source notebook file name
    :type destination_notebook: str
    :param infra_args: Infrastructure arguments
    :type infra_args: dict
    :param papermill_args: Papermill arguments
    :type papermill_args: dict
    :param notebooks_args: Notebook arguments
    :type notebooks_args: dict
    """

    # if kernel name is specified
    kernel_name = papermill_args.get("kernel_name")

    # if not specified try to get it from the notebook
    if not kernel_name:
        with open(source_notebook) as nbfile:
            notebook = json.loads(nbfile.read())
        try:
            kernel_name = notebook.get("metadata").get("kernelspec").get("name")
        except:
            pass

    # create a kernel spec if not installed
    try:
        if kernel_name:
            from jupyter_client.kernelspec import KernelSpecManager
            if not KernelSpecManager().get_all_specs().get(kernel_name):
                # TODO: replace jupyter_client.kernelspec.KernelSpecManager logic
                from ipykernel.kernelspec import install
                install(kernel_name=kernel_name)
            papermill_args["kernel_name"] = kernel_name
    except:
        pass

    papermill_args = _update_kwargs(papermill_args,
                                    input_path=source_notebook,
                                    output_path=destination_notebook,
                                    parameters=notebooks_args)

    infra_args["history"] = infra_args.get("history", False) and _sb

    # check if pm<1.0 to skip all the parameters and use defaults
    from pkg_resources import parse_version
    if parse_version("1.0.0") < parse_version(pm.__version__):
        papermill_args = _update_kwargs(papermill_args, **infra_args)
        pm.execute_notebook(**papermill_args)
    else:
        pm.execute_notebook(**papermill_args)
        if infra_args["history"]:
            from azureml.core import Run
            _log_scraps_from_notebook(destination_notebook, Run.get_context())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", default="",
                        help="input notebook")
    parser.add_argument("-o", "--output", default="",
                        help="output notebook")
    parser.add_argument("-e", "--execution_args", default="",
                        help="execution options")
    parser.add_argument("-p", "--papermill_args", default="",
                        help="papermill arguments")
    parser.add_argument("-n", "--notebook_args", default="",
                        help="notebook parameters")

    args = parser.parse_args()

    execute_notebook(args.input, args.output,
                     json.loads(args.execution_args),
                     json.loads(args.papermill_args),
                     json.loads(args.notebook_args))
