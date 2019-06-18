from lntime.common import exttime_fpage,exttime_fgg
from lntime.common import exttime_guangdong_zhongshan

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

        ,"gansu_baiyin","gansu_dingxi","gansu_gansu","gansu_jiayuguan","gansu_jiuquan","gansu_lanzhou","gansu_longnan","gansu_pingliang"
        ,"gansu_qingyang","gansu_tianshui","gansu_wuwei","gansu_zhangye"

        ,"guangdong_chaozhou","guangdong_dongguan","guangdong_foshan","guangdong_guangdong","guangdong_guangzhou","guangdong_heyuan"
        ,"guangdong_huizhou","guangdong_jiangmen","guangdong_jieyang","guangdong_lianzhou","guangdong_maoming","guangdong_meizhou"
        ,"guangdong_nanxiong","guangdong_shantou","guangdong_shanwei","guangdong_shaoguan","guangdong_shenzhen"
        ,"guangdong_sihui","guangdong_yangjiang","guangdong_yingde","guangdong_yunfu","guangdong_zhanjiang","guangdong_zhaoqing","guangdong_zhuhai"

        ,"guangxi_baise","guangxi_beihai","guangxi_chongzuo","guangxi_fangchenggang"
        ,"guangxi_guangxi","guangxi_guigang","guangxi_guilin","guangxi_hechi","guangxi_hezhou"
        ,"guangxi_laibin","guangxi_liuzhou","guangxi_nanning","guangxi_qinzhou","guangxi_wuzhou"
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
    elif quyu in['guangdong_zhongshan']:
        fbtime=exttime_guangdong_zhongshan(page)
        if fbtime is not None:return fbtime
        fbtime=exttime_fpage(page)
        if fbtime is not None:return fbtime
        fbtime=exttime_fgg(ggtime)
        if fbtime is not  None:return fbtime


    return None