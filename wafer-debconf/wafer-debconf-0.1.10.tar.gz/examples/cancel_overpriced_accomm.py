# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from invoices.prices import ACCOMM_INVOICE_INFO
from invoices.models import InvoiceLine

SUBJECT = u'[DebConf18]: Invoice cancelled due to price change'
TXT = u"""Hi,

The price of on-site accommodation at DebConf18 has decreased.  We have
accordingly cancelled your previous invoice [0].  Please visit the registration
wizard [1] again in order to generate a new invoice at the lower price.

[0]: https://debconf18.debconf.org/invoices/{reference_number}/
[1]: https://debconf18.debconf.org/register

Thanks for your understanding,

The DebConf registration team
"""


class Command(BaseCommand):
    help = 'Cancel pending overpriced accommodation invoices'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')

    def cancel(self, invoice, dry_run):
        if dry_run:
            print('I would cancel: {}'.format(invoice.reference_number))
            return
        invoice.status = 'canceled'
        invoice.save()

        attendee = invoice.recipient.attendee
        attendee.completed_register_steps = 9
        attendee.save()

        to = invoice.recipient.email
        body = TXT.format(reference_number=invoice.reference_number)
        email_message = EmailMultiAlternatives(SUBJECT, body, to=[to])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        seen = set()
        for line in InvoiceLine.objects.filter(
                    invoice__status='new',
                    reference=ACCOMM_INVOICE_INFO['reference']
                ).exclude(unit_price=ACCOMM_INVOICE_INFO['unit_price']):
            invoice = line.invoice
            if invoice.reference_number in seen:
                continue
            seen.add(invoice.reference_number)

            self.cancel(invoice, dry_run)
