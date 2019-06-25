"""
Module:
    unicon.plugins.ise.statemachine

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
    This subpackage implements state machine for Ise 
"""

from unicon.statemachine import Path, State, StateMachine
from unicon.plugins.ise.patterns import IsePatterns

p = IsePatterns()

class IseStateMachine(StateMachine):
    def create(self):
        shell = State('shell', p.prompt)
        config = State('config', p.config_prompt)
        shell_to_config = Path(shell, config, 'config term', None)
        config_to_shell = Path(config, shell, 'end', None)
        self.add_state(shell)
        self.add_state(config)
        self.add_path(shell_to_config)
        self.add_path(config_to_shell)
