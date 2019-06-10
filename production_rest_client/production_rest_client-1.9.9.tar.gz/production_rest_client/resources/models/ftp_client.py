import os
from ftplib import FTP


class FtpClient(object):

    def __init__(self, ip_addr, port, user, password, time_out=300):
        self.ip_addr = ip_addr
        self.port = port
        self.user = user
        self.password = password
        self.time_out = time_out
        self.ftp = FTP()
        self.connect()

    def __del__(self):
        self.ftp.quit()

    def connect(self):
        self.ftp.connect(self.ip_addr, self.port, self.time_out)
        self.ftp.login(self.user, self.password)

    def upload_binary_file(self, file_path):
        ret = False
        if os.path.exists(file_path):
            file_ = open(file_path, 'rb')
            file_name = os.path.basename(file_path)
            return_code = self.ftp.storbinary('STOR ' + file_name, file_)
            if "226" in return_code:
                ret = True
        else:
            print("upload file not exist: {}".format(file_path))
        return ret

if __name__ == '__main__':
    pass
    # try:
    #     Client = FtpClient("172.29.130.138", 10021, "ftp_user", "Cnex!321")
    #     ret = Client.upload_binary_file(r"d:\2.bin")
    #     print(ret)
    # except Exception as e:
    #     print(e)
