import importlib
import inspect
import logging

from enum import Enum

from qmenta.sdk.context import NoFilesError


class AnalysisState(Enum):
    RUNNING = 'running'
    COMPLETED = 'completed'
    EXCEPTION = 'exception'
    NO_FILES = 'no_files'


class ExecClient(object):

    def __init__(self, analysis_id, comm, context, log_path):
        self.__analysis_id = analysis_id
        self.__comm = comm
        self.__context = context
        self.__log_path = log_path

    def __call__(self, user_script_path):
        """
        Run an analysis provided by the user

        Parameters
        ----------
        user_script_path : str
            Should look like 'path.to.module:object', where 'object' should be an importable analysis tool class
            or a function taking one 'context' argument.
        """

        logger = logging.getLogger(__name__)
        logger.info("Launching: {}".format(user_script_path))

        analysis_state = None
        try:
            # noinspection PyTypeChecker
            self.set_state(AnalysisState.RUNNING, log_path=self.__log_path)
            class_or_func = load_user_analysis(user_script_path)
            self.__context.fetch_analysis_data()

            # run the analysis
            # may allow classes to be used later
            assert inspect.isfunction(class_or_func)
            self.__context.set_progress(value=0, message='Running')
            class_or_func(self.__context)
        except NoFilesError:
            logger.warning('No files found')
            analysis_state = AnalysisState.NO_FILES
        except Exception as e:
            logger.exception(e)
            self.__context.set_progress(message='Error')
            analysis_state = AnalysisState.EXCEPTION
            raise e
        else:
            self.__context.set_progress(message='Completed', value=100)
            analysis_state = AnalysisState.COMPLETED
        finally:
            self.upload_log()
            # noinspection PyTypeChecker
            self.set_state(analysis_state)

    def set_state(self, state, **kwargs):
        """
        Set analysis state

        Parameters
        ----------
        state : AnalysisState
            One of AnalysisState.RUNNING, AnalysisState.COMPLETED, AnalysisState.EXCEPTION or AnalysisState.NO_FILES
        kwargs : dict
        """
        assert isinstance(state, AnalysisState), "'state' is {}, not an 'AnalysisState'".format(state)
        data_to_send = {
            "analysis_id": self.__analysis_id,
            "state": state.value,
        }
        data_to_send.update(kwargs)
        logging.getLogger(__name__).info(
            'State = {state!r} for analysis {analysis_id}'.format(**data_to_send))
        self.__comm.send_request(
            "analysis_manager/set_analysis_state", data_to_send)

    def upload_log(self):

        data_to_send = {
            'analysis_id': self.__analysis_id
        }
        log_contents = ''
        try:
            with open(self.__log_path, 'r') as log_file:
                log_contents = log_file.read()
        except IOError:
            log_contents = "Log file error ({})".format(self.__log_path)
        finally:
            self.__comm.send_files('analysis_manager/upload_log',
                                   files={'file': ('exec.log', log_contents)},
                                   req_data=data_to_send)


def load_user_analysis(user_script_path):
    module_name, class_or_func_name = user_script_path.split(':')
    user_module = importlib.import_module(module_name)
    class_or_func = getattr(user_module, class_or_func_name)
    return class_or_func
