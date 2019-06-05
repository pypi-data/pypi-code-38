'''
Primary Client module for Spreader
'''
import datetime
import platform
import psutil
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

class SpreadClient:
    '''
    Main Client
    '''
    _engine = None
    _session = None
    debug_mode = False
    __current_agent_id = None
    _connection = None

    _client_version_string = '0.0.1a1'
    agent_name = ''

    def __init__(self, **kwargs):
        if 'debug' in kwargs:
            self.debug_mode = kwargs['debug']
        if self.debug_mode:
            self.debug_log('Debug Mode')

        print('Connection String: ', kwargs['connection_string'])
        self._engine = create_engine(kwargs['connection_string'],
            #connect_args={'application_name': str.format('Python Ref Client {}', self._client_version_string)},
            convert_unicode=True)
        self._session = scoped_session(sessionmaker(autocommit=False,
            autoflush=False,
            bind=self._engine))

    def debug_log(self, log_string):
        '''
        Default Logging to Console
        '''
        if self.debug_mode:
            print(str.format('{} - {}', datetime.datetime.now(), log_string))

    def _call_stored_procedure_with_output(self, procedure_name, *args):
        result = None
        try:
            cursor = self._connection.connection.cursor()
            cursor.callproc(procedure_name, args)
            result = cursor.fetchall()
        finally:
            cursor.close()
        return result

    def _call_stored_procedure(self, procedure_name, *args):
        self._call_stored_procedure_with_output(procedure_name, *args)

    def _do_agent_init(self, netname, version, cpucount, memory):
        return self._call_stored_procedure_with_output('agent_init', netname, version, cpucount, memory)[0][0]

    def connect(self):
        '''
        Calls initial agent_init Stored Procedure
        '''
        self.debug_log('Initializing')
        if not self._connection:
            self._connection = self._engine.connect()
        if self.agent_name == '':
            self.agent_name = 'Python Ref Client'
        __current_agent_id = self._do_agent_init(platform.node(), self.agent_name, psutil.cpu_count(),
            psutil.virtual_memory().total // 1048576)
        return __current_agent_id

class MSSQLSpreadClient(SpreadClient):
    '''
    Spreader client for MSSQL
    '''
    def _do_agent_init(self, netname, version, cpucount, memory):
        sqlcmd = '''
        DECLARE @agentid INT;
        EXEC agent_init "{}", "{}", "{}", "{}", @agentid OUT;
        SELECT @agentid
        '''.format(netname, version, cpucount, memory)

        cursor = self._connection.connection.cursor()
        try:
            cursor.execute(sqlcmd)
            res = cursor.fetchone()[0]
            self._connection.connection.commit()
        finally:
            cursor.close()

        return res
