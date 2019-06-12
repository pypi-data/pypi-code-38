import pymysql


class sql:
    def lianjie_sql(self, sql_shujuku_name, sql_yuju):
        '''
        :param sql_shujuku_name:
        :param sql_yuju:
        :return:
        # self.sql_ip=sql_ip
        # self.sql_name=sql_name
        # self.sql_paword=sql_pasword
        '''
        self.sql_shujuku_name = sql_shujuku_name
        self.sql_yuju = sql_yuju
        '''打开数据库连接'''
        db = pymysql.connect("39.107.239.18", "root", "wdtx.2016", self.sql_shujuku_name, charset='utf8')
        '''使用cursor()方法获取操作游标'''
        cursor = db.cursor()
        '''执行sql语句'''
        cursor.execute(self.sql_yuju)
        '''
        #获取一行输出结果
        data = cursor.fetchone()

        #获取输出结果
        #data_one = cursor.fetchone()
        #data_many = cursor.fetchmany()
        '''
        data_all = cursor.fetchall()
        '''关闭数据库连接'''
        db.close()
        return data_all

# sql_yuju="SELECT * FROM `ceshi_xinxi`"
# sql_yuju2="SELECT *,sum(id) as '合计',COUNT(id) as '总人数' FROM `ceshi_xinxi`"
# sql_yuju3="SELECT a.`name` as 'name' , a.age as '姓名',a.sex as '性别',b.`name` as '性格' FROM ceshi_xinxi as a,xingge as b where a.xinge=b.id"
# s=sql()
# data_s=s.lianjie_sql("39.107.239.18","root","wdtx.2016","ceshi_test_chenya",sql_yuju3)
#
# print(data_s)
#
# print(data_s[0])