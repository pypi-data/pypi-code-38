"""
打算在这里提供在ftp 服务器上需要进行的一系列工作的帮助cli工具
"""
import cli, click, zipfile
from .controllers.ftpserver_helper_controller import FtpServerHelperStep1, FtpServerHelperStep2
import os.path as path


# -------------------------- 命令逻辑区域 ----------------------------------

# step1. ftp 账户上传的数据从ftp目录中移到数据处理目录，并进行按命名规范存放，并解压，进行包分析
@click.argument("file_path", type=click.Path(exists=True))
@click.command()
def mv_unzip_analysis(file_path: str):
    """
        针对ftp上传的zip文件进行，移动、解压、包分析
    """

    if not path.isfile(file_path) or not file_path.endswith(".zip"):
        cli.error("{} 不是文件 or 不是 zip 压缩文件，请传入需要处理的 zip 压缩包的路径".format(file_path))
        exit()

    file_path = path.abspath(file_path)

    helper = FtpServerHelperStep1(file_path)

    # 开始任务
    cli.warning("Task Start...")
    helper.ls_lah(helper.zipfile_path)

    # 0. 分析路径获取相关信息
    helper.show_zipfile_info()

    # 1. 挪动文件到 Configs['ftp_data_tmp'] 下,为了避免文件名不规范导致数据丢失，给文件重新起名
    helper.mv()
    helper.show_tree()

    # 2. 解压
    helper.unzip()

    # 3. 进行包分析，修复，生成excel
    cli.info("正在针对解压后的目录进行数据解密，数据清洗工作")
    helper.package_analysis()

    # 完成
    cli.warning("Task Finished！")


# step2. 重新压缩，并上传到微软服务器
@click.argument("packages_folder_path", type=click.Path(exists=True))
@click.command()
def tar_upload(packages_folder_path: str):
    """
        针对待数据核对的包目录进行，压缩、上传到微软服务器
    """

    if not path.isdir(packages_folder_path):
        cli.error("{} 必须是一个目录".format(packages_folder_path))
        exit()

    packages_folder_path = path.abspath(packages_folder_path)

    helper = FtpServerHelperStep2(packages_folder_path)

    # 开始任务
    cli.warning("Task Start...")

    # 1.需要压缩tar.gz 放入 data_sync_backup目录下
    helper.compress_folder()
    # 2.上传到微软服务器
    helper.upload_2_weiruan()
    # 完成
    cli.warning("Task Finished！")
