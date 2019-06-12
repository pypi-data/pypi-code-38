# encoding: utf-8

import os
from ftplib import FTP


class FTPHelper(FTP):

    def __init__(self,
                 *args,
                 **kwargs):

        FTP.__init__(self, *args, **kwargs)

        self.buffer = []

    def list_current_ftp_dir(self):

        self.buffer = []

        self.dir(self.__handle_list_response)

        return self.buffer

    def __handle_list_response(self,
                               line):

        filename = line.split(u' ').pop()

        # Append separator for directories
        if line.startswith(u'd'):
            filename += u'/'

        self.buffer.append(filename)

    def download_file(self,
                      filename,
                      output_dir):

        local_file = open(u'{d}{s}{f}'.format(d=output_dir,
                                              s=os.sep,
                                              f=filename), 'wb')

        self.retrbinary(u'RETR {f}'.format(f=filename),
                        local_file.write,
                        1024)

        local_file.close()
