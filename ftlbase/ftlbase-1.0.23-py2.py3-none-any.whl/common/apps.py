from django.apps import AppConfig
from django.conf import settings


class CommonConfig(AppConfig):
    name = 'common'
    label = 'common'

    def ready(self):
        super().ready()

        from common.models import Configuracao
        import common

        try:
            common.empresa = Configuracao.objects.get(pk=settings.EMPRESA_CORRENTE)
        except Exception as v:
            common.empresa = Configuracao(pk=settings.EMPRESA_CORRENTE, apelido='Exemplo Ltda.')
