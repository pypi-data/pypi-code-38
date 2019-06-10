# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Execute notebook with papermill."""
from papermill.engines import NBConvertEngine, papermill_engines, NotebookExecutionManager, catch_nb_assignment
from ._utils import _extract_scraps_from_cell, _log_scrap_to_history, _batchsize
from azureml.core import Run


class AzureMLNotebookExecutionManager(NotebookExecutionManager):
    _run = None

    # TODO: autosave every x seconds to upload the output
    def __init__(self,
                 nb,
                 output_path,
                 log_output,
                 history):
        super().__init__(nb, output_path, log_output)
        self.history = history

        if history:
            self._run = Run.get_context()

    def _log_metrics(self, cell):
        if not self.history:
            return
        for name, scrap in _extract_scraps_from_cell(cell).items():
            _log_scrap_to_history(scrap, self._run, _batchsize)

    # To be implemented when UX renders notebooks
    def _upload(self):
        pass

    @catch_nb_assignment
    def cell_complete(self, cell, cell_index=None, **kwargs):
        super(AzureMLNotebookExecutionManager, self).cell_complete(cell, cell_index=None, **kwargs)
        self._log_metrics(cell)
        self._upload()

    @catch_nb_assignment
    def notebook_complete(self, **kwargs):
        super(AzureMLNotebookExecutionManager, self).notebook_complete(**kwargs)
        self._upload()


class AzureMLEngine(NBConvertEngine):

    @classmethod
    def execute_notebook(
        cls,
        nb,
        kernel_name,
        output_path=None,
        progress_bar=True,
        log_output=False,
        history=None,
        timeout=None,
        **kwargs
    ):
        nb_man = AzureMLNotebookExecutionManager(
            nb,
            output_path=output_path,
            log_output=log_output,
            history=history
        )

        nb_man.notebook_start()
        try:
            nb = cls.execute_managed_notebook(nb_man, kernel_name, log_output=log_output, timeout=timeout, **kwargs)
            if nb:
                nb_man.nb = nb
        finally:
            nb_man.cleanup_pbar()
            nb_man.notebook_complete()

        return nb_man.nb


papermill_engines.register('azureml_engine', AzureMLEngine)
