from socket import *
import os


def download(data,secret=None):
    if type(data) != type('data'):
        raise Exception("dataset MUST be StringType")
    if data == None or data=='':
        raise Exception("dataset CAN NOT be NoneType")
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_ip='193.168.1.129'
    tcp_port=8888
    tcp_socket.connect((tcp_ip, tcp_port))
    file_name='{}*#*{}'.format(data,secret)
    tcp_socket.send(file_name.encode())
    new_file = open(data, "wb")
    time = 0    
    while True:
        mes = tcp_socket.recv(4096000)
        if mes:
            if mes== 'Incorrect Secret,Please confirm!'.encode():
                raise Exception('Incorrect Secret,Please confirm!')
            new_file.write(mes)
            time += len(mes)         
        else:
            if time == 0:
                new_file.close()
                os.remove(data)
                print("没有您要下载的文件")
            else:
                print("文件下载成功")
             
            break
    tcp_socket.close() 
 
if __name__ == '__main__':
    download('netcamera_inroom_zhengli.zip',secret='123')