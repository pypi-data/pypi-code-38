import click, cli, os, os.path as path, glob, re

"""
按照给定的目录去找每个包里面的.metadata文件 读取传递的key 对应的值
"""


def get_package_metadata_file_con_by_key(package_path: str, keys: list) -> dict:
    """
    读取给定包中的metadata文件并获取给定Key列表的值 并返回key-value组成的dict
    :param package_path: 包路径
    :param keys:    key 列表 如 "BIR" "SRC"
    :return: 返回key和value组成的dict
    """
    key_values_dict = {}
    meta_data_files_path = path.join(package_path, "session")
    meta_data_files = glob.glob(path.join(meta_data_files_path, "*.metadata"))
    meta_data_file = meta_data_files[0] if len(meta_data_files) > 0 else False

    if meta_data_file:
        with open(meta_data_file, "rb") as mf:
            mf_con = mf.read()
            mf_con_str = mf_con.decode("utf-8")

            for key in keys:
                search = re.search("%s.*" % key, mf_con_str)
                re_result =search.group() if search else ""
                re_result = re_result.split(" ") if len(re_result) > 0 else []
                key_value = re_result[1].strip() if len(re_result) >= 2 else '无法解析，原文' + str(re_result)
                key_values_dict[key] = key_value

    return key_values_dict


@click.argument("keys", nargs=-1)
@click.argument('packages_path', type=click.Path(exists=True))
@click.command()
def get_package_metadata_info(packages_path, keys):
    """
     读取每个包中任意一个metadata 获取给定key列表，count(keys) >=1
    """
    if not path.isabs(packages_path):
        packages_path = (path.abspath(packages_path)).rstrip("//")

    if not len(keys) > 0:
        cli.error("Warning:keys 必须得有一个")
        return

    cli.warning("Task Starting...")

    for package in os.listdir(packages_path):
        package_path = path.join(packages_path, package)
        key_values = get_package_metadata_file_con_by_key(package_path, keys)
        cli.info("%s 包 %s" % (package, str(key_values)))
    cli.warning("Task Finish!")
