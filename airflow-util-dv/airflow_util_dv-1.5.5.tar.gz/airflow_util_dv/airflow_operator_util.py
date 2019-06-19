import pipes
import signal
import subprocess
from subprocess import Popen, STDOUT, PIPE
from tempfile import gettempdir, NamedTemporaryFile

from builtins import bytes
from builtins import str
from airflow.exceptions import AirflowException
from airflow.utils.file import TemporaryDirectory
from airflow.utils.operator_helpers import context_to_airflow_vars
import os
from airflow.utils.decorators import apply_defaults
from airflow.hooks.oracle_hook import OracleHook
from airflow.models import BaseOperator
from airflow.operators.sensors import BaseSensorOperator
import re
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
home = os.path.dirname(os.path.realpath(__file__))
path_flag = home


class OracleOperator(BaseOperator):
    """
     Executes sql code in a specific Oracle database

     :param sql: the sql code to be executed. (templated)
     :type sql: Can receive a str representing a sql statement,
         a list of str (sql statements), or reference to a template file.
         Template reference are recognized by str ending in '.sql'
     :param oracle_conn_id: reference to a specific Oracle database
     :type oracle_conn_id: str
     :param parameters: (optional) the parameters to render the SQL query with.
     :type parameters: mapping or iterable
     :param autocommit: if True, each command is automatically committed.
         (default value: False)
     :type autocommit: bool
     """
    template_fields = ('sql',)
    template_ext = ('.sql',)
    ui_color = '#ededed'

    @apply_defaults
    def __init__(
            self, sql, oracle_conn_id='oracle_default', parameters=None,
            task_name=None,
            flag=None,
            autocommit=False, *args, **kwargs):
        super(OracleOperator, self).__init__(*args, **kwargs)
        self.oracle_conn_id = oracle_conn_id
        self.sql = sql
        self.autocommit = autocommit
        self.parameters = parameters
        self.flag = flag
        self.task_name = task_name


class PythonOperator(BaseOperator):
    template_fields = ('templates_dict',)
    template_ext = tuple()
    ui_color = '#ffefeb'

    # since we won't mutate the arguments, we should just do the shallow copy
    # there are some cases we can't deepcopy the objects(e.g protobuf).
    shallow_copy_attrs = ('python_callable', 'op_kwargs',)

    @apply_defaults
    def __init__(
            self,
            python_callable,
            op_args=None,
            op_kwargs=None,
            provide_context=False,
            templates_dict=None,
            templates_exts=None,
            task_name=None,
            flag=None,
            *args, **kwargs):
        super(PythonOperator, self).__init__(*args, **kwargs)
        if not callable(python_callable):
            raise AirflowException('`python_callable` param must be callable')
        self.python_callable = python_callable
        self.op_args = op_args or []
        self.op_kwargs = op_kwargs or {}
        self.provide_context = provide_context
        self.templates_dict = templates_dict
        self.flag = flag
        self.task_name = task_name
        if templates_exts:
            self.template_ext = templates_exts

    def execute(self, context):
        try:
            # Export context to make it available for callables to use.
            airflow_context_vars = context_to_airflow_vars(context, in_env_var_format=True)
            self.log.info("Exporting the following env vars:\n" +
                          '\n'.join(["{}={}".format(k, v)
                                     for k, v in airflow_context_vars.items()]))
            os.environ.update(airflow_context_vars)

            if self.provide_context:
                context.update(self.op_kwargs)
                context['templates_dict'] = self.templates_dict
                self.op_kwargs = context

            return_value = self.execute_callable()
            self.log.info("Done. Returned value was: %s", return_value)
            return return_value
        except Exception as e:
            with open(str(path_flag + self.flag + ".txt"), mode='a', encoding='utf-8') as f:
                f.write(self.flag + " " + str(self.task_name) + " run failed !!!!!\n")
                f.write("error is " + str(e) + "\n")
                f.close()
                raise Exception

    def execute_callable(self):
        return self.python_callable(*self.op_args, **self.op_kwargs)


class BashOperator(BaseOperator):
        template_fields = ('bash_command', 'env')
        template_ext = ('.sh', '.bash',)
        ui_color = '#f0ede4'

        @apply_defaults
        def __init__(
                self,
                bash_command,
                xcom_push=False,
                env=None,
                output_encoding='utf-8',
                task_name=None,
                flag=None,
                *args, **kwargs):

            super(BashOperator, self).__init__(*args, **kwargs)
            self.bash_command = bash_command
            self.env = env
            self.xcom_push_flag = xcom_push
            self.output_encoding = output_encoding
            self.flag = flag
            self.task_name = task_name

        def execute(self, context):
            try:
                """
                Execute the bash command in a temporary directory
                which will be cleaned afterwards
                """
                self.log.info("Tmp dir root location: \n %s", gettempdir())

                # Prepare env for child process.
                if self.env is None:
                    self.env = os.environ.copy()
                airflow_context_vars = context_to_airflow_vars(context, in_env_var_format=True)
                self.log.info("Exporting the following env vars:\n" +
                              '\n'.join(["{}={}".format(k, v)
                                         for k, v in
                                         airflow_context_vars.items()]))
                self.env.update(airflow_context_vars)

                self.lineage_data = self.bash_command

                with TemporaryDirectory(prefix='airflowtmp') as tmp_dir:
                    with NamedTemporaryFile(dir=tmp_dir, prefix=self.task_id) as f:

                        f.write(bytes(self.bash_command, 'utf_8'))
                        f.flush()
                        fname = f.name
                        script_location = os.path.abspath(fname)
                        self.log.info(
                            "Temporary script location: %s",
                            script_location
                        )

                        def pre_exec():
                            # Restore default signal disposition and invoke setsid
                            for sig in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                                if hasattr(signal, sig):
                                    signal.signal(getattr(signal, sig), signal.SIG_DFL)
                            os.setsid()
                        self.log.info("Running command: %s", self.bash_command)
                        sp = Popen(
                            ['bash', fname],
                            stdout=PIPE, stderr=STDOUT,
                            cwd=tmp_dir, env=self.env,
                            preexec_fn=pre_exec)
                        self.sp = sp
                        self.log.info("Output:")
                        line = ''
                        for line in iter(sp.stdout.readline, b''):
                            line = line.decode(self.output_encoding).rstrip()
                            self.log.info(line)
                        sp.wait()
                        self.log.info(
                            "Command exited with return code %s",
                            sp.returncode
                        )

                        if sp.returncode:
                            raise AirflowException("Bash command failed")

                if self.xcom_push_flag:
                    return line
            except Exception as e:
                self.log.info("exec throw a exception " + str(e))
                with open(str(path_flag+self.flag+".txt"), mode='a', encoding='utf-8') as f:
                    f.write(self.flag + " " + str(self.task_name) + " run failed !!!!!\n")
                    f.write("error is " + str(e) + "\n")
                    f.close()
                    raise Exception

        def on_kill(self):
            self.log.info('Sending SIGTERM signal to bash process group')
            os.killpg(os.getpgid(self.sp.pid), signal.SIGTERM)


class FileOracleOperator(BaseOperator):
    """
    Executes sql code in a specific Oracle database

    :param sql: the sql code to be executed. (templated)
    :type sql: Can receive a str representing a sql statement,
        a list of str (sql statemen   ts), or reference to a template file.
        Template reference are recognized by str ending in '.sql'
    :param oracle_conn_id: reference to a specific Oracle database
    :type oracle_conn_id: str
    :param parameters: (optional) the parameters to render the SQL query with.
    :type parameters: mapping or iterable
    :param autocommit: if True, each command is automatically committed.
        (default value: False)
    :type autocommit: bool
    """

    template_fields = ('sql',)
    template_ext = ('.sql',)
    ui_color = '#ededed'

    @apply_defaults
    def __init__(
            self, file, oracle_conn_id='oracle_default', parameters=None,
            autocommit=False, *args, **kwargs):
        super(FileOracleOperator, self).__init__(*args, **kwargs)
        self.oracle_conn_id = oracle_conn_id
        self.sql_file = file
        self.sql = ''
        self.autocommit = autocommit
        self.parameters = parameters

    def execute(self, context):
        try:
            self.sql = return_sql(self.sql_file)
            self.log.info('Executing: %s', self.sql)
            hook = OracleHook(oracle_conn_id=self.oracle_conn_id)
            hook.run(
                self.sql,
                autocommit=self.autocommit,
                parameters=self.parameters)
        except Exception as e:
            raise e


def return_sql(sql_name, need_chinese=True):
    r"""
    return sql list
    :param sql_path:
    :param sql_name:
    :param need_chinese:
    :return:
    """
    try:
        sql_file_name = sql_name
        sql_file_path = os.path.join(sql_file_name)

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
    except Exception as e:
       print("exec throw a exception " + str(e))


