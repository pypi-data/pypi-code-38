import cli, click
import os.path as path
from .controllers.package_analysis_controller import PackageAssistantController


# -------------------------- 命令逻辑区域 ----------------------------------
@click.option("--auto_clean/--no_auto_clean", '-auto', default=False,
              help="自动清理包中所有已知问题，默认不会。")
@click.option("--quiet/--no_quiet", "-q", default=False,
              help="静默运行，只显示进度条和错误信息。默认显示所有信息")
@click.option("--delete_single_txt/--no_delete_single_txt", '-del_txt', default=False,
              help="删除没有对应audio的txt文件，默认不删除")
@click.option("--decrypt_endswith_enc_file/--no_decrypt_endswith_enc_file", "-decrypt", default=False,
              help="解密，默认不会")
@click.option("--delete_unknown_suffix_file/--no_delete_unknown_suffix_file", '-suffix', default=False,
              help="删除skip、sk、pk等后缀的文件，默认不删")
@click.option("--delete_duplicated_underline_number_file/--no_delete_duplicated_underline_number_file", '-d',
              default=False,
              help="删除重复文件 xxx_1.wav|txt ，默认不删")
@click.option("--rename_endswith_u_file/--no_rename_endswith_u_file", '-u', default=False,
              help=".u文件重命名，默认不会。如果去掉.u后的文件存在的话、将先删除然后重命名")
@click.option("--replace_folder_wav_files/--no_replace_folder_wav", '-r', default=False,
              help="wav目录处理,默认不会")
@click.option("--delete_unknown_folder/--no_delete_unknown_folder", '-e', default=False,
              help="删除包中的 m4a mp3 temp,默认不删")
@click.option("--package_info_write_excel_file/--no_package_info_write_excel_file", '-excel', default=False,
              help="生成所有包的 excel 详情文件，默认不生成。\b 生成文件:目录名+assistant_packages_info.xls")
@click.option("--result_write_file/--no_result_write_file", '-o', default=False,
              help="运行结果写入文件，默认不会写入。 \b 文件:目录名+assistant_result.txt")
@click.option("--result_send_mail/--no_result_send_mail", '-m', default=False,
              help="运行结果以及附件是否发送邮件")
@click.option("--result_echo_via_pager/--no_result_echo_via_pager", '-page', default=False,
              help="运行结果是否分页显示,默认不分页")
@click.argument("packages_path", type=click.Path(exists=True))
@click.command()
def package_assistant(packages_path,
                      result_send_mail,
                      result_write_file,
                      result_echo_via_pager,
                      package_info_write_excel_file,
                      delete_unknown_folder,
                      replace_folder_wav_files,
                      rename_endswith_u_file,
                      delete_duplicated_underline_number_file,
                      delete_unknown_suffix_file,
                      decrypt_endswith_enc_file,
                      delete_single_txt,
                      quiet,
                      auto_clean
                      ):
    """
        命令：包助理。
        用于：包分析，包清理等等
    """

    if not path.isabs(packages_path):  # 路径转绝对路径
        cli.warning("程序按照给定的相对路径: %s 进行处理" % packages_path)
        packages_path = path.abspath(packages_path)

    # 清除目录最后一个斜杠
    packages_path = packages_path.rstrip("//")

    cli.info("Task Starting...")

    assistant_controller = PackageAssistantController(packages_path)
    assistant_controller.do_analysis()

    if auto_clean:
        # 1. wav 目录下的文件移到wav同级目录下
        replace_folder_wav_files = True
        # 2. 删除 包中出现的 m4a mp3 temp 目录
        delete_unknown_folder = True
        # 3. 删除后缀 skip、sk、pk等文件
        delete_unknown_suffix_file = True
        # 4. .u后缀文件rename
        rename_endswith_u_file = True
        # 5. 删除重复录制产生的 xxx_1.wav xxx_2.wav 这种文件
        delete_duplicated_underline_number_file = True
        # 6. 解密被加密的文件
        decrypt_endswith_enc_file = True
        # 7. 删除没有对应音频的txt
        delete_single_txt = True

    # wav 目录下的文件移到wav同级目录下
    if replace_folder_wav_files:
        assistant_controller.replace_folder_wav_files()

    # 删除 包中出现的 m4a mp3 temp 目录
    if delete_unknown_folder:
        assistant_controller.delete_unknown_folders()

    # 删除后缀 skip、sk、pk等文件
    if delete_unknown_suffix_file:
        assistant_controller.delete_unknown_suffix_file()

    # .u后缀文件rename
    if rename_endswith_u_file:
        assistant_controller.rename_endswith_u_file()

    # 删除重复录制产生的 xxx_1.wav xxx_2.wav 这种文件
    if delete_duplicated_underline_number_file:
        assistant_controller.delete_duplicated_underline_number_file()

    # 解密被加密的文件
    if decrypt_endswith_enc_file:
        assistant_controller.decrypt_endswith_enc_file()

    # 删除没有对应音频的txt
    if delete_single_txt:
        assistant_controller.delete_single_txt()

    # 是否静默运行
    if not quiet:
        # 运行结果是否分页显示
        if result_echo_via_pager:
            assistant_controller.result_echo_via_pager()
        else:
            assistant_controller.result_echo_no_via_pager()

    # 运行结果是否写入文件
    if result_write_file:
        assistant_controller.result_write_2_file()

    # 生成package_info的excel文件
    if package_info_write_excel_file:
        assistant_controller.package_info_write_to_excel()

    # 运行结果以及附件发送邮件
    if result_send_mail:
        # 1. 判断是否写入了文件，没写入不用带附件
        # 2. 判断是否生成了excel，没生成过的话不用带附件
        assistant_controller.send_mail(result_write_file, package_info_write_excel_file)

    cli.info("Task Finish!")
