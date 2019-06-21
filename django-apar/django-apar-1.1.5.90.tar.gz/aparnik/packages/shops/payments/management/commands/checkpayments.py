# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

from aparnik.packages.shops.payments.models import Payment, Order


class Command(BaseCommand):
    # Show this when the user types help
    help = "check payments"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        # one_hours = now() - relativedelta(hours=1)
        # current_time = now()

        payments = Payment.objects.active().filter(status=Payment.STATUS_COMPLETE,
                                                   order_obj__status=Order.query_waiting(),
                                                   # update_at__range=[one_hours, current_time]
                                                   )
        for payment in payments:
            payment.order_obj.pay_success()
        finished_time = now()

        print(('check payments %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))
