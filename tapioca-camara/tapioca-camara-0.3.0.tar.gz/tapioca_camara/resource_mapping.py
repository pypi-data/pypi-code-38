# coding: utf-8

RESOURCE_MAPPING = {
    # Deputados
    'deputados': {
        'resource': 'deputados',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    'deputado': {
        'resource': 'deputados/{id}',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    # Órgãos
    'orgaos': {
        'resource': 'orgaos',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    'orgao': {
        'resource': 'orgaos/{id}',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    'orgao_eventos': {
        'resource': 'orgaos/{id}/eventos',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    'orgao_membros': {
        'resource': 'orgaos/{id}/membros',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    'orgaos_tipos': {
        'resource': 'referencias/tiposOrgao',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    'orgaos_situacoes': {
        'resource': 'referencias/situacoesOrgao',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    # Proposições
    'proposicoes': {
        'resource': 'proposicoes',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
    'proposicao': {
        'resource': 'proposicoes/{id}',
        'docs': 'https://dadosabertos.camara.leg.br/swagger/api.html#api'
    },
}
