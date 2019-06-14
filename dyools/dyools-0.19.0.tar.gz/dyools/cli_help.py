from __future__ import (absolute_import, division, print_function, unicode_literals)

import click

from .klass_print import Print


@click.group()
def cli_help():
    pass


@cli_help.command('list')
def __list():
    """
CLI: command line interfaces :
------------------------------
    - etl: realize a workflow of a real ETL (extract, transform, Load, process errors)
    - job: execute a bunch of commands, possible to use them in a loop with some prompts
    - po: make a database of translations and help translating a file
    - rpc: interacts with odoo instances
    - sign: save time passed on a project by date and show it on a calendar
    - todo: save tasks to do
    - tool: contains random cli, encrypt/decrypt and fake command line interfaces
    - ws_agent: launch a python agent on a server, iby default launched on 0.0.0.0:5000 (use the class Consumer to
    interact with it)
    - xml: receive an xml in the STDIN and parse it (a separator may be used) and offer the possibility to extract xpaths

Decorators:
-----------
    - log: Log arguments, response and elapsed time when executing a function
    - raise_exception: for functions that return a boolean, it is possible with this decorator to raise an exception if
    the function decorated return False

Misc:
-----
    - connector, job: generic connector and job utilities for the ETL, see 'etl' for more information
    - odooconnector, odoojob: odoo connector and job utilities for the ETL, see 'etl' for more information
    - odoosimplemigrate: a simple migrate class from odoo to odoo instance
    - csvconnector, csvjob: odoo connector and job utilities for the ETL, see 'etl' for more information
    - consumer: communicate with the remote python agent (ws_agent)
    - convert: convert data type and time (MB -> GB, seconds -> hours)
    - counter: a helper to compute the elapsed time
    - data: a data wrapper and normalizer, the aim of this class to compute header (list) and lines (list pf lists)
    - date: work with string dates
    - default_value: work with default values on objects
    - df: a simple dataframe object with operations 'add' and 'remove', each data is a Serie object
    - env: new odoo environment inside odoo shell
    - serie: a simple Serie object
    - eval: evaluate variables within a data structure
    - inspect: inspect source code
    - is: check a type
    - logger: log to console using colors if possible
    - path: make operations on files and directories
    - offset_limit: generate tuples of offset/limit
    - operator: make operations on data, flat lists, intersection, unique, etc
    - print: print data to console like logger with header and footer
    - progress_bar: print the progression of a tasks
    - queue: pipeline implementation
    - random: generate some randoms
    - rpc: construct an odoo API RPC
    - sample: generate some sample data
    - sftp: tools for paramiko SFTP instance
    - slice: slice iterable objects
    - str: tools around the string objects, can also format a numeric value
    - table: a wrapper around list of lists, remove columns and rows and flat data to make the iterations
    - tool: some tools to redirect stdout/stdin, encrypt/decrypt, protect attributes/items and construct an Odoo domain from a string
    - ws: launch an python remote server, see also 'ws_agent'
    - xlsreader: export tables from an Excel file
    - xlswriterr: create an excel file
    - xml: work with XML architecture
    - yamlconfig: work with Yaml files for configuration

    """
    Print.info(__list.__doc__)


@cli_help.command('raise_exception')
def __raise_exception():
    """raise_exception: for functions that return a boolean, it is possible with this decorator to raise an exception if the
function returns False

    from dyools import raise_exception
    @raise_exception(exception=TypeError, exception_msg='[%s] is not valid')
    def foo(x..):
       pass

default arguments:
    1 - exception = Exception,
    2 - exception_msg = 'Error'

    """
    Print.info(__raise_exception.__doc__)


@cli_help.command('log')
def __log():
    """log: this decorator logs :
    1 - arguments and theirs types
    2 - response and its type
    3 - elapsed time in seconds

    from dyools import log
    @log
    def foo(x..):
       pass
    """
    Print.info(__log.__doc__)


@cli_help.command('etl')
def __etl():
    """ETL: Extract, Transform, Load and process errors

Configuration steps:
--------------------
1 - Create two connectors class for source an destination streams
A connector should inherit from Connector class and define the method 'get' that should open a stream

    from dyools import Connector
    class CLASS_A(Connector):
        def get(self):
            # self contains params token from configuration file
            # self.params['param_1'] => value_1
            return open_stream...


2 - Create an extractor class
An extractor class should inherit from JobExtractorAbstract class and define the methods 'load' and 'count'
    - self.context contains information about source/destination streams and global job information
    - self.params contains parameters about the related stream
    - self.X can return information about the split : self.offset, self.limit, self.domain


    class ProductExtractor(JobExtractorAbstract):
        def extract(self, methods, queued_data, pool):
            # methods: are the chain in the pipeline
            # queued_data: data to process
            # pool: list to fill before quit
            # if necessary self.get_source() return the source stream
            return pool.append((methods, new_data))

        def count(self):
            # if necessary self.get_source() and self.get_destination() returns the two streams
            return X

3 - Create a transformer class
A transformer class should inherit from JobTransformerAbstract class and define the methods 'transform'
    - self.context contains information about source/destination streams and global job information
    - self.params contains parameters about the related stream
    - self.X can return information about the split : self.offset, self.limit, self.domain


    class ProductTransform(JobTransformerAbstract):
        def transform(self, methods, queued_data, pool):
            # methods: are the chain in the pipeline
            # queued_data: data to process
            # pool: list to fill before quit
            # if necessary self.get_source() return the source stream
            return pool.append((methods, new_data))

4 - Create a loader class
A loader class should inherit from JobLoaderAbstract class and define the methods 'load'
    - self.context contains information about source/destination streams and global job information
    - self.params contains parameters about the related stream
    - self.X can return information about the split : self.offset, self.limit, self.domain


    class ProductLoader(JobLoaderAbstract):
        def load(self, methods, queued_data, pool):
            # methods: are the chain in the pipeline
            # queued_data: data to process
            # pool: list to fill before quit
            # if necessary self.get_source() return the source stream
            return pool.append((methods, new_data))

5 - Create an error processing class
An error processing class should inherit from JobErrorAbstract class and define the methods 'transform'
    - self.context contains information about source/destination streams and global job information
    - self.params contains parameters about the related stream
    - self.X can return information about the split : self.offset, self.limit, self.domain


    class ProductError(JobErrorAbstract):
        def error(self, methods, queued_data, pool):
            # methods: are the chain in the pipeline
            # queued_data: data to process
            # pool: list to fill before quit
            # if necessary self.get_source() return the source stream
            return pool.append((methods, new_data))


6 - Create a migrate file configuration
Example of a configuration file
        connectors:
          source_a: con.py::CLASS_A
          source_b: con.py::CLASS_B
        params:
          source_a:
            param_1: value_1
            param_2: value_2
          source_b:
            param_1: value_1
            param_2: value_2
        jobs:
          - extract: product_template.py::Template
            load: product_template.py::Template
            transform: product_template.py::Template
            error: product_template.py::Template
            priority: 1
            threads: 6
            limit: 50
            active: 1
            tag: product_template

7 - Launch the pipeline
Commands :
    etl -c PATH_TO_MIGRATE_FILE --logfile=PATH_TO_OPTIONAL_LOG_FILE
    etl -c --start=PRIORITY_START --stop=PRIORITY_STOP
    etl -c --select=PRIORITY_1,PRIORITY_2,PRIORITY_3
    etl -c --tags=TAG_A,TAG_B

Odoo Implementation:
--------------------
1 - Create two connectors classes for source an destination streams

    class SOURCE_DB(OdooConnector):
        pass

    class SOURCE_DESTINATION(OdooConnector):
        pass

2 - Create job classes for each object to migrate

    from dyools import OdooJobExtractor, OdooJobLoader, OdooJobTransformer, OdooJobError

    class Partner(OdooJobExtractor, OdooJobTransformer, OdooJobLoader, OdooJobError):
        _source_name = 'res.partner'
        _destination_name = 'res.partner'
        _source_fields = ['id', 'name', ]
        _destination_fields = ['id', 'name',  ]
        _destination = 's_db'
        _source = 'd_db'

        def transform(self, methods, queued_data, pool):
            # transform data
            pool.append((methods, queued_data))
3 - Create a migrate file configuration
Example of a configuration file

    connectors:
      s_db: con.py::SOURCE_DB
      d_db: con.py::SOURCE_DESTINATION
    params:
      s_db:
        host: localhost
        port: 8069
        user: admin
        password: admin
        dbname: SOURCE
      d_db:
        host: localhost
        port: 8069
        user: admin
        password: admin
        dbname: DESTINATION
    jobs:
      - extract: res_partner.py::Partner
        load: res_partner.py::Partner
        transform: res_partner.py::Partner
        error: res_partner.py::Partner
        priority: 1
        threads: 6
        limit: 50
        active: 1
        tag: partners

    Automatically OdooLoader use Load to send datas, if a create/write is required with a test by keys, in the job, add :
        primary_keys:
          - name
          - city

CSV Implementation:
-------------------
1 - Create a connector class for the CSV source stream

    class SOURCE_CSV(CsvConnector):
        pass

2 - Create job extractor class

    from dyools import CsvJobExtractor

    class Partner(CsvJobExtractor):
        pass

3 - Create a migrate file configuration
Example of a configuration file

    connectors:
      s_csv: con.py::SOURCE_CSV
      ...
    params:
      s_csv:
        path: PATH_TO_CSV.CSV
      ...
    jobs:
      - extract: res_partner.py::Partner
        ...
    """
    Print.info(__etl.__doc__)


@cli_help.command('consumer')
def __consumer():
    """Consumer: communicate with remote python agent, for the security reason, use a token

    from dyools import Consumer
    c = Consumer(host='127.0.0.1', port=5000, token=None)
    c.ping()  #check if remote agent is up
    c.info()  #see variables available on the agent
    c.flush() #remove all results in the local
    c.print() #print the result
    c.stop()  #shutdown the remote agent

1 - Execute OS commands :

    from dyools import Consumer
    c = Consumer(host='127.0.0.1', port=5000)
    c.add(['ls','-alh'])
    c.add(['ls'])
    c.cmdline()
    c.print()

    OR :

    from dyools import Consumer
    c = Consumer(host='127.0.0.1', port=5000)
    c.cmdline(['ls','-alh'])
    c.print()

2 - Execute python expressions :

    from dyools import Consumer
    c = Consumer(host='127.0.0.1', port=5000)
    c.add('import os;import sys')
    c.add('dirs = os.listdir();a = 8;b = 10')
    c.add('tbl = {"a": 20, "b": 40}')
    c.console()
    c.print_dirs() #pprint a variable
    c.data_dirs()  #return the value of a variable
    c.table_tbl()
    c.print_b()

    OR :

    from dyools import Consumer
    c = Consumer(host='127.0.0.1', port=5000)
    c.console('b = 33')
    c.print_b()


3 - Get OS stats: disk usage, cpu and memory usage

    from dyools import Consumer
    c = Consumer(host='127.0.0.1', port=5000)
    c.top()    #get a summary of a top command
    c.top(['/tmp', '/bin', '/usr']) #get a summary of a top command with the disk usage of some paths

    """
    Print.info(__consumer.__doc__)


@cli_help.command('convert')
def __convert():
    """Convert: convert data types and time types, units are not case sensible

1 - Convert data types

    from dyools import Convert
    mb = 1024 #variable in megabytes (units: ["B", "K", "M", "G", "T", "P", "E", "Z", "Y"])
    Convert.data(mb, 'mb', 'gb') #=> 1.0 (float)
    Convert.data(mb, 'mb', 'gb', r=2) #=> 1.0 (float) with a round

1 - Convert time types

    from dyools import Convert
    seconds = 3600 #variable in seconds (units: ["MS", "S", "M", "H"])
    Convert.time(seconds, 's', 'm') #=> 60.0 (float)
    Convert.time(seconds, 's', 'h') #=> 1.0 (float)
    Convert.time(seconds, 's', 'h', r=2) #=> 1.0 (float) using a round
    """
    Print.info(__convert.__doc__)


@cli_help.command('odoo_simple_migrate')
def __odoo_simple_migrate():
    """Odoo Simple Migrate: migrate data from odoo to odoo

    from dyools import OdooSimpleMigrate
    remote = RPC()
    local = RPC()
    #or local = Env(env, odoo)
    m = OdooMigrate(local, remote) #from local to remote
    m.migrate('res.partner') #migrate all partner data (all columns except access log), for relational data use xmlid by default
    m.migrate(
        src_model='res.users',
        dest_model='res.partner',
        src_context={},
        dest_context={},
        by=100,      #send 100 by 100
        domain=[],   #migrate records that fit the domain
        limit=1000,  #migrate the first 1000 records
        offset=60,   #migrate from the offset 60
        order='id desc',    #begin with the last created
        fields=['name],     #fields to migrate
        exclude_fields=[],  #exclude some fields
        include_fields=[],  #force include some fields like create_date
        many2one_with_names=[],  #as default is xmlid, it's possible to force using names on some many2one fields
        debug=True,  #print to console the header and data sent to server
    )
    """
    Print.info(__odoo_simple_migrate.__doc__)


@cli_help.command('counter')
def __counter():
    """Counter: compute the time elapsed after an execution

    from dyools import Counter
    c = Counter('A test counter') #the name is optional, automatically the counter is started
    c.start()    #start the counter
    c.restart()  #restart the counter
    c.stop()     #stop the counter
    c.resume()   #resume the counter
    c._get_elapsed_time()   #get a dictionary of data: hours, minutes, seconds and total
    c.to_str(r=True, title='')   #get the string, by default the round is active and title is empty
    c.print(r=True, title='')    #print the string to the console
    """
    Print.info(__counter.__doc__)


@cli_help.command('data')
def __data():
    """Data: a data wrapper

    from dyools import Data
    d = Data(data, has_header=True, header=[], name='__NAME')

Data can be :
    - dictionary of dictionaries (not need for header, the wrapper will compute them, the parent key will mapped with the
    value of name='__NAME')
    - dictionary of values (not need for header, the wrapper will compute them)
    - list of dictionaries (not need for header, the wrapper will compute them)
    - list of lists (has_header=True to specify if the first item is a header else  give a header)
    - list of values (has_header=True to specify if the data is a header else give a header)
    - object (should specify the header to get attributes)


    from dyools import Data
    d = Data(data, has_header=True, header=[], name='__NAME')
    d.get_header()         #return header
    d.get_default_header() #return header if computed else if there are some lines, an index will be generated
    d.get_lines()          #return data lines
    d.get_pretty_table(pretty=True, add_index=False, grep=False, index=False) #return the Prettytable object
    d.get_html()           #get the html
    d.to_list()            #get a list of two list, the first item is the header, the second is the list of lines
    d.to_dictlist()        #get a list of dictionaries
    d.show(pretty=True, add_index=False, grep=False, index=False, header=False, footer=False, exit=False) #print to console
    """
    Print.info(__data.__doc__)


@cli_help.command('date')
def __date():
    """Data: work with string dates
Date accepts string, date and datetime objects as argument and compute the default format
A format can be forced
If not argument is given the value will be the result of datetime.now()

Some global format are :
    - Date.DATETIME_FORMAT      '%Y-%m-%d %H:%M:%S'
    - Date.DATETIME_FR_FORMAT   '%d/%m/%Y %H:%M:%S'
    - Date.DATETIME_HASH_FORMAT '%Y%m%d_%H%M%S'
    - Date.DATE_FORMAT          '%Y-%m-%d'
    - Date.DATE_FR_FORMAT       '%d/%m/%Y'
    - Date.DATE_HASH_FORMAT     '%Y%m%d'

1 - Initialize the object


    from dyools import Date
    d = Date().to_str() #return a string of now format: YYYY-mm-dd HH:MM:SS
    d = Date().to_str(fmt='%Y') #return a string of now format: YYYY
    d = Date(fmt='%Y').to_str() #return a string of now format: YYYY
    d = Date(fmt='%Y').to_str() #return a string of now format: YYYY
    d = Date('2019-01-01').to_str() #return '2019-01-01'
    d = Date(date()).to_str() #return '2019-01-01'
    d = Date(date.today()).to_str() #return a string of today, format: YYYY-mm-dd
    d = Date(datetime.now()).to_str() #return a string of now, format: YYYY-mm-dd HH:MM:SS

2 - Transformation

    from dyools import Date
    d = Date()
    d.relativedelta(days=7, months=-2, years=1, hours=3, minutes=20, seconds=-30) #return a string after transformation
    d.apply(days=7, months=-2, years=1, hours=3, minutes=20, seconds=-30)         #return an object of Str
    d.set_format('%d') #change the default format
    d.last_day()    #return a string of last day format: default format
    d.fist_day()    #return a string of first day format: default format
    d.to_datetime() #return a datetime object
    d.to_date()     #return a date object
    d.to_fr()       #return a string with format Date.DATE_FR_FORMAT if date else Date.DATETIME_FR_FORMAT for datetime
    d.is_between('2019-01-01', date(2030, 3, 1))   #return a boolean if the date is between two date, the arguments will
    convert to Date before comparison

3 - Date range

    for dt in Date.date_range('2010-01-01', date(2030, 1, 23), months=3):
        print(dt)

3 - Operations
    1 - add values to Date: Date('2010-01-01') + '3m'  #=> '2010-04-01' list: ['d','m','y','H','M', 'S']
    2 - compare two objects or with strings Date('2019') > Date('2020') or Date('2019') > '2010-04-01'

    """
    Print.info(__date.__doc__)


@cli_help.command('default_value')
def __default_value():
    """DefaultValue: work with default data on objects

    from dyools import DefaultValue
    obj = type('obj', (object,), {'a': 10, 'b': False})
    dv_obj = DefaultValue(obj) # (obj, defaults={False: '', None: ''}, types=()) #types on which apply the default values
    dv_obj.a == 10   #True
    dv_obj.b == ''   #True
    """
    Print.info(__default_value.__doc__)

@cli_help.command('df')
def __df():
    """DF: a simple dataframe object

    from dyools import DF
    d = DF(index=[0, 1], is_responsible=[True, False])
    d.add('name', ['Jean', 'Luc'])
    d.add('age', [30, 45])
    d.remove('index')
    """
    Print.info(__df.__doc__)


@cli_help.command('serie')
def __serie():
    """Serie: a simple Serie object
Operations:
    - addition
    - subtraction
    - division
    - multiplication

    from dyools import Serie
    s1 = Serie([1, 2, 3])
    s2 = Serie([10, 20, 30])
    s3 = Serie([100, 200, 300])
    s1+s2+s3 #return a Serie object that make a sum of each tuple => <Serie [111, 222, 333]>
    s1[0] #return the first item as a value
    s1[1:-1] #return the first item as a value
    """
    Print.info(__serie.__doc__)


@cli_help.command('env')
def __env():
    """Env: New odoo environment inside odoo shell

    from dyools import Env
    e = Env(env, odoo)
    e = Env(odoo=odoo, dbname='DEMO')
    # Instance operations
    r.dump_db(dest, zip=True)
    r.create_db(dbname=False, with_demo=False, language='fr_FR') #argument is optional
    r.drop_db(dbname=False) #argument is optional
    r.restore_db(path, drop=False)
    r.list_db()
    # Operations
    e.get_addons(self, enterprise=False, core=False, extra=True, addons_path=False) #return tuple of lists (installed, uninstalled)
    addons_path is used to replace the default addons_path
    e.check_uninstalled_modules(self, enterprise=False, core=False, extra=True, addons_path=False) #exit -1 if all selected not installed
    e.info('msg') #e.debug e.warning e.error
    e.set_param('key', 'value')
    e.get_param('key')
    e.read(model, domain=[], limit=False, order=False, fields=[], **kwargs) #arguments are optionals
    e.get(model, domain=[], limit=False, order=False, **kwargs) #get objects (recordset)
    e.update_xmlid(record, xmlid=False) #record should be valid, the function create the xmlid in the database (__import__)
    e.xmlid_to_object(XMLID)
    # Module management
    e.update_list()
    e.install('sale,account')
    e.upgrade('sale')
    e.uninstall('account')
    # Misc
    e.fields(self, model, fields=[])
    e.menus(self, debug=False, xmlid=False, action=False, user=False, crud=False)


    """
    Print.info(__env.__doc__)


@cli_help.command('eval')
def __eval():
    """Eval: evaluate variable in a data structure

    from dyools import Eval
    ctx = {'a': 3}
    data = {'m': [{'{a}': '{a}'}], 'n' : ['{a}', 6]}
    Eval(data, ctx).eval()                   #return {'m': [{3: 3}], 'n': [3, 6]}
    Eval(data, ctx).eval(eval_result=False)  #return {'m': [{'3': '3'}], 'n': ['3', 6]}
    Eval(data, ctx).eval(keep_classes=False) #by default classes founds after evaluation a kept in string
    """
    Print.info(__eval.__doc__)


@cli_help.command('inspect')
def __inspect():
    """Inspect: inspect source code

    from dyools import Inspect, Signature
    import os
    Signature(os.path.isfile)
    Inspect.signature(os.path.isfile)
    Inspect.source(os.path.isfile)
    """
    Print.info(__inspect.__doc__)


@cli_help.command('is')
def __is():
    """Is: test type of a variable
All tests can be forced to raise an exception if it fails

    from dyools import IS
    Is.dict({}) #return True
    Is.dict([]) #return False
    Is.dict([], exception=True) #raise TypeError
    Is.list(txt)
    Is.instance(txt)
    Is.xmlid(txt)
    Is.domain(txt)
    Is.str(txt)
    Is.tuple(txt)
    Is.empty(txt) #if txt is an empty string
    Is.iterable(txt) #return True if txt is not string and has __iter__ methods
    Is.eval(txt, context) #return True the result of Eval(txt, context).eval() is different to txt
    IS.list_or_tuple(arg)
    IS.list_of_list(arg)
    IS.list_of_values(arg)
    IS.list_of_dict(arg)
    IS.dict_of_dict(arg)
    IS.dict_of_values(arg)
    IS.file(arg)
    IS.dir(arg)
    """
    Print.info(__is.__doc__)


@cli_help.command('logger')
def __logger():
    """Logger: log to console using colors if possible

    from dyools import Logger
    Logger.info('test')  #print to console the text using default color
    Logger.info('test', exit=True) #force exit
    Logger.warning('test') #color=yellow
    Logger.debug('test')   #color=blue
    Logger.success('test') #color=green
    Logger.code('test')    #color=cyan
    Logger.error('test')   #color=red default exit=True
    Logger.title('test')   #color=white bold=True

    """
    Print.info(__logger.__doc__)


@cli_help.command('offset_limit')
def __offset_limit():
    """OffsetLimit: generate tuples of offset/limit

    from dyools import OffsetLimit
    for offset, limit in OffsetLimit(0, 2, 7):
        print(offset, limit) #[0, 2] until [6, 1]

    from dyools import OffsetLimit
    for offset, limit in OffsetLimit(0, 2):
        print(offset, limit) #[0, 2] infinite loop

    """
    Print.info(__offset_limit.__doc__)


@cli_help.command('operator')
def __operator():
    """Operator: make operations on data, flat lists, intersection, unique, etc

    from dyools import Operator
    Operator.flat([1, 2, [2], 3])                            # [1, 2, 2, 3]
    Operator.unique([1, 2, 2, 3])                            # [1, 2, 3]
    Operator.split_and_flat(',', '1, 2, 2, 3')               # ['1', ' 2', ' 2', ' 3']
    Operator.intersection([1, 2, 2, 3], [1, 2], [2])         # [2, 2]
    Operator.unique_intersection([1, 2, 2, 3], [1, 2], [2])  # [2]

    """
    Print.info(__operator.__doc__)


@cli_help.command('path')
def __path():
    """Path: tools around files and directories

    from dyools import Path
    with Path.chdir('/tmp'):
        "change temporary the path"
        pass

    with Path.tempdir() as d:
        "d <string> is temporary folder that will be deleted at the end"
        pass

    with Path.tempfile(mode='wb+') as f:
        "f <tempfile> is temporary file created with the mode 'wb+' that will be deleted at the end"
        f.name          # path of the file
        f.write('data') # create some data

    Path.subpaths('/x/y/z/test/txt.txt') # ['/x', '/x/y', '/x/y/z', '/x/y/z/test']
    Path.create_file('file.txt', 'some data', eol=0, mode='wb+') #create the file if not exists, else change the content if different
    and add N 'eof' lines as '\\n'
    Path.read('file.txt', mode='rb')           #read a file
    Path.write('file.txt', 'data', mode='wb+') #write to a file
    Path.home() #return the home folder, full path
    Path.join('p1', 'p2', 'p3', 'file.txt')   #or pass a list
    Path.touch(''/x/y/z/txt.txt')   #create all folders if not exists and touch the file
    Path.create_dir('/x/y/z')       #create folders
    Path.create_parent_dir('/x/y/z')#create parent directory of a path
    Path.clean_dir('/x/y/z')        #remove folders and files under the path
    Path.delete_dir('/x/y/z')       #remove the folder
    Path.remove('/x/y/z')           #remove the folder or the file
    Path.clean_empty_dirs('/x/y/z') #get all directories (recursively) and delete the empty ones, if a folder contains an
    empty folder then it will be deleted also

    Path.size_str('/x/y', 'mb')     # 120 MB  works for folders and files
    Path.size('/x/y/z', 'mb')       # 120     works for folders and files
    Path.find_files('K*R.PY', '/x/y') #return the list of full paths of all python files that begins with K and ends with R
    Path.find_file_path('test.txt', '/tmp') #try to find the file in the current path else, try to look in a specific path
    declaration: find_file_path(path, home=False, raise_if_not_found=False)

    Path.find_dir_path('folder', '/x/y') #like find_file_path but it works for folders
    Path.grep(cls, expressions, files, comment=False) #expressions['dump','print'] files=['file1.txt', 'file2.txt'] comment='#'
    check if there are files that contains one of the expressions, ignore lines that match the comment, expressions and
    comment are regular expressions, this function return dictionary of dictionaries file => expression > line number
    """
    Print.info(__path.__doc__)


@cli_help.command('print')
def __print():
    """Print: print to console, see also 'logger'
Print data with header, footer, total of item and exit if needs, just data is required, other arguments are False

    from dyools import Print, P
    P([])     #shortcut of pprint.pformat
    Print.info('test', header='Title', footer='Summary', total=False, exit=False)  #print to console the text using default color
    Print.info('test', exit=True) #force exit
    Print.success('test') #color=green
    Print.error('test')   #color=red default exit=True
    Print.warning('test') #color=yellow
    Print.debug('test')   #color=cyan
    Print.abort('test')   #color=red default exit=True and text is 'Aborted' if not provided
    """
    Print.info(__print.__doc__)


@cli_help.command('progress_bar')
def __progress_bar():
    """ProgressBar: print the progression of a task

    from dyools import ProgressBar
    P = ProgressBar()
    P.start()
    for i in range(1000):
        i += 1
        P.percent = i / 1000
        P.suffix = 'suffix'
        P.prefix = 'prefix'
        P.update(percent=i / 1000, suffix='suffix', prefix='prefix')
        time.sleep(0.02)
    P.stop()
    # prefix [100 %] suffix
    """
    Print.info(__progress_bar.__doc__)


@cli_help.command('queue')
def __queue():
    """Queue: pipeline implementation
Prepare data and put them to Queue, the queue create N threads got from queue and dispatch data to each thread for processing
It's possible to chain Queues to construct a pipeline

    from dyools import Pipeline
    pipeline = Pipeline()
    pipeline.add_worker(name='Extract', maxsize=4)
    pipeline.add_worker(name='Transform', maxsize=4)
    pipeline.add_worker(name='Load', maxsize=4)
    pipeline.add_worker(name='Error', maxsize=1)
    pipeline.start()
    ...
    pipeline.put(queue_data) #structure of queue_data is [[methods, data], [methods, data], ...]
        methods is a list of chained methods, each methods should have three arguments and return two (the first and the last)
        def process_something(methods, data, pool):
            ...
            pool.append((methods, new_data))
    ...
    pipeline.stop()
    """
    Print.info(__queue.__doc__)


@cli_help.command('random')
def __random():
    """Random: generate some randoms

    from dyools import Random
    Random.uuid()
    Random.base64(10)
    Random.alphanum(12)
    Random.digits(20)
    Random.alpha(80)
    """
    Print.info(__random.__doc__)


@cli_help.command('rpc')
def __rpc():
    """RPC: Odoo API
Some Odoo tools to interact with instances

    from dyools import RPC
    #protocol = 'jsonrpc+ssl' or 'jsonrpc' (default)
    r = RPC(host='localhost', port=8069, dbname='DEMO', user='admin', password='admin', superadminpassword='admin')
    r = RPC(server='http://localhost:8069/?dbname=DEMO&user=admin@password=admin&superadminpassword='admin')
    r = RPC(config_name='NAME', config_file='PATH_TO_DYOOLS.YML') #config_file is optional, see cli_rpc
    r = RPC() #get variables from environments RPC_HOST, RPC_PORT, RPC_DBNAME, RPC_USER, RPC_PASSWORD, etc
    # Instance operations
    r.dump_db(dest, zip=True)  #path can be a directory or a name of configuration from dyools.yml
    r.create_db(dbname=False, with_demo=False, language='fr_FR') #arguments are optionals
    r.drop_db(dbname=False) #argument is optional
    r.restore_db(path, drop=False) #path can be a file path or a name of configuration from dyools.yml
    r.list_db()
    # Operations
    r.login(self, user=False, password=False, dbname=False) #arguments are optionals
    r.info('msg') #r.debug r.warning r.error
    r.set_param('key', 'value')
    r.get_param('key')
    r.read(model, domain=[], limit=False, order=False, fields=[], **kwargs) #arguments are optionals
    r.get(model, domain=[], limit=False, order=False, **kwargs) #get objects (recordset)
    r.update_xmlid(record, xmlid=False) #record should be valid, the function create the xmlid in the database (__import__)
    r.xmlid_to_object(XMLID)
    # Module management
    r.update_list()
    r.install('sale,account')
    r.upgrade('sale')
    r.uninstall('account')
    # Misc
    r.fields(self, model, fields=[])
    r.menus(self, debug=False, xmlid=False, action=False, model=False, domain=False, context=False, user=False, crud=False)


    """
    Print.info(__rpc.__doc__)


@cli_help.command('sample')
def __sample():
    """Sample: generate some sample data
First argument is the number of items, the second is the number of nested items

    from dyools import Sample
    Sample.dict(10)
    Sample.list(20)
    Sample.list_of_alpha(10)
    Sample.list_of_digits(10)
    Sample.list_of_dicts(6, 4)
    Sample.dict_of_lists(6, 4)
    Sample.dict_of_ints(6, 4)
    """
    Print.info(__sample.__doc__)


@cli_help.command('sftp')
def __sftp():
    """SFTP: tools for paramiko SFTP instance

    from dyools import SFTP
    with SFTP(sftp_instance).chdir('/tmp'):
        ...
    """
    Print.info(__sftp.__doc__)


@cli_help.command('slice')
def __slice():
    """Slice: slice iterable object

    from dyools import Slice
    s = [1, 2, 3, 4, 5, 6]
    for item in Slice(s, 3):
        print(item) #[1, 2, 3]

    from dyools import Slice
    s = [1, 2, 3, 4, 5, 6, 7]
    for item, p in Slice(s, 3, with_percent=True):
        print(item, p) #[1, 2, 3] 0.42857142857142855

    """
    Print.info(__slice.__doc__)


@cli_help.command('str')
def __str():
    """Str: tools for string management
An Str instance can accept a numeric value to make some specific format

    from dyools import Str
    Str('  &tés °ma_').to_code()         #'TES_MA'
    Str('.te..xt.').dot_to_underscore()  #'_te__xt_'
    Str(' test1 test2 ').to_title()      #'Test1 Test2'
    Str(' test1 test2 ').remove_spaces() #'test1test2'
    Str('text').replace(dict(z=['t','x'], x='e') #'zxzz'
    Str(2300000, precision=2, numeric=True).with_separator(sep='_', nbr=3, rtl=True) #'2_300_000'
    Str('2300000.0', precision=2, numeric=True).with_separator(sep='_', nbr=3, rtl=True) #'2_300_000.00'
    Str('up').case_combinations()        #['Up', 'up', 'uP', 'UP']
    Str('téxt').remove_accents()         #'text'
    Str('te1.8 9xt').to_number()         #1.89 pass ttype=str to get a string
    Str('te1.8 9xt').get_first_number()  #1.8  force the type with ttype
    Str('te1.8 9xt').get_last_number()   #9.0  force the type with ttype
    Str('weight 1-89 kg').to_range()     #(1.0, 89.0) force the type with ttype
    Str('weight >89 kg').to_range()      #(89.01, 99999)
    Str('weight 20-*-40 kg').to_range(ttype=int, min_number=10, max_number=100, separators=['*','-'])
    Str('weight <40 kg').to_range(ttype=int, min_number=10, max_number=100) #(10, 39)
    Str('weight <40 kg').to_range(ttype=int, min_number=10, max_number=100, or_equal=True) #(10, 40)
    Str('text').to_str()                 #'text'
    Str('te xt').is_equal('TEXT')        #True remove space and strip and compare the lowercase of the two strings

    """
    Print.info(__str.__doc__)


@cli_help.command('table')
def __table():
    """Table: a wrapper around list of lists, remove columns and rows and flat data to make the iterations
Accept a data like [['', 'name','age'], [1, 'John',30], [2, 'Luc',28]]

    from dyools import Table
    tbl = Table([['id', 'name','age'], [1, 'John',30], [2, 'Luc',28]])
    tbl.set_row_index([0])
    tbl.set_col_index([0])
    tbl.get_flat()             #[['name', 1, 'John'], ['name', 2, 'Luc'], ['age', 1, 30], ['age', 2, 28]]
    tbl.get_data()             #[['id', 'name', 'age'], [1, 'John', 30], [2, 'Luc', 28]]
    tbl.get_rows([0, 1])   #[['id', 'name', 'age'], [1, 'John', 30]]
    tbl.get_columns([1, 2])    #[['name', 'John', 'Luc'], ['age', 30, 28]]
    tbl[1:1] #'John'
    tbl.ncols                  #3
    tbl.nrows                  #3
    tbl.remove_cols([2])
    tbl.remove_rows([2])
    tbl.get_flat()             #[['name', 1, 'John']]
    """
    Print.info(__table.__doc__)


@cli_help.command('tool')
def __tool():
    """Tool: some tools to redirect stdout/stdin, protect attributes/items and construct an Odoo domain from a string

    from dyools import Tool

    Tool.encrypt('message', 'password')
    Tool.decrypt('xxxx', 'password')

    output = {}
    with Tool.stdout_in_memory(output):
        print('test')
    print(output)   #{'data': 'test\n'}

    class O(object):
        pass
    o = O()
    o.a, o.b = 10, 20
    with Tool.protecting_attributes(o, attrs=['a','b']):
        o.a, o.b = 0, 1
        print(o.a, o.b)       #0 1
    print(o.a, o.b)           #10 20

    l = ['a', 'b', 'c', 1, 2, 3]
    with Tool.protecting_items(l, items=[0, 1]):
        l[0], l[1] = 'x', 'y'
        print(l)               #['x', 'y', 'c', 1, 2, 3]
    print(l)                   #['a', 'b', 'c', 1, 2, 3]

    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
    with Tool.protecting_items(d, items=['a', 'b']):
        d['a'], d['b'] = 20, 30
        print(d)                #{'a': 20, 'b': 30, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
    print(d)                    #{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}

    Tool.construct_domain_from_str('id = 1 and name = "Test"') #['&', ('id', '=', 1), ('name', '=', 'Test')]
    """
    Print.info(__tool.__doc__)


@cli_help.command('ws')
def __ws():
    """WS: a method to launch a python webservice based on Flask

    from dyools import WS
    ws = WS(port=5000, env=None, host='0.0.0.0', token=None, name=None, ctx={}, **kwargs)
    ws.start() #start the webservice
    ws.stop()  #stop the server or get url /shutdown
    #see 'consumer' for more details
    """
    Print.info(__ws.__doc__)


@cli_help.command('xlsreader')
def __xlsreader():
    """XlsReader: export tables from an Excel file

    from dyools import XlsReader
    xls = XlsReader('example.xls', sheets=['Sheet1'], options={'formatting_info':True)} #sheets and options (xlrd) are optional
    xls = XlsReader('example.xls', right_bottom=True} #if the first cell is empty
    xls.get_data()   #get a dictionary, keys are name of sheets, values are content
    xls.get_tables() #get a dictionary, keys are name of sheets, values are tables
    """
    Print.info(__xlsreader.__doc__)


@cli_help.command('xlswriterr')
def __xlswriterr():
    """XlsWriter: create and excel file

    from dyools import XlsWriter
    xls = XlsWriter(filename='example.xlsx', options={}) #filename is optional, options are xlsxwriter workbook options
    xls.set_sheet('NAMES')        #if default sheet rename it else create a new one
    xls.add_header(['NAME'])
    xls.add_line(['John'])
    xls.add_line(['Luc'])
    xls.set_sheet('Data')         #if default sheet rename it else create a new one
    xls.set_offset(3, 3)          #set the offset of table
    xls.add_header(['ID','NAME','AGE'])
    xls.add_line(['1','John',20])
    xls.add_line(['2','Luc',24])
    xls.add_footer('AGE', 'avg')  #or xls.add_footer(2, 'avg') operators: min/max/avg/sum
    xls.add_footer_name('AVERAGE')
    xls.get()                     #get the workbook data, can be writen directly to a file
    xls.save()                    #save the file, xls.save('/tmp/file.xlsx')
    """
    Print.info(__xlswriterr.__doc__)


@cli_help.command('xml')
def __xml():
    """XML: work with XML architecture

    from dyools import Xml
    xml = Xml('<div name="first_div">Text</div>')
    xml.nodes()         #return XmlNode apply attrib(attr, value) or text(txt)
    xml.nodes().attrib('name', 'not_first_div')
    xml.nodes().text('Text 2)
    xml.to_string()     #'<div name="not_first_div">Text 2</div>'
    xml.pretty()        #'<div name="not_first_div">Text 2</div>'
    xml.get_xpath_expr('div', name='not_first_div') #['//div[@name="not_first_div"]']
    xml.expr_with_arch('div', name='not_first_div') #[['Xpath', '//div[@name="not_first_div"]'], ['Expression', '///div[@name="not_first_div"]'], ['Architecture', '<div name="not_first_div">Text 2</div>']]
    xml.xpath('div', name='not_first_div') #[b'<div name="not_first_div">Text 2</div>']
    xml.expr('div', name='not_first_div')  #[['Xpath', '//div[@name="not_first_div"]'], ['Expression', '///div[@name="not_first_div"]']]
    xml = Xml('<div name="parent_div"><div name="first_div">Text</div></div>')
    xml.query('div', 'name') #[['parent_div', 'parent_div', 'div'], ['first_div', 'parent_div.first_div', 'div.div']]
    xml.query('div', 'name', only_parent=True)      #[['parent_div', 'parent_div', 'div']]
    xml.query('div', 'name', child_of='parent_div') #[['first_div', 'parent_div.first_div', '']]
    xml.query('div', 'name', under='span')          #[]
    #full declaration xml.query(tag, attr, attrs={}, only_parent=False, child_of=False, under=False)
    """
    Print.info(__xml.__doc__)


@cli_help.command('yamlconfig')
def __yamlconfig():
    """YamlConfig: work with yaml file configuration

    from dyools import YamlConfig
    yml = YamlConfig('config.yml')
    yml = YamlConfig('config.yml', defaults={'port': 8069}, create_if_not_exists=True, many=False)
    yml.get_data() #{}
    yml.add('server1', name='Server A', port=8000) #the first item is the keys, the others are parameters
    yml.add('server2', name='Server B', is_ok=False)
    yml.get_data() #{'server1': {'port': 8000, 'name': 'Server A'}, 'server2': {'port': 8069, 'name': 'Server B', 'is_ok': False}}
    yml.get_values()                #{}
    yml.get_values(_name='server1') #{'port': 8000, 'name': 'Server A'}
    yml.get_values(server=8000) #{}
    yml.get(_name='server1')  #{'server1': {'port': 8000, 'name': 'Server A'}}
    yml.get_list() #[{'name': 'Server A', 'port': 8000}, {'name': 'Server B', 'port': 8069, 'is_ok': False}]
    yml.delete(_name='server1')
    yml.dump()  #save data to file
    yml.set_data({}) #erase data
    """
    Print.info(__yamlconfig.__doc__)
