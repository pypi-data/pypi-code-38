import cli, os, os.path as path, glob
from cli.packages.utils.remove_utf8_bom import remove_utf8_bom

"""
按照给定的目录去找每个包里面的.txt文件（语料和info）检测是否存在bom 如果存在bom 将清除bom 重新写入无bom信息
"""
import click, os, os.path as path, cli


@click.option("--write_clean_con/--no_write_clean_con", "-w", default=False,
              help="检测、清除文件的Bom后，把内容写入文件中,默认只做检测，不写入")
@click.argument('packages_path', type=click.Path(exists=True))
@click.command()
def remove_bom(packages_path, write_clean_con):
    """
    清除包中所有txt文件的Bom（corpus & info）
    """
    if not path.isabs(packages_path):
        packages_path = (path.abspath(packages_path)).rstrip("//")

    cli.warning("Task Starting...")

    with click.progressbar(os.listdir(packages_path),
                           label="正在检测包中的带bom的文件",
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
                cli.warning("\n跳过非目录文件:" + package_path)
                continue

            deep = 5  # 格式化显示的时的字符长度
            for file in glob.glob(path.join(package_path, "*.txt")):

                has_bom = remove_utf8_bom(file, write_clean_con)
                pre_fix = (" " * deep) + "|" + ("-" * deep)
                if has_bom:
                    cli.warning("\n"+pre_fix + " %s 文件存在Bom" % path.basename(file))
                # else:
                # cli.info(pre_fix + " %s 文件无bom" % path.basename(file))

    cli.warning("Task Finish!")
