# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

from aparnik.contrib.reviews.models import Review, ReviewSummary
from aparnik.contrib.basemodels.models import BaseModel
import datetime

User = get_user_model()


class Command(BaseCommand):
    # Show this when the user types help
    help = "calculate for Review Model"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        #
        reindex = False
        if Review.objects.update_needed().count() > 0:
            reindex = True

        if reindex:
            self.reindex()

        # Course.objects.update()
        Review.objects.update_needed().update(update_needed=False)
        finished_time = now()

        print(('reindex reviews %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))

    def reindex(self):
        models = []
        for obj in Review.objects.active():
            models.append(obj.model_obj)

        models = list(set(models))
        for obj in models:
            obj.review_average = Review.objects.model_review_avg(obj)
            obj.save()
            count_all = Review.objects.filter(model_obj=obj).count()

            for i in range(6):
                count = Review.objects.filter(rate=i, model_obj=obj).count()
                percentage = (float(count) / float(count_all)) * 100
                summary = None
                try:
                    summary = obj.review_summaries.get(rate=i)
                    summary.count = count
                    summary.percentage = percentage
                    summary.save()
                except:
                    summary = ReviewSummary.objects.create(rate=i, count=count, model=obj, percentage=percentage)
