from lmf.dbv2 import db_command 

import traceback

import time

# for i in range(100):
#     try:
#         bg=time.time()
#         j=i+18
#         sql="""
#         insert into mine.t_entarr(html_key,href,entarr)

#         select html_key,href,mine.findent(txt) as entarr from mine.t_txt where html_key>%d00000 and html_key<=%d00000
#         """%(j,j+1)

#         print(sql)
#         conp=["gpadmin",'since2015','192.168.4.179','base_db','mine']


#         db_command(sql,dbtype="postgresql",conp=conp)
#         ed=time.time()
#         cost=int(ed-bg)
#         print("耗时%d秒"%cost)
#     except:
#         bg=time.time()
#         j=i+170
#         sql="""
#         insert into mine.t_entarr(html_key,href,entarr)

#         select html_key,href,mine.findent(txt) as entarr from mine.t_txt where html_key>%d0000 and html_key<=%d0000
#         """%(j,j+1)

#         print(sql)
#         conp=["gpadmin",'since2015','192.168.4.179','base_db','mine']


#         db_command(sql,dbtype="postgresql",conp=conp)
#         ed=time.time()
#         cost=int(ed-bg)
#         print("耗时%d秒"%cost)


def execute_p(j):
    try:
        bg=time.time()
      
        sql="""
        insert into mine.t_entarr(html_key,href,entarr)

        select html_key,href,mine.findent(txt) as entarr from mine.t_txt where html_key>%d00000 and html_key<=%d00000
        """%(j,j+1)

        print(sql)
        conp=["gpadmin",'since2015','192.168.4.179','base_db','mine']


        db_command(sql,dbtype="postgresql",conp=conp)
        ed=time.time()
        cost=int(ed-bg)
        print("耗时%d秒"%cost)
    except:
        bg=time.time()
        j=i+170
        sql="""
        insert into mine.t_entarr(html_key,href,entarr)

        select html_key,href,mine.findent(txt) as entarr from mine.t_txt where html_key>%d0000 and html_key<=%d0000
        """%(j,j+1)

        print(sql)
        conp=["gpadmin",'since2015','192.168.4.179','base_db','mine']


        db_command(sql,dbtype="postgresql",conp=conp)
        ed=time.time()
        cost=int(ed-bg)
        print("耗时%d秒"%cost)


execute_p(90)