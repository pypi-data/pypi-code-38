"""
这个脚本用于修复包中包含的不属于这个包的文件列表，修复成包名是属于这个包
仅限用于格式像 2017001P00012a1234 这种格式的文件列表

"""

import click, cli, os, os.path as path
from cli.packages.controllers.package_analysis_controller import PackageAssistantController, PackageModel


@click.argument('packages_path', type=click.Path(exists=True))
@click.command()
def fix_wrong_packagename_files(packages_path):
    """
    包中错误包名文件修改成当前包名,文件格式实例： 2017001P00012a1234.wav|txt
    """
    """
    :param packages_path:
    :return:
    """
    cli.info("Task starting...")
    assistant_controller = PackageAssistantController(packages_path)
    assistant_controller.do_analysis()

    package_models = assistant_controller.abnormal_packages

    script_info = []
    for package_model in package_models:
        for wrong_file in package_model.wrong_package_files:
            file_full_path = path.join(package_model.package_path, wrong_file)
            package_name_start_point = wrong_file.find("P")
            package_name_end_point = wrong_file.find("i") if "i" in wrong_file else wrong_file.find("a")
            file_package_name = wrong_file[package_name_start_point:package_name_end_point]
            # if len(file_package_name) == 0 or len(file_package_name) > 6:  # P00474 包名一般6位
            #     cli.error("推算文件包名有误，暂无处理，请核对。file:%s" % file_full_path)
            #     continue
            script_info.append("%s 文件被修改包名,原: %s -->> 新: %s" % (file_full_path, file_package_name, package_model.package_name))

            # 替换包名
            file_new_full_path = path.join(package_model.package_path,
                                           wrong_file.replace(file_package_name, package_model.package_name))
            os.rename(file_full_path, file_new_full_path)
    if len(script_info) > 0:
        cli.warning("\n".join(script_info))

    cli.info("Task finished!")


if __name__ == '__main__':
    fix_wrong_packagename_files()
