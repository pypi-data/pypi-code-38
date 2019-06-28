# -*- coding: utf-8 -*-

# Constantes do módulo
from django.conf import settings
from django.db import models
from django.db.models import Model
from django.utils import timezone
from polymorphic.models import PolymorphicModel

import common.fields as common_fields

ESTADOCIVIL_C = (('C', 'Casado'), ('S', 'Solteiro'), ('D', 'Divorciado'), ('', 'União Civil'))
SEXO_C = (('F', 'Feminino'), ('M', 'Masculino'))
ATIVO_C = (('S', 'Ativo'), ('I', 'Inativo'))
SIM_NAO_C = (('S', 'Sim'), ('N', 'Não'))
TIPO_DIAS_C = (('F', 'Dia Fixo'), ('C', 'Dias Corridos'), ('U', 'Dias Úteis'))


class UserAudit(Model):
    """
    Usado para auditar usuário e datas de criação e modificação
    """
    # Log
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='%(class)s_created_by', blank=True, null=True,
                                   verbose_name=u'Cadastrado Por')
    created_at = common_fields.AutoCreatedAtField(verbose_name=u'Data de Criação')

    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='%(class)s_modified_by', blank=True, null=True,
                                    verbose_name=u'Modificado Por')
    modified_at = common_fields.AutoModifiedAtField(verbose_name='Última Modificação', default=timezone.now)

    class Meta:
        verbose_name = u'Auditoria de Usuário'
        verbose_name_plural = u'Auditoria de Usuários'
        abstract = True

    def __str__(self):
        return 'Criado por {} em {}, modificado por {} em {}'.format(self.created_by, self.created_at,
                                                                     self.modified_by, self.modified_at)


class Configuracao(PolymorphicModel, UserAudit):
    """
    Configuração
    """
    apelido = models.CharField(max_length=20, null=False, blank=False, unique=True, verbose_name=u'Apelido', default='')
    # Status
    ativo = models.CharField(max_length=1, null=True, blank=True, verbose_name=u'Status', default='S',
                             choices=ATIVO_C)
    # Log
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    #                                related_name='configuracao_created_by', blank=True, null=True,
    #                                verbose_name=u'Cadastrado Por')
    # created_at = common_fields.AutoCreatedAtField(verbose_name=u'Data de Criação')
    #
    # modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    #                                 related_name='configuracao_modified_by', blank=True, null=True,
    #                                 verbose_name=u'Modificado Por')
    # modified_at = common_fields.AutoModifiedAtField(verbose_name='Última Modificação', default=timezone.now)

    class Meta:
        verbose_name = u'Configuracao'
        verbose_name_plural = u'Configurações'
        ordering = ('apelido',)
        # abstract = True
        # managed = False

    def __str__(self):
        return u'%s' % self.apelido
