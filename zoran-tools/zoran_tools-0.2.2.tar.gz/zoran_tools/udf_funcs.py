# coding=utf-8


import time
import datetime
import json
import csv
from math import log10


__doc__ = """
你已导入模块：{file}
本模块中归集PySpark中处理数据常用的一些函数，可以作为UDF函数使用
Auth: chenzhongrun
Mail: chenzhongrun@bonc.com.cn
ReleaseDate: 2019-04-17


Usage：

from pyspark.sql import SparkSession

spark = SparkSession.builder \\
             .appName("bonc_model")\\
             .enableHiveSupport()\\
             .getOrCreate()


spark.sparkContext.addPyFile('file:///tmp/geodata/udf_funcs.py')
import udf_funcs


e.g:

spark.udf.register('stripLeftZero', udf_funcs.strip_left_zero_and_86)  # 去除对端号码的开头的所有0和86，使得号码格式标准化

query = \"\"\"select distinct opp_nbr
                ,stripLeftZero(opp_nbr) opp_none_86
           from source_zjdw.NET_CDR_VS_O
          where input_day = "20190401" \"\"\"
df = spark.sql(query)
df.filter('opp_nbr <> opp_none_86').show()

+-------------+-----------+                                                     
|      opp_nbr|opp_none_86|
+-------------+-----------+
| 057188661027|57188661027|
| 057182191628|57182191628|
|8618758881103|18758881103|
| 057186789250|57186789250|
| 057128154833|57128154833|
| 057182208591|57182208591|
|8615027490666|15027490666|
+-------------+-----------+

there are the funcs you can import and register:
{funcs}
"""


funcs = dict()
funcs_names = dict()


def udf_funcs(func):
    func_name = func.__name__
    func_name_upper = ''.join([w.capitalize() for w in func_name.split('_')])
    funcs_names[func_name_upper] = func_name
    funcs[func_name_upper] = func
    return func


##################################################################
#   以下函数，对经度进行Geohash编码和解码                            #
##################################################################
#  Note: the alphabet in geohash differs from the common base32
#  alphabet described in IETF's RFC 4648
#  (http://tools.ietf.org/html/rfc4648)
__base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
__decodemap = {}
for i in range(len(__base32)):
    __decodemap[__base32[i]] = i
del i


def decode_exactly(geohash):
    """
    Decode the geohash to its exact values, including the error
    margins of the result.  Returns four float values: latitude,
    longitude, the plus/minus error for latitude (as a positive
    number) and the plus/minus error for longitude (as a positive
    number).
    """
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    lat_err, lon_err = 90.0, 180.0
    is_even = True
    for c in geohash:
        cd = __decodemap[c]
        for mask in [16, 8, 4, 2, 1]:
            if is_even: # adds longitude info
                lon_err /= 2
                if cd & mask:
                    lon_interval = ((lon_interval[0]+lon_interval[1])/2, lon_interval[1])
                else:
                    lon_interval = (lon_interval[0], (lon_interval[0]+lon_interval[1])/2)
            else:      # adds latitude info
                lat_err /= 2
                if cd & mask:
                    lat_interval = ((lat_interval[0]+lat_interval[1])/2, lat_interval[1])
                else:
                    lat_interval = (lat_interval[0], (lat_interval[0]+lat_interval[1])/2)
            is_even = not is_even
    lat = (lat_interval[0] + lat_interval[1]) / 2
    lon = (lon_interval[0] + lon_interval[1]) / 2
    return lat, lon, lat_err, lon_err


@udf_funcs
def decode(geohash):
    """
    Decode geohash, returning two strings with latitude and longitude
    containing only relevant digits and with trailing zeroes removed.
    """
    lat, lon, lat_err, lon_err = decode_exactly(geohash)
    # Format to the number of decimals that are known
    lats = "%.*f" % (max(1, int(round(-log10(lat_err)))) - 1, lat)
    lons = "%.*f" % (max(1, int(round(-log10(lon_err)))) - 1, lon)
    if '.' in lats: lats = lats.rstrip('0')
    if '.' in lons: lons = lons.rstrip('0')
    return lats, lons


def encode(latitude, longitude, precision=12):
    """
    Encode a position given in float arguments latitude, longitude to
    a geohash which will have the character count precision.
    """
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    geohash = []
    bits = [ 16, 8, 4, 2, 1 ]
    bit = 0
    ch = 0
    even = True
    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= bits[bit]
                lon_interval = (mid, lon_interval[1])
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= bits[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash += __base32[ch]
            bit = 0
            ch = 0
    return ''.join(geohash)


@udf_funcs
def geohash_encode(latitude, longitude, precision=12):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except Exception:
        return '0' * precision
    return encode(latitude, longitude, precision)


##################################################################
#     以下函数，用于为时间打上标签，如交通高峰期，非高峰期等         #
##################################################################
@udf_funcs
def peak(start_time):
    # 7：00-9：30 morning peak，17：00-20：00 evening peak，others non-peak
    if time.strptime(start_time, "%Y%m%d%H%M%S").tm_hour in [7, 8]:
        return 'mor_peak'
    elif time.strptime(start_time, "%Y%m%d%H%M%S").tm_hour == 9 and time.strptime(start_time, "%Y%m%d%H%M%S").tm_min in list(range(0, 30)):
        return 'mor_peak'
    elif time.strptime(start_time, "%Y%m%d%H%M%S").tm_hour in [17, 18, 19]:
        return 'even_peak'
    else:
        return ''


@udf_funcs
def weekday(start_time):
    week_day = [0, 1, 2, 3, 4]
    if time.strptime(start_time, "%Y%m%d%H%M%S").tm_wday in week_day:
        return 'weekday'
    else:
        return 'weekend'


@udf_funcs
def daytime(start_time):
    # 7:00-20:00 daytime，23:00-7:00 night，others non
    day_time = ['07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
    # night: from 23 o'clock to 7 o'clock
    night = ['23', '00', '01', '02', '03', '04', '05', '06']
    if start_time[8: 10] in day_time:
        return 'daytime'
    elif start_time[8: 10] in night:
        return 'night'
    else:
        return ''


@udf_funcs
def day_of_week(starttime, fm='%Y-%m-%d %H:%M:%S'):
    """
    返回starttime是周几
    0对应周一，6对应周日
    """
    if not starttime or not isinstance(starttime, str):
        return 0
    week_day = datetime.datetime.strptime(starttime, fm).weekday()
    return week_day


@udf_funcs
def is_weekend(starttime, fm='%Y-%m-%d %H:%M:%S'):
    """
    返回starttime是否是周末(周六周日)
    """
    return int(day_of_week(starttime, fm) >= 5)


##################################################################
#   以下函数，对字符串进行处理                                      #
##################################################################
@udf_funcs
def strip_left_zero_and_86(phone_num):
    """
    去除号码的开头的所有0和86，使得号码格式标准化
    """
    return phone_num.lstrip('0').lstrip('86')


@udf_funcs
def trans_latin_to_utf8(s):
    """
    对latin编码的字符进行解码为utf-8
    """
    return s.encode('latin').decode('utf8')


class AppLogger(object):
    def __init__(self, file, level='DEBUG', role='root', p=True):
        self.file = file
        self.levels = {
            'ERROR': 900,
            'WARN': 700,
            'INFO': 500,
            'DEBUG': 300,
        }
        self.level = level.upper()
        self.p = p
        self.role = role

    def log(self, level, message):
        if self.levels.get(level.upper()) < self.level:
            return
        
        log_time = time.strftime('%Y-%m-%d %H:%M:%S')
        content = '{} {} {}'.format(log_time, self.role, message)
        if self.p:
            print(content)
        with open(self.file, mode='a+') as f:
            f.write(content)


def open_csv(file):
    with open(file, mode='r') as f:
        f_csv = csv.reader(f)
        rows = [row for row in f_csv]
        return rows


def create_df_from_csv(file, spark):
    rows = open(file)
    rdd = spark.sparkContext.parallelize(rows)
    df = spark.createDataFrame(rdd)
    return df


__doc__ = __doc__.format(file=__file__, funcs=json.dumps(funcs_names, ensure_ascii=False, indent=2))
print(__doc__)
