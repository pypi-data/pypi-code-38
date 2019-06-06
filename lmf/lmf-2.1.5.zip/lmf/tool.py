
import datetime 
import calendar
import pandas as pd 
import os 
class tools:

    def __init__(self):
        pass

    @staticmethod
    def add_months(dt,months):
        dt=datetime.datetime.strptime(dt,'%Y-%m-%d')
        month = dt.month - 1 + months
        if month>=0:
             year = dt.year + int(month / 12)
        else:
              year = dt.year + int(month / 12)-1
        month = int(month % 12 + 1)
        day = min(dt.day,calendar.monthrange(year,month)[1])
        x=dt.replace(year=year, month=month, day=day)
        x=datetime.datetime.strftime(x,'%Y-%m-%d')
        return x 




class office_io:


    def __init__(self,path=None):
        if path is None:
          self.path="d:\\UserData\\lanmengfei\\Desktop\\myfile"
        else:
          self.path=path

    @staticmethod
    def log_time(func):
        def wrapper(*args,**kw):
          begin=datetime.datetime.now()
          a=func(*args,**kw)
          end=datetime.datetime.now()
          div=(end-begin).seconds
          print(func.__name__, div)
          return a
        return wrapper



    def mypath(self,wb_name,tail='xlsx'):
         
         path=self.path
         i=0
         name=path+'\\%s.'%wb_name+tail
         while os.path.exists(name):
              i+=1
              name=(path+'\\%s%d.'+tail)%(wb_name,i)
         print(name)
         return name

    def outdf(self,df,ws_name='Sheet1',wb_name='a'):
         wb_absname=self.mypath(wb_name)
         self._outdf(df,ws_name,wb_absname)
    def _outdf(self,df,ws_name,wb_absname):
         w=pd.ExcelWriter(wb_absname)
         df.to_excel(w,sheet_name=ws_name,index=False)
         wb=w.book
         ws=w.sheets[ws_name]
         fm=wb.add_format({'font_size':'10'})
         ws.set_column('A:AA',8.43,fm)
         w.save()

    def outdfs(self,dfs,ws_name='Sheet1',wb_name='a'):

         wb_absname=self.mypath(wb_name)
         self._outfs(dfs,ws_name,wb_absname)
    def _outdfs(self,dfs,ws_name,wb_absname):
         w=pd.ExcelWriter(wb_absname)
         n=0
         wb=w.book
         fm=wb.add_format({'font_size':'10'})

         for df in dfs:
                m=len(df)
                df.to_excel(w,sheet_name=ws_name,startrow=n,index=False)
                ws=w.sheets[ws_name]
                ws.set_column('A:AA',8.43,fm)
                n+=m+5
         w.save()

    def outdfss(self,dfss,ws_names,wb_name='a'):
         wb_absname=self.mypath(wb_name)
         self._outdfss(dfss,ws_names,wb_absname)
    def _outdfss(self,dfss,ws_names,wb_absname):
         w=pd.ExcelWriter(wb_absname)
         for i in range(len(dfss)):
              st=ws_names[i]
              n=0
              for df in dfss[i]:
                   m=len(df)
                   df.to_excel(w,sheet_name=st,startrow=n,index=False)
                   n+=m+5
                   wb=w.book
                   ws=w.sheets[st]
                   fm=wb.add_format({'font_size':'10'})
                   ws.set_column('A:AA',8.43,fm)
                   
              print('工作表-%s完成'%st)
         wb_name=os.path.basename(wb_absname)
         print('工作簿-%s完成'%wb_name)
         w.save()
    def outdfsss(self,dfsss,wdict1=None,wdict2=None,wb_path='xxx',tail='xlsx'):
         wb_abspath=os.path.join(self.path,wb_path)
         i=0
         dirname=wb_abspath
         while os.path.exists(dirname):
              i+=1
              dirname="%s(%d)"%(wb_abspath,i)
         os.mkdir(dirname)

         if wdict1 is None:
            #*wdict=['a1','a2'],[['Sheet1','Sheet2'],['Sheet1','Sheet2','Sheet3']]
            mm=len(dfsss)
            wdict1=['a%d'%(i+1) for i in range(i)]
         
         for ii in range(len(dfsss)):
            dfss=dfsss[ii]
            nn=len(dfss)
            if wdict2 is None:
              w_sheetsname=['Shheet%d'%(i+1) for i in range(nn)]
            else:
              w_sheetsname=wdict2[ii]
            wb_absname=os.path.join(dirname,'%s.%s'%(wdict1[ii],tail))
            
            self._outdfss(dfss,w_sheetsname,wb_absname)
            
            


