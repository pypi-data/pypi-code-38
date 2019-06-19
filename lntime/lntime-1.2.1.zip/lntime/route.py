from lntime.common import exttime_fpage,exttime_fgg
from lntime.common import exttime_guangdong_zhongshan

def exttime(ggtime,page,quyu):
    normal=set(
        ["chongqing_chongqing","chongqing_yongchuan"

        ,"fujian_fujian","fujian_nanan"

        ]
        )
    if quyu in normal:
        fbtime=exttime_fpage(page)
        if fbtime is not None:return fbtime
        fbtime=exttime_fgg(ggtime)
        if fbtime is not  None:return fbtime

    elif quyu in['guangdong_zhongshan']:
        fbtime=exttime_guangdong_zhongshan(page)
        if fbtime is not None:return fbtime
        fbtime=exttime_fpage(page)
        if fbtime is not None:return fbtime
        fbtime=exttime_fgg(ggtime)
        if fbtime is not  None:return fbtime

    fbtime=exttime_fgg(ggtime)
    if fbtime is not  None:return fbtime
    fbtime=exttime_fpage(page)
    if fbtime is not None:return fbtime
    return None