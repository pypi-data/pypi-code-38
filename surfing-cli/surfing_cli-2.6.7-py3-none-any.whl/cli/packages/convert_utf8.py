import click, cli, os, os.path as path, glob, chardet

"""
按照给定的目录去找每个包里面的.txt文件（语料和info）检测是否是utf-8编码的,如果不是转换成utf-8写入文件中
"""


def check_and_convert2utf8(file_path, is_write_new_utf8_con):
    """
    检测并写入utf-8内容
    :param file_path: 文件路径
    :param is_write_new_utf8_con: 是否吧新的utf-8内容写入文件
    :return:
    """
    is_utf8 = False
    with open(file_path, "rb+") as f:
        file_contents = f.read()
        char_det_detect = chardet.detect(file_contents)
        if char_det_detect['encoding'] in ["utf-8", "ascii"]:
            is_utf8 = True
        if is_write_new_utf8_con:
            new_con = file_contents.decode(char_det_detect['encoding'])
            f.seek(0)
            f.truncate()
            f.write(new_con.encode("utf-8"))

    return is_utf8


@click.option("--write_utf8_con/--no_write_utf8_con", "-w", default=False,
              help="检测,重写utf8内容，默认只做检测，不写入")
@click.argument('packages_path', type=click.Path(exists=True))
@click.command()
def convert_utf8(packages_path, write_utf8_con):
    """
    包中所有txt文件的编码转换成utf-8编码（corpus & info）
    """
    if not path.isabs(packages_path):
        packages_path = (path.abspath(packages_path)).rstrip("//")

    cli.warning("Task Starting...")

    with click.progressbar(os.listdir(packages_path),
                           label="正在检测包中的无utf8文件",
                           fill_char='*',
                           show_eta=True,
                           show_percent=True,
                           show_pos=True,
                           ) as packages_bar:

        for package in packages_bar:
            packages_bar.label = "正在检测包 {}".format(package)
            if packages_bar.finished:
                packages_bar.label = "检测已完成"

            package_path = path.join(packages_path, package)
            if not path.isdir(package_path):
                cli.warning("\n 跳过非目录文件:" + package_path)
                continue
            deep = 5
            for file in glob.glob(path.join(package_path, "*.txt")):

                is_utf8 = check_and_convert2utf8(file, write_utf8_con)
                pre_fix = (" " * deep) + "|" + ("-" * deep)
                if not is_utf8:
                    cli.warning("\n"+pre_fix + " %s 文件不是utf-8" % path.basename(file))
                # else:
                # cli.info(pre_fix + " %s 文件无bom" % path.basename(file))

    cli.warning("Task Finish!")


if __name__ == '__main__':
    print(chardet.detect("hello".encode()))
