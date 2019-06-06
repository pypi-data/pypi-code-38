"""
判断 source 目录下的包是否在destination 目录下存在
"""
import click, os, os.path as path, cli


@click.argument("dst")
@click.argument("src")
@click.command()
def src_exist_on_dst_packages(src, dst):
    """
    获取目标中已经存在的源包列表 \n
    """
    pass
    src = src if path.isabs(src) else path.abspath(src)
    dst = dst if path.isabs(dst) else path.abspath(dst)

    if not path.exists(src) or not path.exists(dst):
        info = "源和目标目录必须得存在 %s %s %s" % (src, "__" * 5, dst)
        cli.error(info)
        return

    diff_packages = [sp for sp in os.listdir(src) if path.exists(path.join(dst, sp))]

    cli.info(str(diff_packages))
