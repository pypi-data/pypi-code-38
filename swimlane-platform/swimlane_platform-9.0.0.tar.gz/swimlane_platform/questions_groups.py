from swimlane_platform.lib import Automation, names, LogFileOptional

automation_questions = [
    {
        'type': 'list',
        'name': names.AUTOMATION,
        'message': 'Do you want to save your configuration selections for future use, or load previously saved '
                   'selections?',
        'choices': [
            {
                'name': 'No thanks',
                'value': Automation.Normal
            },
            {
                'name': 'Save',
                'value': Automation.Save
            },
            {
                'name': 'Load',
                'value': Automation.Load
            }
        ]
    },
    {
        'type': 'input',
        'name': names.AUTOMATION_FILE,
        'message': 'Specify the full path to your configuration file.',
        'when': lambda a: 'automation' in a and a['automation'] != Automation.Normal
    }
]

logging_questions = [
    {
        'type': 'list',
        'message': 'What logging level do you want?',
        'name': 'verbose',
        'default': 0,
        'choices': [
            {
                'name': 'Info',
                'value': 0
            },
            {
                'name': 'Verbose',
                'value': 1
            },
            {
                'name': 'Debug',
                'value': 2
            }
        ]
    },
    {
        'type': 'input',
        'name': 'log',
        'message': 'If you would like program output written to a file, specify the path to the log '
                   'file (leave your answer blank if no log file is needed).',
        'validate': LogFileOptional
    }
]

dev_question = [
    {
        'type': 'confirm',
        'name': 'dev',
        'message': 'hidden question for cli overwrite only',
        'default': False,
        'when': lambda a: False
    }
]
