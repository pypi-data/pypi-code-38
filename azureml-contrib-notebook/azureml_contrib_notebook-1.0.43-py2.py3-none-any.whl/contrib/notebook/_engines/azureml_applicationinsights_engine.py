# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Execute notebook with papermill."""
import json

from papermill.engines import NBConvertEngine, papermill_engines, catch_nb_assignment
from .azureml_engine import AzureMLNotebookExecutionManager


try:
    from ansiwrap import strip_color
except:
    def strip_color(value):
        return value


def _dump_dict_json(_dict):
    return {k: v if not isinstance(v, dict) else json.dumps(v) for k, v in _dict.items()}


class AzureMLAppInsightsNotebookExecutionManager(AzureMLNotebookExecutionManager):
    _run = None

    # TODO: autosave every x seconds to upload the output
    def __init__(self,
                 nb,
                 output_path,
                 log_output,
                 history,
                 appinsights_key,
                 tag,
                 payload=None):
        super().__init__(nb, output_path, log_output, history)
        from applicationinsights import TelemetryClient
        self.tc = TelemetryClient(appinsights_key)
        self.tag = tag
        self.payload = payload if payload else {}

    def _log_to_appinsights(self, **payload):
        self.tc.track_event(self.tag, dict(_dump_dict_json(self.nb.metadata.papermill), **payload))
        self.tc.flush()

    @catch_nb_assignment
    def notebook_complete(self, **kwargs):
        super(AzureMLNotebookExecutionManager, self).notebook_complete(**kwargs)
        new_payload = dict(self.payload, status="completed")
        for cell in self.nb.cells:
            if cell.cell_type == "code":
                # Timeout behavior is not determinitstic
                if not cell.metadata.papermill.get('duration') or not cell.execution_count:
                    self._log_to_appinsights(**dict(new_payload,
                                                    error_type="TimeoutError",
                                                    error_message="Cell execution timed out",
                                                    status="timeout"))
                    return

            if cell.get("outputs") is not None:
                for output in cell.outputs:
                    if output.output_type == "error":
                        self._log_to_appinsights(**dict(new_payload,
                                                        cell_index=cell.execution_count,
                                                        source=cell.source,
                                                        error_type=output.ename,
                                                        error_message=output.evalue,
                                                        traceback=strip_color("\n".join(output.traceback)),
                                                        status="failed"))
                        return

        self._log_to_appinsights(**new_payload)


class AzureMLAppInsightsEngine(NBConvertEngine):

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
        appinsights_key=None,
        tag="notebook",
        payload=None,
        **kwargs
    ):
        nb_man = AzureMLAppInsightsNotebookExecutionManager(
            nb,
            output_path=output_path,
            log_output=log_output,
            history=history,
            appinsights_key=appinsights_key,
            tag=tag,
            payload=payload
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


papermill_engines.register('azureml_appinsights_engine', AzureMLAppInsightsEngine)
