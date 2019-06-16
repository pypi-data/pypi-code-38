# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from collections import defaultdict
from missinglink.core import ApiCaller


def _complete_type(config, session, resources, resource_name=None):
    resource_name = resource_name or resources
    resources_result = ApiCaller.call(config, session, 'get', resources)

    resources_result = resources_result.get(resource_name, [])

    result = []
    for resource in resources_result:
        if 'org' not in resource:
            resource['org'] = 'me'

        result.append(resource)

    return result


def _complete_type_callback(config, session, get_resources, name, prompt_message):
    from missinglink.core.default_params import get_default

    def ask_for_value(resources):
        from .whaaaaat import prompt, Separator
        from pygments.token import Token
        from .whaaaaat.prompt_toolkit.styles import style_from_pygments_dict

        if not sys.stdout.isatty():
            print('You need a console to display selection menu.\nIf you are using PyCharm check the "Emulate terminal in output window"', file=sys.stderr)
            sys.exit(1)

        def prepare_choices():
            results = []
            for resource_id, resource in resources.items():
                display_name = resource.get('display_name')

                if display_name:
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

        style = style_from_pygments_dict({
            Token.Separator: '#6C6C6C',
            Token.QuestionMark: '#FF9D00 bold',
            Token.Selected: '#5F819D',
            Token.Pointer: '#FF9D00 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#5F819D bold',
            Token.Question: '',
        })

        choices_dict = defaultdict(list)
        choices = prepare_choices()
        for option in choices:
            org = option['value'].get('org')
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

        answers = prompt(questions, style=style)

        return answers.get(name)

    value_from_default = get_default(name)

    if value_from_default is not None:
        return value_from_default

    lst = get_resources(config, session)

    if len(lst) == 0:
        return None

    if len(lst) == 1:
        return list(lst.values())[0]

    return ask_for_value(lst)


def __get_projects(config, session):
    projects = _complete_type(config, session, 'projects')

    return {project['project_id']: project for project in projects}


def __get_data_volumes(config, session):
    data_volumes = _complete_type(config, session, 'data_volumes', 'volumes')

    return {data_volume['id']: data_volume for data_volume in data_volumes}


def select_volume_id(config, session):
    return _complete_type_callback(config, session, __get_data_volumes, 'data_volume', 'Select Data Volume')


def select_project(config, session):
    return _complete_type_callback(config, session, __get_projects, 'project', 'Select Project')
