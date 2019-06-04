# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template import Context, engines

from invoices.models import Invoice


class Command(BaseCommand):
    help = 'Badger outstanding invoices'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),

    def badger(self, invoice, dry_run):
        to = invoice.recipient.email
        name = invoice.recipient.get_full_name()
        invoice_number = invoice.reference_number
        total = invoice.total

        if not total:
            return

        if dry_run:
            print('I would badger %s <%s> (%s: %s CAD)' %
                  (name, to, invoice_number, total))
            return

        ctx = Context({
            'name': name,
            'total': total,
            'invoice_number': invoice_number,
            'invoice_details': invoice.text_details(),
        })

        template = engines['django'].get_template(
            'invoices/outstanding_invoices-subject.txt')
        subject = template.render(ctx)

        template = engines['django'].get_template(
            'invoices/outstanding_invoices-body.txt')
        body = template.render(ctx)

        email_message = EmailMultiAlternatives(subject, body,
                                               to=["%s <%s>" % (name, to)])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        for invoice in Invoice.objects.filter(status='new'):
            self.badger(invoice, dry_run)
