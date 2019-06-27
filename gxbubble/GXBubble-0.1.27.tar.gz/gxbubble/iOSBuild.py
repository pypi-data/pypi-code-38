#! /usr/bin/python
# coding:utf-8
import os
import re
import shutil
import sys
import time
import subprocess

from OpenSSL import crypto
from OpenSSL.crypto import load_certificate, FILETYPE_PEM


class IOSBuild:

    def __init__(self,ProjectPath):
        self.projectPath = ProjectPath;

    #获取目标目录文件名
    def access_filename(cwd_patch,file_suffix):
        for file_name in os.listdir(cwd_patch):
            if os.path.splitext(file_name)[1] == file_suffix:
                return file_name
        return ""

    #查询mobileprovision key信息
    def value_mobileprovision(self,findKey,valueLabel):
        file_mobileprovision = "";
        valueLabel_ = valueLabel.replace("/", '')
        file_mobileprovision = self.Provision_dis  #access_filename(provision_dis)
        if not file_mobileprovision.strip():
            print("获取配置文件.mobileprovision文件失败，请检查文件是否存在")
            sys.exit(1)

        string_mobileprovision = self.string_subprocessPopen('security cms -D -i %s' % (file_mobileprovision),None,False)
        if findKey == "输出mobileprovision":
            return string_mobileprovision

        findKey_location = string_mobileprovision.find('%s' % (findKey))
        string_mobileprovision = string_mobileprovision[findKey_location:]
        findKey_location = string_mobileprovision.find('%s' % valueLabel_)
        value = string_mobileprovision[findKey_location + len('%s' % valueLabel_) :string_mobileprovision.find('%s' % valueLabel)]
        return  value

    #执行终端系统命名，获取打印数据
    def string_subprocessPopen(self,command,cwd_patch,cancel_newline):
        command_file = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=cwd_patch)
        command_file.wait()
        command_string = command_file.stdout.read().decode()
        if cancel_newline == True:
            command_string = command_string.replace("\n", '')
        return command_string

    # 获取mobileprovision配置文件相关信息
    def current_mobileprovision_method(self):
        #global uuid_mobileprovision, teamName_mobileprovision, fileName_mobileprovision
        #global bundleId_mobileprovision, cerId_mobileprovision

        self.uuid_mobileprovision = self.value_mobileprovision("<key>UUID</key>", "</string>")
        self.fileName_mobileprovision = self.value_mobileprovision("<key>Name</key>", "</string>")
        self.cerId_mobileprovision = self.value_mobileprovision("<key>com.apple.developer.team-identifier</key>", "</string>")
        self.teamName_mobileprovision = "iPhone Distribution: " + self.value_mobileprovision("<key>TeamName</key>", "</string>")
        self.bundleIdTemp_mobileprovision = self.value_mobileprovision("<key>application-identifier</key>", "</string>")
        self.bundleId_mobileprovision = self.bundleIdTemp_mobileprovision[len('%s' % (self.cerId_mobileprovision)) + 1:len('%s' % (self.bundleIdTemp_mobileprovision))]

    def OpenSSLGetP12Info(self):
        # open it, using password. Supply/read your own from stdin.
        p12 = crypto.load_pkcs12(open(self.P12File_dis, 'rb').read(), self.p12Password)
        pemInfo = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
        cert = load_certificate(FILETYPE_PEM, pemInfo)
        subject = cert.get_subject();
        #global SSLCommonName;
        self.SSLCommonName = subject.commonName;

    def XCodeToSetAutoMatically(self):
        print( 'start python script! Delete AutoMatically Manage Signing')
        filePath = self.projectPath + "/Unity-iPhone.xcodeproj/project.pbxproj"
        if(os.path.exists(filePath)):
            f = open(filePath, 'r+')
            contents = f.read()
            f.seek(0)
            f.truncate()
            pattern = re.compile(r'(TestTargetID = (\w*)) \/\* Unity-iPhone \*\/;')
            f.write(pattern.sub(r'\1;\n\t\t\t\t\t};\n\t\t\t\t\t\2 = {\n\t\t\t\t\t\tProvisioningStyle = Manual;', contents))
            f.close()
        else:
            print("Not Found Path File : "+filePath)
            sys.exit(1)

        print( 'end python script !')

    def XcodeToIPA(self,p12file_dis,provision_dis,exportOptionPlistPath,iPASavePath,P12PassWord,IPAName,SHA1,ShowLog,PCUserName):
        #global projectPath, P12File_dis, Provision_dis, ExportOptionPlistPath,IPASavePath,p12Password;

        # exportOptionPlist文件路径
        self.ExportOptionPlistPath = exportOptionPlistPath
        self.P12File_dis = p12file_dis;
        self.Provision_dis = provision_dis;
        # 打包路径
        self.IPASavePath = iPASavePath
        self.p12Password = P12PassWord

        # 解锁Keychain
        os.system ('security unlock-keychain -p ztgame@123 /Users/'+PCUserName+'/Library/Keychains/login.keychain')
        os.system('security list-keychains -s /Users/'+PCUserName+'/Library/Keychains/login.keychain')
        # 导入证书

        if(p12file_dis != "" ):
            os.system("security import '+ p12File_dis +' -k /Users/"+PCUserName+"/Library/Keychains/login.keychain -P "+self.p12Password+" -T /usr/bin/codesign")

        # 清屏
        os.system('clear')

        #更改XCode项目 自动选择证书 模式
        if (ShowLog):
            print("Change XCodeAuto To Manual");
        self.XCodeToSetAutoMatically();

        #获取 证书的CommonName
        print("GetCommonName")
        self.OpenSSLGetP12Info()

        # 获取mobileprovision配置文件相关信息
        print("Get Mobileprovision Info")
        self.current_mobileprovision_method();

        provision_bds_dir = "/Users/"+PCUserName+"/Library/MobileDevice/Provisioning Profiles/";
        if(self.Provision_dis != ""):
            distMobileprovision = provision_bds_dir+self.uuid_mobileprovision+".mobileprovision";
            if(not os.path.exists(distMobileprovision)):
                if(self.uuid_mobileprovision != ""):
                    shutil.copy(self.Provision_dis,distMobileprovision);

        if(not os.path.exists(self.IPASavePath)):
            os.makedirs(self.IPASavePath);

        self.BuildIPA(self.IPASavePath,self.SSLCommonName,self.uuid_mobileprovision,self.ExportOptionPlistPath,IPAName)

        if (ShowLog):
            print(" CODE_SIGN_IDENTITY: " + self.SSLCommonName)
            print(" PROVISIONING_PROFILE: "+ self.uuid_mobileprovision)

        if(SHA1 != ""):
            os.system("security delete - certificate - Z "+SHA1);
            print("Delete P12");

        print("XCodeToIPAOver")

    def BuildIPA(self, IPASavePath, SSLCommonName, uuid_mobileprovision, ExportOptionPlistPath,IPAName):

        # 进入工程目录
        print("os.cdhir " + self.projectPath);

        if (os.path.exists(self.projectPath)):
            os.chdir(self.projectPath)
        else:
            print("Not found Path :" + self.projectPath);
            sys.exit(1);

        # 生成archive文件
        print("Clean XCodeBuild")
        os.system("xcodebuild clean -project Unity-iPhone.xcodeproj -scheme Unity-iPhone -configuration Release")

        print("Achieve Proj"); 
        os.system("xcodebuild archive -project Unity-iPhone.xcodeproj -scheme Unity-iPhone -configuration Release -archivePath " + IPASavePath + "/Unity-iPhone CODE_SIGN_IDENTITY='" + SSLCommonName + "' PROVISIONING_PROFILE=" + uuid_mobileprovision)

        # # 生成iPa包
        print("ExportAchieve");
        if (os.path.exists(IPASavePath + "/Unity-iPhone.xcarchive")):
            os.system("xcodebuild -exportArchive -archivePath " + IPASavePath + "/Unity-iPhone.xcarchive -exportPath " + IPASavePath + " -exportOptionsPlist " + ExportOptionPlistPath)
        else:
            print("Not found xcarchiveFile :"+IPASavePath + "/Unity-iPhone.xcarchive" + "Look Achieve Log");
            sys.exit(1);

        ## 改名
        os.chdir(IPASavePath)
        if (os.path.exists("Unity-iPhone.ipa")):
            print("Rename Unity-iPhone To ProjectName : " + IPAName);
            os.rename("Unity-iPhone.ipa", IPAName + ".ipa");

#xcodebuild -project xcodeprojPath -sdk iphoneos -scheme "Unity-iPhone" CONFIGURATION_BUILD_DIR='./' CODE_SIGN_IDENTITY="Yours" PROVISIONING_PROFILE="Yours"

