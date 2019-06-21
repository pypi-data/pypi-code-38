from lmf.dbv2 import db_command ,db_write,db_query 

from os.path import join ,dirname

import pandas as pd



def get_conp(name,database=None):
    path1=join(dirname(__file__),"cfg_db")
    if database is None:
        df=db_query("select * from cfg where schema='%s' "%name,dbtype='sqlite',conp=path1)
    else:
        df=db_query("select * from cfg where schema='%s' and database='%s' "%(name,database),dbtype='sqlite',conp=path1)
    conp=df.values.tolist()[0]
    return conp

def get_conp1(name):
    path1=join(dirname(__file__),"cfg_db")

    df=db_query("select * from cfg where database='%s' and schema='public' "%name,dbtype='sqlite',conp=path1)
    conp=df.values.tolist()[0]
    return conp





def command(sql):
    path1=join(dirname(__file__),"cfg_db")
    db_command(sql,dbtype="sqlite",conp=path1)

def query(sql):
    path1=join(dirname(__file__),"cfg_db")
    df=db_query(sql,dbtype='sqlite',conp=path1)
    return df 

def update(user=None,password=None,host=None):

    if host is not None:
        sql="update cfg set host='%s' "%host
        command(sql)
    if user is not None:
        sql="update cfg set user='%s' "%user
        command(sql)
    if password is not None:
        sql="update cfg set password='%s' "%password
        command(sql)

def add_conp(conp):
    sql="insert into cfg values('%s','%s','%s','%s','%s')"%(conp[0],conp[1],conp[2],conp[3],conp[4])
    command(sql)

data1={
        'a_b':['b2bcoal_crp_net_cn', 'b2b_10086_cn', 'baowu_ouyeelbuy_com','bidding_ceiec_com_cn',
               'bid_ansteel_cn', 'bidding_crmsc_com_cn','bid_powerchina_cn', 'buy_cnooc_com_cn'],

        'c_d':['caigou_ceair_com', 'csbidding_csair_com', 'dfqcgs_dlzb_com','dzzb_ciesco_com_cn'],

        'e_f':[ 'ebid_aecc_mall_com', 'ec1_mcc_com_cn', 'ecp_sgcc_com_cn','ec_ccccltd_cn', 'ec_ceec_net_cn',
                'ec_chalieco_com','epp_ctg_com_cn', 'eps_sdic_com_cn', 'etp_fawiec_com','ecp_cgnpc_com_cn'],

        'f_v':[ "fwgs_sinograin_com_cn", "gs_coscoshipping_com","jzcg_cfhi_com", "srm_crland_com_cn",
                "syhggs_dlzb_com","sytrq_dlzb_com","thzb_crsc_cn","uat_ec_chng_com_cn"],

        'w_z':['ysky_dlzb_com','zb_crlintex_com','zgdxjt_dlzb_com','zgdzxx_dlzb_com','zghkgy_dlzb_com',
         'zghkyl_dlzb_com','zgyy_dlzb_com','zljt_dlzb_com','wzcgzs_95306_cn'],

        'www_a_c':[ "www_bidding_csg_cn","www_cdt_eb_com", "www_cgdcbidding_com", "www_chdtp_com","www_chinabidding_com_total",
                    "www_china_tender_com_cn","www_chinabidding_com", "www_cnbmtendering_com", "www_cnpcbidding_com", "www_crpsz_com"],


        'www_d_p':['www_dlswzb_com','www_dlzb_com','www_dlzb_com_c1608','www_dlztb_com',
         'www_gmgitc_com','www_mgzbzx_com','www_ngecc_com','www_namkwong_com_mo'],

        'www_q_z':['www_qhbidding_com','www_sinochemitc_com','www_sztc_com',
         'www_wiscobidding_com_cn','www_ykjtzb_com','www_zeec_cn','www_zmzb_com']

        }


def get_df():

    data=[]

    for w in data1.keys():
        tmp1=data1[w]
        for w1 in tmp1:
            tmp=["postgres","since2015","192.168.4.175",'qycg',w1]
            data.append(tmp)

    df=pd.DataFrame(data=data,columns=["user",'password',"host","database","schema"])
    return df

def create_all_schemas():
    conp = get_conp1('qycg')
    for w in data1.keys():
        tmp1=data1[w]
        for w1 in tmp1:
            sql = "create schema if not exists %s" % (w1)
            db_command(sql, dbtype="postgresql", conp=conp)


def update_schemas(schema_list=[], drop_html=False):

    '''
    :param schema_list: 一个包含多个schema的列表; list 格式
    :param drop_html: False 不删除gg_html;True 删除gg_html;just 只删除gg_html
    :return:
    '''

    conp = get_conp1('qycg')


    sql1 = '''select schemaname,tablename from pg_tables;'''
    tables = db_query(sql1, dbtype='postgresql', conp=conp)

    for table in tables.values:

        if drop_html == 'just':
            if (table[0] in schema_list) and ('gg_html' in table[1]):
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp)
                print('已删除 %s.%s 表' % (table[0], table[1]))

        elif not drop_html:

            if (table[0] in schema_list) and ('gg_html' not in table[1]):
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp)
                print('已删除 %s.%s 表' % (table[0], table[1]))

        else:
            if table[0] in schema_list:
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp)
                print('已删除 %s.%s 表' % (table[0], table[1]))




    return 'over'




# df=get_df()
# db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))
# #
# add_conp(["postgres","since2015","192.168.4.175",'qycg','public'])
#
# df=query("select * from cfg")
# print(df.values)


