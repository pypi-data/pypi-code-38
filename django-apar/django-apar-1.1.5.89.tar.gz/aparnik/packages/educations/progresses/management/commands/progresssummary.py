# -*- coding: utf-8 -*-


from django.db.models import Sum, Avg
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

from aparnik.packages.educations.courses.models import Course, CourseSummary
from aparnik.packages.educations.progresses.models import Progresses, ProgressSummary
from aparnik.contrib.basemodels.models import BaseModel
import datetime

User = get_user_model()


class Command(BaseCommand):
    # Show this when the user types help
    help = "calculate for Progress Model"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        #
        reindex = False
        if Progresses.objects.update_needed().count() > 0:
            reindex = True

        if reindex:
            self.reindex()

        Progresses.objects.update_needed().update(update_needed=False)
        finished_time = now()

        print(('reindex progress %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))

    def reindex(self):
        models = []
        for user_id in Progresses.objects.update_needed().values_list('user_obj', flat=True).distinct():
            user = User.objects.get(pk=user_id)
            # prefetch_related('file_obj__course_obj').
            progresses_user = Progresses.objects.this_user(user=user).prefetch_related('file_obj__course_obj__parent_obj')
            courses_ids = progresses_user.values_list('file_obj__course_obj', flat=True).distinct()
            parents = []
            # CourseSummary.objects.filter(course__id__in=courses_ids).annotate(total_pages=Sum('book__pages'))
            # فقط دوره هایی که فایل دارند حساب می شوند و رکورد آن ها درج می شود.
            for course_id in courses_ids:
                course = Course.objects.get(pk=course_id)
                if course.parent_obj:
                    parents.append(course.parent_obj)

                total_time_seconds = CourseSummary.objects.filter(course=course).aggregate(total_time_seconds=Sum('total_time_seconds'))['total_time_seconds'] or 0.0
                total_complete = progresses_user.filter(file_obj__course_obj=course).aggregate(total_time_seconds=Sum('file_obj__seconds'))['total_time_seconds'] or 0.0
                try:
                    percentage = (total_complete / total_time_seconds) * 100
                except:
                    percentage = 0.0

                try:

                    progress_summary = ProgressSummary.objects.get(user_obj=user, model=course)
                    progress_summary.percentage = percentage
                    progress_summary.save()
                except Exception as e:

                    ProgressSummary.objects.create(user_obj=user, model=course, percentage=percentage)

            # حساب درصد دوره های بالا دستی از روی سامری!
            while(parents):
                parents_tmp = list(set(parents))
                parents = []
                for obj in parents_tmp:
                    if obj.parent_obj:
                        parents.append(obj.parent_obj)
                    percentage = ProgressSummary.objects.active().filter(user_obj=user, model__parent_obj=obj).aggregate(percentage_avg=Avg('percentage'))['percentage_avg'] or 0.0
                    try:

                        progress_summary = ProgressSummary.objects.get(user_obj=user, model=obj)
                        progress_summary.percentage = percentage
                        progress_summary.save()
                    except Exception as e:

                        ProgressSummary.objects.create(user_obj=user, model=obj, percentage=percentage)
