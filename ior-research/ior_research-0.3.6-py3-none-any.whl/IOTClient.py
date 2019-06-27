import threading
import time
import json
import socket
import os

class IOTClient(threading.Thread):
    """Class used to access IOR Server"""
    __port = 8000

    def __init__(self,code,token,to,time_delay = 90,debug=False,on_close = None,save_logs=False,server = "iorcloud.ml"):
        """
        :param code: Current Device code
        :param token: Subscription Key
        :param to: Receiver Device Code
        :param time_delay: Time Delay for a Heartbeat @Deprecated
        :param debug: See all the message in I/O stream on the CLI
        :param on_close: a function that has to be called when the connection is closed
        :param save_logs: Save Logs of all the messages
        """
        threading.Thread.__init__(self)
        self.__code = code
        self.__token = token
        self.__to = to
        self.__time_delay = time_delay
        self.debug = debug
        self.__on_close = on_close
        self.__save_logs = save_logs
        self.__lock = threading.Lock()
        self.__isClosed = False
        self.__server = server

        self.__writeline("*" * 80)
        self.__writeline("Using Beta - Version: %s" % self.version())
        self.__writeline("Server Configuration IP: %s" % (self.__server))
        self.__writeline("User Token %s" % self.__token)
        self.__writeline("From Code: %d    To Code: %d" % (self.__code, self.__to))
        self.__writeline("Time Delay(in Seconds): %d" % self.__time_delay)
        self.__writeline("*" * 80)
        if not os.path.exists('./logs') and save_logs == True:
            os.mkdir('./logs')
        self.reconnect()

    @staticmethod
    def version():
        return "v0.3.6"

    def reconnect(self):
        import requests
        r = requests.post('http://%s/IOT/dashboard/socket/subscribe/%s/%d/%d' % (self.__server, self.__token, self.__code,self.__to))
        if r.status_code == 404:
            self.__writeline("Request Failed")
            return self.reconnect()
        if r.status_code != 201:
            raise Exception("Invalid Credentials")

        print("Request Successfully made to Server")
        s = r.content
        print(s)

        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((self.__server, self.__port))
        self.__s.sendall(s);
        self.__file_descriptor = self.__s.makefile('r')
        #self.__s.settimeout(2);
        self.__writeline("Connected to Socket Server")

        thread_0 = threading.Thread(target=self.__sendThread)
        thread_0.start()

    def __del__(self):
        if not self.__isClosed:
            self.close();

    def __sendThread(self):
        time.sleep(10)
        self.__isClosed = False
        self.__writeline("Starting Heartbeat Thread")
        while not self.__isClosed:
            self.sendMessage("<HEARTBEAT>")
            time.sleep(self.__time_delay)

    def set_on_receive(self,fn):
        self.on_receive = fn

    def __writeline(self,msg):
        if self.debug:
            print(msg)

    def __send(self,msg):
        if not self.__isClosed:
            try:
                data = json.dumps(msg)
                self.__lock.acquire()
                self.__s.send(data.encode() + b'\r\n')

                self.__writeline("Sending Message:")
                self.__writeline(data)
                self.time_start = time.time()*1000
            finally:
                self.__lock.release()


    def sendMessage(self,message,metadata = None):
        if self.__isClosed:
            return None

        msg = dict()
        if message == "<HEARTBEAT>":
            metadata = None

        msg["message"] = message
        if metadata is not None:
            msg["syncData"] = metadata

        self.__send(msg)

    def close(self):
        self.__isClosed = True

        self.__s.close()
        self.__file_descriptor.close()

        self.__writeline("Socket Closed")
        if self.__on_close != None:
            self.__on_close()

    def readData(self):
        if self.__isClosed:
            return None
        dataString = self.__file_descriptor.readline()
        print("DataString: ",dataString)
        data = json.loads(dataString)
        self.sendMessage("ack");
        return data

    def run(self):
        print("Starting Thread")
        while not self.__isClosed:
            try:
                msg = self.readData()
                if msg is not None:
                    self.__writeline("Message Received:")
                    self.__writeline(msg)
                    try:
                        self.on_receive(msg)
                    except Exception as ex:
                        print("Error Occured while invoking Receive Function")
                        self.__writeline(ex)
            except socket.timeout:
                print("socket timeout")
            except Exception as cae:
                print("Error Occured!!!")
                print(cae)
                break;
            time.sleep(0.01)
        print("Thread Terminated")
        self.close()


