"""
Author: Christopher Mendoza
A framework to analyze fiber optic connections.
Version 2.0

"""

import pandas as pd
from netmiko import ConnectHandler
import paramiko
import re
import datetime


def device_driver(model):
    """
    Returns the information needed to parse switch CLI output

    model: The model name string

    returns: Dictionary with the CLI command the units and output format
    """
    return{
            'ubiquiti_edgeswitch' : ['ubiquiti_edgeswitch','show fiber-ports optics all','dBm',4,5],
            'dlink_dgs' : ['ubiquiti_edgeswitch','show interfaces transceiver','mW',4,5]
            }[model]



def dBmtomw(value):
    """
    Converts dBm to mw

    value: dBm value

    returns: mW value
    """
    return round(10**(value/10),3)    
    

def strtofloat(string,units):
    """
    Converts the string from the CLI output to a float value.

    string: The CLI output string
    units: mW or dBm

    returns: Float value
    """
    pattern = re.compile('-?\d+\.?\d*')
    match = pattern.findall(string)
    if len(match) > 0:
        value = [m for m in match][0]
    elif units == 'mW':
        value = 0
    elif units == 'dBm':
        value = -40
    return round(float(value),3)

 
def getCS(Tx,Rx,delta,TxAcc,RxAcc):
    """
    Provides contamination analysis between two SFPs connected by a fiber optic cable.

    Tx: the Tx power in mW
    Rx: the Rx power in mW
    delta: The amount of expected power loss due to non-contaminant factors
    TxAcc: The accuracy of the tx SFP
    RxAcc: The accuracy of the rx SFP

    returns: Dictionary with the power lost, contamination score, contamination threshold and if the analysis declares the connection as contaminated.
    """
    IL = round(Tx - Rx,3)
    alpha = Tx * (1 - (10**(-delta/10)))
    PowerThresh = alpha + Tx*((10**(TxAcc/10)) - 1) - Rx*((10**(-RxAcc/10)) - 1)
    CC = 100/(10**(5*(Tx-alpha)) - 1)
    CS = CC*(10**(5*(IL - alpha)) - 1)
    CS = max(0,CS)
    CSThresh = CC*(10**(5*(PowerThresh - alpha)) - 1) 
    return {'Power Lost (mW)' : max(0,IL), 'Contamination Score' : round(CS,2), 'Contamination Threshold' : round(CSThresh,2), 'Contaminated' : CS >= CSThresh}




class node:
    """
    A class for a switch or other SFP enabled device.
    """
    def __init__(self,name,ip,model,usr,pas):
        """
        Sets up switch model, ip address and gives it a name.

        name: name of node
        ip: ip address of node
        model: model of node, must be same as in device_driver
        usr: username for CLI
        pas: password for CLI
        """
        self.model, self.ip, self.name = model, ip, name
        self.devtype , self.command, self.units, self.Txpos, self.Rxpos = device_driver(model) 
        self.setup = {
            'device_type': self.devtype,
            'ip':   ip,
            'username': usr,
            'password': pas,
            }
        
    def Connect(self):
        """
        Connects to node
        """
        self.Conn = ConnectHandler(**self.setup)
        
    def Disconnect(self):
        """
        Disconnects from node
        """
        self.Conn.disconnect()
        
    def sendCommand(self,s):
        """
        Sends command to node.

        s: command to send

        returns: CLI output
        """
        out = self.Conn.send_command(s)
        return out
    
    def sendCommandTiming(self,s,res):
        """
        Send command with timing, this is necessary for certain commands.

        s: command to send
        res: response to s command

        returns: CLI output
        """
        out = self.Conn.send_command_timing(s).split('\n')[:-1]
        outcomp = []
        while True:
            if outcomp != out:
                outcomp = out[:]
                new = self.Conn.send_command_timing(res).split('\n')[:-1]
                for n in new:
                    out.append(n)
                print(out)
                print('\n\n\n\n\n',outcomp)
            else:
                break
        return out
        
class connection:
    """
    Class for connection between two nodes
    """
    def __init__(self,name,node1,node2,port1,port2,delta,p1acc,p2acc):
        """
        Sets up connection

        name: name of connection
        node1: instance of node class
        node2: instance of node class
        port1: the port of interest on node1
        port2: the port of interest on node2
        delta: the amount of power loss due to non-contaminant factors
        p1acc: the accuracy of the SFP in port1
        p2acc: the accuracy of the SFP in port2
        """
        self.name = name
        self.node1 = node1
        self.node2 = node2
        self.port1 = port1
        self.port2 = port2
        self.delta = delta
        self.p1acc = p1acc
        self.p2acc = p2acc
        
    def __enter__(self):
        self.Connect()
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.Disconnect()


    def Connect(self):  
        """
        Connect to both nodes involved in this connection
        """          
        while True:
            try:
                self.Conn1 = ConnectHandler(**self.node1.setup)
                self.Conn2 = ConnectHandler(**self.node2.setup)
            except paramiko.ssh_exception.SSHException:
                continue
            except OSError:
                print('Could not connect')
                break
            break
            
            
    def DetectContamination(self):
        """
        Uses getCS function to detect contamination.
        """

        out1 = self.Conn1.send_command(self.node1.command).split('\n')
        out2 = self.Conn2.send_command(self.node2.command).split('\n')
        now = datetime.datetime.now()
        
        for n in out1:
            if f'/{self.port1}' in n:
                n1vals = n.split()
                n1Tx = strtofloat(n1vals[self.node1.Txpos],self.node1.units)
                n1Rx = strtofloat(n1vals[self.node1.Rxpos],self.node1.units)
                
                if self.node1.units == 'dBm':
                    n1Tx = dBmtomw(n1Tx)
                    n1Rx = dBmtomw(n1Rx)
                
        for n in out2:
            if f'/{self.port2}' in n:
                n2vals = n.split()
                n2Tx = strtofloat(n2vals[self.node2.Txpos],self.node2.units)
                n2Rx = strtofloat(n2vals[self.node2.Rxpos],self.node2.units)
                
                if self.node2.units == 'dBm':
                    n2Tx = dBmtomw(n2Tx)
                    n2Rx = dBmtomw(n2Rx)
                    
        res1 = getCS(n1Tx,n2Rx,self.delta,self.p1acc,self.p2acc)
        res2 = getCS(n2Tx,n1Rx,self.delta,self.p2acc,self.p1acc)
        res = {}
        res['Time'] = now.strftime("%Y-%m-%d %H:%M")
        res['Connection'] = self.name
        res['IP 1'] = self.node1.ip
        res['IP 2'] = self.node2.ip
        res['Node Name 1'] = self.node1.name
        res['Node Name 2'] = self.node2.name
        res['Port 1'] = self.port1
        res['Port 2'] = self.port2
        res['Power Lost 1 (mW)'] = res1['Power Lost (mW)']
        res['Power Lost 2 (mW)'] = res2['Power Lost (mW)']
        res['Contamination Score 1'] = res1['Contamination Score']
        res['Contamination Score 2'] = res2['Contamination Score']
        res['Contamination Threshold 1'] = res1['Contamination Threshold']
        res['Contamination Threshold 2'] = res2['Contamination Threshold']
        res['Contaminated'] = res1['Contaminated'] | res2['Contaminated']
        
        df = pd.DataFrame([res])
        df = df[['Time','Connection','IP 1','IP 2','Node Name 1','Node Name 2','Port 1','Port 2','Power Lost 1 (mW)','Power Lost 2 (mW)','Contamination Score 1','Contamination Score 2','Contamination Threshold 1','Contamination Threshold 2','Contaminated']]
        df.head()
        self.dic = res
        self.data = df
        
        return df

    def Disconnect(self):
        """
        Closes Connections
        """
        self.Conn1.disconnect()
        self.Conn2.disconnect()