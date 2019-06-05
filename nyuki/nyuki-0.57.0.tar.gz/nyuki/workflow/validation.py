import logging
from enum import Enum
from jsonschema import ValidationError, validate as validate_schema
from jsonschema.validators import Draft4Validator, extend as extend_validator
from jsonschema._validators import type_draft4
from jsonschema import _utils

from tukio import TaskRegistry, UnknownTaskName
from tukio.workflow import WorkflowRootTaskError


log = logging.getLogger(__name__)


class ErrorInfo(Enum):
    """
    Generic error messages for template validation.
    """
    UNKNOWN = 'Unknown error'
    UNKNOWN_TASK = 'Unknown task name'
    INVALID_GRAPH = 'Invalid graph semantic'
    INVALID_TASK = 'Invalid task config'


class TemplateError(Exception):
    """
    Workflow template exception descriptor.
    """
    def __init__(self, *, key=ErrorInfo.UNKNOWN, message=None, details=None):
        self.key = key
        self.message = message or key.value
        self.details = details or list()

    def as_dict(self):
        return {
            'key': self.key.name,
            'message': self.message,
            'details': self.details
        }

    @staticmethod
    def format_details(exc, task):
        """
        Gives JSON formatted details for a given exception on a task:
        {
            "task_id": "<id>",
            "config_path": "<key.key.key>",
            "error": "<type>",
            "info": "<extra>"
        }
        """
        path = [str(i) for i in list(exc.absolute_path)]
        error = exc.validator
        value = exc.validator_value

        # Get a proper path for the `required` validation error
        if error == 'required':
            cursor = task.get('config', {})
            for key in path:
                cursor = cursor[key] if isinstance(cursor, dict) else cursor[int(key)]
            # We are looking for the missing key (not always the first item)
            for key in value:
                if key not in cursor:
                    path.append(key)
                    break

        return {
            'task_id': task['id'],
            'config_path': '.'.join(path),
            'error': error,
            'info': value
        }

    def __str__(self):
        return self.message


def validate(template):
    """
    Validate a template dict and aggregate all errors that could occur.
    Return a tempplate object or raise a ValidationError
    """
    # Task name validation
    errors = list()
    for task in template.tasks:
        try:
            TaskRegistry.get(task.name)
        except UnknownTaskName:
            errors.append(task.name)
    if errors:
        log.debug('unknown tasks: %s', errors)
        raise TemplateError(
            key=ErrorInfo.UNKNOWN_TASK,
            details=errors
        )

    # DAG semantic validation
    try:
        template.validate()
    except WorkflowRootTaskError as exc:
        log.debug('workflow validation error: %s', exc)
        raise TemplateError(
            key=ErrorInfo.INVALID_GRAPH,
            message='Workflow validation error: {}'.format(exc)
        ) from exc

    # Task config validation
    errors = list()
    tasks = template.as_dict().get('tasks', [])
    for task in tasks:
        err = validate_task(task, tasks)
        if err:
            errors.append(err)
    if errors:
        raise TemplateError(
            key=ErrorInfo.INVALID_TASK,
            details=errors
        )

    return template


def validate_task(task, tasks=None):
    """
    Validate the jsonschema configuration of a task
    """
    name = task['name']
    config = task.get('config', {})
    schema = getattr(TaskRegistry.get(name)[0], 'SCHEMA', {})
    format_checker = getattr(TaskRegistry.get(name)[0], 'FORMAT_CHECKER', None)
    try:
        validate_schema(config, schema, format_checker=format_checker)
    except ValidationError as exc:
        return TemplateError.format_details(exc, task)
