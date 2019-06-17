from selenium import webdriver
from tkinter import *
import time
import requests

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from tkinter import *
import traceback
import sys
import psutil



class geturl():
    """
    传入url，作为全局变量
    """
    value=1
    num=0
    numd=0

    if "win" in sys.platform:
        system="win"
        try:
            llq = webdriver.Firefox()
        except:
            llq = webdriver.Chrome()

    elif "linux" in sys.platform:
        from pyvirtualdisplay import Display
        a = Display(visible=0, size=(800, 600))
        a.start()
        b = webdriver.ChromeOptions()
        b.add_argument('--headless')
        llq = webdriver.Chrome(chrome_options=b)
        system="lin"

    def __init__(self, url):
        self.url = url
        geturl.llq.get(self.url)

#关闭浏览器的方法，if是linux系统，就多一步关闭webdriver
    def end(self):
        geturl.llq.quit()
        if geturl.system == "lin":
            geturl.a.stop()
# **************获取控件的value
    def Value(self, aa):
        self.aa = aa
        geturl.value =geturl.llq.find_element_by_xpath(self.aa).get_attribute("value")

#**************获取当前页面的url

    def Url(self):
        """
        获取当前页面的url
        :return:
        """
        try:
            aurl=geturl.llq.current_url
        except:
            aurl="meiyou"
        return aurl
        #**************************************获取错误
    def error(self):
        """
        获取错误,并进行输出
        :return:
        """
        try:
            ee=traceback.format_exc()
            print("报错开始")
            print(ee)
            print("报错结束")
        except:
            print("未获取到报错信息")
# ******************************************获取句柄个数
    def Jubing(self):
        """
        获取句柄个数
        :return: 句柄个数
        """
        try:
            Handler = geturl.llq.window_handles
        except:
            Handler={1}
        s = 0
        for i in Handler:
            s += 1
        if s > 1:
            print("当前有句柄：",Handler)
            return s

    # ******************************************获取当前标签的句柄
    def Dq_jubing(self):
        """
        获取当前标签的句柄
        :return: 句柄个数
        """
        try:
            handler = geturl.llq.current_window_handle
        except:
            geturl.error(1)
            handler="ss"
        return handler

#******************************************关闭第二个句柄
    def close_jubing_two(self):
        """
        关闭第二个句柄
        :return:
        """
        handles = geturl.llq.window_handles
        print(handles)
        geturl.llq.switch_to.window(handles[1])
        geturl.llq.close()

# ******************************************判断并进行句柄切换,句柄从0开始算,这里已经主动-1了
    def Jubing_go(self,sum,go_int):
        """
        判断并进行句柄切换,句柄从0开始算,这里已经主动-1了
        :param sum: 预计总句柄
        :param go_int: 切换到第几个句柄
        :return:
        """
        new_go_int=go_int-1
        handler = geturl.llq.window_handles
        while len(handler)<sum:
            handler = geturl.llq.window_handles
            time.sleep(1)
        try:
            # handler = geturl.llq.window_handles
            print("共有句柄个数:",len(handler))
            # print(handler)
        except:
            geturl.error(1)
            handler="ss"
        # time.sleep(5)
        if len(handler)>=int(sum):
            print("切换到第",go_int,"个句柄")
            geturl.llq.switch_to.window(handler[new_go_int])
            print("第",go_int,"个句柄切换成功")
        # time.sleep(5)

# ******************************************提示框
    def tishi(tsy):
        root=Tk()
        li=[tsy]
        ts=Listbox(root)
        for item in li:
            ts.insert(0, item)
        ts.pack()
        root.mainloop()

# *****************************判断控件是否存在
    def pxpath(self, s):
        self.s = s
        i=1
        xxx=0
        while xxx==0 and i<=30:
            try:
                geturl.llq.find_element_by_xpath(self.s)
                ss=1
            except:
                i += 1
                time.sleep(1)
            if ss==1:
                print("第", i, "次判断，本次判断该控件存在，执行下一步")
                xxx=1
        if i == 31:
            print("Bug--该属性不存在")

    def Pxpath(self, s):
        if not geturl.llq.find_element_by_xpath(self.s):
            ax=1
        else:
            ax=2
#*****************************拍照
    def paizhao_pc(self,zhaopian_name):
        self.zhaopian_name=zhaopian_name
        a = "D:\\img\\"
        b = ".png"
        Time = time.strftime("%Y-%m-%d--%H^%M^%S", time.localtime())
        png_name = a + Time + self.zhaopian_name + b
        geturl.llq.get_screenshot_as_file(png_name)
        return png_name
#*****************************鼠标指向
    def shubiao_zhixiang_xpath(self,shuxing):
        try:
            article = geturl.llq.find_element_by_xpath(shuxing)
            ActionChains(geturl.llq).move_to_element(article).perform()
        except:
            geturl.error(1)
# #******************************************输入事件
    def Sname(self,shuxing,name,shuruzhi,ok,game_over,Time=30):
        self.s = shuxing
        self.d = shuruzhi
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                geturl.llq.find_element_by_name(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_name(self.s).clear()
                        geturl.llq.find_element_by_name(self.s).send_keys(self.d)
                        geturl.num += 1
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx = 2
                    elif ss == False:
                        print(self.b)
                    ii += 1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)

        if i > Time:
            try:
                geturl.llq.find_element_by_name(self.s).clear()
                geturl.llq.find_element_by_name(self.s).send_keys(self.d)
                geturl.num += 1
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def C_class_text(self,name,tag_name, class_, text, ok, game_over,Time=30):
        i = 1
        ic = 1
        c = "//%s"%tag_name+"[@class='%s'" % (class_) + " and text()='%s']" % (text)
        while i < Time and ic == 1:
            try:
                article=geturl.llq.find_element_by_xpath(c)
                ActionChains(geturl.llq).move_to_element(article).perform()
                print(name, "存在，执行下一步")
                geturl.llq.find_element_by_xpath(c).click()
                ic = 2
            except:
                ee=traceback.format_exc()
                print(name, "不存在，执行等待操作，当前等待%s秒" % i)
                time.sleep(1)
            if ic == 2:
                print(ok)
            i += 1
        if i > Time:
            print(game_over)
            print("错误开始：")
            print(ee)
            print("报错结束————————")

    def Sid(self, shuxing, name, shuruzhi, ok, game_over,Time=30):
        # s属性，c控件的称呼，d输入的值，a事件成功的提示语,b事件失败的提示语
        self.s = shuxing
        self.d = shuruzhi
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                geturl.llq.find_element_by_id(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_id(self.s).clear()
                        geturl.llq.find_element_by_id(self.s).send_keys(self.d)
                        geturl.num += 1
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print(self.b)
                    ii+=1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)

        if i > Time:
            try:
                geturl.llq.find_element_by_id(self.s).clear()
                geturl.llq.find_element_by_id(self.s).send_keys(self.d)
                geturl.num += 1
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def Sname_zidingyi_s(self,shuxing,get_zidingyi,ok_text,neirong,name,ok,game_over,Time=30):
        i=1
        i_s=1
        while i<Time and i_s==1:
            try:
                np = geturl.llq.find_elements_by_name(shuxing)
                for npi in np:
                    if get_zidingyi == "text":
                        npi_text =npi.text
                    else:
                        npi_text = npi.get_attribute(get_zidingyi)
                    if npi_text == ok_text:
                        print(name,"已找到，开始执行下一步")
                        npi.send_keys(neirong)
                        print(ok)
                        i_s=2
                        break
            except:
                ee=traceback.format_exc()
                print(name,"未找到,执行等待操作，当前等待%d秒"%i)
                print("报错开始")
                print(ee)
                print("报错结束")
                i+=1
        if i> Time:
            print(game_over)

    def Stext(self, shuxing, name, shuruzhi, ok, game_over,Time=30):
        # s属性，c控件的称呼，d输入的值，a事件成功的提示语,b事件失败的提示语
        self.s = shuxing
        self.d = shuruzhi
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                geturl.llq.find_element_by_link_text(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_link_text(self.s).clear()
                        geturl.llq.find_element_by_link_text(self.s).send_keys(self.d)
                        geturl.num += 1
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print(self.b)
                    ii+=1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)

        if i > Time:
            try:
                geturl.llq.find_element_by_link_text(self.s).clear()
                geturl.llq.find_element_by_link_text(self.s).send_keys(self.d)
                geturl.num += 1
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def Sxpath(self,shuxing,name,shuruzhi,ok,game_over,Time=30):
    #s属性，c控件的称呼，d输入的值，a事件成功的提示语,b事件失败的提示语
        self.s=shuxing
        self.d=shuruzhi
        self.a = ok
        self.b = game_over
        self.c=name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                geturl.llq.find_element_by_xpath(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_xpath(self.s).clear()
                        geturl.llq.find_element_by_xpath(self.s).send_keys(self.d)
                        geturl.num += 1
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print( self.b)
                    ii+=1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)

        if i > Time:
            try:
                geturl.llq.find_element_by_xpath(self.s).clear()
                geturl.llq.find_element_by_xpath(self.s).send_keys(self.d)
                geturl.num += 1
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)



#*******************************************普通点击事件

    def Cid(self,shuxing,name,ok,game_over,Time=30):
#s属性，c代表名称，a成功输出,b失败提示
        self.s=shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_id(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ActionChains(geturl.llq).move_to_element(article).perform()
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:

                        geturl.llq.find_element_by_id(self.s).click()
                        geturl.num += 1
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx = 2
                    elif ss == False:
                        print(self.b)
                    ii += 1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time:
            try:
                geturl.llq.find_element_by_id(self.s).click()
                geturl.num += 1
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def Cname(self,shuxing,name,ok,game_over,Time=30):
        #s属性，c代表名称，a成功输出,b失败提示
        self.s=shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_name(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                # ActionChains(geturl.llq).move_to_element(article).perform()
                # print("指向后点击")
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_name(self.s).click()
                        geturl.num += 1
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print(self.b)
                    ii+=1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time:
            try:
                geturl.llq.find_element_by_name(self.s).click()
                geturl.num += 1
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)
    '''封装一个获取标签类型的方法'''
    def CTag_name(self,shuxing,zhengque_text,name,ok,game_over,Time=30):
        i = 1
        ss = 1
        while i < Time and ss == 1:
            try:
                aa = geturl.llq.find_elements_by_tag_name(shuxing)
                print("共", len(aa), "个", shuxing, "控件")
                for a in aa:
                    a_gei_value=a.get_attribute("value")
                    a_get_text=a.text
                    if a_gei_value==zhengque_text:
                        print(name, "存在，执行下一步")
                        try:
                            a.click()
                        except:
                            a.send_keys(Keys.ENTER)
                        print(ok)
                        ss = 2
                        break
                    if a_get_text==zhengque_text and ss==1:
                        print(name, "存在，执行下一步")
                        try:
                            a.click()
                        except:
                            a.send_keys(Keys.ENTER)
                        print(ok)
                        ss = 2
                        break
                i+=1
            except:
                ee=traceback.format_exc()
                print(ee)
                print(name, "未找到，执行等待操作")
                time.sleep(1)
                i += 1
        if i > Time:
            print(game_over)

    def CTag_name_zidingyi(self,tag_name,get_zidingyi,zhengque_text,name,ok,game_over,Time=30):
        i = 1
        ss = 1
        while i < Time and ss == 1:
            try:
                aa = geturl.llq.find_elements_by_tag_name(tag_name)
                print("共", len(aa), "个", tag_name, "控件")
                for a in aa:
                    if get_zidingyi == "text":
                        a_gei_get_zidingyi = a.text
                    else:
                        a_gei_get_zidingyi=a.get_attribute(get_zidingyi)
                    #print(a_gei_get_zidingyi)
                    if a_gei_get_zidingyi == zhengque_text :
                        print(name, "存在，执行下一步")
                        try:
                            a.click()
                        except:
                            a.send_keys(Keys.ENTER)
                        print(ok)
                        ss = 2
                        break
                if ss==1:
                    print(name, "未找到，执行等待操作,当前等待第",i,"秒")
                    i+=1
                    time.sleep(1)
            except:
                ee=traceback.format_exc()
                print(ee)
                print(name, "未找到，执行等待操作,当前等待第", i, "秒")
                time.sleep(1)
                i += 1
        if i > Time:
            print(game_over)


    def STag_name_zidingyi(self,tag_name,get_zidingyi,zhengque_text,input_text,name,ok,game_over,Time=30):
        i = 1
        ss = 1
        while i < Time and ss == 1:
            try:
                aa = geturl.llq.find_elements_by_tag_name(tag_name)
                print("共", len(aa), "个", tag_name, "控件")
                for a in aa:
                    a_gei_get_zidingyi=a.get_attribute(get_zidingyi)
                    if a_gei_get_zidingyi==zhengque_text:
                        print(name, "存在，执行下一步")
                        a.send_keys(input_text)
                        print(ok)
                        ss = 2
                        break
                if ss==1:
                    print(name, "未找到，执行等待操作,当前等待第",i,"秒")
                    i+=1
                    time.sleep(1)
            except:
                ee=traceback.format_exc()
                print(ee)
                print(name, "未找到，执行等待操作,当前等待第", i, "秒")
                time.sleep(1)
                i += 1
        if i > Time:
            print(game_over)

    '''封装一个获取name控件组的方法'''
    def CClassNameS_danxuan(self,shuxing, zhengque_text, name, ok, game_over,Time=30):
        i = 1
        ss=1
        while i < Time and ss==1:
            try:
                aa = geturl.llq.find_elements_by_class_name(shuxing)
                print("共有", len(aa), "个", shuxing, "控件")
                for a in aa:
                    #print(a.text)
                    if a.text == zhengque_text or a.get_attribute("value")==zhengque_text:
                        print(name, "存在，执行下一步")
                        try:
                            a.click()
                        except:
                            a.send_keys(Keys.ENTER)
                        print(ok)
                        ss=2
                i+=1
                time.sleep(1)
            except:
                ee = traceback.format_exc()
                print(name, "未找到，执行等待操作,当前等待",i,"秒")
                time.sleep(1)
                i += 1
        if i > Time:
            print(game_over)



    '''封装一个获取text控件组的方法'''

    def CTextS(self,shuxing, name, ok, game_over,Time=30):
        self.shuxing=shuxing
        self.name=name
        self.ok=ok
        self.game_over=game_over
        xs = 1
        xx=1
        while xs < Time and xx==1:
            try:
                aa = geturl.llq.find_elements_by_link_text(self.shuxing)
                print("共有",len(aa),"个",self.shuxing,"控件")
                if len(aa)>0:
                    for ixs in aa:
                        if ixs.text == self.shuxing:
                            print(self.name, "存在，执行下一步")
                            try:
                                ixs.click()
                            except:
                                ixs.send_keys(Keys.ENTER)
                            print(self.ok)
                            xx = 2
                            break
                else:
                    print(self.name, "未找到，执行等待操作")
                    xs+=1
                time.sleep(1)
            except:
                ee = traceback.format_exc()
                print(ee)
                time.sleep(1)
                xs += 1
        if xs > Time:
            print(self.game_over)

    def CTextS_Key(self,shuxing, name, ok, game_over,Time=30):
        self.shuxing=shuxing
        self.name=name
        self.ok=ok
        self.game_over=game_over
        xs = 1
        xx=1
        while xs < Time and xx==1:
            try:
                aa = geturl.llq.find_elements_by_link_text(self.shuxing)
                print("共有",len(aa),"个",self.shuxing,"控件")
                if len(aa)>0:
                    for ixs in aa:
                        if ixs.text == self.shuxing:
                            print(self.name, "存在，执行下一步")
                            ixs.send_keys(Keys.ENTER)
                            print(self.ok)
                            xx = 2
                            break
                else:
                    print(self.name, "未找到，执行等待操作")
                    xs+=1
                time.sleep(1)
            except:
                ee = traceback.format_exc()
                print(ee)
                time.sleep(1)
                xs += 1
        if xs > Time:
            print(self.game_over)

    def CClass(self,shuxing, name, ok, game_over,Time=30):
        i = 1
        ia = 1
        while i < Time and ia == 1:
            try:
                geturl.llq.find_element_by_class_name(shuxing)
                print(name, "控件存在，执行下一步")
                geturl.llq.find_element_by_class_name(shuxing).click()
                print(ok)
                ia = 2
            except:
                print(name, "不存在，执行等待操作，当前等待第", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time and ia == 1:
            print(game_over)


    def Ctext(self,shuxing,name,ok,game_over,Time=30):
#s属性，c代表名称，a成功输出,b失败提示
        self.s=shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_link_text(self.s)
                xxx=1
                print(self.c, "存在，执行下一步操作")
                ActionChains(geturl.llq).move_to_element(article).perform()
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_link_text(self.s).click()
                        geturl.num += 1
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)

                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print(self.b)
                    ii+=1
            except:

                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time:
            try:
                geturl.llq.find_element_by_link_text(self.s).click()
                geturl.num += 1
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)



    def Cxpath(self,shuxing,name,ok,game_over,Time=30):
        self.s=shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_xpath(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ActionChains(geturl.llq).move_to_element(article).perform()
                ii=1
                while xxx==1 and ii<=Time:
                    try:
                        geturl.llq.find_element_by_xpath(self.s).click()
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print(self.b)
                    ii+=1
            except Exception as e:
                print(e)
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)

        if i > Time:
            try:
                geturl.llq.find_element_by_xpath(self.s).click()
                ss = True
            except Exception as e:
                geturl.error(1)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def Cxpath_cler(self,shuxing,name,ok,game_over,Time=30):
        self.s=shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                geturl.llq.find_element_by_xpath(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")

                ii=1
                while xxx==1 and ii<=Time:
                    try:
                        geturl.llq.find_element_by_xpath(self.s).click()
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print(self.b)
                    ii+=1
            except Exception as e:
                print(e)
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)

        if i > Time:
            try:
                geturl.llq.find_element_by_xpath(self.s).click()
                ss = True
            except Exception as e:
                geturl.error(1)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)
#****************************************************特殊点击事件
    def CId(self,shuxing,name,ok,game_over,Time=30):
        self.s = shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_id(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ActionChains(geturl.llq).move_to_element(article).perform()
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_id(self.s).send_keys(Keys.ENTER)
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx = 2
                    elif ss == False:
                        print(self.b)
                    ii += 1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time:
            try:
                geturl.llq.find_element_by_id(self.s).send_keys(Keys.ENTER)
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def CName(self,shuxing,name,ok,game_over,Time=30):
        self.s = shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_name(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ActionChains(geturl.llq).move_to_element(article).perform()
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_name(self.s).send_keys(Keys.ENTER)
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx = 2
                    elif ss == False:
                        print(self.b)
                    ii += 1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time:
            try:
                geturl.llq.find_element_by_name(self.s).send_keys(Keys.ENTER)
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def CText_partial_s(self,shuxing, name, ok, game_over,Time=30):
        i = 1
        ia = 1
        while i < Time and ia == 1:
            try:
                kk = geturl.llq.find_elements_by_partial_link_text(shuxing)
                print("共有",len(kk),"个",name,"控件")
                for a in kk:
                    if shuxing in a.text:
                        print(name, "存在，执行下一步操作")
                        ActionChains(geturl.llq).move_to_element(a).perform()
                        try:
                            a.click()
                        except:
                            a.send_keys(Keys.ENTER)
                        print(ok)
                        ia = 2
                        break
                if len(kk)==0:
                    print(name, "不存在，执行等待操作，当前等待", i, "秒")
                    i += 1
                    time.sleep(1)
            except:
                print(name, "不存在，执行等待操作，当前等待", i, "秒")
                geturl.error(1)
                i += 1
                time.sleep(1)
        if i> Time:
            print(game_over)

    def CText(self,shuxing,name,ok,game_over,Time=30):
        self.s = shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_link_text(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ActionChains(geturl.llq).move_to_element(article).perform()
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_link_text(self.s).send_keys(Keys.ENTER)
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx = 2
                    elif ss == False:
                        print(self.b)
                    ii += 1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time:
            try:
                geturl.llq.find_element_by_link_text(self.s).send_keys(Keys.ENTER)
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)

    def CText_partial_s_key(self,shuxing, name, ok, game_over,Time=30):
        i = 1
        ia = 1
        while i < Time and ia == 1:
            try:
                kk = geturl.llq.find_elements_by_partial_link_text(shuxing)
                print("共有",len(kk),"个",name,"控件")
                for a in kk:
                    if shuxing in a.text:
                        print(name, "存在，执行下一步操作")
                        ActionChains(geturl.llq).move_to_element(a).perform()
                        a.send_keys(Keys.ENTER)
                        print(ok)
                        ia = 2
                        break
                if len(kk)==0:
                    print(name, "不存在，执行等待操作，当前等待", i, "秒")
                    i += 1
                    time.sleep(1)
            except Exception as e:
                print(name, "不存在，执行等待操作，当前等待", i, "秒")
                geturl.error(1)
                i += 1
                time.sleep(1)
        if i> Time:
            print(game_over)

    def CXpath(self,shuxing,name,ok,game_over,Time=30):
        self.s = shuxing
        self.a = ok
        self.b = game_over
        self.c = name
        geturl.num += 1
        i = 1
        xxx = 0
        while xxx == 0 and i <= Time:
            try:
                article=geturl.llq.find_element_by_xpath(self.s)
                xxx = 1
                print(self.c, "存在，执行下一步操作")
                ActionChains(geturl.llq).move_to_element(article).perform()
                ii = 1
                while xxx == 1 and ii <= Time:
                    try:
                        geturl.llq.find_element_by_xpath(self.s).send_keys(Keys.ENTER)
                        ss = True
                    except:
                        ss = False
                        time.sleep(1)
                    if ss == True:
                        print(self.a)
                        xxx=2
                    elif ss == False:
                        print(self.b)
                    ii+=1
            except:
                print(self.c, "不存在，执行等待操作，当前等待", i, "秒")
                i += 1
                time.sleep(1)
        if i > Time:
            try:
                geturl.llq.find_element_by_xpath(self.s).send_keys(Keys.ENTER)
                ss = True
            except Exception as e:
                print("当前报错信息：",e)
                ss = False
            if ss == True:
                print(self.a)
            elif ss == False:
                print(self.b)


    '''单选框的操作'''
    def Danxuan(self, shuxing, name, jiaobiao, ok, game_over,Time=30):
        self.shuxing = shuxing
        self.name = name
        self.jiaobiao = jiaobiao
        self.ok = ok
        self.game_over = game_over
        '''这里0-4代表着：实体商品,虚拟商品,虚拟物品(卡密),批发商品,记次/时商品'''
        '''定义一个数组，将获取到的name=type的控件集，保存在数组中'''
        num = 1
        xxx = 0
        while xxx == 0 and num <= Time:
            try:
                geturl.llq.find_elements_by_name(self.shuxing)
                xxx = 1
                print(self.name, "存在，执行下一步操作")
                try:
                    s = geturl.llq.find_elements_by_name(self.shuxing)
                    '''使用数组定位的形式，对指定的控件进行点击'''
                    s[self.jiaobiao].click()
                except:
                    print(self.game_over)
            except:
                print(self.name, "不存在，执行等待操作，当前等待", num, "秒")
                num += 1
                time.sleep(1)
        if num > Time:
            try:
                s = geturl.llq.find_elements_by_name(self.shuxing)
                '''使用数组定位的形式，对指定的控件进行点击'''
                s[self.jiaobiao].click()
            except:
                print(self.name, "不存在，执行等待操作，当前等待", num, "秒")
        ss = 0
        '''定义一个for循环，来判断哪一个控件被选中了'''
        for i in s:
            try:
                kk = s[ss].is_selected()
            except:
                print("Bug--无法找到控件们")
            if kk == False:
                if s[self.jiaobiao] == s[ss]:
                    print(self.game_over)
            if kk == True:
                if s[self.jiaobiao] == s[ss]:
                    print(self.ok)
            ss += 1

    def C_xialakuang_zidingyi_text(self,shuxing, ok_text, ok_tag_name, name, ok, game_over,Time=30):
        try:
            if ok_tag_name == "id":
                Select(geturl.llq.find_element_by_id(shuxing)).select_by_visible_text(ok_text)
                print(name, "存在执行下一步")
                print(ok)
        except:
            print(game_over)
    def title_panduan(self,bt):
        bt_sum=1
        bt_ok=0
        while bt_sum<30 and bt_ok==0:
            try:
                d_bt=geturl.llq.title
                if bt==d_bt:
                    bt_ok=1
                    print("**********************************************标题一致，通过标题核对测试！！")
            except:
                print("未获取到标题，执行等待操作，当前等待第%d秒"%bt_sum)
                geturl.error(1)
            bt_sum+=1
        if bt_sum==30 and bt_ok==0:
            print("***************************************************************Bug--获取标题失败！！")

    def lonely_applet_input(self,ho):
        # print("111111111111")
        tt = 1
        '''确认控件是否已经能够获取'''
        # aa = geturl.llq.find_elements_by_xpath("//ul[@class='clearfix']/li/div/div[2]/div/p[1]")
        # print("aa:",len(aa))
        while tt == 1:
            '''开始获取真实控件'''
            try:
                xx = "//ul[@class='clearfix']/li/div/div[2]/div/p[text()=\'" + ho + "\']/../../../../a/p"
                #xx="/p[text()=\'" + ho + "\']/../../../../a/p"
                # print(xx)
                aa = geturl.llq.find_elements_by_xpath(xx)
                for a in aa:
                    # print(len(aa))
                    # print("class:",a.get_attribute("class"))    #临时检测点
                    # print("text:", a.text)  # 临时检测点
                    # a.send_keys(Keys.ENTER)
                    a.click()
                    # print(xx)
                    tt = 2
                    break
            except:
                geturl.error(1)
            time.sleep(1)

    def yingyong_shop(self,ok_text):
        cishu = 1
        end_cishu = 0
        while cishu < 30 and end_cishu == 0:
            print("第%d次尝试"%cishu)
            try:
                s=geturl.llq.find_elements_by_xpath("//div[@class = 'ext-apply-item ']")
                s = geturl.llq.find_elements_by_class_name("ext-apply-item ")
                k = 1
                for i in s:
                    if ok_text in i.text:
                        # print("第%d个文本" % k)
                        # print(i.text)
                        ActionChains(geturl.llq).move_to_element(i).perform()
                        i.click()
                        print("进入",ok_text)
                        end_cishu = 1
                        break
                    k += 1
            except:
                geturl.error(1)
            cishu += 1
            time.sleep(1)
        if cishu==30:
            print("没进入",ok_text)

    def danxuan_tagname(self,dtext):
        k_sum = 1
        while k_sum < 30:
            try:
                k = geturl.llq.find_elements_by_tag_name("label")
                for k_i in k:
                    try:
                        k_i_t = k_i.text
                    except:
                        k_i_t = k_i.get_attribute("value")
                    print(k_i_t)
                    if k_i_t in dtext:
                        k_i.click()
                        print("选择单选框：",dtext)
                k_sum = 31
            except:
                print("再来一次")
                k_sum += 1

    def jiekou_post(self,url,datas,xiaoxitou_text):
        r = requests.post(url, data=datas, headers=xiaoxitou_text)
        return r.text

    # 滚动条的操作(可以以任何控件为坐标，拉动滚动条)
    def huadongpingmu_diduan(self,xpath):
        try:
            geturl.llq.find_element_by_xpath(xpath).send_keys(Keys.END)
            print('将滚动条拉到底端')
            time.sleep(2)
        except:
            geturl.error()

    def huadongpingmu_upduan(self, xpath):
        try:
            geturl.llq.find_element_by_xpath(xpath).send_keys(Keys.UP)
            print('将滚动条拉到上端')
            time.sleep(2)
        except:
            geturl.error()

    def huadongpingmu_xiayige(self, xpath):
        try:
            geturl.llq.find_element_by_xpath(xpath).send_keys(Keys.DOWN)
            print('将滚动条下拉一格')
        except:
            geturl.error()

if __name__ == "__main__":
    go=geturl("https://www.baidu.com")
    go.CTag_name_zidingyi(1,2,3,4,5,6)