# ------------------------------------------------------------------------------
# Test Widgets
# ------------------------------------------------------------------------------
import sys
import datetime as dt
from django.test import TestCase
from wagtail.admin.widgets import AdminTimeInput, AdminDateInput
from ls.joyous.utils.recurrence import Recurrence
from ls.joyous.utils.recurrence import YEARLY, WEEKLY, MONTHLY
from ls.joyous.utils.recurrence import MO, TU, WE, TH, FR, SA, SU
from ls.joyous.widgets import RecurrenceWidget, Time12hrInput, ExceptionDateInput
from .testutils import datetimetz, freeze_timetz, getPage


from django import forms
from django.contrib.auth.models import AnonymousUser
from django.core import checks
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.test import RequestFactory, TestCase, override_settings

from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, ObjectList, PageChooserPanel,
    RichTextFieldPanel, TabbedInterface, extract_panel_definitions_from_model_class,
    get_form_for_model)
from wagtail.admin.forms import WagtailAdminModelForm, WagtailAdminPageForm
from wagtail.admin.rich_text import DraftailRichTextArea
from wagtail.admin.widgets import AdminAutoHeightTextInput, AdminDateInput, AdminPageChooser
from wagtail.core.models import Page, Site
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.tests.testapp.forms import ValidatedPageForm
from wagtail.tests.testapp.models import (
    EventPage, EventPageChooserModel, EventPageSpeaker, PageChooserModel,
    SimplePage, ValidatedPage)
from wagtail.tests.utils import WagtailTestUtils

# ------------------------------------------------------------------------------
class TestExceptionDatePanel(TestCase):
    def setUp(self):
        pass

#     def testNullValue(self):
#         widget = ExceptionDateInput()
#         self.assertEqual(widget.value_from_datadict({}, {}, 'xdate'), None)
#
#     def testRenderNone(self):
#         widget = ExceptionDateInput()
#         out = widget.render('xdate', None, {'id': "id_xdate"})
#         lines = [line for line in out.split("\n") if line]
#         self.assertHTMLEqual(lines[0], """
# <input type="text" name="xdate" id="id_xdate" autocomplete="{0.newDate}">""".format(self))
#         self.assertIn('<script>initExceptionDateChooser("id_xdate", null, ', lines[1]);
#         self.assertIn('"dayOfWeekStart": 0', lines[1])
#         self.assertIn('"format": "Y-m-d"', lines[1])
#         self.assertIn('</script>', lines[1])
#
#     @freeze_timetz("2019-04-06 9:00")
#     def testValidDates(self):
#         widget = ExceptionDateInput()
#         widget.overrides_repeat = Recurrence(dtstart=dt.date(2009, 1, 1),
#                                              freq=MONTHLY, byweekday=MO(1))
#         self.assertEqual(widget.valid_dates(),
#                          ["20180903", "20181001", "20181105", "20181203", "20190107", "20190204",
#                           "20190304", "20190401", "20190506", "20190603", "20190701", "20190805",
#                           "20190902", "20191007", "20191104", "20191202", "20200106", "20200203",
#                           "20200302", "20200406", "20200504", "20200601", "20200706", "20200803",
#                           "20200907", "20201005" ])
#
#     def testMedia(self):
#         widget = ExceptionDateInput()
#         self.assertEqual(widget.media._css, {'all': ["/static/joyous/css/recurrence_admin.css"]})
#         self.assertEqual(widget.media._js, ["/static/joyous/js/recurrence_admin.js"])

# ------------------------------------------------------------------------------
# class TestTime12hrPanel(TestCase):
#     def setUp(self):
#         self.newTime = AdminTimeInput().attrs.get('autocomplete', "new-time")
#
#     def testNullValue(self):
#         widget = Time12hrInput()
#         self.assertEqual(widget.value_from_datadict({}, {}, 'time'), None)
#
#     def testRenderNone(self):
#         widget = Time12hrInput()
#         out = widget.render('time', None, {'id': "time_id"})
#         self.assertHTMLEqual(out, """
# <input type="text" name="time" id="time_id" autocomplete="{0.newTime}">
# <script>
# $(function() {{
#     initTime12hrChooser("time_id");
# }});
# </script>""".format(self))


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
