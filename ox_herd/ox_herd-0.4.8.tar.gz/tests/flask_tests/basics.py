"""Basic tests using flask.
"""

import logging

from seleniumbase import BaseCase


DO_CLEANUP_FILES = True


class TestWithServer(BaseCase):

    server_info = None
    dead_server = None
    cleanup_files = []
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            cls.risky_set_up_class()
        except Exception as problem:  # pylint: disable=broad-except
            logging.warning('In %s.setUpClass, got problem %s',
                            cls.__name__, problem)
            logging.warning('Will force calling tearDownClass then re-raise')
            cls.tearDownClass()
            raise

        
    @classmethod
    def risky_set_up_class(cls):
        """Heper to setup stuff in the class.

We break this function out of setUpClass and call it `risky` because
it could fail with an exception. In that case, we want the calling
function (usually setUpClass) to still call tearDownClass in case
things got partially setup.
        """
        cls.server_info = cls.setup_server(cls.cleanup_files)
        cls.emp_port = cls.server_info.port

    @classmethod
    def setup_server(
            debug='1',      # Useful in debugging tests.
            reloader='0'):  # Use reload 0 to prevent flask weirdness
            
    """Start flask server.

    :param debug='1':     Whether to run in debug mode.

    :param reloader='0':  Whether to use reloader in server. Often this
                          causes problems so it is best not to.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :return:  Instance of ServerInfo containing information about the
              server we started.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Use python subprocess module to start an instance of the
              server in the background. You can use the returned
              ServerInfo instance to interact with the server. This is
              useful for making the test self-contained.

              You can call kill_server to cleanup or restart_server
              if you want to restart during interactive testing.
    """
    cwd = cwd if cwd else os.path.join(os.path.dirname(apps.__file__), 'mngr')
    emp_port = emp_port if emp_port else str(find_free_port())
    cmd = [sys.executable, 'manage.py', 'web',
           '-d', str(debug), '-r', str(reloader),
           '-e', '1', '--port', emp_port]
    server = run_cmd(cmd=cmd, cwd=cwd, timeout=-4)
    return ServerInfo(server, int(emp_port), emp_settings)
        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        if DO_CLEANUP_FILES:
            cls.cleanup(cls.cleanup_files)
        else:
            logging.info('Skipping cleanup_files: %s', str(cls.cleanup_files))

        cls.dead_server = cls.cleanup([], cls.server_info)

