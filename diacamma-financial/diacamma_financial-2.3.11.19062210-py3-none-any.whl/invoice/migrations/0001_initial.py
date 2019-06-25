# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import deletion
from django.utils import translation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from lucterios.CORE.models import PrintModel


def initial_values(*args):
    translation.activate(settings.LANGUAGE_CODE)
    PrintModel().load_model('diacamma.invoice', "Bill_0001", is_default=True)
    PrintModel().load_model('diacamma.invoice', "Bill_0002", is_default=False)


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('payoff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vat',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(verbose_name='name', max_length=20)),
                ('rate', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    99.9)], decimal_places=2, max_digits=6, verbose_name='rate', default=10.0)),
                ('isactif', models.BooleanField(
                    verbose_name='is actif', default=True)),
            ],
            options={
                'verbose_name_plural': 'VATs',
                'verbose_name': 'VAT'
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(
                    verbose_name='reference', max_length=30)),
                ('designation', models.TextField(verbose_name='designation')),
                ('price', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.999)], decimal_places=3, max_digits=10, verbose_name='price', default=0.0)),
                ('unit', models.CharField(
                    verbose_name='unit', null=True, default='', max_length=10)),
                ('isdisabled', models.BooleanField(
                    verbose_name='is disabled', default=False)),
                ('sell_account', models.CharField(
                    verbose_name='sell account', max_length=50)),
                ('vat', models.ForeignKey(to='invoice.Vat', null=True,
                                          on_delete=deletion.PROTECT, verbose_name='vat', default=None))
            ],
            options={
                'verbose_name_plural': 'articles',
                'verbose_name': 'article'
            },
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('supporting_ptr', models.OneToOneField(auto_created=True, parent_link=True,
                                                        serialize=False, primary_key=True, to='payoff.Supporting', on_delete=models.CASCADE)),
                ('fiscal_year', models.ForeignKey(on_delete=deletion.PROTECT,
                                                  null=True, to='accounting.FiscalYear', default=None, verbose_name='fiscal year')),
                ('bill_type', models.IntegerField(null=False, default=0, db_index=True, verbose_name='bill type', choices=[
                 (0, 'quotation'), (1, 'bill'), (2, 'asset'), (3, 'receipt')])),
                ('num', models.IntegerField(
                    null=True, verbose_name='numeros')),
                ('date', models.DateField(null=False, verbose_name='date')),
                ('comment', models.TextField(
                    verbose_name='comment', null=False, default='')),
                ('status', models.IntegerField(verbose_name='status', db_index=True, default=0, choices=[
                 (0, 'building'), (1, 'valid'), (2, 'cancel'), (3, 'archive')])),
                ('cost_accounting', models.ForeignKey(to='accounting.CostAccounting', null=True,
                                                      on_delete=deletion.PROTECT, verbose_name='cost accounting', default=None)),
                ('entry', models.ForeignKey(to='accounting.EntryAccount', null=True,
                                            on_delete=deletion.PROTECT, verbose_name='entry', default=None)),
            ],
            options={
                'verbose_name_plural': 'bills',
                'verbose_name': 'bill'
            },
        ),
        migrations.CreateModel(
            name='Detail',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.TextField(verbose_name='designation')),
                ('price', models.DecimalField(verbose_name='price', max_digits=10, default=0.0,
                                              decimal_places=3, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])),
                ('vta_rate', models.DecimalField(default=0.0, verbose_name='vta rate', decimal_places=4,
                                                 max_digits=6, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])),
                ('unit', models.CharField(
                    null=True, verbose_name='unit', default='', max_length=10)),
                ('quantity', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.99)], decimal_places=2, verbose_name='quantity', default=1.0, max_digits=10)),
                ('reduce', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.999)], decimal_places=3, verbose_name='reduce', default=0.0, max_digits=10)),
                ('article', models.ForeignKey(null=True, default=None, to='invoice.Article',
                                              on_delete=deletion.PROTECT, verbose_name='article')),
                ('bill', models.ForeignKey(
                    to='invoice.Bill', verbose_name='bill', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'details',
                'default_permissions': [],
                'verbose_name': 'detail'
            },
        ),
        migrations.RunPython(initial_values),
    ]
