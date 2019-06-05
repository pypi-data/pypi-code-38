from os import environ
from swimlane_platform.install import run as install_run
from swimlane_platform.lib import ArgsConfigQuestions, Actions, BaseWithLog, ExpectedException
from swimlane_platform.upgrade import run as upgrade_run
from swimlane_platform.backup.backup import run as backup_run
from swimlane_platform.backup.restore import run as restore_run
from swimlane_platform.questions_groups import automation_questions, logging_questions, dev_question
from swimlane_platform.environment_updater import run_environment_updater_validate, run_environment_updater_audit


class SwimlaneWizard(BaseWithLog):

    # noinspection PyBroadException
    def run(self, config):
        command = self.args.command
        try:
            if command == Actions.Install:
                install_run(config)
            elif command == Actions.Upgrade:
                upgrade_run(config)
            elif command == Actions.Backup:
                backup_run(config)
            elif command == Actions.Restore:
                restore_run(config)
            elif command == Actions.Validate:
                run_environment_updater_validate(config)
            elif command == Actions.Audit:
                run_environment_updater_audit(config)
        except ExpectedException as e:
            self.logger.error(e.message)
        except Exception:
            self.logger.exception("Unexpected error.")


def run():
    questions = [
        {
            'type': 'list',
            'name': 'command',
            'message': 'What action do you want to perform?',
            'choices': [
                {
                    'name': 'Install:   Install Swimlane.',
                    'value': Actions.Install
                },
                {
                    'name': 'Upgrade:   Upgrade to a newer version of Swimlane.',
                    'value': Actions.Upgrade
                },
                {
                    'name': 'Audit:     Verify Swimlane is ready to upgrade from the current version.',
                    'value': Actions.Audit
                },
                {
                    'name': 'Validate:  Verify Swimlane record data integrity for the current version.',
                    'value': Actions.Validate
                },
                {
                    'name': 'Backup:    Create a backup of Swimlane data.',
                    'value': Actions.Backup
                },
                {
                    'name': 'Restore:   Restore Swimlane data from backup.',
                    'value': Actions.Restore
                }
            ]
        }
    ]
    questions.extend(dev_question)
    questions.extend(logging_questions)
    questions.extend(automation_questions)
    config = ArgsConfigQuestions()
    config.collect(questions)
    wizard = SwimlaneWizard(config.to_arguments())
    wizard.run(config)
