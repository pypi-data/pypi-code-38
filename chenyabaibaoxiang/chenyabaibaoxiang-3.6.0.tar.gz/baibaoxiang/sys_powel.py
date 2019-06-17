import psutil
import os
import time
class powel_go:
    """
    只显示一次，在服务器运行时，写个定时文件，或者shell脚本持续运行
    """
    def print_cpu(self):
        # print("cpu个数:\t",psutil.cpu_count())
        m_all = psutil.virtual_memory().total / 1024 / 1024
        # print("全部内存大小为%sM"%m_all)
        # m_new=psutil.virtual_memory().free/1024/1024
        # m_new_bl=float(m_new)/float(m_all)
        # print("剩余内存大小为%sM，剩余占比为%f"%(m_new,m_new_bl*100),"%")
        # m=psutil.virtual_memory().available/1024/1024
        m = psutil.virtual_memory().used / 1024 / 1024
        # print("已使用内存大小为%sM,已用占比为%s"%(m,m/m_all*100),"%")
        neicun_bl = psutil.virtual_memory().percent
        cpu=psutil.cpu_percent(0.1)
        bingfa=os.system("netstat -nat|grep 80|wc -l")
        cipan=psutil.disk_usage('/').percent
        inter=psutil.net_io_counters()
        # print(cpu)
        t = time.strftime("%Y-%m-%d--%H:%M:%S", time.localtime())
        print(t," CPU使用率:\t",psutil.cpu_percent()  ,"%\t|\t内存使用百分比：", neicun_bl, "%\t", m, "M/", m_all, "M\t当前访问人数：",bingfa,"磁盘使用",cipan,"%","网络使用情况",inter)
        all={
            "CPU使用率":cpu,
            "内存使用百分比":neicun_bl,
            "内存已使用":m,
            "内存总量":m_all,
            "访问人数":bingfa,
            "磁盘使用百分比":cipan,
            "网络使用情况":inter
        }
        return all


if __name__ == "__main__":
    powel_go().print_cpu()