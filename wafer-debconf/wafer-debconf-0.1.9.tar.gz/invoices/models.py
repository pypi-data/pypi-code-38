from decimal import Decimal
from django.conf import settings
from django.core.signing import Signer
from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.urls import reverse

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('new', 'Invoiced'),
        ('pending', 'Payment pending'),
        ('paid', 'Payment received'),
        ('canceled', 'Invoice canceled'),
    )

    reference_number = models.CharField(max_length=128, unique=True,
                                        null=False, blank=False)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES,
                              default='new')
    date = models.DateField()

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='invoices',
                                  on_delete=models.PROTECT)
    invoiced_entity = models.CharField(max_length=128, blank=True)
    billing_address = models.TextField()
    compound = models.BooleanField(default=False)

    transaction_id = models.CharField(max_length=128, null=False, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    signer = Signer(sep=':', salt='invoices.Invoice')

    @property
    def total(self):
        return sum(line.total for line in self.lines.all())

    @property
    def total_local(self):
        return round(self.total * settings.DEBCONF_LOCAL_CURRENCY_RATE, 2)

    def paypal_data(self):
        data = settings.PAYPAL_DATA.copy()

        data['cmd'] = '_cart'
        data['invoice'] = settings.INVOICE_PREFIX + self.reference_number
        data['upload'] = '1'

        i = 1
        for line in self.lines.all():
            if line.quantity * line.unit_price < 0:
                discount = data.get('discount_amount_cart', 0)
                discount += - (line.quantity * line.unit_price)
                data['discount_amount_cart'] = discount
                continue
            data['item_name_%d' % i] = line.description
            data['quantity_%d' % i] = line.quantity
            data['amount_%d' % i] = line.unit_price
            i = i + 1

        return data

    def text_details(self):
        header = ('Reference', 'Description', 'Qty', 'Unit', 'Total')
        footer = ('', '', '', 'Total', str(self.total))
        lines = [
            (line.reference, line.description, line.quantity, line.unit_price,
             line.total)
            for line in self.lines.all()
        ]
        all_lines = (
            [
                header,
                ('', '', '', '', ''),
            ]
            + lines
            + [
                ('', '', '', '-------', '-------'),
                footer,
            ]
        )

        col_width = [max(len(str(x)) for x in col) for col in zip(*all_lines)]
        formats = ['{:{}}'] * 3 + ['{:>{}}'] * 2
        return "\n".join(
            ("| " + " | ".join(formats[i].format(x, col_width[i])
                               for i, x in enumerate(line)) + " |")
            for line in all_lines
        )

    def save(self, *args, **kwargs):
        # generate reference number on save
        if not self.reference_number:
            year = str(self.date.year)
            last_invoice = Invoice.objects.filter(
                reference_number__startswith=year
            ).order_by('-reference_number').first()

            if last_invoice:
                year, seqnum = last_invoice.reference_number.split('-')
                seqnum = int(seqnum, 10) + 1
            else:
                seqnum = 1

            self.reference_number = '%s-%05d' % (year, seqnum)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'invoices:display',
            kwargs={'reference_number': self.reference_number})

    def get_signed_url(self):
        signed_reference = self.signer.sign(self.reference_number)
        return reverse(
            'invoices:display',
            kwargs={'reference_number': signed_reference})


@receiver(valid_ipn_received)
def update_invoice_on_ipn_received(sender, **kwargs):
    ipn = sender
    paypal_data = settings.PAYPAL_DATA
    if ipn.payment_status == ST_PP_COMPLETED:
        if ipn.receiver_email != paypal_data['business']:
            return
        if not ipn.invoice.startswith(settings.INVOICE_PREFIX):
            return

        invoice_number = ipn.invoice[len(settings.INVOICE_PREFIX):]
        invoice = Invoice.objects.get(reference_number=invoice_number)
        invoice.status = 'paid'
        invoice.transaction_id = ipn.txn_id
        invoice.save()

        if invoice.compound:
            for line in invoice.lines.all():
                reference = line.reference.split('#', 1)[1]
                child_invoice = Invoice.objects.get(reference_number=reference)
                child_invoice.status = 'paid'
                child_invoice.transaction_id = ipn.txn_id
                child_invoice.save()


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='lines',
                                on_delete=models.CASCADE)
    line_order = models.IntegerField()
    reference = models.CharField(max_length=32)
    description = models.CharField(max_length=1024)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    @property
    def total(self):
        return self.unit_price * self.quantity

    class Meta:
        unique_together = ('invoice', 'line_order')
        ordering = ('invoice', 'line_order')

    def __str__(self):
        return 'InvoiceLine(%s [%s] %d @ %.02f = %.02f)' % (
            self.reference,
            self.description,
            self.quantity,
            self.unit_price,
            self.total,
        )
