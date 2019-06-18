#-*- encoding:utf-8 -*-
import os, sys, json, re
from xyscript.xylog import*
import xyscript.globalvar as gv

class Cert:
    def run_cert_syn(self,ispackage=None):
        """
        拉取最新证书 等效于 fastlane syn
        """
        print("start pull lastest certs")
        if self.fastlane_is_in_gem() or self.fastlane_is_in_brew() :
            shell_str = "fastlane syn"
            try:
                if self._have_fastfile():
                    # os.system(shell_str)
                    # result = os.popen(shell_str)
                    # text = result.read()
                    text = printandresult(shell_str)
                    # print(text)
                    if "fastlane.tools finished successfully" in text:
                        successlog("pull latest certs success")
                    else:
                        faillog("pull latest certs failed")
                    
                    # result.close()
                else:
                    faillog("You may not have the fastfile,please set fastlane up first!")
                    if ispackage:
                        pass
                        # Email(gv.get_value("NOTIFICATION_EMAILS")).send_package_email(False)
                    sys.exit()
                
            except BaseException  as error:
                faillog(str(error))
                sys.exit()
        else:
            warninglog("You may not have the fastlane installed yet,autoinstall now...")
            self._install_fastlane()
            self.run_cert_syn(ispackage)
    
    def run_cert_pps(self):
        """
        配置证书 等效于 fastlane pps
        """
        print("start config certs")
        if self.fastlane_is_in_gem() or self.fastlane_is_in_brew() :
            shell_str = "fastlane pps"
            try:
                if self._have_fastfile():
                    os.system(shell_str)
                    successlog("config certs success")
                else:
                    faillog("You may not have the fastfile,please set fastlane up first!")
                    sys.exit()
                
            except BaseException  as error:
                faillog(str(error))
                sys.exit()
        else:
            warninglog("You may not have the fastlane installed yet,autoinstall now...")
            self._install_fastlane()
            self.run_cert_pps()

    def fastlane_is_in_gem(self):
        shell_str = "gem list"
        # r = os.popen(shell_str)
        # text = r.read()
        # r.close()
        text = printandresult(shell_str)
        # part = "fastlane\s\(\d{1,10}\.\d{1,10}\.\d{1,10}\.\)"
        # result = re.findall(text,part)
        # faillog(text)
        return "fastlane (" in text

    def fastlane_is_in_brew(self):
        shell_str = "brew list"
        # r = os.popen(shell_str)
        # text = r.read()
        # r.close()
        text = printandresult(shell_str)
        return "fastlane" in text
    
    def _have_fastfile(self):
        path = os.getcwd() + "/fastlane/Fastfile"
        return os.path.isfile(path)

    def _install_fastlane(self):
        try:
            #install xcode-select
            os.system("xcode-select --install")
            warninglog("start install fastlane,you may need to enter a password...")
            os.system("sudo gem install fastlane -NV")
        except BaseException as error:
            faillog(str(error))
            sys.exit()

    def pgyerplugin_is_in_gem(self):
        pass

        # gen_list = os.system(shell_str)
        # print(count(gen_list))
        # try:
        #     os.system(shell_str)
        # except BaseException as error:
        #     faillog(error)
       
        # successlog("run fastlane success")


if __name__ == "__main__":
    Cert().fastlane_is_in_gem()