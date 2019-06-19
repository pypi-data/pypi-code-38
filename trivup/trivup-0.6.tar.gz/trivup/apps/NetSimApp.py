from trivup import trivup

import os
import time
import subprocess

class NetSimApp (trivup.App):
    """ Network simulator app
        Simulates slow or high-latency networks between apps """
    def __init__(self, cluster, conf=None, on=None):
        """
        @param cluster     Current cluster
        @param conf        Configuration dict, see below.
        @param on          Node name to run on (ignored)
        """
        super(NetSimApp, self).__init__(cluster, conf=conf, on=on)

    def operational (self):
        return True

    def exec_cmd (self, cmd, fatal=True):
        r = subprocess.call(cmd, shell=True)
        if r != 0:
            if fatal:
                raise Exception('exec failed with ret %d: %s' % (r, cmd))
                
    def deploy (self):
        """ Set up all shapers """

        dev = "lo"

        self.exec_cmd('tc qdisc add dev %s root handle 1: prio' % dev, fatal=False)
        # Find all allocated TCP ports and create markers for each one.
        for port in self.cluster.tcp_ports:
            self.dbg('Port %d owned by %s' % (port, self.cluster.tcp_ports[port]))
            mark = port
            self.exec_cmd('iptables -t mangle -A POSTROUTING -o %s -p tcp --sport %d -j MARK --set-mark %s' % (dev, port, mark))
            self.exec_cmd('iptables -t mangle -A POSTROUTING -o %s -p tcp --dport %d -j MARK --set-mark %s' % (dev, port, mark))
        

    # Overrides
    def start_cmd (self):
        return None
