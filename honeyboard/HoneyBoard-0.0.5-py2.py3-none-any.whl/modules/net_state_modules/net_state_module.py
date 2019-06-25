import socket
import logging


#GET NET STATE INFO BY PINGING GOOGLE IP
def get_net_state_info():
    try:
        # return "OK"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        result =(s.getsockname()[0])
        s.close()
        return result
    except Exception as e:
        logging.error("Error. " + str(e))
        return str(e)
