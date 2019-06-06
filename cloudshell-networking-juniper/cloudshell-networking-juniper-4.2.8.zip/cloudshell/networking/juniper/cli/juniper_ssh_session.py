from collections import OrderedDict

from cloudshell.cli.session.ssh_session import SSHSession


class JuniperSSHSession(SSHSession):
    def _connect_actions(self, prompt, logger):
        action_map = OrderedDict()
        cli_action_key = r'[%>#]{1}\s*$'

        def action(session, sess_logger):
            session.send_line('cli', sess_logger)
            del action_map[cli_action_key]

        action_map[cli_action_key] = action
        self.hardware_expect(None, expected_string=prompt, action_map=action_map, timeout=self._timeout,
                             logger=logger)
        self._on_session_start(logger)
