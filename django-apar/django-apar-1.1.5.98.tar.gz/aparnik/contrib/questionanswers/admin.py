# -*- coding: utf-8 -*-


from django.contrib import admin

from dynamic_raw_id.admin import DynamicRawIDMixin
from .models import QA
from aparnik.contrib.reviews.admin import BaseReviewAdmin, BaseReviewInline


# Register your models here.
class QuestionAnswerInline(DynamicRawIDMixin, BaseReviewInline):
    model = QA
    dynamic_raw_id_fields = ['files']
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = QuestionAnswerInline
        Klass_parent = BaseReviewInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude

    def get_queryset(self, request):
        return QA.objects.filter(parent_obj__isnull=False)


class QuestionAnswerAdmin(BaseReviewAdmin):

    fields = ['files', 'model_obj', ]
    list_display = []
    search_fields = []
    list_filter = []
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = ['files', 'model_obj', ]
    inlines = [QuestionAnswerInline]

    def __init__(self, *args, **kwargs):
        Klass = QuestionAnswerAdmin
        Klass_parent = BaseReviewAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = QA

    def get_queryset(self, request):
        return QA.objects.filter(parent_obj__isnull=True)


admin.site.register(QA, QuestionAnswerAdmin)
