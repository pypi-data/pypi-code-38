# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-03 07:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import silver.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('silver', '0050_auto_20190408_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingdocumentbase',
            name='pdf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='silver.PDF'),
        ),
        migrations.AlterField(
            model_name='billingdocumentbase',
            name='related_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reverse_related_document', to='silver.BillingDocumentBase'),
        ),
        migrations.AlterField(
            model_name='billinglog',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_billing_logs', to='silver.BillingDocumentBase'),
        ),
        migrations.AlterField(
            model_name='billinglog',
            name='proforma',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proforma_billing_logs', to='silver.BillingDocumentBase'),
        ),
        migrations.AlterField(
            model_name='documententry',
            name='product_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoices', to='silver.ProductCode'),
        ),
        migrations.AlterField(
            model_name='meteredfeature',
            name='product_code',
            field=silver.utils.models.UnsavedForeignKey(help_text='The product code for this plan.', on_delete=django.db.models.deletion.PROTECT, to='silver.ProductCode'),
        ),
        migrations.AlterField(
            model_name='plan',
            name='product_code',
            field=models.ForeignKey(help_text='The product code for this plan.', on_delete=django.db.models.deletion.PROTECT, to='silver.ProductCode'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='fail_code',
            field=models.CharField(blank=True, choices=[('default', 'default'), ('insufficient_funds', 'insufficient_funds'), ('expired_payment_method', 'expired_payment_method'), ('expired_card', 'expired_card'), ('invalid_payment_method', 'invalid_payment_method'), ('invalid_card', 'invalid_card'), ('limit_exceeded', 'limit_exceeded'), ('transaction_declined', 'transaction_declined'), ('transaction_declined_by_bank', 'transaction_declined_by_bank'), ('transaction_hard_declined', 'transaction_hard_declined'), ('transaction_hard_declined_by_bank', 'transaction_hard_declined_by_bank')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_transactions', to='silver.BillingDocumentBase'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='silver.PaymentMethod'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='proforma',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proforma_transactions', to='silver.BillingDocumentBase'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='state',
            field=django_fsm.FSMField(choices=[('initial', 'Initial'), ('pending', 'Pending'), ('settled', 'Settled'), ('failed', 'Failed'), ('canceled', 'Canceled'), ('refunded', 'Refunded')], default='initial', max_length=8),
        ),
    ]
