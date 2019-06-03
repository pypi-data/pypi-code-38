from django.contrib import admin
from ls.joyous.models import (SimpleEventPage, MultidayEventPage,
        RecurringEventPage, MultidayRecurringEventPage,
        CancellationPage, ExtraInfoPage, PostponementPage,
        RescheduleMultidayEventPage, GroupPage,
        CalendarPage, GeneralCalendarPage, SpecificCalendarPage)

admin.site.register(CalendarPage)
admin.site.register(SimpleEventPage, date_hierarchy = 'date')
admin.site.register(MultidayEventPage, date_hierarchy = 'date_from')
admin.site.register(RecurringEventPage)
admin.site.register(CancellationPage, date_hierarchy = 'except_date')
admin.site.register(ExtraInfoPage, date_hierarchy = 'except_date')
admin.site.register(PostponementPage, date_hierarchy = 'except_date')
admin.site.register(GroupPage)
