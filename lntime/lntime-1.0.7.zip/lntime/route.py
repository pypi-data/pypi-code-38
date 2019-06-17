from lntime.common import exttime_fpage,exttime_fgg

def exttime(ggtime,page,quyu):
    normal=set(
        ['anhui_anqing',"anhui_bengbu","anhui_bozhou","anhui_chaohu","anhui_chizhou","anhui_chuzhou","anhui_fuyang","anhui_hefei","anhui_huaibei","anhui_huainan"
        ,"anhui_huangshan","anhui_luan","anhui_maanshan","anhui_suzhou","anhui_tongling","anhui_wuhu","anhui_xuancheng"

        ]
        )
    if quyu in normal:
        fbtime=exttime_fgg(ggtime)
        if fbtime is not  None:return fbtime
        fbtime=exttime_fpage(page)
        if fbtime is not None:return fbtime

    return None