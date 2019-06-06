import click
from cli.packages import assistant, is_src_exist_on_dest, remove_bom, convert_utf8, compare_file
from cli.packages import read_metadata_file, fix_wrong_packagename_files
from cli.devops import ftpserver_helper
from cli.send_mail import send_mail


# cli入口
@click.version_option()
@click.group()
def cli():
    '''
        冲浪科技专用的命令脚本集 \n
        获取帮助: \n
        surfing_cli COMMAND --help
    '''
    pass


# server_cli入口
@click.version_option()
@click.group()
def ftp_server_cli():
    '''
        冲浪科技FTP服务器专用的命令脚本集 \n
        获取帮助: \n
        surfing_cli COMMAND --help
    '''
    pass


'''
    cli 开始绑定子命令
'''
# ------------ cli --------------#
# 包助理脚本
cli.add_command(assistant.package_assistant)
# 获取目标目录中重现的源包列表
cli.add_command(is_src_exist_on_dest.src_exist_on_dst_packages)
# 清除包中存在Bom文件中的bom
cli.add_command(remove_bom.remove_bom)
# 检测并转换文件为utf-8
cli.add_command(convert_utf8.convert_utf8)
# 获取包的metadata info
cli.add_command(read_metadata_file.get_package_metadata_info)
# 修复包中出现的错误包名文件
cli.add_command(fix_wrong_packagename_files.fix_wrong_packagename_files)
# 发送邮件
cli.add_command(send_mail.send_mail)
# 比较两个文本文件
cli.add_command(compare_file.compare_file)
# ------------包处理相关--------------#

# ------------FTP 服务器上的业务处理相关--------------#
# ftp 上传数据处理助理
ftp_server_cli.add_command(ftpserver_helper.mv_unzip_analysis)
ftp_server_cli.add_command(ftpserver_helper.tar_upload)
# ------------FTP 服务器上的业务处理相关--------------#
