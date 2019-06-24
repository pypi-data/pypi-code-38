import psutil
import time
import configparser
import json
import os
from datetime import datetime

class stat:
    def __init__(self):
        self.cpu = str(psutil.cpu_percent())
        self.mem = str(psutil.virtual_memory().percent)
        self.ro = str(psutil.disk_io_counters().read_bytes >> 10)
        self.rw = str(psutil.disk_io_counters().write_bytes >> 10)
        self.snet = str(psutil.net_io_counters().bytes_sent >> 10)
        self.rnet = str(psutil.net_io_counters().bytes_recv >> 10)

print(stat.__doc__)

conf = configparser.ConfigParser()
conf.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'conf.ini'))

interval = conf.get('begin', 'interval')
outputformat = conf.get('begin', 'output')

f = open("statlog." + outputformat, "w")

i = 1
while i > 0:
    if outputformat == "json":
        prints = json.dumps({
            "SNAPSHOT": str(i),
            "Timestamp": datetime.now().strftime('%Y.%m.%d, %H.%M.%S'),
            "cpu,%": stat().cpu,
            "memory_info": stat().mem,
            "hard_ro_kb": stat().ro,
            "hard_rw_kb": stat().rw,
            "network_sent_kb": stat().snet,
            "network_recv_kb": stat().rnet
        }, indent=2)
        f.write(prints)
        f.write('\n')
        time.sleep(int(interval))
        i += 1
    elif outputformat == "txt":
        prints = "SNAPSHOT :" + str(i), \
        datetime.now().strftime('%Y.%m.%d, %H.%M.%S') + ":", \
        "cpu,%:" + stat().cpu, \
        "memory_info:" + stat().mem, \
        "hard_ro_kb: " + stat().ro, \
        "hard_rw_kb: " + stat().rw, \
        "network_sent_kb: " + stat().snet, \
        "network_recv_kb: " + stat().rnet
        f.write(str(prints))
        f.write('\n')
        time.sleep(int(interval))
        i += 1

stat().func()
