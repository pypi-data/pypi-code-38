# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.db.models import Count, Subquery, OuterRef, F
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

from aparnik.settings import aparnik_settings, Setting
from aparnik.contrib.counters.models import Counter
from aparnik.contrib.basemodels.models import BaseModel

UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


class Command(BaseCommand):
    # Show this when the user types help
    help = "Updates visit counter for models based on a variable in settings app"

    # A command must define handle()
    def handle(self, *args, **options):
        start_time = now()

        try:
            is_count_per_view = Setting.objects.get(key='VISIT_COUNT_PER_VIEW').get_value()
        except:
            is_count_per_view = False

        # Update visit for each user
        if (is_count_per_view):
            BaseModel.objects.update(
                visit_count=Coalesce(Subquery(
                    BaseModel.objects.active().filter(
                        counter__model_obj=OuterRef('id'), counter__action='v'
                    ).annotate(count=(Count('counter__create_date') or 0)).values('count')

                ), 0)
            )

        if (not is_count_per_view):
            # This case devided into two query to improve performance
            # count normal users
            BaseModel.objects.update(
                visit_count=Coalesce(Subquery(
                    BaseModel.objects.active().filter(
                        counter__model_obj=OuterRef('id'), counter__action='v'
                    ).annotate(count=

                               Count('counter__user_obj', distinct=True)

                               ).values('count')

                ), 0)
            )

            # Add anonymous users visit count
            BaseModel.objects.update(
                visit_count=F('visit_count') + Coalesce(Subquery(
                    BaseModel.objects.active().filter(
                        counter__model_obj=OuterRef('id'), counter__user_obj_id__isnull=True, counter__action='v'
                    ).annotate(count=

                               Count('counter__user_obj', distinct=True)

                               ).values('count')

                ), 0)
            )

        finished_time = now()
        # print(' Success. \n Counter values for models updated; setting flag VISIT_COUNT_PER_VIEW = ' + str(
        #     is_count_per_view))

        print(('counters updated %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))
