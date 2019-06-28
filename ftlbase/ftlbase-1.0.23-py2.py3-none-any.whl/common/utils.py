# -*- coding: utf-8 -*-

import re
from _pydecimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import EMPTY_VALUES
from django.db.models.signals import post_migrate
# message.attach('design.png', img_data, 'image/png')
# message.attach_file('/images/weather_map.png')
from django.utils.translation import ugettext_lazy as _


cpf_digits_re = re.compile(r'^(\d{3})\.(\d{3})\.(\d{3})-(\d{2})$')
cnpj_digits_re = re.compile(
    r'^(\d{2})[.-]?(\d{3})[.-]?(\d{3})/(\d{4})-(\d{2})$'
)


def DV_maker(v):
    if v >= 2:
        return 11 - v
    return 0


def validate_cpf(value):
    """
    A form field that validates a CPF number or a CPF string. A CPF number is
    compounded by XXX.XXX.XXX-VD. The two last digits are check digits.
    More information:
    http://en.wikipedia.org/wiki/Cadastro_de_Pessoas_F%C3%ADsicas
    """
    error_messages = {
        'invalid': _("CPF inválido."),
        'max_digits': _("Esse campo deve ter 11 or 14 characters."),
    }

    if value in EMPTY_VALUES:
        return ''
    orig_value = value[:]
    if not value.isdigit():
        cpf = cpf_digits_re.search(value)
        if cpf:
            value = ''.join(cpf.groups())
        else:
            raise ValidationError(error_messages['invalid'])

    if len(value) != 11:
        raise ValidationError(error_messages['max_digits'])
    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx])
                   for idx, i in enumerate(range(10, 1, -1))])
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx])
                   for idx, i in enumerate(range(11, 1, -1))])
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise ValidationError(error_messages['invalid'])
    if value.count(value[0]) == 11:
        raise ValidationError(error_messages['invalid'])
    return orig_value


def validate_cnpj(value):
    """
    A form field that validates input as `Brazilian CNPJ`_.
    Input can either be of the format XX.XXX.XXX/XXXX-XX or be a group of 14
    digits.
    .. _Brazilian CNPJ: http://en.wikipedia.org/wiki/National_identification_number#Brazil
    """
    error_messages = {
        'invalid': _("CNPJ Inválido"),
        'max_digits': _("Esse campo dve ter pelo menos 14 digitos"),
    }

    """
    Value can be either a string in the format XX.XXX.XXX/XXXX-XX or a
    group of 14 characters.
    """
    if value in EMPTY_VALUES:
        return ''
    orig_value = value[:]
    if not value.isdigit():
        cnpj = cnpj_digits_re.search(value)
        if cnpj:
            value = ''.join(cnpj.groups())
        else:
            raise ValidationError(error_messages['invalid'])

    if len(value) != 14:
        raise ValidationError(error_messages['max_digits'])
    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(list(range(5, 1, -1)) + list(range(9, 1, -1)))])
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(list(range(6, 1, -1)) + list(range(9, 1, -1)))])
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise ValidationError(error_messages['invalid'])

    return orig_value


def validate_pessoa_slug(value):
    """
    Slug de Pessoa é o nome mais id, mas o validade não é executado, pois o slug é montado no save
    """
    if value in EMPTY_VALUES:
        return ''
    return value


def moneyfmt(value, places=2, curr='', sep='.', dp=',',
             pos='', neg='(', trailneg=')'):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places  # 2 places --> '0.01'
    sign, digits, exp = Decimal(value).quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


# Adiciona permissão view_* para models através do Signal enviado após a migração: post_migrate signal
def add_view_permissions(sender, **kwargs):
    """
    This syncdb hooks takes care of adding a view permission too all our
    content types.
    """
    # Só executa se não está em modo de test
    if not settings.IN_TEST_MODE:
        # for each of our content types
        for content_type in ContentType.objects.all():
            # build our permission slug
            codename = "view_%s" % content_type.model

            # if it doesn't exist..
            if not Permission.objects.filter(content_type=content_type, codename=codename):
                # add it
                Permission.objects.create(content_type=content_type,
                                          codename=codename,
                                          name="Can view %s" % content_type.name)
                print("Added view permission for %s" % content_type.name)


# check for all our view permissions after a migrate
post_migrate.connect(add_view_permissions)


def testeEmail():
    subject, from_email, to, cc = 'Sincronização Imobiliar - Google Drive', 'brasil.helpdesk@gmail.com', 'was@ftl.com.br', 'wash@tbridge.com.br'
    text_content = 'Segue anexo log do sincronismo entre o servidor do Imobiliar do Imobiliar e o Google Drive'
    html_content = '<p>Segue anexo log do sincronismo entre <strong>o servidor do Imobiliar</strong> e o <strong>Google Drive</strong>.</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, to=[to], cc=[cc])
    msg.attach_alternative(html_content, "text/html")
    msg.attach_file('../backup.log')
    msg.send()


"""

Configuring email for development¶

There are times when you do not want Django to send emails at all. For example, while developing a website, 
you probably don’t want to send out thousands of emails – but you may want to validate that emails will be sent to 
the right people under the right conditions, and that those emails will contain the correct content.

The easiest way to configure email for local development is to use the console email backend. 
This backend redirects all email to stdout, allowing you to inspect the content of mail.

The file email backend can also be useful during development – this backend dumps the contents of every SMTP 
connection to a file that can be inspected at your leisure.

Another approach is to use a “dumb” SMTP server that receives the emails locally and displays them to the terminal, 
but does not actually send anything. Python has a built-in way to accomplish this with a single command:

python -m smtpd -n -c DebuggingServer localhost:1025


import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alugarImovel.settings")

from django.core.mail import EmailMultiAlternatives

def testeEmail():
    subject, from_email, to, cc = 'Sincronização Imobiliar - Google Drive', 'brasil.helpdesk@gmail.com', 'was@ftl.com.br', 'wash@tbridge.com.br'
    text_content = 'Segue anexo log do sincronismo entre o servidor do Imobiliar e o Google Drive'
    html_content = '<p>Segue anexo log do sincronismo entre <strong>o servidor do Imobiliar</strong> e o <strong>Google Drive</strong>.</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, to=[to], cc=[cc])
    msg.attach_alternative(html_content, "text/html")
    msg.attach_file('/home/was/alugarImovel/x.py')
    msg.send()
testeEmail()


"""
