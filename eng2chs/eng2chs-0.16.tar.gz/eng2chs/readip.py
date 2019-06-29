import random
from eng2chs import getip
def readip():
    try:
        getma = random.randint(0,20)
        if getma == 10:
            try:
                getip.get_ip()
            except:
                pass
        try:
            f = open('ip.txt', 'r')
        except FileNotFoundError:
            getip.get_ip()
            f = open('ip.txt', 'r')
            text = f.read()
            f.close()
        else:
            text = f.read()
            f.close()
        ip = text.split()
        id = []
        for i in range(0,100):
            id.append(i)
        # print(len(ip),len(id))
        ip_list = []
        for i in range(0,100):
            ip_list.append([id[i],ip[i]])

        # print(proxies)

        num = random.randint(0,100)
        # print(num)
        ip = ['http',ip_list[num][1]]
        # print(ip)
        proxies = dict((ip,))
        # print(proxies)
        return proxies
    except:
        return 'Failed to get proxies'