# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

# from fcm_django.models import FCMDevice
from aparnik.contrib.notifications.models import Notification
from aparnik.contrib.notifiesme.models import NotifyMe
from aparnik.contrib.basemodels.models import BaseModel
from aparnik.packages.educations.courses.models import Course, CourseFile
from aparnik.packages.shops.products.models import Product
import datetime

User = get_user_model()


class Command(BaseCommand):
    # Show this when the user types help
    help = "send notifies me"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        current_time = now()
        # TODO: get last_time
        last_time = now() + relativedelta(minutes=-4)

        notifies_request_id = NotifyMe.objects.active().values_list('model_obj__id', flat=True).distinct()

        ids = []
        # parent, file and etc.....
        course_queryset = Course.objects.children_deep(course_ids=list(notifies_request_id))
        courses_ids = course_queryset.values_list('id', flat=True)
        courses_new_ids = []
        if course_queryset.filter(publish_date__range=[last_time, current_time]).exists():
            courses_new_ids = course_queryset.filter(publish_date__range=[last_time, current_time]).values_list('id', flat=True)
            # new course published

        file_queryset = CourseFile.objects.active().filter(course_obj_id__in=courses_ids, publish_date__range=[last_time, current_time])
        files_new_ids = []
        if file_queryset.exists():
            files_new_ids = file_queryset.values_list('id', flat=True)
            # new file publish

        if len(files_new_ids) or len(courses_new_ids):
            self.reindex(notifies_request_id, courses_new_ids, files_new_ids)
        finished_time = now()

        print(('send notifies me %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))

    def reindex(self, notifies_request_id, courses_new_ids, files_new_ids):
        union_ids = list(courses_new_ids) + list(files_new_ids)
        for nid in union_ids:

            ids = []
            try:
                ids.append(CourseFile.objects.get(id=nid).course_obj.id)
            except:
                pass
            finally:
                ids.append(nid)

            ids = ids + list(Course.objects.parents_deep(course_id=ids[0]).values_list('id', flat=True).distinct())

            ids = list(set(ids))

            compare_ids = [x for x in ids if x not in union_ids]

            if not(len(compare_ids) == len(ids)):
                users_id = NotifyMe.objects.active().filter(model_obj_id__in=ids).order_by('user_obj').values_list('user_obj', flat=True).distinct()
                product = Product.objects.get(id=nid)
                try:
                    Notification.objects.send_notification(
                        type=Notification.NOTIFICATION_INFO,
                        users=User.objects.filter(pk__in=users_id),
                        title='فایل جدید',
                        description='%s در دسترس قرار گرفت.' %product.title,
                        from_user_obj=None,
                        model_obj=product
                    )
                except Exception as e:
                    print((e.message))
