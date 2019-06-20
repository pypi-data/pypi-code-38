import serial
import serial.tools.list_ports
import time
import threading
import os

class WBSerial(object):
    '''
    单例类
    主要负责串口通信： 连接，收发串口数据，处理串口数据
    '''

    # 初始化标志
    _init_flag = False
    # 是否开启控制台输出串口数据日志
    _is_show_console = False

    def __init__(self):
        if WBSerial._init_flag:
            return
        WBSerial._init_flag = True
        # 初始化一些必要参数，出错时会重置这些参数
        self._initProperty()
        # 连接成功的回调函数
        self.connected_cb = None
        
        # 事件数据的回调函数
        self.event_data_cb = None #ddd
        # 带返回值数据命令的回调
        self.reporter_data_cb = None
        
        # 设置类命令的回调函数
        self._command_finish = None
        self.command_finish_cb = None

        # 开启一个子线程进行轮询串口
        # 若发现有我们的板子，就会尝试连接下
        # 如果板子有多块，第一块连不上的情况下会自动连接第二块，依次类推，直到连上我们的板子位置
        threading.Thread(target=self._create_try_connect_py_serial_thread, args=('_create_try_connect_py_serial_thread',)).start()
    
    def _initProperty(self):
        '''
        初始化该类的一些属性
        '''
        self._ser = None
        self._canUsedPort = []
        self._initIndex = 0
        self._canUseCount = 0
        self._canSend = False
    
    def write_command(self, command):
        '''
        发送命令给串口
        '''
        try:
            cmd = '{}\r\n'.format(command).encode('gbk')
            while not self._canSend:
                time.sleep(.001)
            self._canSend and self._ser.write(cmd)
        except KeyboardInterrupt as e:
            print('exit-wb')
            os._exit(0)

    def _write_raw_command(self, raw_command):
        '''
        发送命令给串口
        '''
        try:
            while not self._canSend:
                time.sleep(.001)
            self._canSend and self._ser.write(raw_command)
        except KeyboardInterrupt as e:
            print('exit-wb')
            os._exit(0)

    def _create_listen_serial_port_data_event_thread(self, name):
        '''
        监听串口数据(轮询)
        '''
        _buffer = ''
        try:
            while True:
                oneByte = self._ser.read(1)
                try:
                    _buffer += oneByte.decode("gbk")
                except:
                    continue
                if oneByte == b"\n":
                    if _buffer.find('Traceback') != -1:
                        self.reporter_data_cb and threading.Thread(target=self._create_return_serial_data_thread, args=('_create_return_serial_data_thread', "-1")).start()
                        _buffer = ''
                        continue
                    self._handle_serial_data(_buffer)
                    self._command_finish = _buffer
                    _buffer = ''
                if oneByte == b">" and _buffer[-3:] == '>>>':
                    self._handle_serial_data(_buffer)
                    _buffer = ''
                    if self._command_finish and self.command_finish_cb:
                        # 设置类命令 完成时通知
                        threading.Thread(target=self._create_return_command_finished_thread, args=('_create_return_command_finished_thread',self._command_finish)).start()
                        self._command_finish = None
                
        except KeyboardInterrupt as e:
            print('exit-wb')
            os._exit(0)

        except OSError as e:
            print('设备未配置')
            self._initProperty()

        except Exception as e:
            print("串口异常：{}".format(e))

    def _handle_serial_data(self, r_str = ''):
        '''
        处理串口数据
        '''
        if not r_str:
            return
        if WBSerial._is_show_console:
            print(r_str, end="")
        receive_str = r_str.strip()
        if receive_str.find('Type "help()" for more') != -1:
            self._canSend = True
            self.connected_cb and self.connected_cb()
        elif receive_str.startswith("{") and receive_str.endswith('}') and self.event_data_cb:
            # 事件触发返回数据
            threading.Thread(target=self._create_return_event_data_thread, args=('_create_return_event_data_thread',receive_str)).start()
        elif not receive_str.endswith(")") and receive_str.find('>>>') == -1 and self.reporter_data_cb:
            # 获取类返回值
            threading.Thread(target=self._create_return_serial_data_thread, args=('_create_return_serial_data_thread', receive_str)).start()

    def _create_return_event_data_thread(self, name, result):
        '''
        事件类通知回调
        '''
        self.event_data_cb(result)

    def _create_return_serial_data_thread(self, name, value):
        '''
        获取类执行完毕回调
        '''
        self.reporter_data_cb(value)

    def _create_return_command_finished_thread(self, name, key):
        '''
        设置类执行完毕回调
        '''
        self.command_finish_cb(key)

    def _initConnect(self):
        '''
        初始化连接本地串口，获取串口信息
        '''
        if self._ser != None:
            return
        self._initProperty()
        port_list = list(serial.tools.list_ports.comports())
        for i in range(len(port_list)):
            port = port_list[i]
            if port.pid == 29987 or port.pid == 60000:
                self._canUsedPort.append(port)
                # print(port.device, port.pid, port.vid, port.hwid)
                self._canUseCount = len(self._canUsedPort)

    def _connect_serial(self, index=0):
        '''
        根据指定端口，连接本地串口
        '''
        try:
            portx = self._canUsedPort[index].device
            bps = 115200
            timex = 1
            self._ser = serial.Serial(portx, bps, timeout=timex)
            cmd = '{}\r\n'.format("reset()").encode('gbk')
            self._ser.write(cmd)
        
            # 监听串口返回的数据
            threading.Thread(target=self._create_listen_serial_port_data_event_thread, args=('_create_listen_serial_port_data_event_thread',)).start()
            
        except serial.serialutil.SerialException as e:
            print("串口异常{}".format(e))
            if self._initIndex < self._canUseCount - 1:
                self._connect_serial(self._initIndex)
            else:
                self._initProperty()

        except Exception as e:
            print("通用异常：{}".format(e))
            self._initProperty()

    def _create_try_connect_py_serial_thread(self, thread_name):
        '''
        监听串口变化，初始化或者连接
        '''
        try:
            while True:
                self._initConnect()
                if not self._canUseCount:
                    print('无可用串口')
                    os._exit(0)        
                else:
                    if self._ser == None and self._canUseCount != 0:
                        self._connect_serial()
                time.sleep(.5)
        except KeyboardInterrupt as e:
            print('exit-wb')
            os._exit(0)