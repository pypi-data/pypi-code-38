# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

try:
    import scrapbook as sb
    from scrapbook.models import Notebook
    from nbformat.notebooknode import NotebookNode
except ImportError:
    pass


_batchsize = 50


# TODO: nteract-scrapbook should provide public method to get scraps from cell
def _extract_scraps_from_cell(cell):
    nb = Notebook(NotebookNode({"cells": [cell]}))
    return nb.scraps


def _log_scrap_to_history(scrap, run, batchsize):
    if isinstance(scrap.data, list):
        for index in range(0, len(scrap.data), batchsize):
            run.log_list(scrap.name, scrap.data[index:index + batchsize])
    else:
        run.log(scrap.name, scrap.data)


def _log_scraps_from_notebook(notebook, run, batchsize=_batchsize):
    results = sb.read_notebook(notebook)
    for key, value in results.scraps.items():
        _log_scrap_to_history(value, run, batchsize)


def _update_kwargs(args, **kwargs):
    return dict(args, **kwargs)
