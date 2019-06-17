import pickle
import time as ost
import xlwt
import numpy as np
from VNE_SIM.VNR import *
from VNE_SIM.SN import *
class simulation:
    def __init__(self,u,duration,SNpath,vnrpath,vnrnumber=2000):  #5/100 unit time
        self.resource_set=""
        self.vnrnumber=vnrnumber
        self.VNRS = []
        self.sn = []
        self.timeframe = []
        self.environment="snpath:"+str(SNpath)+" vnrpath:"+str(vnrpath)+" u:"+str(u)+"/100"+" duration:"+str(duration)+"\n"
        self.acceptrate = []
        self.acceptrateContainer={}
        self.revenue_cost = []
        self.revenue_costContainer={}
        self.nodesuccessrate = []
        self.nodesuccessrateContainer={}
        self.nodeopen = []
        self.nodeopentmp = []
        self.nodeopenContainer={}
        self.edegesuccessrate = []
        self.edegesuccessrateContainer={}
        self.edegeopen = []
        self.edegeopentmp = []
        self.edegeopenContainer={}
        self.nodereloadbalance = []
        self.edegereloadbalance = []
        self.maptime=[]
        self.maptimeContainer={}
        self.x=[]
        self.t=0
        self.energy=0
        self.average_energy=[]
        self.average_energyContainer={}
        self.nodeutilrate = []
        self.nodeutilratetmp = []
        self.edegeutilrate = []
        self.edegeutilratetmp=[]
        self.nodeutilrateContainer={}
        self.edegeutilrateContainer={}
        self.suipianrate = []
        self.node_load=[]
        self.node_loadContainer={}
        self.link_load=[]
        self.link_loadContainer = {}
        self.expdistr = np.around(np.random.exponential(1/u, self.vnrnumber) * 100) + 1
        t=0
        a=[]
        for i in range(self.vnrnumber):
            t=t-np.round(1/u*np.log(np.random.rand(1)) * 100)
            a.append(t[0])
        self.expdistr =a
        vnrstmp=VNRS(vnrpath, vnrnumber)
        vnrstmp.changeDelayDistribution(duration)
        self.VNRS = vnrstmp.vnr
        vn = len(self.VNRS)
        self.VNRS[0].time = 0
        for vi in range(1, vn):
            # self.VNRS[vi].time = self.VNRS[vi - 1].time + self.expdistr[vi]
            self.VNRS[vi].time = self.expdistr[vi]
        self.sn = SN(SNpath)
        self.sn.changedistributioneNergy([150, 150], [300, 300], 15)
        self.revenuetmp=[]
        self.revenueContainer={}
    def init(self,frametime=1000):
        self.sn.resetResource()
        self.average_energy = []
        self.timeframe=frametime
        self.acceptrate=[]
        self.revenue_cost=[]
        self.nodeopen=[]
        self.nodeopentmp = []
        self.edegeopen=[]
        self.edegeopentmp = []
        self.maptime = []
        self.nodereloadbalance=[]
        self.edegereloadbalance=[]
        self.energy = 0
        self.suipianrate=[]
        self.nodeutilrate=[]
        self.edegeutilrate=[]
        self.nodeutilratetmp = []
        self.edegeutilratetmp = []
        self.revenuetmp = []
        self.node_load = []
        self.node_loadtmp = []
        self.link_load = []
        self.link_loadtmp = []
     #   self.sn.SN4cnn_img(self.VNRS[1])
    def simulation_run(self,mapfunction_handle,functionname_str):
        print("total time unit:", self.expdistr[self.vnrnumber-1])
        t = 500
        n_vnr = len(self.VNRS)
        duration = []
        for i_ in range(n_vnr):
            duration.append(self.VNRS[i_].duration)
        reqi = [z for z in range(n_vnr)]
        time = self.VNRS[0].time
        total = 0
        nodesuc = 0;
        mapsuccess = 0
        _, base = self.cost_sn()
        revenue = 0
        cost = 0
        self.energy=0
        self.t = self.VNRS[0].time
        self.energy = self.energy + self.sn.power(self.t)
        for i in range(n_vnr):
            vnr = self.VNRS[i]
            dtime = vnr.time - time
            while dtime > 0:
                dtime = dtime - 1
                self.t = self.t + 1
                ii = 0
                while reqi[ii] < i:
                    if duration[reqi[ii]] <= 0:
                        self.sn.removenodemapping(self.VNRS[reqi[ii]])
                        self.sn.removeedegemapping(self.VNRS[reqi[ii]])
                        reqi.remove(reqi[ii])
                        ii = ii - 1
                    else:
                        duration[reqi[ii]] = duration[reqi[ii]] - 1
                    ii = ii + 1
                self.energy = self.energy + self.sn.power(self.t)
            noderate,edegerate=self.sn.node_edege_util_rate()
            node_load,link_load=self.load_balance()
            self.nodeutilratetmp.append(noderate)
            self.edegeutilratetmp.append(edegerate)
            self.nodeopentmp.append(self.nodeopenf())
            self.edegeopentmp.append(self.edegeopenf())
            self.node_loadtmp.append(node_load)
            self.link_loadtmp.append(link_load)
            starttime = ost.time()
            success, v2sindex, ve2seindex = mapfunction_handle(vnr,self.sn)
            if success:
                _, base = self.cost_sn(base)
                nodesuc = nodesuc + 1
                self.sn.nodemapping2(vnr, v2sindex)
                self.sn.edegemapping(vnr, ve2seindex)
                self.maptime.append(ost.time() - starttime)
                self.energy = self.energy + self.sn.power(self.t)
                noderate, edegerate = self.sn.node_edege_util_rate()
                self.nodeutilratetmp.append(noderate)
                self.edegeutilratetmp.append(edegerate)
                tmpcost, base = self.cost_sn(base)
                cost = cost + tmpcost
                tempreven = self.revenue_vnr(vnr)
                self.revenuetmp.append(tempreven*vnr.duration)
                revenue = revenue + tempreven
                mapsuccess = mapsuccess + 1
            else:
                print("map vnr  fail ", vnr.id)
            total = total + 1
            time = vnr.time
            if time > t:
                self.acceptrate.append(mapsuccess / total)
                self.revenue_cost.append(revenue / (cost + 0.01))
                self.nodesuccessrate.append(nodesuc / total)
                self.average_energy.append(self.energy / vnr.time)
                self.x.append(t)
                t = t + self.timeframe
                self.nodeutilrate.append(np.mean(self.nodeutilratetmp))
                self.edegeutilrate.append(np.mean(self.edegeutilratetmp))
                self.nodeopen.append(np.mean(self.nodeopentmp))
                self.edegeopen.append(np.mean(self.edegeopentmp))
                self.node_load.append(np.mean(self.node_loadtmp))
                self.node_loadtmp.clear()
                self.link_load.append(np.mean(self.link_loadtmp))
                self.link_loadtmp.clear()
                # revenue = 0
                # cost = 0
        self.RecordData(functionname_str)
    def savevarible(self):
        pickle.dump(self.sn, open('.\\topology\\sn\\sn.data', 'wb'))
        pickle.dump(self.VNRS, open('.\\topology\\sn\\vnrs.data', 'wb'))
    def loadvarible(self):
        self.sn=pickle.load(open('.\\topology\\sn\\sn.data', 'rb'))
        self.VNRS=pickle.load(open('.\\topology\\sn\\vnrs.data', 'rb'))
    def changedistrbution(self,scpu=[],sbanwidth=[],vcpu=[],vbandwidth=[],dtype=np.float32):
        self.resource_set ="scpu:"+str(scpu)+" sbw:"+str(sbanwidth)+" vcpu:"+str(vcpu)+" vbw:"+str(vbandwidth)
        self.sn.changedistribution(scpu,sbanwidth,dtype)
        n=len(self.VNRS)
        for i in range(n):
            vn=len(self.VNRS[i].vnode)
            for j in range(vn):
                self.VNRS[i].vnode[j].cpu=float("%.3f"%rd.uniform(*vcpu))
            en=len(self.VNRS[i].vedege)
            for j in range(en):
                self.VNRS[i].vedege[j].bandwidth=float("%.3f"%rd.uniform(*vbandwidth))
    def cost_sn(self,temp1=0):
        temp2=0
        sn=len(self.sn.snode)
        for i in range(sn):
            temp2=temp2+self.sn.snode[i].lastcpu
        en=len(self.sn.sedege)
        for i in range(en):
            temp2 = temp2 + self.sn.sedege[i].lastbandwidth
        cost=abs(temp2-temp1)
        return cost,temp2
    def revenue_vnr(self,vnr):
        revenue=0
        for node in vnr.vnode:
            revenue=revenue+node.cpu
        for edege in vnr.vedege:
            revenue=revenue+edege.bandwidth
        return revenue
    def nodeopenf(self):
        opennode=0
        sn = len(self.sn.snode)
        for i in range(sn):
            if self.sn.snode[i].open:
                opennode=opennode+1
        return opennode
    def edegeopenf(self):
        openedege=0
        en = len(self.sn.sedege)
        for i in range(en):
            if self.sn.sedege[i].open:
                openedege=openedege+1
        return openedege
    def load_balance(self):
        node_util=np.array([(snode.cpu-snode.lastcpu)/snode.cpu for snode in self.sn.snode])
        node_load=np.sqrt(np.sum(np.square(node_util-np.mean(node_util)))/len(node_util))
        link_util=np.array([(sedge.bandwidth-sedge.lastbandwidth)/sedge.bandwidth for sedge in self.sn.sedege])
        link_load=np.sqrt(np.sum(np.square(node_util-np.mean(link_util)))/len(link_util))
        return node_load,link_load
    def RecordData(self,algorithmName):
        self.acceptrateContainer[algorithmName]=tuple(self.acceptrate)
        self.revenue_costContainer[algorithmName]=tuple(self.revenue_cost)
        self.nodesuccessrateContainer[algorithmName]=tuple(self.nodesuccessrate)
        self.average_energyContainer[algorithmName]=tuple(self.average_energy)
        self.nodeopenContainer[algorithmName]=tuple(self.nodeopen)
        self.edegeopenContainer[algorithmName]=tuple(self.edegeopen)
        self.maptimeContainer[algorithmName]=tuple(self.maptime)
        self.nodeutilrateContainer[algorithmName]=tuple(self.nodeutilrate)
        self.edegeutilrateContainer[algorithmName]=tuple(self.edegeutilrate)
        self.revenueContainer[algorithmName]=tuple(self.revenuetmp)
        self.node_loadContainer[algorithmName]=tuple(self.node_load)
        self.link_loadContainer[algorithmName]=tuple(self.link_load)
    def draw(self,show=True,split=False):
        if split:
            fig1=plt.figure()
            for alg_i in self.acceptrateContainer.keys():
                plt.plot(self.acceptrateContainer[alg_i], label=alg_i)
            plt.title("acceprate")
            plt.xlabel("time")
            plt.ylabel("acceprate")
            plt.legend(loc="upper right")
            plt.grid(True)
            fig1.savefig("output\\excelData\\acceprate.png",dpi=100)
            fig1.show()
            fig2=plt.figure()
            for alg_i in self.revenue_costContainer.keys():
                plt.plot(self.revenue_costContainer[alg_i], label=alg_i)
            plt.title("revenue_cost")
            plt.xlabel("time")
            plt.ylabel("revenue_cost")
            plt.legend(loc="upper right")
            plt.grid(True)
            fig2.savefig("output\\excelData\\revenue_cost.png", dpi=100)
            fig2.show()
            fig3=plt.figure()
            for alg_i in self.nodeutilrateContainer.keys():
                plt.plot(self.nodeutilrateContainer[alg_i], label=alg_i)
            plt.title("node util rate")
            plt.xlabel("time")
            plt.ylabel("node util rate")
            plt.legend(loc="upper right")
            plt.grid(True)
            fig3.savefig("output\\excelData\\node_rate.png", dpi=100)
            fig3.show()
            fig4=plt.figure()
            for alg_i in self.edegeutilrateContainer.keys():
                plt.plot(self.edegeutilrateContainer[alg_i], label=alg_i)
            plt.title("edege util rate")
            plt.xlabel("time")
            plt.ylabel("edege util rate")
            plt.legend(loc="upper right")
            plt.grid(True)
            fig4.savefig("output\\excelData\\edege_rate.png", dpi=100)
            fig4.show()
            fig5 = plt.figure()
            i=0
            for alg_i in self.maptimeContainer.keys():
                plt.bar(10+i*10,sum(self.maptimeContainer[alg_i]) / (len(self.maptimeContainer[alg_i])+0.01), width=2,label=alg_i)
                i=i+1
            plt.title("average map time")
            plt.xlabel("time")
            plt.ylabel("average map time")
            plt.legend(loc="upper right")
            plt.grid(True)
            if i < 7: plt.gca().set_xlim([0, 80])
            fig5.savefig("output\\excelData\\map_time.png", dpi=100)
            fig5.show()
        else:
            linestyle=["-","-","-","-","-","-","-","-","-","-","-","-","-"]
            plt.figure(figsize=(30,30)).suptitle(self.environment+self.resource_set)
            plt.subplot(4, 2, 1)
            i=0
            for alg_i in self.acceptrateContainer.keys():
                plt.plot(self.acceptrateContainer[alg_i],linestyle[i],label=alg_i)
                i=i+1
            plt.title("acceptrate")
            plt.xlabel("time")
            plt.ylabel("acceptrate")
            plt.legend(loc="upper right")
            plt.grid(True)

            plt.subplot(4, 2, 2)
            i=0
            for alg_i in self.revenue_costContainer.keys():
                plt.plot(self.revenue_costContainer[alg_i],linestyle[i],label=alg_i)
                i=i+1
            axes = plt.gca()
            #axes.set_xlim([0, 1])
            axes.set_ylim([0.3, 1])
            plt.title("revenue_cost")
            plt.xlabel("time")
            plt.ylabel("revenue_cost")
            plt.legend(loc="upper right")
            plt.grid(True)

            plt.subplot(4, 2, 3)
            i=0
            for alg_i in self.nodeopenContainer.keys():
                plt.plot(self.nodeopenContainer[alg_i],linestyle[i],label=alg_i)
                i=i+1
            plt.title("nodeopen")
            plt.xlabel("time")
            plt.ylabel("nodeopen")
            plt.legend(loc="upper right")
            plt.grid(True)

            plt.subplot(4, 2, 4)
            i=0
            for alg_i in self.edegeopenContainer.keys():
                plt.plot(self.edegeopenContainer[alg_i],linestyle[i],label=alg_i)
                i=i+1
            plt.title("edegeeopen",)
            plt.xlabel("time")
            plt.ylabel("edegeeopen")
            plt.legend( loc="upper right")
            plt.grid(True)

            plt.subplot(4, 2, 5)
            i=0
            for alg_i in self.average_energyContainer.keys():
                plt.plot(self.average_energyContainer[alg_i],linestyle[i],label=alg_i)
                i=i+1
            plt.title("average_energy consumption", )
            plt.xlabel("time")
            plt.ylabel("average_energy consumption")
            plt.legend( loc="upper right")
            plt.grid(True)

            plt.subplot(4, 2, 6)
            i=0
            for alg_i in self.maptimeContainer.keys():
                plt.bar(10+i*10,sum(self.maptimeContainer[alg_i]) / (len(self.maptimeContainer[alg_i])+0.01), width=2,label=alg_i)
                i=i+1
            if i<7:plt.gca().set_xlim([0, 80])
            plt.title("average map time", )
            plt.xlabel("time")
            plt.ylabel("average map time")
            plt.legend( loc="upper right")
            plt.grid(True)

            plt.subplot(4, 2, 7)
            i = 0
            for alg_i in self.nodeutilrateContainer.keys():
                plt.plot(self.nodeutilrateContainer[alg_i], linestyle[i], label=alg_i)
                i = i + 1
            plt.title("node util rate", )
            plt.xlabel("time")
            plt.ylabel("node util rate")
            plt.legend(loc="upper right")
            plt.grid(True)

            plt.subplot(4, 2, 8)
            i = 0
            for alg_i in self.edegeutilrateContainer.keys():
                plt.plot(self.edegeutilrateContainer[alg_i], linestyle[i], label=alg_i)
                i = i + 1
            plt.title("edege util rate", )
            plt.xlabel("time")
            plt.ylabel("edege util rate")
            plt.legend(loc="upper right")
            plt.grid(True)
            fig = plt.gcf()
            if show:plt.show()
            fig.savefig("output\\excelData\\result.png",dpi=100)
    def saveexcel(self):
        j=0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1')
        for alg_i in self.acceptrateContainer.keys():
            booksheet.write(j, 0,alg_i )
            for i,d in zip(range(len(self.acceptrateContainer[alg_i])),self.acceptrateContainer[alg_i]):
                booksheet.write(j, i+1, d)
            j=j+1
        workbook.save('output\\excelData\\请求接受率.xls')
        j=0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1')
        for alg_i in self.revenue_costContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.revenue_costContainer[alg_i])),self.revenue_costContainer[alg_i]):
                booksheet.write(j, i+1, d)
            j=j+1
        workbook.save('output\\excelData\\收益成本比.xls')
        j=0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1')
        for alg_i in self.average_energyContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.average_energyContainer[alg_i])), self.average_energyContainer[alg_i]):
                booksheet.write(j, i+1, d)
            j=j+1
        workbook.save('output\\excelData\\平均能量消耗.xls')
        j=0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1')
        for alg_i in self.maptimeContainer.keys():
            booksheet.write(j, 0, alg_i)
            booksheet.write(j,1,np.mean(self.maptimeContainer[alg_i]))
            j=j+1
        workbook.save('output\\excelData\\映射时间.xls')
        j=0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)

        for alg_i in self.nodeopenContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.nodeopenContainer[alg_i])), self.nodeopenContainer[alg_i]):
                booksheet.write(j, i+1, d)
            j=j+1
        workbook.save('output\\excelData\\节点开启量.xls')
        j=0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
        for alg_i in self.edegeopenContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.edegeopenContainer[alg_i])), self.edegeopenContainer[alg_i]):
                booksheet.write(j, i+1, d)
            j=j+1
        workbook.save('output\\excelData\\链路开启量.xls')
        j=0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
        for alg_i in self.nodeutilrateContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.nodeutilrateContainer[alg_i])), self.nodeutilrateContainer[alg_i]):
                booksheet.write(j, i+1, d)
            j=j+1
        workbook.save('output\\excelData\\节点利用率.xls')
        j = 0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
        for alg_i in self.edegeutilrateContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.edegeutilrateContainer[alg_i])), self.edegeutilrateContainer[alg_i]):
                booksheet.write(j, i + 1, d)
            j = j + 1
        workbook.save('output\\excelData\\链路利用率.xls')
        j = 0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
        for alg_i in self.revenueContainer.keys():
            booksheet.write(j, 0, alg_i)
            booksheet.write(j, 1, sum(self.revenueContainer[alg_i]))
            j = j + 1
        workbook.save('output\\excelData\\总收益.xls')

        j = 0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
        for alg_i in self.node_loadContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.node_loadContainer[alg_i])), self.node_loadContainer[alg_i]):
                booksheet.write(j, i + 1, d)
            j = j + 1
        workbook.save('output\\excelData\\节点负载均衡.xls')
        j = 0
        workbook = xlwt.Workbook(encoding='utf-8')
        booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
        for alg_i in self.link_loadContainer.keys():
            booksheet.write(j, 0, alg_i)
            for i, d in zip(range(len(self.link_loadContainer[alg_i])), self.link_loadContainer[alg_i]):
                booksheet.write(j, i + 1, d)
            j = j + 1
        workbook.save('output\\excelData\\链路负载均衡.xls')
