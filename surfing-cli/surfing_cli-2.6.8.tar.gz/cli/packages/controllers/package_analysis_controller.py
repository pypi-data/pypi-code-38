import os, cli, click, xlwt, shutil, glob
import os.path as path
from models.package_model import PackageModel
from cli.send_mail.send_mail import SendMailController

"""
针对 assistant 命令的控制器
"""


class PackageAssistantController:

    def __init__(self, packages_path):
        self.packages_path = packages_path  # 包所有路径
        self.abnormal_packages = []  # 正常包列表
        self.normal_packages = []  # 不正常包列表
        self.result_txt_filename = "assistant_result.txt"
        self.package_info_excel_filename = "assistant_packages_info.xls"

    def do_analysis(self):
        """
        给定目录下的所有包进行分析
        :return:
        """
        packages_path = self.packages_path

        with click.progressbar(os.listdir(packages_path),
                               label="包分析进度",
                               fill_char='*',
                               show_eta=True,
                               show_percent=True,
                               show_pos=True,
                               ) as packages_bar:

            for package in packages_bar:
                if not path.isdir(path.join(self.packages_path, package)):
                    continue

                packages_bar.label = "正在分析 %s 包" % (package)
                package_model = PackageModel(path.join(packages_path, package))

                if package_model.is_normal_package:
                    self.normal_packages.append(package_model)
                else:
                    self.abnormal_packages.append(package_model)

                if packages_bar.finished:
                    packages_bar.label = "包分析已结束"

    def result_echo_via_pager(self):
        """
        用click的echo_via_pager 输出运行结果
        :return:
        """
        all_packages = (self.normal_packages + self.abnormal_packages)
        print_normal_list = []
        print_abnormal_list = []
        for package in all_packages:
            if package.is_normal_package:
                print_normal_list.append(package.get_formatted_package_info())
            elif not package.is_normal_package:
                print_abnormal_list.append(package.get_formatted_abnormal_reason())

        click.echo_via_pager("\n".join((print_normal_list + print_abnormal_list)))

    def result_echo_no_via_pager(self):
        """
        不使用click的echo_via_pager 输出运行结果
        :return:
        """
        all_packages = (self.normal_packages + self.abnormal_packages)
        print_normal_list = []
        print_abnormal_list = []
        for package in all_packages:
            if package.is_normal_package:
                print_normal_list.append(package.get_formatted_package_info())
            elif not package.is_normal_package:
                print_abnormal_list.append(package.get_formatted_abnormal_reason())

        cli.info("\n".join(print_normal_list))

        cli.error("\n".join(print_abnormal_list))

    def result_write_2_file(self):
        spl_path = path.split(self.packages_path.rstrip("/"))
        result_file_full_path = path.join(
            spl_path[0],
            spl_path[1] + "_" + self.result_txt_filename
        )
        """
        把运行结果写入到指定的文件
        :return:
        """
        with open(result_file_full_path, "w+", encoding="utf-8") as file:
            all_packages = (self.normal_packages + self.abnormal_packages)
            print_normal_list = []
            print_abnormal_list = []

            for package in all_packages:
                if package.is_normal_package:
                    print_normal_list.append(package.get_formatted_package_info())
                elif not package.is_normal_package:
                    print_abnormal_list.append(package.get_formatted_abnormal_reason())

            file.write('\n'.join([
                "\n".join(print_normal_list),
                "\n".join(print_abnormal_list)
            ]))

    def package_info_write_to_excel(self):
        """
        吧所有包的详情信息写入excel文件中
        :return:
        """
        # 打开xlsx表格，写入表头：包名, 音频数量, 安卓音频数量, ios音频数量, 文本数量, info, 是否正常包, 不正常原因
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet('包详情', cell_overwrite_ok=True)
        title = ['包名',
                 '音频数量',
                 '安卓音频数量',
                 'ios音频数量',
                 '文本数量',
                 '是否存在info',
                 '是否正常包',
                 '不正常原因',
                 "名字",
                 "性别",
                 "岁数",
                 "手机号",
                 "住址",
                 ]
        for i in range(len(title)):
            sheet.write(0, i, title[i])

        all_packages = self.normal_packages + self.abnormal_packages
        order_num = 0
        with click.progressbar(all_packages,
                               label="正在生成excel",
                               fill_char='*',
                               show_eta=True,
                               show_percent=True,
                               show_pos=True,
                               ) as all_packages_bar:
            for package in all_packages_bar:
                all_packages_bar.label = "正在写入 %s 包的信息到excel" % package.package_name
                # info信息
                info_file_info = package.get_info_file_info()
                name = "暂无"
                sex = "暂无"
                age = "暂无"
                phone = "暂无"
                place = "暂无"
                if info_file_info:
                    name = info_file_info['name']
                    sex = info_file_info['gender'] if "gender" in info_file_info else "未知字段名"
                    age = info_file_info['age']
                    phone = info_file_info['phone']
                    place = info_file_info['nativePlace'] if "nativePlace" in info_file_info else "未知字段名"

                # 每列内容
                abnormal_reason = ''.join(package.abnormal_reason)
                if len(abnormal_reason) > 32700:  # 因excel的ceil 放不下这么长字符所以进行了处理
                    abnormal_reason = abnormal_reason[0:32700] + "...."
                order_num += 1
                package_info = [package.package_name,
                                len(package.audio_files),
                                len(package.android_audio_files),
                                len(package.ios_audio_files),
                                len(package.corpus_files),
                                "是" if package.exist_info_file else "否",
                                "是" if package.is_normal_package else "否",
                                abnormal_reason,
                                name,
                                sex,
                                age,
                                phone,
                                place,
                                ]
                for i in range(len(package_info)):
                    sheet.write(order_num, i, package_info[i])

                if all_packages_bar.finished:
                    all_packages_bar.label = "生成excel 完成"

            spl_path = path.split(self.packages_path.rstrip("/"))
            excel_file_full_path = path.join(
                spl_path[0],
                spl_path[1] + "_" + self.package_info_excel_filename
            )

            if path.exists(excel_file_full_path):
                os.remove(excel_file_full_path)

            book.save(excel_file_full_path)

    def delete_unknown_folders(self):
        """
        删除包中出现的 m4a mp3 temp 目录
        :return:
        """
        # todo 这里需要扩展成可以传递需要删除的目录
        for package in self.abnormal_packages:
            package.delete_unknown_folders()

    def replace_folder_wav_files(self):
        """
        当包中存在wav 目录时把wav目录中的所有文件移到外面并吧wav 目录删除
        :return:
        """
        with click.progressbar(self.abnormal_packages,
                               label="检测、处理 wav 目录",
                               fill_char='*',
                               show_eta=True,
                               show_percent=True,
                               show_pos=True) as abnormal_packages_bar:
            for package in abnormal_packages_bar:
                abnormal_packages_bar.label = "正在处理 %s 包中的 wav 目录" % package.package_name
                package.replace_folder_wav_files()

                if abnormal_packages_bar.finished:
                    abnormal_packages_bar.label = "检测、处理 wav 目录完成"

    def rename_endswith_u_file(self):
        """
        后缀.u 的文件重命名
        :return:
        """

        for package in self.abnormal_packages:
            package.rename_endswith_u_file()

    def delete_duplicated_underline_number_file(self):
        """
        删除重复录制产生的 xxx_1.wav xxx_2.wav 这种文件
        :return:
        """

        for package in (self.abnormal_packages + self.normal_packages):
            package.delete_duplicated_underline_number_file()

    def delete_unknown_suffix_file(self):
        """
            删除后缀 skip、sk、pk等文件
        :return:
        """
        for package in self.abnormal_packages:
            package.delete_unknown_suffix_file()

    def decrypt_endswith_enc_file(self):
        """
        解密文件中带有 enc 后缀的被加密文件
        :return:
        """

        with click.progressbar(self.abnormal_packages,
                               label="检测、解密进度",
                               fill_char='*',
                               show_eta=True,
                               show_percent=True,
                               show_pos=True,
                               ) as abnormal_packages_bar:

            for package in abnormal_packages_bar:
                abnormal_packages_bar.label = "正在解密 %s 包" % package.package_name
                package.decrypt_endswith_enc_file()

                if abnormal_packages_bar.finished:
                    abnormal_packages_bar.label = "检测、解密结束"

    def delete_single_txt(self):
        """
        删除没有对应音频的txt文件
        :return:
        """
        for package in self.abnormal_packages:
            package.delete_single_txt()

    def run_result_str(self):
        """
        返回所有包分析结果换行拼接生成的字符串
        :return:
        """
        all_packages = (self.normal_packages + self.abnormal_packages)
        print_normal_list = []
        print_abnormal_list = []

        for package in all_packages:
            if package.is_normal_package:
                print_normal_list.append(package.get_formatted_package_info())
            elif not package.is_normal_package:
                print_abnormal_list.append(package.get_formatted_abnormal_reason())

        # 顺便更新全局的正常不正常列表

        return '\n'.join([
            "\n".join(print_normal_list),
            "\n".join(print_abnormal_list)
        ])

    def send_mail(self, is_result_write_file=False, is_package_info_write_excel_file=False):
        """
        运行完程序以后运行结果和附件以邮件方式发送发出通知
        :param bool is_result_write_file: cli 运行是否选择运行结果写入文件
        :param bool is_package_info_write_excel_file: cli 是否选择生成excel
        :return:
        """
        # 因处理结束时全局正常不正常列表还没更新 所以临时先放这块代码，后期优化
        all_packages = (self.normal_packages + self.abnormal_packages)
        print_normal_list = []
        print_abnormal_list = []

        for package in all_packages:
            if package.is_normal_package:
                print_normal_list.append(package.get_formatted_package_info())
            elif not package.is_normal_package:
                print_abnormal_list.append(package.get_formatted_abnormal_reason())

        # 1. 邮件正文
        cli.info("正在生成邮件内容")
        content = "主人主人，我处理了 {packages_path} 目录下的所有包，结果放邮件正文，你快看快看，嘻嘻嘻.\n\n\n " \
                  "总结果为： 正常: {normal_count} , 不正常: {unnormal_count}  \n \n \n {result} \n \n \n".format(
            packages_path=self.packages_path,
            normal_count=str(len(print_normal_list)),
            unnormal_count=str(len(print_abnormal_list)),
            result=self.run_result_str()
        )
        # 2.附件
        attechments = []
        if is_result_write_file:
            spl_path = path.split(self.packages_path.rstrip("/"))
            result_file_full_path = path.join(
                spl_path[0],
                spl_path[1] + "_" + self.result_txt_filename
            )

            attechments.append(result_file_full_path)

        if is_package_info_write_excel_file:
            spl_path = path.split(self.packages_path.rstrip("/"))
            excel_file_full_path = path.join(
                spl_path[0],
                spl_path[1] + "_" + self.package_info_excel_filename
            )

            attechments.append(excel_file_full_path)

        # 3. 发送邮件
        mail_controller = SendMailController(receivers=["surfing_it@surfingtech.cn"])
        mail_controller.send_mail_with_attachment(
            sub="【自动化】【包处理助手】包分析脚本运行结果",
            content=content,
            attachment=attechments
        )
