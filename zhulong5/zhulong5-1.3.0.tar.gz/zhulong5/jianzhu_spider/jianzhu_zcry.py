# encoding:utf-8
import json
import os
from multiprocessing import Semaphore
import pandas as pd
from bs4 import BeautifulSoup
from gzqzl.jianzhu_etl import jianzhu_zcry_est_html


_name_ = "jianzhu"


sema = Semaphore(1)

# ---------------------------------------------------------程序主入口------------------------------------------------------

def f71(driver, arr):
    href = arr[0]
    zcry = arr[1]
    if (zcry == '暂未查询到已登记入库信息') or (zcry == 'None'):
        col = ["href", "zcry", "ryxx_name", "ryxx_href", "id_number", "zclb", "zch", "zczy"]
        return pd.DataFrame(columns=col)
    try:
        zcry_list = [k['trs'] for k in (json.loads(w) for w in json.loads(zcry))]
        datas = []
        for trs in zcry_list:
            dat = get_ryxx(driver, href, trs)
            if dat:
                datas.append(dat)
        data = []
        for d in datas:
            data += d
    except ValueError:
        data = get_ryxx(driver, href, zcry)
    df = pd.DataFrame(data=data)
    return df


# -------------------------------------------------多线程获取人员基本信息—---------------------------------------------------


def get_ryxx(driver, href, zcry):
    div = BeautifulSoup(zcry, 'html.parser')
    # 获取注册人员等详细信息
    ul = div.find('table', class_='pro_table_box pro_table_borderright').tbody
    trs = ul.find_all('tr')
    lis = []
    for tr in trs:
        if tr.find('div', class_='clearfix'):
            continue
        td = tr.find('td', attrs={"data-header": "姓名"})
        try:
            a = td.find('a')
        except:
            # print(href)
            sema.acquire()
            if not os.path.exists('./zcry.txt'):
                course = open('./rerun.txt', 'w', encoding='utf8')
                course.close()
            with open('zcry.txt', 'a', encoding='utf-8') as ft:
                ft.writelines("%s\n" % [href, trs])  # "a"就是append的意思,就是有写文件的时候不会覆盖前面的内容后追加到后面.
                ft.flush()
                ft.close()
                sema.release()
            print('数据错误！')
            continue
        ryxx_name = td.find('a').text.strip()
        id_number = tr.find('td', attrs={"data-header": "身份证号"})
        if id_number:id_number=id_number.text.strip()
        else:id_number=None
        zclb = tr.find('td', attrs={"data-header": "注册类别"})
        if zclb:zclb=zclb.text.strip()
        else:zclb=None
        zch = tr.find('td', attrs={"data-header": "注册号（执业印章号）"})
        if zch:zch = zch.text.strip()
        else:zch = None
        zczy = tr.find('td', attrs={"data-header": "注册专业"})
        if zczy:zczy = zczy.text.strip()
        else:zczy = None
        ryxx_href = 'http://jzsc.mohurd.gov.cn' + a['onclick'].split('=')[1].replace("'", '')
        tmp = [href, zcry, ryxx_name, ryxx_href, id_number, zclb, zch, zczy]
        lis.append(tmp)
    return lis


dd = ["href", "zcry", "ryxx_name", "ryxx_href", "id_number", "zclb", "zch", "zczy"]

def work(conp, **args):
    jianzhu_zcry_est_html(conp, f=f71, data=dd, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"], pageloadtimeout=180)

