from lmf.dbv2 import db_query 
import sys,os 
def write_file():
    path=os.path.join(os.path.dirname(__file__),'words.txt')
    sql="select distinct jgmc from ent.t_base_est"

    df=db_query(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])

    arr=df['jgmc'].values 

    with open(path,'w',encoding='utf8') as f:
        for w in arr:f.write(w+'\n')


def read_file():
    path=os.path.join(os.path.dirname(__file__),'words.txt')

    with open(path,'r',encoding='utf8') as f:
        arr=f.readlines()
    arr=[w.strip() for w in arr ]
    return arr


