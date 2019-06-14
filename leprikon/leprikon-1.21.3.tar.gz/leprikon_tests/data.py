from datetime import date, timedelta

from django.contrib.auth.models import User
from django.utils.timezone import now

from leprikon.models.courses import Course
from leprikon.models.schoolyear import SchoolYear
from leprikon.models.subjects import SubjectType

school_year = SchoolYear.objects.get_current()
current_period = school_year.periods.get_or_create(
    name='current period',
    start=date.today()-timedelta(10),
    end=date.today()+timedelta(10),
)[0]
next_period = school_year.periods.get_or_create(
    name='next period',
    start=date.today()+timedelta(11),
    end=date.today()+timedelta(22),
)[0]

subject_type_event = SubjectType.objects.get_or_create(subject_type=SubjectType.EVENT, name='event')
subject_type_course = SubjectType.objects.get_or_create(subject_type=SubjectType.COURSE, name='course')

user1 = User.objects.get_or_create(username='testuser1')[0]
