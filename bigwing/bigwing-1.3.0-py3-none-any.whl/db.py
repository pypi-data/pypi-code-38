import pymysql
import numpy as np
import pandas as pd
from pymongo import MongoClient
from IPython.display import clear_output

class BigwingMysqlDriver() :
    '''BigwingMysqlDriver 모듈 클래스<br />

         - 사용법 : 인스턴스명 = BigwingMysqlDriver("호스트명", "DB명", "유저명", "패스워드")

         - port는 3306 을 디폴트로 사용 (변경시 port=포트번호 를 인수로 넘김)
    '''
    def __init__(self, host, dbname, user, passwd, port=3306):

        self.__host = host
        self.__user = user
        self.__dbname = dbname
        self.db = pymysql.connect(user=self.__user, host=self.__host, db=self.__dbname, passwd=passwd, port=port, charset='utf8')
        self.cursor = self.db.cursor() #커서 객체 생성

        #테이블 정보 로드
        self.tables = {}
        self.cursor.execute("show tables")
        tables_info = self.cursor.fetchall()

        for table_info in tables_info :

            table = table_info[0]
            self.cursor.execute("show columns from `{}`".format(table))
            columns_info = self.cursor.fetchall()
            columns = []
            for column_info in columns_info :
                columns.append(column_info[0])
            columns = tuple(columns)
            self.tables[table] = columns

    def show(self, table=None):
        ''' 테이블과 컬럼 정보를 출력하는 함수

             - 사용법 : 인스턴스명.show()  또는 인스턴스명.show(특정테이블명)
        '''
        if table != None :
            try :
                return self.tables[table]
            except :
                print('{} 테이블이 존재하지 않습니다.'.format(table))
                return None

        return self.tables


    def create(self, table, *args):
        '''테이블을 생성하는 함수

            - 사용법 : 인스턴스명.create('테이블명', (컬럼1, 컬럼2,...) )

            - 특징 : 모든 컬럼은 varchar(50) default null 형으로 일괄 생성됨
        '''
        if self.show(table) != None :
            print('{} 테이블이 이미 존재합니다.'.format(table))
            return
        SQL = " CREATE TABLE """ + table + """ ( """
        cols = []

        for arg in args[0] :
            SQL = SQL + "{} varchar(100) DEFAULT NULL,".format(arg)
        SQL = SQL[:-1] # 쉼표제거
        SQL = SQL + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        print(SQL)
        self.cursor.execute(SQL)
        self.tables[table] = args[0]
        print("{} 테이블이 생성되었습니다.".format(table))


    def delete(self, table):
        ''' 특정 테이블을 삭제하는 함수

             - 사용법 : 인스턴스명.delete('테이블명')
        '''
        if self.show(table) == None :
            return
        SQL = "DROP TABLE {}".format(table)
        self.cursor.execute(SQL)
        del self.tables[table]
        print("{} 테이블이 삭제되었습니다.".format(table))


    def insert(self, table, *args):
        ''' 특정 테이블에 데이터를 입력하는 함수

             - 사용법 : 인스턴스명.insert('테이블명', (컬럼1, 컬럼2, 컬럼3, ...))
        '''
        if table not in self.tables.keys() :
            print("{} 테이블이 존재하지 않습니다.".format(table))
            return;

        if  np.size(self.tables[table]) != np.size(args[0]) :
            print("{} 테이블의 컬럼은 {} 이며 총 {}개 입니다.".format(table, self.tables[table], np.size(self.tables[table])))
            return;

        SQL = "insert into {} (".format(table)
        for col in self.tables[table] :
            SQL = SQL + "{}, ".format(col)
        SQL = SQL[:-2] # 쉼표제거
        SQL = SQL + ") values ("
        for len in range(np.size(self.tables[table])) :
            SQL = SQL + "%s, "
        SQL = SQL[:-2] # 쉼표제거
        SQL = SQL + ")"
        self.cursor.execute(SQL, *args)

    def insert_bulk(self, table, data):
        '''
        특정 테이블에 데이터프레임 형태의 자료를 한번에 입력하는 함수

        - 사용법 : 인스턴스명.insert_bulk('테이블명', '데이터프레임변수')
        '''
        if type(data) != type(pd.DataFrame()):
            print("입력데이터 타입이 데이터프레임이어야 합니다.")
            return;

        for i in range(data.shape[0]) :
            self.insert(table, tuple(data.loc[i]))
            print("%.1f%% 진행중" % ((i+1)/data.shape[0]*100))
            clear_output(wait=True)

        print("총 {}건의 데이터 입력이 완료되었습니다.\n종료전 Commit 여부를 확인하세요.".format(data.shape[0]))

    def commit(self):
        ''' insert()함수 사용후 커밋을 실행하는 함수

             - 사용법 : 인스턴스명.commit()
        '''
        self.db.commit()
        print("커밋이 완료되었습니다.")


    def takeout(self, table):
        ''' 테이블 데이터를 데이터프레임 타입으로 가져오는 함수

             - 사용법 : 인스턴스명.takeout('테이블명')
        '''
        self.cursor.execute("select * from {}".format(table))
        df = pd.DataFrame(columns=self.tables[table])
        while True :
            row = self.cursor.fetchone()
            if row == None :
                break;
            df.loc[df.shape[0]] = row
        print("데이터를 반출합니다.")
        return df

    def close(self):
        print("DB연결을 종료합니다.")
        self.cursor.close()
        self.db.close()

    def __del___(self): #커서종료
        print("DB연결을 종료합니다.")
        self.cursor.close()
        #DB커넥터종료
        self.db.close()


'''현재 개발진행중'''
class BigwingMongoDriver() :

    def __init__(self, db, collection):

        self.client = MongoClient()
        self.collection = self.client[db][collection]

    def save(self, **kwargs) :

        print(kwargs)
        try :
            self.collection.insert_one(kwargs)
        except :
            print("저장되지 않았습니다.")
            return

    def find_all(self):

        for n in self.collection.find() :
            yield n
