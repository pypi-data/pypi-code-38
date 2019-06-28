import os
import re
import types
import sys
import traceback
from io import StringIO
#from multiprocessing import Process, Queue
from billiard import Process, Queue
from commandRunner import commandRunner
from subprocess import Popen
from subprocess import PIPE

# runs a dialect of python where escapes must be doubled \\n etc...


class pythonRunner(commandRunner.commandRunner):

    def __init__(self, **kwargs):
        commandRunner.commandRunner.__init__(self, **kwargs)
        self.script = ""
        self.script_header = ""
        self.script_footer = ""
        self.compiled_script = None

        if isinstance(kwargs['script'], str):
            self.script = kwargs.pop('script', '')
        else:
            raise TypeError('script must be a string')

    def prepare(self):
        '''
            override the default prepare to add some bits of code to
            provide the input, output filehandles and param as variables
        '''
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if self.input_data is not None:
            for key in self.input_data.keys():
                file_path = self.path+key
                fh = open(file_path, 'w')
                fh.write(self.input_data[key])
                fh.close()

        self.script_header += "import os\nos.chdir('"+self.path+"')\n"
        # files have been written to the tmp space, now we create python
        # commands to open them in the script
        in_dir = sorted(os.listdir(self.path))
        for i, this_glob in enumerate(self.in_globs):
            for infile in in_dir:
                if infile.endswith(this_glob):
                    self.script_header += "I"+str(i+1)+" = open('" +\
                                          infile+"', 'r')\n"
                    self.script_footer += "I"+str(i+1)+".close()\n"

        # now we open a set of files for the outglobs, given the identifier
        #
        for i, this_glob in enumerate(self.out_globs):
            self.script_header += \
                   "O"+str(i+1)+" = open('"+self.tmp_id+this_glob+"', 'w')\n"
            self.script_footer += "O"+str(i+1)+".close()\n"

        # create the params that are passed in
        for i, this_param in enumerate(self.params):
            if this_param in self.param_values:
                self.script_header += "P"+str(i+1)+" = {'"+this_param+"': '" +\
                                      self.param_values[this_param]['value'] +\
                                      "'}\n"
            else:
                self.script_header += "P"+str(i+1)+" = True\n"

        if self.env_vars is not None:
            for key in sorted(self.env_vars):
                self.script_header += "os.environ['"+key+"'] = '" +\
                                       self.env_vars[key]+"'\n"

        # having prepped the header elements we prepend them to the provided
        # script
        self.script = self.script.replace("\r", '')
        self.script = self.script_header+self.script+"\n"+self.script_footer
        try:
            self.compiled_script = compile(self.script, self.tmp_id+".py",
                                           "exec")
        except SyntaxError as e:
            raise SyntaxError("Could not compile provided script. "
                              "Check syntax")
        except Exception as e:
            raise Exception("Script could not compile")

    def exec_code(self, stdoq, stdeq):
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        error_string = ''
        try:
            exec(self.compiled_script)
        except Exception as e:
            # if the script fails here makes sure we close all the file handles
            # before returning to the parent process
            exec(self.script_footer)
            error_string = traceback.format_exc()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        stdoq.put(stdout_buffer.getvalue())
        error_string += stderr_buffer.getvalue()
        stdeq.put(error_string)

    def run_cmd(self):
        '''
            run the command we constructed when the object was initialised.
            If exit is 0 then pass back if not decide what to do next. (try
            again?)
        '''
        self.output_data = {}
        try:
            stdout_queue = Queue()
            stderr_queue = Queue()
            p = Process(target=self.exec_code,
                        args=(stdout_queue, stderr_queue))
            p.start()
            p.join()

            self.output_data[self.std_out_str] = stdout_queue.get().encode()
            self.output_data[self.tmp_id+".stderr"] = \
                stderr_queue.get().encode()

        except Exception as e:
            raise Exception("Unable to call child process:"+str(e))

        output_dir = os.listdir(self.path)
        for this_glob in self.out_globs:
            for outfile in output_dir:
                if outfile.endswith(this_glob):
                    os.chmod(self.path+outfile, 0o666)
                    with open(self.path+outfile, 'rb') as content_file:
                        content = content_file.read()
                        if len(content) > 0:
                            self.output_data[outfile] = content

        if self.std_out_str is not None and os.path.isfile(self.std_out_str):
            os.chmod(self.std_out_str, 0o666)

        return(0)
