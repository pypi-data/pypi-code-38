import sys

from time import sleep
from core import tor_network as tn


def start():
    tn.TorService._maxtor = 3
    tn.TorService._db_type = 'ms'
    tn.TorService._database_config = r'C:\Users\draganm\Documents\database.config'
    ts = tn.TorService()
    while True:
        ts.main()
        waittime = 360
        for i in range(waittime):
            sys.stdout.write("\rwait {}/{}".format(i, waittime))
            sleep(1)
        print("\n")

start()
