ENABLED_MODULES = [
    'thyme',
    'gitmodule',
    'toggl',
    'taiga',
    'jira',
    'slack',
]

TIMEZONE = 'Europe/Helsinki'

TESTING = False

UI_SETTINGS = {
    'toggl': {
        'global': '#E01A22'
    },
    'thyme': {
        'global': '#1aef65'
    },
    'gitmodule': {
        'global': '#F44D27'
    },
    'slack': {
        'global': '#4A154B'
    }
}

TOGGL = {
    'global': {
        'API_KEY': '779e369d872d75354fa05f5eb7d0b7dc'
    },
    'outdoor': {
        'NAME': 'Scandinavian Outdoor',
        'PROJECTS': {
            'Verkkokauppakehitys': 'default',
        }
    },
    'storm': {
        'NAME': 'Storm',
        'PROJECTS': {
            'Verkkokauppakehitys': 'default',
        }
    },
    'myssy': {
        'NAME': 'Myssyfarmi',
        'PROJECTS': {
            'Verkkokauppakehitys': 'default',
        }
    }
}

GIT = {
    'global': {
        'EMAILS': ['eero.vilpponen@gmail.com', 'eero.vilpponen@protecomp.fi'],
    },
    'outdoor': {
        'REPOS': ['/home/eero/Documents/outdoor/sos',
                  '/home/eero/Documents/outdoor/tilhi', '/home/eero/Documents/outdoor/soi',
                  '/home/eero/Documents/outdoor/soi/shared-apps']
    },
    'storm': {
        'REPOS': ['/home/eero/Documents/storm']
    },
    'myssy': {
        'REPOS': ['/home/eero/Documents/myssyfarmi']
    },
    'cloudprice': {
        'REPOS': ['/home/eero/Documents/cloudprice']
    },
}

JIRA = {
    'outdoor': {
        'CREDENTIALS': ('eero.vilpponen@protecomp.fi', '.A8Ai-ngyfhXu7F-r-BC'),
        'URL': 'https://scandinavianoutdoor.atlassian.net',
        'PROJECT_KEY': 'DEV',
    }
}

TAIGA = {
    'global': {
        'CREDENTIALS': ['eerovilpponen', 'pru2-.34Ndw*WMjqT24w']
    },
    'storm': {
        'project_slug': 'msvilp-storm'
    },
    'myssy': {
        'project_slug': 'msvilp-myssyfarmi'
    }
}

THYME = {
    'global': {
        'DIR': '/home/eero/Documents/thyme',
        'IDLE': 900,
        'CUTOFF': 300,
    }
}

SLACK = {
    'global': {
        'API_KEY': 'xoxp-13389763879-213139729830-637577337329-5befc4931ec28f32c6b0b2769d0a0cfa',
        'USER_ID': 'U6943MFQE',
    },
    'outdoor': {
        'API_KEY': 'xoxp-13373711861-338515366999-643893862037-93e50147016e9a20d1d81323625343dc',
        'USER_ID': 'U9YF5ASVD'
    },
}

# from tracklater.test_settings import *  # noqa
