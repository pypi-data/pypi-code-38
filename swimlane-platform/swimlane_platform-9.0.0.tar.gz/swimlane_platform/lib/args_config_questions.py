from argparse import Namespace, ArgumentParser, SUPPRESS
from typing import Dict, List, Union
from env_manager import read_dict, add_values_to_file
from PyInquirer import prompt, Validator, ValidationError
from swimlane_platform.lib.models import Automation
from swimlane_platform.lib.names import names
from swimlane_platform.lib.functions import semver_try_parse
from os import path


class AnswerRequiredValidator(Validator):
    def validate(self, document):
        if not document or not document.text:
            raise ValidationError(
                message='Entry required.',
                cursor_position=len(document.text))  # Move cursor to end


class VersionValidator(AnswerRequiredValidator):
    def validate(self, document):
        super(VersionValidator, self).validate(document)
        success, _ = semver_try_parse(document.text)
        if not success:
            raise ValidationError(message='Version provided is invalid semver and cannot be parsed.',
                                  cursor_position=len(document.text))


class PathExistsValidator(AnswerRequiredValidator):
    def validate(self, document):
        super(PathExistsValidator, self).validate(document)
        if not path.exists(document.text):
            raise ValidationError(
                message='Path doesn\'t exist.',
                cursor_position=len(document.text))  # Move cursor to end


class ContainingDirectoryExistsValidator(AnswerRequiredValidator):
    def validate(self, document):
        super(ContainingDirectoryExistsValidator, self).validate(document)
        if not path.exists(path.dirname(document.text)):
            raise ValidationError(
                message='Path doesn\'t exist.',
                cursor_position=len(document.text))  # Move cursor to end


class LogFileOptional(Validator):
    def validate(self, document):
        if not document or not document.text:
            return
        if not path.exists(path.dirname(document.text)):
            raise ValidationError(
                message='Directory doesn\'t exist.',
                cursor_position=len(document.text))  # Move cursor to end


class Configuration(Namespace):

    def __init__(self, **kwargs):
        super(Configuration, self).__init__(**kwargs)

    def __getattr__(self, item):
        return None

    def to_dict(self):
        return dict(self.__dict__)


class ArgsConfigQuestions(dict):

    def __init__(self, parent_config=None):
        # type: ((Dict[str, Union[str, List[str]]])) -> None
        super(ArgsConfigQuestions, self).__init__(parent_config if parent_config else {})

    def _add_config_file(self, filename):
        # type: (str) -> None
        config = read_dict(filename)
        self.update(config)

    def add_other_source(self, other_config):
        # type: (Dict[str, Union[str, List[str]]]) -> None
        for key, value in other_config.items():
            if key not in self and value:
                self[key] = value

    def collect(self, questions):
        # type: (List[Dict[str, str]]) -> None
        self._add_question_lookup_in_args(questions)
        automation = self.get(names.AUTOMATION)
        if automation and automation == Automation.Load:
            self._add_config_file(self[names.AUTOMATION_FILE])
        remaining_questions = [q for q in questions if not q.get('name') in self]
        self.update(prompt(remaining_questions, answers=self))
        if automation and automation == Automation.Save:
            self._save_config_file(self[names.AUTOMATION_FILE])

    def to_arguments(self):
        # type: () -> Configuration
        return Configuration(**self)

    def _add_question_lookup_in_args(self, questions):
        # type: (List[Dict[str, str]]) -> None
        parser = ArgumentParser()

        def get_argument_type(question_type):
            if question_type == 'input' or question_type == 'password' or question_type == 'list':
                return 'store'
            elif question_type == 'confirm':
                return 'store_true'
            else:
                raise Exception("The question type is not mapped.")

        for question in questions:
            parser.add_argument('--{name}'.format(name=question.get('name')),
                                help=question.get('message'),
                                default=SUPPRESS,
                                action=get_argument_type(question.get('type')))
        args, _ = parser.parse_known_args()
        self.update(dict(args.__dict__))

    def _save_config_file(self, file_name):
        # type: (str) -> None
        excluded = [names.AUTOMATION, names.AUTOMATION_FILE]
        clean_dict = dict([(key, value) for key, value in self.items() if key not in excluded])
        add_values_to_file(file_name, clean_dict)
