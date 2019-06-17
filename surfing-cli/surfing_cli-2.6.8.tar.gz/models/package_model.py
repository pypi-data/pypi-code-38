'''
按照给定的包路径 /xxx/yyy/package1 进行分析、归类、以及执行有些必要操作
'''
import os.path as path, glob, os, json, cli, shutil, codecs
from cli.packages.utils.decrypt_audio import decrypt_file


class PackageModel:

    def __init__(self, package_path):
        """
        :param package_path:string 包的路径
        """

        self.init(package_path)
        '''
            业务逻辑
        '''
        self._classify()  # 归档
        self._judge_if_normal_package()  # 判断包是否正常

    def init(self, package_path):
        # 属性列表
        self.files_in_package = os.listdir(package_path)  # 包内部文件列表
        self.package_path = package_path
        self.package_name = path.basename(package_path)
        self.is_normal_package = True  # 是否完备无误的包
        self.abnormal_reason = []  # 当包存在不正常因素是的说明列表
        self.audio_files = []  # 音频文件列表
        self.corpus_files = []  # 语料文件列表
        self.exist_info_file = False  # 判断info文件是否存在
        self.unknown_folders = []  # 包中出现的未知目录列表
        self.unknown_files = []  # 未知文件
        self.wrong_package_files = []  # 不属于这个包的文件列表
        self.single_corpus_files = []  # 没有对应音频的语料文件列表
        self.single_audio_files = []  # 没有对应语料的音频文件列表
        self.android_audio_files = []  # 包中的安卓音频文件总数
        self.ios_audio_files = []  # 包中的 iOS 音频文件总数

    def update_info(self):
        """
        由于包中有时候存在删除文件或者目录等操作，操作完需要重新获取包信息  此方法就完成这个任务
        :return:
        """
        self.init(self.package_path)
        self._classify()  # 归档
        self._judge_if_normal_package()  # 判断包是否正常

    def _classify(self):
        """
        分析包中的每一个文件 并归类
        :return:
        """

        # 归类
        for file in self.files_in_package:
            # 是否属于这个包的文件
            if path.isdir(path.join(self.package_path, file)):
                self.unknown_folders.append(file)
                continue

            # if not file.find(self.package_name):
            if "info.txt" == file or "info" in file:
                self.exist_info_file = True
                continue

            if self.package_name not in file:
                self.wrong_package_files.append(file)

            if "wav" == file[len(file) - 3:]:

                self.audio_files.append(file)
                if "a" in file[:-3]:
                    self.android_audio_files.append(file)
                elif "i" in file[:-3]:
                    self.ios_audio_files.append(file)

            elif "txt" == file[len(file) - 3:]:
                self.corpus_files.append(file)
            else:
                self.unknown_files.append(file)

        # 不对应文件列表
        self.single_corpus_files = [f for f in self.corpus_files if f[:-3] + "wav" not in self.audio_files]
        self.single_audio_files = [f for f in self.audio_files if f[:-3] + "txt" not in self.corpus_files]

    def _judge_if_normal_package(self):
        """
        处理包是否正常包，不正常的原因的逻辑
        :return:
        """
        #  存在目录
        if len(self.unknown_folders) > 0:
            self.is_normal_package = False
            self.abnormal_reason.append("包中存在未知目录" + json.dumps(self.unknown_folders))

        #  info 文件不存在
        if not self.exist_info_file:
            self.is_normal_package = False
            self.abnormal_reason.append("info 文件不存在")

        # 没有音频
        if len(self.audio_files) == 0:
            self.is_normal_package = False
            self.abnormal_reason.append("包中没有音频文件")

        # 不属于本包的文件存在
        if len(self.wrong_package_files) > 0:
            self.is_normal_package = False
            self.abnormal_reason.append("存在不属于这个包的文件" + json.dumps(self.wrong_package_files))

        # 文本没有音频
        if len(self.single_corpus_files) > 0:
            self.is_normal_package = False
            self.abnormal_reason.append("存在没有对应音频的语料文件 :" + json.dumps(self.single_corpus_files))

        #  音频没有文本
        if len(self.single_audio_files) > 0:
            self.is_normal_package = False
            self.abnormal_reason.append("存在没有对应语料文件的音频 :" + json.dumps(self.single_audio_files))

        # 存在未知文件
        if len(self.unknown_files) > 0:
            self.is_normal_package = False
            self.abnormal_reason.append("存在未知文件" + json.dumps(self.unknown_files))

        # 音频 文本数量不相等
        if len(self.corpus_files) != len(self.audio_files):
            self.is_normal_package = False
            self.abnormal_reason.append(
                "音频文件和语料文件数量不相等 audio_count:%s,text_count:%s" % (len(self.audio_files), len(self.corpus_files)))

        #  设备类型不是同一种
        if len(self.android_audio_files) > 0 and len(self.ios_audio_files) > 0:
            self.is_normal_package = False
            # strange = self.android_audio_files if len(self.android_audio_files) > len(
            #     self.ios_audio_files) else self.ios_audio_files
            # self.abnormal_reason.append("存在多设备文件" + json.dumps(strange))
            self.abnormal_reason.append("存在多设备文件")

        # 不规范包名,包名以P字母开头，当包名和包内的包名匹配，但是包名不是以P开头时 视为可能存在问题的包
        if self.package_name[0].upper() != "P":
            self.is_normal_package = False
            self.abnormal_reason.append("%s 包名不符合规范，包名应该以 P 字母开头" % self.package_name)

    def get_device_type(self):
        """
        :return: string device_type 设备类型  未知 安卓&iOS 安卓 iOS
        """
        device_type = "未知"
        android_file_length = len(self.android_audio_files)
        ios_file_length = len(self.ios_audio_files)

        if android_file_length > 0 and ios_file_length > 0:
            device_type = "安卓&iOS"
        if android_file_length > 0 and ios_file_length == 0:
            device_type = "安卓"
        if ios_file_length > 0 and android_file_length == 0:
            device_type = "iOS"

        return device_type

    def get_formatted_abnormal_reason(self):
        """
        返回格式化后的异常信息
        :return:
        """
        return '\n'.join([
            "-" * 5 + "不正常包:" + self.package_name + "-" * 50,
            self.get_formatted_package_info(),
            '\n'.join(self.abnormal_reason),
            '-' * (len("不正常包:") * 2 + len(self.package_name) + 55)
        ])

    def get_formatted_package_info(self):
        """
        返回格式化后的 包详情信息
        :return:
        """
        message = """({package_device_type})包:{package_name} """ \
                  """语音:{audio_file_count}(a:{android_audio_file_count},i:{ios_audio_file_count}) """ \
                  """文本:{corpus_file_count} info:{info_file_count} 子目录:{unknown_folders}""" \
            .format(package_device_type=self.get_device_type(),
                    package_name=self.package_name,
                    audio_file_count=len(self.audio_files),
                    android_audio_file_count=len(self.android_audio_files),
                    ios_audio_file_count=len(self.ios_audio_files),
                    corpus_file_count=len(self.corpus_files),
                    info_file_count=1 if self.exist_info_file else 0,
                    unknown_folders=self.unknown_folders
                    )
        return message

    def delete_unknown_folders(self):
        """
        删除包中出现的 m4a mp3 temp 目录
        :return:
        """
        update_package = False

        if not self.is_normal_package:
            for folder in self.unknown_folders:
                if folder in ["m4a", "mp3", "temp"]:
                    shutil.rmtree(path.join(self.package_path, folder))
                    update_package = True

        if update_package:
            # 重新整理一次包信息
            self.update_info()

    def replace_folder_wav_files(self):
        """
        当包中存在wav 目录时把wav目录中的所有文件移到外面并吧wav 目录删除
        :return:
        """
        if not self.is_normal_package:
            if "wav" in self.unknown_folders:

                wav_full_path = path.join(self.package_path, "wav")

                for file in os.listdir(wav_full_path):

                    file_full_path = path.join(wav_full_path, file)

                    if path.exists(path.join(self.package_path, file)):
                        os.remove(path.join(self.package_path, file))

                    shutil.move(file_full_path, self.package_path)

                # 最终删除空目录wav
                shutil.rmtree(wav_full_path)
                # 重新整理一次包信息
                self.update_info()

    def rename_endswith_u_file(self):
        """
        后缀.u 的文件重命名
        :return:
        """
        pattern = path.join(self.package_path, "*.u")
        update_flag = False

        for file in glob.glob(pattern):
            if path.exists(file[:-2]):
                os.remove(file[:-2])
            os.rename(file, file[:-2])
            update_flag = True

        if update_flag:
            self.update_info()

    def delete_duplicated_underline_number_file(self):
        """
        删除重复录制产生的 xxx_1.wav xxx_2.wav 这种文件
        :return:
        """

        update_flag = False

        # 删除 _[1-9]
        pattern = path.join(self.package_path, "*_[0-9].*")
        for file in glob.glob(pattern):
            os.remove(file)
            update_flag = True
        # 删除 _[1-9][1-9] 两位数字
        pattern = path.join(self.package_path, "*_[0-9][0-9].*")
        for file in glob.glob(pattern):
            os.remove(file)
            update_flag = True

        if update_flag:
            self.update_info()

    def delete_unknown_suffix_file(self):
        """
         删除后缀 skip、sk、pk等文件
        :return:
        """
        update_flag = False
        for file in self.unknown_files:
            file_suffix = file[file.rfind(".") + 1:]
            if file_suffix in ["skip", "sk", "pk"]:
                os.remove(path.join(self.package_path, file))
                update_flag = True

        if update_flag:
            self.update_info()

    def decrypt_endswith_enc_file(self):
        """
                 删除后缀 skip、sk、pk等文件
                :return:
                """
        update_flag = False
        for file in self.unknown_files:
            file_full_path = path.join(self.package_path, file)
            file_suffix = file[file.rfind(".") + 1:]
            if file_suffix == "enc":
                try:
                    decrypt_file(file_full_path)
                except:
                    cli.error("\n 当解密(%s)文件的时候出错了" % file_full_path)
                update_flag = True

        if update_flag:
            self.update_info()

    def delete_single_txt(self):
        """
        删除没有对应音频的txt 文件
        :return:
        """
        update_flag = False
        for file in self.single_corpus_files:
            if "info" in file:
                continue
            os.remove(path.join(self.package_path, file))
            update_flag = True

        if update_flag:
            self.update_info()

    def get_info_file_info(self):
        """
        返回info file信息
        :return:
        """
        info_data = {}
        if self.exist_info_file:

            info_file_full_path = path.join(self.package_path, "info.txt")
            with open(info_file_full_path, "rb+") as f:

                try:
                    info_con = f.read()
                    # 如果存在Bom 先处理一下
                    if info_con[:3] == codecs.BOM_UTF8:
                        info_con = info_con[3:]
                        # 重新写入文件
                        f.seek(0)
                        f.truncate()
                        f.write(info_con)

                    if len(info_con.strip()) > 0:
                        info_data = json.loads(info_con.decode())
                    else:
                        pass
                        cli.warning("\ninfo 文件是空的")
                except:
                    cli.error("\n %s 包的 info文件信息解析出错了" % self.package_name)

        return info_data


if __name__ == '__main__':
    PackageModel("/Users/babbage/Desktop/packages/decrypt_test/P00473/")
