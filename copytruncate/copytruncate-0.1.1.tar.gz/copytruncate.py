# -*- coding: utf-8 -*-
import io
import datetime
import click


VERSION = "0.1.0"
BUFFER_SIZE = 1024 * 1024

def copytruncate(src, dst):
    file_src = io.open(src, "ab+")
    file_dst = io.open(dst, "wb")
    file_src.seek(0, 0)
    size = 0
    while True:
        buffer = file_src.read(BUFFER_SIZE)
        if not buffer:
            break
        file_dst.write(buffer)
        size += len(buffer)
    file_src.seek(0, 0)
    file_src.truncate()
    return size


@click.command()
@click.option("-v", "--verbose", is_flag=True, default=False, required=False, help="Show how many bytes copied.")
@click.argument("src_file_path", nargs=1, required=True)
@click.argument("dst_file_path", nargs=1, required=False)
def main(verbose, src_file_path, dst_file_path):
    """文件另存后清空文件，保持文件inode不变。一般可用于大日志文件的交换等场景。

    SRC_FILE_PATH：被复制及清空的文件路径（必填）。
    DST_FILE_PATH：另存为的文件路径（选填），默认为：SRC_FILE_PATH后加年月日时分秒。

    警告：

    由于“文件另存”和“清空文件”两个操作不是原子操作，
    在“另存”和“清空”之间可能会有新插入的数据，
    而清空时也会清掉这部分新插入的数据，
    导致数据部分丢失。
    """
    if dst_file_path is None:
        now = datetime.datetime.now()
        dst_file_path = "{src}.{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}{second:02d}".format(
            src = src_file_path,
            year = now.year,
            month = now.month,
            day = now.day,
            hour = now.hour,
            minute = now.minute,
            second = now.second,
        )
    size = copytruncate(src_file_path, dst_file_path)
    if verbose:
        click.echo("共复制了 {0} 字节.".format(size))


if __name__ == "__main__":
    main()
