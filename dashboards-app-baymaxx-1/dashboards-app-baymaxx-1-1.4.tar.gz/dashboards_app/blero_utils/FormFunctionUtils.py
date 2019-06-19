
import logging
import inspect
import pandas as pd

from celery import Task

from dashboards_app.celery_progress.backend import ProgressRecorder

def SetUserLog(file_name):


    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create a file handler
    handler = logging.FileHandler(file_name)
    handler.setLevel(logging.DEBUG)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(lineno)d- %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)

    return logger




class BaseFormExecution(Task):


    def custom_init(self,file_name,dict_form,data_1,data_2):

        self.set_user_log(file_name)
        self.dict_form=dict_form
        dataf1=pd.DataFrame(data_1)
        dataf1.columns=["selection"]
        dataf2=pd.DataFrame(data_2)
        dataf2.columns=["selection"]
        self.data_1=dataf1
        self.data_2=dataf2
        self.logger_level_print=0
        self.log_file_name=file_name



    def set_grid_data(self,grid_data_df):
        """
        Sets grid data if the form has a grid
        :param grid_data_df:
        :return:
        """

        self.grid_data=grid_data_df.to_json(orient='index')

    def get_value_from_form(self,key_name):
        """
        Returns the value in the input box from a from input
        :param key_name: key_name as described in the form
        :return: returns value as string
        """
        return [ v for k,v in self.dict_form.items() if key_name in k][0]


    def increase_logger_level(self):
        self.logger_level_print=self.logger_level_print+1
        self.pre_text=' '.join(["..."] * self.logger_level_print)


    def decrease_logger_level(self):
        self.logger_level_print=self.logger_level_print-1
        self.pre_text = ' '.join(["..."] * self.logger_level_print)

    def logger_info(self,message):


        self.logger.info(self.pre_text+str(message))

    def logger_debug(self,message):


        self.logger.debug(self.pre_text+str(message))

    def logger_exception(self,message):
        self.logger.exception(self.pre_text + str(message))


    def set_user_log(self,file_name):
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.DEBUG)
        # create a file handler
        handler = logging.FileHandler(file_name)
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(lineno)d- %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(handler)
        self.pre_text = ''
        self.logger=logger

    def run(self, method, **kwargs):
        self.custom_init(**kwargs)

        # Progress recorder
        self.progress_recorder = ProgressRecorder(self)
        self.progress_recorder.set_progress(1, 10)


        # Get the method attribute from the object

        execution_method = getattr(self, method)



        self.progress_recorder.set_progress(2, 10)

        # Execute the method attribute
        execution_method()

        # Example
        self.progress_recorder.set_progress(9, 10)
        import time
        time.sleep(5)
        self.progress_recorder.set_progress(10, 10)

