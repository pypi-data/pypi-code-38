r"""
    All sql put in this pool.
    Send sql-token to get sql string.
"""
import os
import datetime
from time import strftime, localtime
from configparser import ConfigParser
import re
from deprecated import deprecated
import traceback


conf = ConfigParser()
home_dir = os.path.dirname(os.path.realpath(__file__))
conf_path = os.path.join(home_dir, "config.conf")
conf.read(conf_path)

year = strftime("%Y", localtime())
mon = strftime("%m", localtime())
day = strftime("%d", localtime())
hour = strftime("%H", localtime())
min_ = strftime("%M", localtime())
sec = strftime("%S", localtime())
v_date = datetime.datetime.now().strftime('%Y-%m-%d')


def sql_change(sql_path, sql_token):
    r"""
    get sql change
    :param sql_path:
    :param sql_token:
    :return:
    """
    sql_file_name = sql_token
    sql_file_path = os.path.join(sql_path, sql_file_name)

    try:
        fpo = open(sql_file_path, 'r', encoding='utf8')
    except Exception:
        fpo = open(sql_file_path, 'r', encoding='gbk')

    output_string = ''

    try:
        sql_string = fpo.readlines()
        for ele in sql_string:
            output_string += ele.replace('\n', ' ')
    except Exception:
        pass
    finally:
        fpo.close()

    return output_string


def proc_get(proc_name, schema, param):
    r"""
    get proc run sql
    :param proc_name:
    :param schema:
    :param param:
    :return:
    """
    output = "begin     " + schema + "." + proc_name
    params = ""
    lastindex = len(param) - 1
    if proc_name[0:3] == 'EAS':
        if param:
            params += "("
            for i in param:
                if param.index(i) != lastindex:
                    params += "'" + str(i) + "',"
                else:
                    params += "'" + str(i) + "')"
    elif proc_name == 'rtl_rp_seperate':
        if param:
            params += "("
            for i in param:
                if param.index(i) != lastindex:
                    params += "'" + str(i) + "',"
                else:
                    params += "'" + str(i) + "')"
    else:
        formats = 'yyyy-MM-dd'
        if param:
            params += "("
            for i in param:
                if param.index(i) != lastindex:
                    params += "to_date('" + str(i) + "','" + formats + "'),"
                else:
                    params += "to_date('" + str(i) + "','" + formats + "'))"
    output = output + params + ";  end;"
    return output


def get_firstday_of_month():
    r"""
        get the first day of month
        date format = "YYYY-MM-DD"
    """
    year_ = strftime("%Y", localtime())
    mon_ = strftime("%m", localtime())
    days = "01"
    if int(mon) < 10:
        mon_ = "0"+str(int(mon_))
    arr = (year_, mon_, days)
    return "-".join("%s" % i for i in arr)


def is_monthend():
    r"""
    is or not monthend
    :return:
    """
    try:
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        date = now_date
        if date == get_firstday_of_month():
            return "is_month_end"
        else:
            return "not_month_end"
    except Exception as e:
        print(e)
        raise RuntimeError(e)


@deprecated(version='1.2.5', reason="Return Sql is too big, use modify_sql in later version.")
def return_sql(sql_path, sql_name, need_chinese=True):
    r"""
    return sql list
    :param sql_path:
    :param sql_name:
    :param need_chinese:
    :return:
    """

    sql_file_name = sql_name
    sql_file_path = os.path.join(sql_path, sql_file_name)

    try:
        fpo = open(sql_file_path, 'r', encoding='utf-8')
        sql_string = fpo.readlines()
    except Exception:
        fpo = open(sql_file_path, 'r', encoding='gbk')
        sql_string = fpo.readlines()

    for i in sql_string:
        if '--' in i:
            index = sql_string.index(i)
            sql_string[index] = ""
        else:
            pass
    output_string = ''

    try:
        for ele in sql_string:
            output_string += ele.replace('\n', ' ')
    except Exception:
        pass
    finally:
        fpo.close()

    if not need_chinese:
        # 将sql中的中文替换成''
        output_string = re.sub(r'[\u4e00-\u9fa5]', '', output_string)
        # 将sql中的中文字符替换成''
        output_string = re.sub(r'[^\x00-\x7f]', '', output_string)

    list_ = output_string.split(";")
    for i in list_:
        if i.strip() == '':
            list_.remove(i)

    return list_


def modify_sql(fpo, need_chinese=True):
    remark1 = '/*'
    len_r1 = 2
    remark2 = '*/'
    len_r2 = 2
    remark3 = '--'
    len_r3 = 2
    output_string = ''
    try:
        _sqls = fpo.readlines()
    except Exception:
        print('Modify sql error! file pointer cannot be used!')
        print(traceback.format_exc())
        raise Exception

    stack_ = []
    for _sql in _sqls:
        st_remark1 = st_remark2 = st_remark3 = -1
        if _sql.find(remark3) >= 0:
            st_remark3 = _sql.find(remark3)
            stack_.append(3)
        if _sql.find(remark1) >= 0:
            st_remark1 = _sql.find(remark1)
            stack_.append(1)
        if _sql.find(remark2) >= 0:
            st_remark2 = _sql.find(remark2)
            stack_.append(2)

        if len(stack_) == 0:
            output_string += _sql
        elif st_remark1 >= 0:
            if st_remark2 >= 0:
                output_string += _sql[:st_remark1] + _sql[st_remark2 + len_r1:]
            else:
                output_string += _sql[:st_remark1]
        elif st_remark2 >= 0:
            output_string += _sql[st_remark2 + len_r1:]
        elif st_remark3 >= 0:
            output_string += _sql[:st_remark3]
        else:
            continue

        if st_remark2 >= 0:
            stack_.pop()
            if stack_.count(1) > stack_.count(2):
                stack_.pop()
        if st_remark3 >= 0:
            stack_.pop()

    output_string.replace('\n', ' ')

    if not need_chinese:
        # 将sql中的中文替换成''
        output_string = re.sub(r'[\u4e00-\u9fa5]', '', output_string)
        # 将sql中的中文字符替换成''
        output_string = re.sub(r'[^\x00-\x7f]', '', output_string)

    for i in output_string.split(";"):
        if i.strip() == '':
            pass
        else:
            yield i

