import logging 



logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO) 
formatter = logging.Formatter('%(asctime)s | %(levelname)s -> %(message)s') 

stream_handler = logging.StreamHandler() 
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO) 

logger.addHandler(stream_handler) 