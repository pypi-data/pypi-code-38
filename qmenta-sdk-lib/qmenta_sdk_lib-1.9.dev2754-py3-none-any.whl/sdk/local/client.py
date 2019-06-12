import logging

from qmenta.sdk.client import ExecClient


class LocalExecClient(ExecClient):  # Override main execution client

    def __init__(self, context, log_path):
        super(LocalExecClient, self).__init__(
            analysis_id="local",
            comm=None,
            context=context,
            log_path=log_path
        )

    def set_state(self, state, **kwargs):
        """
        Set analysis state

        Parameters
        ----------
        state : AnalysisState
            One of AnalysisState.RUNNING, AnalysisState.COMPLETED, AnalysisState.EXCEPTION or AnalysisState.NO_FILES
        kwargs : dict
        """
        logging.getLogger(__name__).info(
            'State = {state!r} for local execution'.format(state=state.value))

    def upload_log(self):
        pass
