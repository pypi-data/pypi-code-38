# -*- coding: utf-8 -*-
import json
from collections import defaultdict

import click
import click.types
from six import wraps
from missinglink.commands.http_session import create_http_session
from missinglink.core.default_params import get_default
from missinglink.core.api import ApiCaller
from missinglink.core.context import init_context2


def _complete_type(ctx, resources, element_name, resource_name=None):
    if ctx.obj is None:
        init_context2(ctx, create_http_session())

    resource_name = resource_name or resources
    resources_result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', resources)

    resources_result = resources_result.get(resource_name, [])

    result = []
    for resource in resources_result:
        if 'org' not in resource:
            resource['org'] = 'me'

        result.append(resource)

    return {res[element_name]: res for res in result}


class DataVolumeIdParamType(click.types.IntParamType):
    @classmethod
    def get_resources(cls, ctx):
        return _complete_type(ctx, 'data_volumes', 'id', resource_name='volumes')

    # noinspection PyMethodMayBeStatic
    def complete(self, ctx, _incomplete):
        return self.get_resources(ctx)


class ProjectIdParamType(click.types.IntParamType):
    @classmethod
    def get_resources(cls, ctx):
        return _complete_type(ctx, 'projects', 'project_id')

    # noinspection PyMethodMayBeStatic
    def complete(self, ctx, _incomplete):
        return self.get_resources(ctx)


class OrganizationParamType(click.types.StringParamType):
    @classmethod
    def get_resources(cls, ctx):
        return _complete_type(ctx, 'orgs', 'org')

    # noinspection PyMethodMayBeStatic
    def complete(self, ctx, _incomplete):
        return self.get_resources(ctx)


class ArgumentWithRequired(click.Argument):
    pass


class ArgumentWithoutRequired(click.Argument):
    pass


class OptionWithRequired(click.Option):
    pass


class OptionWithoutRequired(click.Option):
    pass


def _get_wrap_class(is_option, is_required):
    if is_option:
        if is_required:
            return OptionWithRequired
        else:
            return OptionWithoutRequired

    if is_required:
        return ArgumentWithRequired
    else:
        return ArgumentWithoutRequired


class DataVolumeOptions(object):
    @staticmethod
    def isolation_token_option():
        def decorator(f):
            return click.option('--isolation-token', required=False, help='Token obtained from an isolated sync.')(f)

        return decorator

    @staticmethod
    def data_volume_id_argument(required=True):
        def prompt_volume_id(ctx, param, value):
            return CommonOptions._complete_type_callback(ctx, param, value, required, 'volume_id', 'Select Data Volume')

        def decorator(f):
            return click.argument(
                'volume-id', type=DataVolumeIdParamType(), callback=prompt_volume_id, required=False, envvar='VOLUMEID', cls=_get_wrap_class(is_option=False, is_required=required))(f)

        return decorator

    @staticmethod
    def data_path_option(required=True):
        def validate_path(ctx, param, value):
            try:
                from missinglink.legit.path_utils import expend_and_validate_dir

                expend_and_validate_dir(value)
            except (IOError, OSError):
                raise click.UsageError('not valid path', ctx=ctx)

            return value

        def decorator(f):
            return click.option('--data-path', callback=validate_path, required=required, help='Path to the data.')(f)

        return decorator


class CommonOptions(object):
    @staticmethod
    def processes_option():
        def decorator(f):
            return click.option('--processes', default=-1, type=int, required=False, hidden=True)(f)

        return decorator

    @staticmethod
    def no_progressbar_option():
        def decorator(f):
            return click.option('--no-progressbar/--enable-progressbar', default=False, is_flag=True, required=False)(f)

        return decorator

    @staticmethod
    def _check_required(ctx, param, required):
        def true_decorator(f):
            @wraps(f)
            def wrap(*args, **kwargs):
                value = f(*args, **kwargs)

                if value is None and required:
                    raise click.MissingParameter(ctx=ctx, param=param)

                return value

            return wrap

        return true_decorator

    @staticmethod
    def alert_type_option(required=False, multiple=False):
        all_options = ['started', 'stopped', 'ended', 'failed', 'data-warning']

        def validate_alert_type(ctx, option, value):
            def normalize_value(current_value):
                for alert_type in current_value:
                    if alert_type == 'all':
                        current_value.extend(all_options)

                return_value = [v for v in current_value if v in all_options]

                return sorted(list(set(return_value)))

            def ask_for_value():
                from .whaaaaat import prompt
                from .whaaaaat.prompt_toolkit.styles import style_from_pygments_dict
                from pygments.token import Token

                questions = [
                    {
                        'type': 'checkbox',
                        'name': 'alert',
                        'message': 'Select Alerts',
                        'choices': [{'name': alert_name} for alert_name in all_options],
                    },
                ]

                style = style_from_pygments_dict({
                    Token.Separator: '#6C6C6C',
                    Token.QuestionMark: '#FF9D00 bold',
                    Token.Selected: '#5F819D',  # default
                    Token.Pointer: '#FF9D00 bold',
                    Token.Instruction: '',  # default
                    Token.Answer: '#5F819D bold',
                    Token.Question: '',
                })

                answers = prompt(questions, style=style)

                return answers['alert']

            @CommonOptions._check_required(ctx, option, required)
            def wrap():
                actual_value = value if value else ask_for_value()

                return normalize_value(list(actual_value))

            return wrap()

        def decorator(f):
            return click.option(
                '--alert-type', '-a', callback=validate_alert_type, type=click.Choice(['all'] + all_options), required=False, multiple=multiple,
                help='Alert type for project subscription', cls=_get_wrap_class(is_option=True, is_required=required))(f)

        return decorator

    @staticmethod
    def org_option(required=True):
        def prompt_org_id(ctx, param, value):
            return CommonOptions._complete_type_callback(ctx, param, value, required, 'org', 'Select Organization', group_by_org=False)

        def decorator(f):
            return click.option(
                '--org', required=False, callback=prompt_org_id, envvar='ML_ORG',
                type=OrganizationParamType(), help='Organization to use.', cls=_get_wrap_class(is_option=True, is_required=required))(f)

        return decorator

    @staticmethod
    def _validate_length(value, min_length, max_length):
        if value is None:
            return value

        if max_length is not None and len(value) > max_length:
            raise click.BadParameter("needs to be shorter than %s characters" % max_length)

        if min_length is not None and len(value) < min_length:
            raise click.BadParameter("needs to be longer than %s characters" % min_length)

        return value

    @staticmethod
    def _input_option(name, required, prompt_message, min_length, max_length):
        def prompt_input_callback(ctx, param, value):
            CommonOptions._validate_length(value, min_length, max_length)

            return CommonOptions._complete_input_callback(ctx, param, value, required, prompt_message, min_length, max_length)

        def decorator(f):
            return click.option(name, required=False, callback=prompt_input_callback)(f)

        return decorator

    @staticmethod
    def display_name_option(required=True, min_length=None, max_length=None):
        return CommonOptions._input_option('--display-name', required, 'Enter display name', min_length, max_length)

    @staticmethod
    def description_option(required=False, min_length=None, max_length=None):
        return CommonOptions._input_option('--description', required, 'Enter description', min_length, max_length)

    # noinspection PyShadowingBuiltins
    @staticmethod
    def project_id_option(required=False, multiple=False, help=None):
        def prompt_project_id(ctx, param, value):
            return CommonOptions._complete_type_callback(ctx, param, value, required, 'project', 'Select Project')

        def decorator(f):
            return click.option(
                '--project', '-p', type=ProjectIdParamType(), envvar='ML_PROJECT',
                callback=prompt_project_id, required=False, multiple=multiple,
                help=help or 'The project Id. Use `ml projects list` to find your project Ids', cls=_get_wrap_class(is_option=True, is_required=required))(f)

        return decorator

    @staticmethod
    def experiment_id_option(required=False):
        def decorator(f):
            return click.option(
                '--experiment', '-e', type=int, metavar='<int>', required=required,
                help='The experiment ID. Use `ml experiments list` to find your experiment IDs')(f)

        return decorator

    @staticmethod
    def _complete_input_callback(ctx, param, value, required, prompt_message, min_length, max_length):
        from .whaaaaat.prompt_toolkit.validation import Validator, ValidationError

        class LengthValidator(Validator):
            def validate(self, document):
                if min_length is not None and len(document.text) < min_length:
                    raise ValidationError(
                        message='Text too short (min: %s)' % min_length,
                        cursor_position=len(document.text))  # Move cursor to end
                elif max_length is not None and len(document.text) > max_length:
                    raise ValidationError(
                        message='Text too long (max: %s)' % max_length,
                        cursor_position=len(document.text))  # Move cursor to end

        def ask_for_value():
            from .whaaaaat import prompt
            from .whaaaaat.prompt_toolkit.styles import style_from_pygments_dict
            from pygments.token import Token

            style = style_from_pygments_dict({
                Token.QuestionMark: '#FF9D00 bold',
                Token.Instruction: '',  # default
                Token.Answer: '#5F819D bold',
                Token.Question: 'bold',
            })

            questions = [
                {
                    'type': 'input',
                    'name': 'input',
                    'message': prompt_message,
                    'validate': LengthValidator,
                },
            ]

            answers = prompt(questions, style=style)
            return answers['input']

        @CommonOptions._check_required(ctx, param, required)
        def wrap():
            if value or not required or (ctx.obj and ctx.obj.disable_interactive):
                return value

            return ask_for_value()

        return wrap()

    @staticmethod
    def fill_value(param_type, ctx, name, prompt_message, group_by_org=True):
        def ask_for_value(resources):
            from .whaaaaat import prompt, Separator
            from .whaaaaat.prompt_toolkit.styles import style_from_pygments_dict
            from pygments.token import Token

            def prepare_choices():
                results = []
                for resource_id, resource in resources.items():
                    display_name = resource.get('display_name')

                    resource['res_id'] = resource_id
                    if display_name and resource_id != display_name:
                        choice_name = '%s - %s' % (resource_id, display_name)
                    else:
                        choice_name = str(resource_id)

                    results.append(
                        {
                            'name': choice_name,
                            'value': resource,
                        }
                    )

                return results

            choices = prepare_choices()
            if len(choices) == 1:
                return choices[0]['value']

            choices_dict = defaultdict(list)

            for option in choices:
                org = option['value'].get('org') if group_by_org else None
                choices_dict[org].append(option)

            choices_dict = {org: sorted(options, key=lambda v: v['name']) for org, options in choices_dict.items()}

            choices = []
            sorted_orgs = sorted(choices_dict.keys())
            if 'me' in sorted_orgs:
                sorted_orgs.remove('me')
                sorted_orgs = ['me'] + sorted_orgs

            for org in sorted_orgs:
                if len(sorted_orgs) > 1:
                    choices.append(Separator(org))

                choices.extend(choices_dict[org])

            questions = [
                {
                    'type': 'list',
                    'name': name,
                    'message': prompt_message,
                    'choices': choices,
                },
            ]

            style = style_from_pygments_dict({
                Token.Separator: '#6C6C6C',
                Token.QuestionMark: '#FF9D00 bold',
                Token.Selected: '#5F819D',
                Token.Pointer: '#FF9D00 bold',
                Token.Instruction: '',  # default
                Token.Answer: '#5F819D bold',
                Token.Question: 'bold',
            })

            answers = prompt(questions, style=style)

            return answers.get(name)

        lst = param_type.get_resources(ctx)

        if len(lst) == 0:
            return None

        resource = ask_for_value(lst)
        return resource.get('res_id')

    @staticmethod
    def _complete_type_callback(ctx, param, value, required, name, prompt_message, group_by_org=True):
        @CommonOptions._check_required(ctx, param, required)
        def wrap():
            if value or not required or (ctx.obj and ctx.obj.disable_interactive):
                return value

            value_from_default = get_default(name)

            if value_from_default is not None:
                return value_from_default

            resource = CommonOptions.fill_value(param.type, ctx, name, prompt_message, group_by_org)

            if resource is None:
                return None

            return resource

        return wrap()

    @staticmethod
    def validate_json(ctx, param, value):
        try:
            if value is None:
                return None

            return json.loads(value)
        except ValueError:
            raise click.BadParameter('not valid json', param=param, ctx=ctx)


class ChartsOptions(object):
    @staticmethod
    def chart_scope_option(required=False):
        def decorator(f):
            return click.option(
                '--chart-scope', '-cs', type=click.Choice(['test', 'validation', 'train']), required=required,
                default='test', help='Scope type.')(f)

        return decorator

    @staticmethod
    def chart_type_option(required=False):
        def decorator(f):
            return click.option(
                '--chart-type', '-ct', type=click.Choice(['line']), required=required,
                default='line', help='Graph type.')(f)

        return decorator

    @staticmethod
    def chart_name_option(required=False):
        def decorator(f):
            return click.option(
                '--chart-name', '-c', metavar='<str>', required=required,
                help='The name of the chart. The name is used in order to identify the chart against different '
                     'experiments and through the same experiment.')(f)

        return decorator

    @staticmethod
    def chart_x_option(required=False):
        def decorator(f):
            return click.option(
                '--chart-x', '-cx', metavar='<json_string>', required=required,
                help='Array of m data points (X axis), Can be Strings, Integers or Floats.')(f)

        return decorator

    @staticmethod
    def chart_y_option(required=False):
        def decorator(f):
            return click.option(
                '--chart-y', '-cy', metavar='<json_string>', required=required,
                help='Array/Matrix of m data values. Can be either array m of Integers/Floats or a matrix (m arrays having n Ints/Floats each),  a full matrix describing the values of every chart in every data point')(f)

        return decorator

    @staticmethod
    def chart_y_name_option(required=False):
        def decorator(f):
            return click.option(
                '--chart-y-name', '-cyn', metavar='<json_str>', required=required, default='Y',
                help='Display name for chart(s) Y axis')(f)

        return decorator

    @staticmethod
    def chart_x_name_option(required=False):
        def decorator(f):
            return click.option(
                '--chart-x-name', '-cxn', metavar='<str>', required=required, default='X',
                help='Display name for charts X axis')(f)

        return decorator


class ExperimentsOptions(object):
    @staticmethod
    def metrics_option(required=False):
        def decorator(f):
            return click.option(
                '--metrics', '-m', metavar='<json_string>', required=required,
                help='The metrics of the experiment as a jsonified string. The key should be the metric '
                     'name with "ex" prefix e.g. "ex_cost". The value is the metric value in String, Float, '
                     'Integer or Boolean.')(f)

        return decorator

    @staticmethod
    def model_weights_hash_option(required=False):
        def decorator(f):
            return click.option(
                '--weights-hash', '-wh', metavar='<sha1_hex>', required=required,
                help="The hexadecimal sha1 hash of the model's weights")(f)

        return decorator
