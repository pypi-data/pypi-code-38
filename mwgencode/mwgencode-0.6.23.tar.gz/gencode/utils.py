from enum import Enum
import socket
from datetime import datetime
import codecs
import os


class Keytype(Enum):
    # TKeyType=(ktUnkown,ktKey,ktForeignKey,ktNotKey,ktsys);
    # 访问方法 Keytype.key.value,Keytype.foreignkey.value
    unkown = 0
    key = 1
    foreignkey = 2
    notkey = 3
    sys = 4

# TFieldFrom=(ffUnknown,ffDatabase,ffLookup,ffCustom);
class FieldFrom(Enum):
    unknown = 0
    database =1
    lookup = 2
    custom =3

class DBDataType(Enum):
    Unknown=''
    bit='bit'
    char='char'
    varchar='varchar'
    datetime='datetime'
    time='time'
    float='float'
    int='int'
    nchar='nchar'
    numeric='numeric'
    guid='uniqueidentifier'
    text='text'
    autoint='AutoInt'
    date='date'
    image='image'

class DBDataType_len(Enum):
    Unknown=0
    bit=1
    char=10
    varchar=50
    datetime=8
    time=8
    float=8
    int=4
    nchar=50
    numeric=13
    guid=16
    text=16
    autoint=4
    date=4
    image=32

def convert2dbType(umlType):
    if umlType.upper() == 'STRING':
        return DBDataType.varchar.value
    elif umlType.upper() == 'INTEGER':
        return DBDataType.int.value
    elif umlType.upper() == 'AUTOINT':
        return DBDataType.autoint.value
    elif umlType.upper()=='DOUBLE' or umlType.upper()=='EXTEND':
        return DBDataType.float.value
    elif umlType.upper()=='TDATE' or umlType.upper()=='DATE':
        return DBDataType.date.value
    elif umlType.upper()=='TDATETIME' or umlType.upper()=='DATETIME':
        return DBDataType.datetime.value
    elif umlType.upper()=='TTIME' or umlType.upper()=='TIME':
        return DBDataType.time.value
    elif umlType.upper()=='BOOLEAN':
        return DBDataType.bit.value
    elif umlType.upper() =='STRING':
        return DBDataType.varchar.value
    elif umlType.upper() =='INT64'or umlType.upper() =='UINT64':
        return DBDataType.numeric.value
    elif umlType.upper() =='VARIANT':
        return DBDataType.varchar.value
    elif umlType.upper() =='TEXT':
        return DBDataType.text.value
    elif umlType.upper() =='IMAGE':
        return DBDataType.image.value
    else:
        return DBDataType.varchar.value

def covert2pytype(dbtype,size):
    if dbtype == 'bit':
        return 'db.Boolean'
    elif dbtype == 'char' or dbtype == 'varchar' or\
        dbtype == 'nchar':
        return 'db.String(%s)'%size
    elif dbtype == 'datetime':
        return 'db.DateTime'
    elif dbtype == 'time':
        return 'db.Time'
    elif dbtype == 'float':
        return 'db.Float'
    elif dbtype == 'int':
        return 'db.Integer'
    elif dbtype == 'numeric':
        return 'db.Float'
    elif dbtype == 'text':
        return 'db.Text'
    elif dbtype == 'AutoInt':
        return 'db.Integer'
    elif dbtype == 'date':
        return 'db.Date'
    elif dbtype == 'image':
        return 'db.LargeBinary'

def hostname():
    return socket.gethostname()

def write_gen_info(f):
    f.write('#' * 40+'\n')
    f.write('# create by :%s'%hostname()+'\n')
    f.write('# create time :%s'%datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+'\n')
    f.write('#' * 40+'\n')


def saveUTF8File(filename,codes,writegeninfo=True,exist_ok=True):
    '''
    把list 中的数据存UTF8格式
    :param filename:
    :param codes: 存放代码的 list
    :return:
    '''
    if not codes:
        return
    if not exist_ok and os.path.exists(filename):
        print('the file(%s) is exist' % filename)
        return
    os.makedirs(os.path.dirname(filename),exist_ok=True)
    with codecs.open(filename, "w", "utf-8") as file:
        if writegeninfo:
            write_gen_info(file)
        for line in codes:
            if not line:
                continue
            file.write(line + '\n')

def get_merge_codes(scodes,dcodes):
    # scodes :新产生的代码集合，dcodes：需更新的代码集合
    isexist = False
    if not scodes:
        return
    # 記錄丟失的屬於方法的代碼
    pass_code = []
    for sindx,sc in enumerate(scodes,0):
        if sc.startswith('from '):
            continue
        if sc.startswith('@'):
            pass_code.append(sc)
            continue
        # isexist = False
        if sc.startswith('def '):
            isexist = False
            c_func = sc.split('(')[0]+'('
            for dindex,dc in enumerate(dcodes,0):
                if dc.startswith(c_func):
                    dcodes[dindex] = scodes[sindx]
                    isexist = True
                    pass_code.clear()
                    break
            else:
                dcodes.extend(pass_code)
                dcodes.append(scodes[sindx])
                pass_code.clear()
        elif not isexist:
            dcodes.append(scodes[sindx])

    return dcodes

def get_merge_file(scodes,dfile):
    assert os.path.exists(dfile),'该文件(%s)不存在'%dfile
    codes = []
    with codecs.open(dfile,"r", "utf-8") as file:
        start = True
        for code in file.readlines():
            if start and code.startswith('#'):
                continue
            else:
                start = False
            codes.append(code.rstrip())
    return get_merge_codes(scodes,codes)

if __name__ == '__main__':
    codes = get_merge_codes(['##############',
                             '#cxh',
                             '#############',
                             'def test(a1)',
                             '    pass',
                             'def test1(a1)',
                             '    print(a)',
                             '    print(c)',
                             'def test2(a1)',
                             '   print(test2)'],
                             ['##############',
                              '#xxxx',
                              '#############',
                              'def test(a2,b2)',
                              '    print(1)',
                              '    #print(2)',
                              'def test2(a2,b2)',
                              '   print(3)',
                              '    print(4)',
                              'def test3(a2,b2)',
                              '    print(5)'])
    for c in codes:
        print(c)
    # codes = []
    # with codecs.open(r'D:\mwwork\projects\its\mobile_gateway_server\app\api\v1_0\rtdatamng.py',
    #                  "r", "utf-8") as file:
    #     for l in file.readlines():
    #         codes.append(l.strip())
    #         print(l.strip())
    #     print(codes)
    #


