# coding: utf-8

RESOURCE_MAPPING = {

    # Senadores
    'senadores': {
        'resource': 'senador/lista/atual',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/ListaSenadorService/resource_ListaSenadorService_listaSenadoresXml_GET',
    },
    'senador': {
        'resource': 'senador/{id}',
        'docs': 'http://legis.senado.leg.br/dadosabertos/docs/resource_ListaSenadorService.html#resource_ListaSenadorService_detalheSenadorXml_GET',
    },

    # Comissões
    'comissoes': {
        'resource': 'comissao/lista/colegiados',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/ListaComissaoService/resource_ListaComissaoService_listaColegiadosXml_GET',
    },
    'comissao': {
        'resource': 'comissao/{sigla}',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/DetalheComissaoService/resource_DetalheComissaoService_detalheComissaoXml_GET',
    },
    'comissoes_tipos_cargo': {
        'resource': 'comissao/lista/tiposCargo',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/ListaComissaoService/resource_ListaComissaoService_listaTiposCargoXml_GET',
    },
    'comissoes_tipos_colegiado': {
        'resource': 'comissao/lista/tiposColegiado',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/ListaComissaoService/resource_ListaComissaoService_listaTiposColegiadoXml_GET',
    },
    'comissoes_por_tipo': {
        'resource': 'comissao/lista/{tipo}',
        'docs': 'http://legis.senado.gov.br/dadosabertos/docs/ui/index.html#!/ListaComissaoService/resource_ListaComissaoService_listaComissoesXml_GET',
    },
}
