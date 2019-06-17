from appium import webdriver
import time
from baibaoxiang import femail
import traceback
import requests
import json
from PIL import Image
import pytesseract





class MGO():
    """
    调用方法go起步
    """
    #1111111111111111111
    '''定义会员折扣信息'''
    huiyuan_zehou = {
        "普通会员": 1,
        "钻石会员": 0.77,
        "白银会员": 1,
        "黄金会员": 1
    }
    '''邮件方法'''
    email = femail.email

    bug_num=0

    '''封装wechat方法'''
    def go(
            self,mobile_name,
            android_lv=9,
            platformName_system_type="Android",
            appPackage="com.tencent.mm",
            appActivity="com.tencent.mm.ui.LauncherUI",
            PC_ip='127.0.0.1',PC_port='4723'
    ):
        """

        :param mobile_name: mobile的名字；；；
        :param android_lv:android版本,默认为9；；；
        :param platformName_system_type: 系统类型，默认为android；；；
        :param appPackage:包名，默认为微信的包；；；
        :param appActivity:接口名，以此为指针操作指定app，默认为微信接口；；；
        :param PC_ip:执行设备的id，默认为本机执行，这里填写那个ip就会调用那个ip上的服务；；；
        :param PC_port:服务端接口，默认为4723；；；
        :return:
        """
        MGO.bug_num=0
        desired_caps = {}
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '5.1.1',
            # 'platformVersion': '7.0',
            # 'deviceName': 'emulator-5554',
            'deviceName': 'freeme-4g-868607020470921',
            #'deviceName': '10.130.33.130:5555',
            # 'deviceName': 'mi_5s-66680442',
            # 'unicodeKeyboard': True,
            # 'resetKeyboard': True,
            'noReset': True,
            'appPackage': 'com.tencent.mm',
            'appActivity': 'com.tencent.mm.ui.LauncherUI',
            'chromeOptions': {'androidProcess': 'com.tencent.mm:tools'}
        }
        desired_caps = {
            'platformName': platformName_system_type,
            'platformVersion':android_lv,
            'deviceName':mobile_name,
            'unicodeKeyboard': True,
            'resetKeyboard': True,
            'noReset': True,
            'appPackage': appPackage,
            'appActivity': appActivity,
            'chromeOptions': {'androidProcess': 'com.tencent.mm:tools'}
        }
        '''开始启动程序'''
        PC='http://'+PC_ip+':'+PC_port+'/wd/hub'
        i=1
        go=1
        while go==1 and i<60:
            try:
                # self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub',desired_caps)
                self.driver = webdriver.Remote(PC,desired_caps)
                #self.driver = webdriver.Remote('http://127.0.0.1:5555/wd/hub', desired_caps)
                print("启动手机程序打开微信")
                self.driver.implicitly_wait(5)
                print("已经打开微信程序")
                self.driver.implicitly_wait(5)
                print("等待五秒")
                time.sleep(10)
                go=2
            except Exception as e:
                ee = traceback.format_exc()
                print("开始打印错误日志")
                print(ee)
                print("结束打印错误日志")
                i+=1
                time.sleep(1)
        if go==1 and i==60:
            return "over"



    '''定义bug数量统计'''

    def bug_new(self):
        MGO.bug_num += 1

    '''封装一个获取积分订单编号的方法'''
    def vip_jifen_dingdan(self,url,data):
        self.url=url
        self.data=data
        r = requests.post(self.url, data=self.data)
        dingdan_bianhao = str(json.loads(r.text)['list'])[26:46]
        dingdan_bianhao = int(dingdan_bianhao[0:14])
        print("最新订单编号为：", dingdan_bianhao)
        return dingdan_bianhao


    '''封装一个在商品详情页面获取商品价格的方法'''
    def get_shoping_img_jiage(self,png_names,box):
        try:
            self.png_names=png_names
            self.box=box
            image = Image.open(self.png_names)
            newImage = image.crop(self.box)
            newImage.save('a.png')
            im = Image.open('a.png')
            print(pytesseract.image_to_string(im))
            jiage = pytesseract.image_to_string(im)
            jiage = float(jiage)
            print("商品价格", jiage, "元")
            return jiage
        except Exception as e:
            ee=traceback.format_exc()
            MGO.email("从图片获取商品价格报错！！报错信息如下<br>%s"%ee,"html",self.png_names)
            MGO.bug_new(0)

    def dianji(self,x_start,y_start,x_end,y_end,dianji_time):
        '''打开所有商品'''

        self.driver.tap([(x_start,y_start), (x_end,y_end)], dianji_time)


    '''判断微信是否正常打开了'''
    def panduan_dakai_wechat(self):

        xxx = 1
        i=1
        while xxx == 1 and i<30:
            try:
                self.driver.find_element_by_id("com.tencent.mm:id/b0w")
                # driver.find_element_by_id("com.tencent.mm:id/chn")
                xxx = 2
                return 1
            except:
                print("微信未完全打开，等待中...")
                i+=1
                time.sleep(1)



    '''封装一个截取手机屏幕的方法'''
    def paizhao(self,mingcheng):
        self.mingcheng=mingcheng
        try:
            a = "D:\\img\\"
            b = ".png"
            Time = time.strftime("%Y-%m-%d--%H^%M^%S", time.localtime())
            png_name = a + Time + self.mingcheng + b
            self.driver.get_screenshot_as_file(png_name)
            return png_name
        except Exception as e:
            ee=traceback.format_exc()
            print("开始打印错误日志")
            print(ee)
            print("结束打印错误日志")
            return 1

    '''封装一个获取会员积分的方法'''
    def vip_jifen(self,url):
        self.url=url
        try:
            r = requests.get(self.url)
            kk = json.loads(r.text)
            jifen_float = float(kk['credit1'])
            print("积分是：", jifen_float)
            return jifen_float
        except Exception as e:
            ee = traceback.format_exc()
            print("开始打印错误日志")
            print(ee)
            print("结束打印错误日志")
            return 1

    '''封装一个获取会员金额的方法'''
    def vip_jine(self,url):
        self.url = url
        try:
            r = requests.get(self.url)
            kk = json.loads(r.text)
            jine_float = float(kk['credit2'])
            print("金额是：", jine_float, "元")
            return jine_float
        except Exception as e:
            ee=traceback.format_exc()
            print("开始打印错误日志")
            print(ee)
            print("结束打印错误日志")
            return 1

    '''封装一个获取会员折扣的方法'''
    def vip_lv_zekou(self,url):
        self.url = url
        try:
            r = requests.get(self.url)
            kk = json.loads(r.text)
            vip_lv = kk['levelname']
            print("等级是：", vip_lv)
            vip_zekou = MGO.huiyuan_zehou[vip_lv]
            vip_zekou=float(vip_zekou)
            print("会员折扣为：", vip_zekou, "折")
            return vip_zekou
        except Exception as e:
            ee=traceback.format_exc()
            print("开始打印错误日志")
            print(ee)
            print("结束打印错误日志")
            return 1



    '''封装一个输出标题的方法'''
    def inputbt(self,dbiaoti, em_neirong_text, shifouquan, geshi_plain_or_html_s, png_name_new,biaoti_id):
        gogo = 2
        ii = 1
        while gogo == 2 and ii < 30:
            try:
                if biaoti_id == "":
                    if dbiaoti != "微信":
                        bt = self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='com.tencent.mm:id/kt']").text
                    if dbiaoti == "微信":
                        bt = self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='android:id/text1']").text
                else:
                    bt = self.driver.find_element_by_id(biaoti_id).text
                gogo = 1
            except Exception as e:
                print("标题获取中。。。")
                time.sleep(1)
                ii+=1
        try:
            if ii==30 and gogo==2:
                print("标题获取失败，结束运行！！")
            if shifouquan == 1:
                if bt != dbiaoti:
                    MGO.email(em_neirong_text, geshi_plain_or_html_s, png_name_new)
                    print("Bug*****************************************************标题不完全一样，已发送邮件")
                    MGO.bug_new(0)
                else:
                    print("标题是：", bt, "标题验证通过")
            if shifouquan == 0:
                if dbiaoti not in bt:
                    MGO.email(em_neirong_text, geshi_plain_or_html_s, png_name_new)
                    print("Bug*****************************************************标题不包含判断值,已发送邮件")
                    MGO.bug_new(0)
                else:
                    print("标题是：", bt, "标题验证通过")
            if shifouquan == 3:
                if dbiaoti not in bt:
                    print("Bug*****************************************************未转跳页面，标题不一致")
                    MGO.bug_new(0)
        except:
            ee=traceback.format_exc()
            print("开始报错")
            print(ee)
            print("结束报错")
        try:
            return bt
        except:
            return "有Bug"

    '''保存运行时间'''
    '''
    def biaoji_time(self):
        t = time.time()
        t = int(t)
        ft = open('D:\\text.txt', 'w')
        ft.write(str(t))
        ft.close()
        '''

    '''封装一个mobile_id点击操作'''
    def Cid(self,shuxing, mingcheng, chenggong, shibai):
        xxx = 1
        i = 1
        while xxx == 1 and i < 30:
            try:
                self.driver.find_element_by_id(shuxing)
                print(mingcheng, "存在，执行下一步")
                xxx = 2
                i = 1
                while xxx == 2 and i < 30:
                    try:
                        i = 1
                        self.driver.find_element_by_id(shuxing).click()
                        print(chenggong)
                        xxx = 3
                    except:
                        print(shibai, "执行等待操作，当前执行", i, "次")
                        i += 1
            except:
                print(mingcheng, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
                ee=traceback.format_exc()
        if xxx==1 and i==30:
            print("报错开始")
            print(ee)
            print("报错结束")

    '''打开指定小程序'''
    def xiaochengxu_id_on(self,shuxing_id, xiao_name):
        i_c=1
        try:
            k = self.driver.find_elements_by_id(shuxing_id)
            for i in k:
                print("当前小程序标题是：",i.text)
                if i.text == xiao_name:
                    i.click()
                    i_c=2
                    break
        except:
            ee=traceback.format_exc()
            print("开始报错")
            print(ee)
            print("报错结束")

    '''封装一个mobile_xpath点击操作'''
    def Cxpath(self,shuxing, mingcheng, chenggong, shibai):
        xxx = 1
        i = 1
        while xxx == 1 and i < 30:
            try:
                self.driver.find_element_by_xpath(shuxing)
                print(mingcheng, "存在，执行下一步")
                xxx = 2
                i = 1
                while xxx == 2 and i < 30:
                    try:
                        self.driver.find_element_by_xpath(shuxing).click()
                        print(chenggong)
                        xxx = 3
                    except:
                        print(shibai, "执行等待操作，当前等待", i, "秒")
                        i += 1
                        time.sleep(1)
            except:
                print(mingcheng, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)

    '''封装一个滑动屏幕的方法'''
    def moblie_huadong(self):
        sss = 1
        ii = 1
        while sss == 1 and ii<30:
            try:
                # driver.get_window_size()['width']
                x = self.driver.get_window_size()['width']
                y = self.driver.get_window_size()['height']
                print("横坐标最大值", x)
                print("纵坐标最大值", y)
                '''尝试滑动屏幕'''
                x1 = x * 0.5
                y1 = y * 0.15
                y2 = y * 0.75
                time.sleep(3)
                print("滑动前")
                '''开始滑动屏幕'''
                self.driver.swipe(x1, y1, x1, y2)
                self.driver.implicitly_wait(5)
                print("滑动后")
                sss = 2
            except:
                ee=traceback.format_exc()
                print("获取分辨率失败，再来一次，当前第", ii, "次")
                ii += 1
                time.sleep(1)
                print("报错开始")
                print(ee)
                print("报错结束")
        if sss==1 and ii==30:
            print("手机连接出现问题")
    def bug_num_new(self):
        return MGO.bug_num

if __name__ == "__main__":
    MGO().go("7&1c3e0558&0&0001")