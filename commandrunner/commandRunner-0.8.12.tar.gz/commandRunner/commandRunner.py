import os
import re
import types
from subprocess import call
import shutil

class commandRunner():

    def __init__(self, **kwargs):
        '''
            Constructs a local job
            takes
            tmp_id = string
            tmp_path="/tmp/"
            command="ls /tmp > $OUTPUT"

            in_globs['.file', ]
            out_globs=['.file', ]
            input_data={filename:data_string}
            params = ['string', ]
            param_values = {'string': {'value': string,
                                       'spacing': True|False,
                                       'switchless': True|False}}
            identifier = "string"
            std_out_string="str.stdout"
            env_vars = {name:value}
            value_string="stuffForCommandline
            debug=[True|False]"
        '''
        self.tmp_id = None  # an id for the task, will be used a dir name for
        # the process
        self.tmp_path = None  # the parent path for the process /tmp is useful
        self.in_globs = []  # list of file endings presemt in input_data
        self.out_globs = []  # a list of file endings you are promising will
        # be produced
        self.command = None  # a bash command for local and ge runners
        self.input_data = None  # dict of file name:data pairs
        self.tokens = []  # each part of the comman divided on space
        self.ge_tokens = []  # set of tokens for ge RUnner (exclueds the exe)
        self.identifier = None  # this is for command interpolation

        self.value_string = None  # an arbitrary string used for $VALUE
        # interpolation
        self.params = []  # a list of param values for interpolation
        # (P1, P2 etc.)
        self.param_values = {}  # a dict of config values for params
        self.output_data = None  # a putative dict that will hold the file
        # data out_globs promises
        self.path = None  # builds a dir name using tmp_path and tmp_id
        self.std_out_str = None  # the name of a file that holds the contents
        # of stdout
        self.env_vars = None  # a dict of name:str pairs for bash env vars
        self.debug = False # in debug mode the tmp directory made is world r/w

        self.__check_arguments(kwargs)

        self.tmp_path = re.sub("/$", '', self.tmp_path)
        self.path = self.tmp_path+"/"+self.tmp_id+"/"
        self.current_umask = 146

        if self.command:
            self.command = self._translate_command(self.command)

    def __check_arguments(self, kwargs):
        # flags = (strings,)
        if os.path.isdir(kwargs['tmp_path']):
            self.tmp_path = kwargs.pop('tmp_path', '')
        else:
            raise OSError('tmp_path provided does not exist')

        if isinstance(kwargs['tmp_id'], str):
            self.tmp_id = kwargs.pop('tmp_id', '')
        else:
            raise TypeError('tmp_id must be a string')

        if 'command' in kwargs:
            if isinstance(kwargs['command'], str):
                self.command = kwargs.pop('command', '')
            else:
                raise TypeError('command must be a string')

        if 'identifier' in kwargs:
            if isinstance(kwargs['identifier'], str):
                self.identifier = kwargs.pop('identifier', '')
            else:
                raise TypeError('identifier must be a str')

        if 'std_out_str' in kwargs:
            if isinstance(kwargs['std_out_str'], str):
                self.std_out_str = kwargs.pop('std_out_str', '')
            else:
                raise TypeError('std_out_str must be a str')

        if 'input_data' in kwargs:
            if isinstance(kwargs['input_data'], dict):
                self.input_data = kwargs.pop('input_data', '')
            else:
                raise TypeError('input_data must be a dict')

        if 'out_globs' in kwargs:
            if isinstance(kwargs['out_globs'], list):
                self.out_globs = kwargs.pop('out_globs', '')
            else:
                raise TypeError('out_globs must be list')

        if 'in_globs' in kwargs:
            if isinstance(kwargs['in_globs'], list):
                self.in_globs = kwargs.pop('in_globs', '')
            else:
                raise TypeError('in_globs must be list')

        if 'value_string' in kwargs:
            if isinstance(kwargs['value_string'], str):
                self.value_string = kwargs.pop('value_string', '')
            else:
                raise TypeError('value_string must be str')

        if 'env_vars' in kwargs:
            if isinstance(kwargs['env_vars'], dict):
                self.env_vars = kwargs.pop('env_vars', '')
            else:
                raise TypeError('env_vars must be dict')
            if not all(isinstance(x, str) for x in self.env_vars.keys()):
                raise TypeError('env_vars keys must be strings')
            if not all(isinstance(x, str) for x in self.env_vars.values()):
                raise TypeError('env_vars values must be strings')

        if 'params' in kwargs:
            if isinstance(kwargs['params'], list):
                self.params = kwargs.pop('params', '')
            else:
                raise TypeError('params must be list')

        if 'param_values' in kwargs:
            if isinstance(kwargs['param_values'], dict):
                self.param_values = kwargs.pop('param_values', '')
            else:
                raise TypeError('param_values must be dict')

        if 'debug' in kwargs:
            if isinstance(kwargs['debug'], bool):
                self.debug = kwargs.pop('debug', '')
            else:
                raise TypeError('debug must be bool')

        if len(self.param_values) > 0:
            if not all(isinstance(x, dict) for x in self.param_values.values()):
                raise TypeError('param_values does not contain key:dict')
            param_keys = ['value', 'spacing', 'switchless']
            for i, param_dict in self.param_values.items():
                if not set(param_keys).issubset(set(param_dict)):
                    raise ValueError(str(i)+" : param_values missing config "
                                     "details")
                if not isinstance(param_dict['value'], str):
                    raise TypeError('param_values "value" provided is not '
                                    'string')
                if not isinstance(param_dict['switchless'], bool):
                    raise TypeError('param_values "switchless" provided is not '
                                    'boolean')
                if not isinstance(param_dict['spacing'], bool):
                    raise TypeError('param_values "spacing" provided is not '
                                    'boolean')

        if self.command:
            if ">" in self.command:
                raise ValueError("Command string provides stdout redirection"
                                 ", please provide std_out_str instead")
            if "$TMP" in self.command and self.tmp_path is None:
                raise ValueError("Command string references $TMP but no "
                                 "tmp_path provided")
            if "$VALUE" in self.command and self.value_string is None:
                raise ValueError("Command string references $VALUE but no "
                                 "value_string provided")
            if "$ID" in self.command and self.identifier is None:
                raise ValueError("Command string references $ID but no "
                                 "identifier provided")

    def _translate_command(self, command):
        '''
            takes the command string and substitutes the relevant files names
        '''
        self.tokens = command.split()

        for idx, p in enumerate(self.params):
            identifier = "$P"+str(idx+1)
            if p in self.param_values:
                options = self.param_values[p]
                value = ''
                if options['switchless']:
                    value = options['value']
                else:
                    value = p
                    if options['spacing']:
                        value += ' '
                    value += options['value']
                self.tokens = [a.replace(identifier, value) for a in self.tokens]
            else:
                self.tokens = [a.replace(identifier, p) for a in self.tokens]
        for idx, i in enumerate(self.in_globs):
            file_name = self.tmp_id+i
            identifier = "$I"+str(idx+1)
            self.tokens = [a.replace(identifier, file_name) for a in self.tokens]
        for idx, o in enumerate(self.out_globs):
            file_name = self.tmp_id+o
            identifier = "$O"+str(idx+1)
            self.tokens = [a.replace(identifier, file_name) for a in self.tokens]

        if self.value_string is not None:
            self.tokens = [a.replace('$VALUE', self.value_string) for a in self.tokens]
        if self.identifier is not None:
            self.tokens = [a.replace('$ID', self.identifier) for a in self.tokens]
        if self.tmp_path is not None:
            self.tokens = [a.replace('$TMP', self.tmp_path) for a in self.tokens]

        self.ge_params = self.tokens[1:]
        self.command_token = self.tokens[0]
        if self.std_out_str is not None:
            self.tokens.extend([">", self.std_out_str])

        command_string = ' '.join(self.tokens)
        return(command_string)

    def prepare(self):
        '''
            Makes a directory and then moves the input data file there
        '''
        if not os.path.exists(self.path):
            if self.debug:
                self.current_umask = os.umask(0O000)
                os.makedirs(self.path)
            else:
                os.makedirs(self.path)

        if self.input_data is not None:
            for key in self.input_data.keys():
                file_path = self.path+key
                fh = None
                if type(self.input_data[key]) is str:
                    fh = open(file_path, 'w')
                else:
                    fh = open(file_path, 'wb')
                fh.write(self.input_data[key])
                fh.close()

    def run_cmd(self):
        '''
            run the command we constructed when the object was initialised.
            If exit is 0 then pass back if not decide what to do next. (try
            again?)
        '''
        raise NotImplementedError

    def tidy(self):
        '''
            Delete everything in the tmp dir and then remove the temp dir
        '''
        shutil.rmtree(self.path)
        if self.debug:
            os.umask(self.current_umask)
