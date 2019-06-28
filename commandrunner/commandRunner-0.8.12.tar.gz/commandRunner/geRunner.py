import os
import re
import types
import drmaa
from commandRunner import commandRunner


class geRunner(commandRunner.commandRunner):

    def __init__(self, **kwargs):
        commandRunner.commandRunner.__init__(self, **kwargs)

    def run_cmd(self, success_params=[0]):
        '''
            run the command we constructed when the object was initialised.
            If exit is 0 then pass back if not decide what to do next. (try
            again?)
        '''
        retval = None
        try:
            with drmaa.Session() as s:
                jt = s.createJobTemplate()
                jt.workingDirectory = self.path
                jt.jobEnvironment = self.env_vars
                jt.outputPath = ":"+self.std_out_str
                jt.remoteCommand = self.command_token
                jt.args = self.ge_params
                jt.joinFiles = False

                jobid = s.runJob(jt)

                retval = s.wait(jobid, drmaa.Session.TIMEOUT_WAIT_FOREVER)
                s.deleteJobTemplate(jt)
        except Exception as e:
            raise OSError("DRMAA session failed to execute: " + str(e))

        output_dir = os.listdir(self.path)

        if retval.exitStatus not in success_params:
            raise OSError("Exit status" + str(retval))

        self.output_data = {}
        for this_glob in self.out_globs:
            for outfile in output_dir:
                if outfile.endswith(this_glob):
                    os.chmod(self.path+outfile, 0o666)
                    with open(self.path+outfile, 'rb') as content_file:
                        self.output_data[outfile] = content_file.read()

        if self.std_out_str is not None and os.path.isfile(self.path+"/"+self.std_out_str):
            os.chmod(self.path+"/"+self.std_out_str, 0o666)

        return(retval.exitStatus)
