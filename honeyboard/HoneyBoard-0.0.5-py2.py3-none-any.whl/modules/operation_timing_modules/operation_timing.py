import datetime
import logging
#get start time
def get_start_time():
    return datetime.datetime.now()


#print execution time
def print_execution_time(start_time, message=""):
    try:

        end_time = datetime.datetime.now()
        if (message==''):
            logging.info('Duration: {}'.format(end_time - start_time))

        else:
            logging.info(message+'. Duration: {}'.format(end_time - start_time))

        pass
    except Exception as e:
        pass