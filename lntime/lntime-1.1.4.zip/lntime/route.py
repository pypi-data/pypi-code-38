from lntime.common import exttime_fpage,exttime_fgg

def exttime(ggtime,page,quyu):
    normal=set(
        ['anhui_anqing',"anhui_bengbu","anhui_bozhou","anhui_chaohu","anhui_chizhou","anhui_chuzhou","anhui_fuyang","anhui_hefei","anhui_huaibei","anhui_huainan"
        ,"anhui_huangshan","anhui_luan","anhui_maanshan","anhui_suzhou","anhui_tongling","anhui_wuhu","anhui_xuancheng"

        ,"chongqing_chongqing","chongqing_yongchuan"

        ,"fujian_fujian","fujian_nanan"

        ]
        )
    fast=set([
        "fujian_fuqing","fujian_fuzhou","fujian_jianou","fujian_longyan","fujian_nanping","fujian_ningde","fujian_putian"
        ,"fujian_quanzhou","fujian_sanming","fujian_shaowu","fujian_wuyishan","fujian_xiamen","fujian_yongan","fujian_zhangzhou"


        ])
    if quyu in normal:
        fbtime=exttime_fpage(page)
        if fbtime is not None:return fbtime
        fbtime=exttime_fgg(ggtime)
        if fbtime is not  None:return fbtime
    elif quyu in fast:
        fbtime=exttime_fgg(ggtime)
        if fbtime is not  None:return fbtime
        fbtime=exttime_fpage(page)
        if fbtime is not None:return fbtime


    return None