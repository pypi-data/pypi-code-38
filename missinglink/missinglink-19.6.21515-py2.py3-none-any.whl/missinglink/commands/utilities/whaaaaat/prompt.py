# -*- coding: utf-8 -*-
import os


def prompt(questions, answers=None, **kwargs):
    # noinspection PyUnresolvedReferences
    from .prompts import list, confirm, input, password, checkbox, rawlist, expand
    from . import PromptParameterException, prompts

    if isinstance(questions, dict):
        questions = [questions]

    answers = answers or {}

    question_type = None

    for question in questions:
        # import the question
        if 'type' not in question:
            raise PromptParameterException('type')

        if 'name' not in question:
            raise PromptParameterException('name')

        if 'message' not in question:
            raise PromptParameterException('message')

        try:
            _kwargs = {
                'mouse_support': kwargs.pop('mouse_support', os.environ.get('ML_MOUSE_SUPPORT', '0') == '1')
            }

            _kwargs.update(kwargs)
            _kwargs.update(question)
            question_type = _kwargs.pop('type')
            name = _kwargs.pop('name')
            message = _kwargs.pop('message')
            when = _kwargs.pop('when', None)
            question_filter = _kwargs.pop('filter', None)
            if when:
                # at least a little sanity check!
                if callable(question['when']):
                    try:
                        if not question['when'](answers):
                            continue
                    except Exception as e:
                        raise ValueError(
                            'Problem in \'when\' check of %s question: %s' %
                            (name, e))
                else:
                    raise ValueError('\'when\' needs to be function that '
                                     'accepts a dict argument')
            if question_filter:
                # at least a little sanity check!
                if not callable(question['filter']):
                    raise ValueError('\'filter\' needs to be function that '
                                     'accepts an argument')

            if callable(question.get('default')):
                _kwargs['default'] = question['default'](answers)

            application = getattr(prompts, question_type).question(message, **_kwargs)

            answer = application.run()

            if answer is not None:
                if question_filter:
                    try:
                        answer = question['filter'](answer)
                    except Exception as e:
                        raise ValueError(
                            'Problem processing \'filter\' of %s question: %s' %
                            (name, e))
                answers[name] = answer

        except AttributeError:
            raise ValueError('No question type \'%s\'' % question_type)

    return answers
