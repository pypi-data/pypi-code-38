import json

from six.moves import zip_longest


def skip_logic_block_data(choice, logic, survey=None, question=None):
    return {
        'choice': choice,
        'skip_logic': logic,
        'survey': survey,
        'question': question,
    }


def skip_logic_data(choices=list(), logics=list(), survey=None, question=None):
    data = [
        {'type': 'skip_logic', 'value': skip_logic_block_data(
            choice,
            logic,
            survey.id if logic == 'survey' else None,
            question.sort_order + 1 if logic == 'question' else None,
        )
        } for choice, logic in zip_longest(choices, logics, fillvalue='next')
    ]
    return json.dumps(data)
