"""
Bebanjo's services API information including authentication realm
"""
from collections import namedtuple


BebanjoEnv = namedtuple('BebanjoEnv', 'base_url realm')
api_meta = {
    'movida': {
        'staging': BebanjoEnv('https://staging-movida.bebanjo.net/api',
                              'Staging Movida'),
        'preproduction': BebanjoEnv('https://preproduction-movida.bebanjo.net/api',
                                    'Preproduction Movida'),
        'production': BebanjoEnv('https://movida.bebanjo.net/api',
                                 'Production Movida')
    },
    'sequence': {
        'staging': BebanjoEnv('https://staging-sequence.bebanjo.net/api',
                              'Staging Sequence'),
        'preproduction': BebanjoEnv('https://preproduction-sequence.bebanjo.net/api',
                                    'Preproduction Sequence'),
        'production': BebanjoEnv('https://sequence.bebanjo.net/api',
                                 'Production Sequence')
    }
}
