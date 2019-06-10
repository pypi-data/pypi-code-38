import pyodbc
import configparser
from collections import OrderedDict

class MSSQLDataHelper():

    def __init__(
        self, 
        logger=None,
        config_file='go_servers.ini',
        host_name='GoServer_Production_ReadOnly'):
        self.logger = logger
        self.config_file = config_file
        self.host_name = host_name

    def connect(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        conn_str = 'DRIVER={ODBC Driver 13 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s;PORT=%s' \
            % (self.config[self.host_name]['Server'], \
            self.config[self.host_name]['Database'], \
            self.config[self.host_name]['Username'], \
            self.config[self.host_name]['Password'], \
            self.config[self.host_name]['PORT'])
        self.conn = pyodbc.connect(conn_str)
        return self.conn

    def get_data(self, sql_str):
        self.logger_info('start get data from %s ... '% self.host_name)
        self.logger_info('\t%s' % sql_str)
        self.connect()
        cursor = self.conn.cursor()
        result = []
    
        try:
            cursor.execute(sql_str)
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            while row is not None:
                row_dict = OrderedDict(zip(columns, row))
                result.append(dict(row_dict))
                row = cursor.fetchone()
        except Exception as e:
            self.logger_info(e)
            raise e
        finally:
            cursor.close()
            self.conn.close()

        self.logger_info('result.count = %s' % len(result))
        if len(result) > 0:
            self.logger_info('result[0] = %s' % result[0])
            #self.logger_info('result[0] = %s' % dict(result[0]))

        return result

    def get_vm_list(self):
        sql_str = """
SELECT Id, Latitude, Longitude, LocName
FROM dbo.Vm vm
LEFT JOIN dbo.VmExt vmExt ON vm.Id = vmExt.vmId
WHERE (STATE = 1 OR STATE = 0 OR STATE = 99 OR STATE = 100)
    AND vmExt.vmId IS NULL
        """
        
        res = self.get_data(sql_str)
        # filter by LocName
        for r in res:
            if '測試' in r['LocName'] or 'Test' in r['LocName'] or '建置' in r['LocName']:
                res.remove(r)

        self.logger_info('result.count = %s' % len(res))
        if len(res) > 0:
            self.logger_info('result[0] = %s' % res[0])

        return res

    def get_exchange_battery_diff(self, dt_start, dt_end):
        sql_str = """
SELECT exitem.ExId, MIN(exitem.Capacity) AS MinCapacity, MAX(exitem.Capacity) AS MaxCapacity
FROM dbo.BatteryExHistory ex
LEFT OUTER JOIN dbo.BatteryExItemHistory exitem ON ex.Id = exitem.ExId
WHERE ex.ExchangeTime >= '%s' 
    AND ex.ExchangeTime < '%s'
    AND VmId IS NOT NULL 
    AND ScooterId IS NOT NULL
    AND exitem.Type = 2
GROUP BY exitem.ExId
    """ % (dt_start, dt_end)

        res = self.get_data(sql_str)

        self.logger_info('result.count = %s' % len(res))
        if len(res) > 0:
            self.logger_info('result[0] = %s' % res[0])

        return res

    def get_scooter_miss_rate(self, dt_start, dt_end, r_min=0, r_max=85):
        sql_str = """
SELECT ex.ScooterId, COUNT(*) AS MissBatteries, COUNT(DISTINCT ExchangeTime) AS MissCount
FROM dbo.BatteryExHistory ex
LEFT OUTER JOIN dbo.BatteryExItemHistory exitem ON ex.Id = exitem.ExId
WHERE ex.ExchangeTime >= '%s' 
    AND ex.ExchangeTime < '%s'
    AND VmId IS NOT null 
    AND ScooterId IS NOT NULL
    AND exitem.Type = 2
    AND (exitem.Capacity >= %s AND exitem.Capacity <= %s)
GROUP BY ex.ScooterId
        """ % (dt_start, dt_end, r_min, r_max)

        res = self.get_data(sql_str)

        self.logger_info('result.count = %s' % len(res))
        if len(res) > 0:
            self.logger_info('result[0] = %s' % res[0])

        return res

    def get_vm_miss_rate(self, dt_start, dt_end):
        sql_str = """
SELECT ex.*, vm.Latitude, vm.Longitude
FROM (
    SELECT ex.VmId, COUNT(*) AS MissBatteries, COUNT(DISTINCT ExchangeTime) AS MissCount
    FROM dbo.BatteryExHistory ex
    LEFT OUTER JOIN dbo.BatteryExItemHistory exitem ON ex.Id = exitem.ExId
    WHERE ex.ExchangeTime >= '%s' 
        AND ex.ExchangeTime < '%s'
        AND VmId IS NOT null 
        AND ScooterId IS NOT NULL
        AND exitem.Type = 2
        AND exitem.Capacity < 85
GROUP BY ex.VmId
) AS ex
LEFT JOIN dbo.vm vm ON vm.id = ex.VmId;
        """ % (dt_start, dt_end)

        res = self.get_data(sql_str)

        self.logger_info('result.count = %s' % len(res))
        if len(res) > 0:
            self.logger_info('result[0] = %s' % res[0])

        return res

    def get_vm_total_exchange(self, dt_start, dt_end):
        sql_str = """
SELECT ex.*, vm.RId, vm.LocName, vm.Latitude, vm.Longitude, vm.Address
FROM (
    SELECT ex.VmId, COUNT(*) AS TotalBatteries, COUNT(DISTINCT ExchangeTime) AS TotalCount
    FROM dbo.BatteryExHistory ex
    LEFT OUTER JOIN dbo.BatteryExItemHistory exitem ON ex.Id = exitem.ExId
    WHERE ex.ExchangeTime >= '%s' 
        AND ex.ExchangeTime < '%s'
        AND VmId IS NOT null 
        AND ScooterId IS NOT NULL
        AND exitem.Type = 2
GROUP BY ex.VmId
) AS ex
LEFT JOIN dbo.vm vm ON vm.id = ex.VmId;
        """ % (dt_start, dt_end)

        res = self.get_data(sql_str)

        self.logger_info('result.count = %s' % len(res))
        if len(res) > 0:
            self.logger_info('result[0] = %s' % res[0])

        return res        

    def logger_info(self, msg):
        if self.logger != None:
            self.logger.info(msg)
