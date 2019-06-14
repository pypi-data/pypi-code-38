import logging

logging.basicConfig(filename='/tmp/console-ui.log', level=logging.INFO)



def log(*args):
    logging.info(' '.join([str(i) for i in args]))
