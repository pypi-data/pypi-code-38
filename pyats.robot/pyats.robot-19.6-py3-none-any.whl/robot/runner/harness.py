import os
import pathlib

from robot.run import RobotFramework

class RobotHarness(RobotFramework):
    '''
    Robot Framework harness for Easypy. This class adapts RobotFramework to be
    able to run under Easypy, consolidating the results together into a typical
    Easypy report along with other suites.

    Behaviors:
        - if --testbed-file option is provided to easypy, sets the TESTBED
          environment variable
    '''
    def run(self, testable, testreporter, runtime, **options):

        # use our custom listener
        options.setdefault('listener', testreporter)

        # create the output directory for this script under runinfo dir
        script_name = pathlib.Path(testable).name
        script_logdir = pathlib.Path(runtime.directory)/script_name
        script_logdir.mkdir()
        options.setdefault('outputdir', str(script_logdir))

        # set the testbed environment variable
        try:
            os.environ['TESTBED'] = runtime.testbed.testbed_file
        except Exception:
            # we may not always have a testbed - if so, ignore
            pass

        # run the suite as expected
        self.execute(testable, **options)
