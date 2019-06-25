# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import time
import glob
from io import open
import click


class TailReader(object):

    def __init__(self, filename, offset_file=None, read_from_end=False, file_encoding="utf-8", backup_patterns=None):
        self.filename = filename
        self.offset_file = offset_file or filename + ".offset"
        self.read_from_end = read_from_end
        self.file_encoding = file_encoding
        self.backup_patterns = backup_patterns
        self.fileobj = None

    def _read_offset_file(self):
        if not os.path.exists(self.offset_file):
            return 0, 0
        with open(self.offset_file, "r", encoding="utf-8") as fobj:
            inode, offset = [int(x) for x in fobj.readlines()[:2]]
            return inode, offset
    
    def _write_offset_file(self, inode, offset):
        with open(self.offset_file, "w", encoding="utf-8") as fobj:
            fobj.write(str(inode) + "\n")
            fobj.write(str(offset) + "\n")

    def _get_filename_and_offset_to_read(self, inode, offset):
        if not inode:
            return self.filename, 0
        try:
            info = os.stat(self.filename)
            if info.st_ino == inode:
                if info.st_size >= offset:
                    return self.filename, offset
                else:
                    return self.filename, 0
        except FileNotFoundError:
            pass
        if self.backup_patterns:
            for filename in glob.glob(self.backup_patterns):
                info = os.stat(filename)
                if info.st_ino == inode:
                    if info.st_size > offset:
                        return filename, offset
        return self.filename, 0

    def readlines(self):
        inode, offset = self._read_offset_file()
        if not inode:
            empty_inode_flag = True
        else:
            empty_inode_flag = False
        filename, offset = self._get_filename_and_offset_to_read(inode, offset)
        try:
            self.fileobj = open(filename, "r", encoding=self.file_encoding)
        except FileNotFoundError:
            return
        if self.read_from_end and empty_inode_flag:
            self.fileobj.seek(0, 2)
        else:
            self.fileobj.seek(offset, 0)

        while True:
            line = self.fileobj.readline()
            if line:
                yield line
            else:
                break

    def update_offset(self):
        if self.fileobj:
            info = os.stat(self.fileobj.fileno())
            self._write_offset_file(info.st_ino, self.fileobj.tell())


def print_line(line):
    if line.endswith("\n"):
        print(line[:-1])
    elif line.endswith("\r"):
        print(line[:-1])
    elif line.endswith("\r\n"):
        print(line[:-2])
    else:
        print(line)


class LineCounter(object):
    def __init__(self, verboes=False):
        self.counter = 0
        self.verboes = verboes
    
    def update(self, line):
        self.counter += 1
        if self.verboes:
            print_line(line)

    def result(self):
        return self.counter


def tail(filename, line_handler, offset_file=None, read_from_end=False, file_encoding="utf-8", backup_patterns=None, sleep_interval=1, update_offset_every_n=100, non_blocking=False):
    filereader = TailReader(filename, offset_file, read_from_end, file_encoding, backup_patterns)
    while True:
        c = 0
        for line in filereader.readlines():
            line_handler(line)
            c += 1
            if c % update_offset_every_n:
                filereader.update_offset()
        filereader.update_offset()
        if non_blocking:
            break
        if c < 1:
            time.sleep(sleep_interval)
    return c

@click.command()
@click.option("-o", "--offset-file", required=False, help="偏移量文件路径。默认为：在文件名后加.offset后缀。")
@click.option("-x", "--read-from-end", is_flag=True, help="如果不存在偏移量文件的话，指定该参数后则从文件的最后开始读取；不指定该参数的话则从文件开始读取。")
@click.option("-e", "--file-encoding", default="utf-8", help="文件读取编码，默认为utf-8。")
@click.option("-p", "--backup-patterns", help="文件可能通过logrotate等方式被备份出来，通过inode识别这些文件，先读取完备份文件中的剩余内容，再读取新文件内容。")
@click.option("-s", "--sleep-interval", type=int, default=1, help="读完文件后，休息一段时间后再续读。休息时间单位为：秒，默认为1秒。")
@click.option("-u", "--update-offset-every-n", type=int, default=100, help="每读取指定行后，更新偏移量文件。默认为100行。")
@click.option("-n", "--non-blocking", is_flag=True, help="指定该参数后，表示读取完文件内容后直接退出，同时sleep-interval参数无效；不指定的话则休眠sleep-interval秒后重新续读。")
@click.argument("filename", nargs=1, required=True)
def main(offset_file, read_from_end, file_encoding, backup_patterns, sleep_interval, update_offset_every_n, non_blocking, filename):
    """文件tail工具。引入“偏移量文件”记录文件读取信息，支持文件内容续读。
    """
    tail(filename, print_line, offset_file, read_from_end, file_encoding, backup_patterns, sleep_interval, update_offset_every_n, non_blocking)


if __name__ == "__main__":
    main()
