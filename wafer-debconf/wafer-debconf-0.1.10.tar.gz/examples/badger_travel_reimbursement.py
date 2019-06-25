# -*- coding: utf-8 -*-

import decimal

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from django.template import Context, Template

from dc17.models.bursary import Bursary

SUBJECT = "[Action needed] Reimbursement process for travel bursary recipients"

BODY_TEMPLATE = Template("""\
{% autoescape off %}
Dear {{object.user.get_full_name}},

You have been granted a travel bursary for DebConf, and now is the time you can
submit documentation for reimbursement. TL;DR: yes, this email is very long,
but all of it contains complete details about the process, so you will need to
read it in full to get travel money back!

Reimbursement for DebConf-related expenses will be processed by Software in the
Public Interest, for all Requestors including Europeans.

The amount you requested is {{object.travel_bursary}} USD. We have had some cancellations up until
the conference, so we have some budgetary leeway, but we ask you to keep your
reimbursement request within 10% of this amount (up to {{travel_bursary_max}} USD).

We're very sorry that the process took this long to materialize, but SPI has
been seeking long-term contracting help to process reimbursements faster, which
took some time to secure but is ready to go now. While this updated process
will take some time to gear up, we are confident that it will make
reimbursement processing run smoother for all SPI projects in the long run.

To process the hundreds of reimbursement requests efficiently and
expeditiously, SPI requires consistency. All requests must include:

 1. an SPI Reimbursement Request Form [1] with accurate banking information as
    SPI uses TransferWise [2]
 2. an Expense Report generated using XE's Travel Expenses Calculator [3], with
    a̲m̲o̲u̲n̲t̲s̲ ̲c̲o̲n̲v̲e̲r̲t̲e̲d̲ ̲t̲o̲ ̲U̲S̲D̲
 3. sufficient documentation substantiating the expense report
 4. a declaration of compliance

[1]: http://www.spi-inc.org/treasurer/SPI_reimbursement_request.pdf
[2]: https://transferwise.com
[3]: http://www.xe.com/travel-expenses-calculator/

Requestors must follow these steps:

Step 1: Prepare an SPI Reimbursement Request Form
 • download it from http://www.spi-inc.org/treasurer/SPI_reimbursement_request.pdf
 • e̲n̲s̲u̲r̲e̲ ̲t̲h̲a̲t̲ ̲t̲h̲e̲ ̲b̲a̲n̲k̲i̲n̲g̲ ̲i̲n̲f̲o̲r̲m̲a̲t̲i̲o̲n̲ ̲i̲s̲ ̲a̲c̲c̲u̲r̲a̲t̲e̲ ̲a̲s̲ ̲i̲n̲c̲o̲r̲r̲e̲c̲t̲ ̲d̲e̲t̲a̲i̲l̲s̲ ̲a̲r̲e̲ ̲a̲
   m̲a̲j̲o̲r̲ ̲s̲o̲u̲r̲c̲e̲ ̲o̲f̲ ̲d̲e̲l̲a̲y̲s̲
 • save as PDF

Step 2: Prepare an Expense Report.
 • use http://www.xe.com/travel-expenses-calculator/ to prepare an expense report
 • enter Your Name, which must match the name in the SPI Reimbursement Request Form
 • set Your Home Currency to USD as S̲P̲I̲ ̲w̲i̲l̲l̲ ̲p̲r̲o̲c̲e̲s̲s̲ ̲r̲e̲i̲m̲b̲u̲r̲s̲e̲m̲e̲n̲t̲s̲ ̲i̲n̲ ̲U̲S̲D̲
 • leave/set Credit Card @ 2%, Debit Card @ 5%, Foreign Cash @ 5%, Traveller's Cheque @ 2%
 • enter Receipt Details, one row per receipt
   • specify the correct date of the transactions
 • save as PDF

Step 3: Collect and order your Receipts.
 • collect your recipts in the SAME ORDER as the rows in the Expense Report
 • if paper receipts, scan them with a multi-function device, converting to PDF
 • save as PDF

Step 4: Prepare the Submission Package.
 • collect into a single PDF, the following:
   • from step 1, the SPI Reimbursement Request From
   • from step 2, the Expense Report
   • from step 3, the Ordered Receipts
 • the poppler-utils package includes the pdfunite utility
   • usage: `pdfunite step1.pdf step2.pdf step3a.pdf step3b.pdf ... step3n.pdf DebConf17ReimbursementRequest-{{short_full_name}}.pdf`
   • warning: ensure that you explicitly mention the destination filename
     (DebConf17ReimbursementRequest-{{short_full_name}}.pdf) otherwise
     step3n.pdf is overwritten
   • notice: please name the file exactly as shown, substituting your name as
     entered in the SPI Reimbursement Request Form, for example,
     DebConf17ReimbursementRequest-NicolasDandrimont.pdf
 • e̲n̲s̲u̲r̲e̲ ̲t̲h̲a̲t̲ ̲t̲h̲e̲ ̲e̲n̲t̲i̲r̲e̲ ̲S̲u̲b̲m̲i̲s̲s̲i̲o̲n̲ ̲P̲a̲c̲k̲a̲g̲e̲ ̲c̲a̲n̲ ̲b̲e̲ ̲e̲a̲s̲i̲l̲y̲ ̲u̲n̲d̲e̲r̲s̲t̲o̲o̲d̲ ̲a̲s̲ ̲p̲o̲o̲r̲
   q̲u̲a̲l̲i̲t̲y̲ ̲s̲u̲b̲m̲i̲s̲s̲i̲o̲n̲s̲ ̲a̲r̲e̲ ̲a̲ ̲m̲a̲j̲o̲r̲ ̲s̲o̲u̲r̲c̲e̲ ̲o̲f̲ ̲d̲e̲l̲a̲y̲s̲

Step 5: Email the Submission Package.
 • prepare an email having these attributes
   • from: you
   • To: debconf-reimbursements@rt.spi-inc.org
   • subject: DebConf17 Reimbursement Request for {{object.user.get_full_name}}
   • attachment: the Submission Package (DebConf17ReimbursementRequest-{{short_full_name}}.pdf) prepared in step 4
   • body: (the text below)
     By submitting this reimbursement request, I declare:
      • that I have accurately prepared an SPI Reimbursement Request Form,
      • that I have prepared an Expense Report using XE's Travel Expense Calculator,
      • that I have attached sufficient documentation substantiating my request,
      • that I seek reimbursement of expenses that are compliant to DebConf policies, and
      • that I have not sought nor will seek reimbursement of these expenses from any other source.

If you have any question, please be sure to contact us at bursaries@debconf.org
and we'll work your issues out.

Thanks for your cooperation!
--\u0020
The DebConf Bursaries team
{% endautoescape %}
""")


class Command(BaseCommand):
    help = 'Send an email to people whose bursary grant expires soon'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually send emails')

    def badger(self, bursary, dry_run):
        context = {
            'object': bursary,
            'user': bursary.user.username,
            'to': '%s <%s>' % (bursary.user.get_full_name(),
                               bursary.user.email),
            'short_full_name': bursary.user.get_full_name().replace(' ', '')
                                                           .replace('-', '')
                                                           .replace("'", '')
                                                           .replace('.', ''),
            'travel_bursary_max': int(bursary.travel_bursary
                                      * decimal.Decimal('1.1')),
        }

        if dry_run:
            print('I would badger {to} (max = {travel_bursary_max})'
                  .format(**context))
            return

        from_email = 'bursaries@debconf.org'
        subject = SUBJECT
        body = BODY_TEMPLATE.render(Context(context))

        msg = EmailMultiAlternatives(subject, body, to=[context['to']],
                                     from_email=from_email)

        msg.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        to_badger = Bursary.objects.filter(
            request_travel=True,
            travel_status='accepted',
            user__attendee__reconfirm=True,
        )

        for bursary in to_badger:
            self.badger(bursary, dry_run)
