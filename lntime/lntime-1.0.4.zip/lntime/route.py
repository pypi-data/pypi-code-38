from lntime.common import exttime_fpage,exttime_fgg

def exttime(ggtime,page,quyu):
    normal=set(['anhui_anqing'])
    if quyu in normal:
        fbtime=gexttime_fgg(gtime)
        if fbtime is not  None:return fbtime
        fbtime=exttime_fpage(page)
        if fbtime is not None:return fbtime

    return None