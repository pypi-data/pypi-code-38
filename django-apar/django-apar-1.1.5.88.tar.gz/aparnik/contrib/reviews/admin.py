# -*- coding: utf-8 -*-


from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Review, Like, BaseReview
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelStackedInline
from aparnik.utils.utils import is_app_installed
# from courses.models import Course

# Register your models here.


# class CourseFilter(admin.SimpleListFilter):
#     title = _('Course')
#     parameter_name = 'course'
#
#     def lookups(self, request, model_admin):
#         courses = BaseModel.objects.instance_of(Course).filter(id__in=model_admin.model.objects.all().values_list('model_obj', flat=True))
#         return [(c.id, c.title) for c in courses]
#         # You can also use hardcoded model name like "Country" instead of
#         # "model_admin.model" if this is not direct foreign key filter
#         # return [('yes', 'yes')]
#
#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(model_obj__id__exact=self.value())
#         else:
#             return queryset


class BaseReviewInline(admin.StackedInline):
    model = BaseReview
    exclude = ['update_needed', 'model_obj', 'user_obj']
    # fields = ['title']
    fk_name = 'parent_obj'
    dynamic_raw_id_fields = ['files']
    extra = 1

    def __init__(self, *args, **kwargs):
        Klass = BaseReviewInline
        Klass_parent = BaseModelStackedInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


    def get_queryset(self, request):
        return BaseReview.objects.filter(parent_obj__isnull=False)


class BaseReviewAdmin(BaseModelAdmin):
    fields = ['title', 'description', 'is_published', 'user_obj']
    list_display = ['title', 'user_obj', 'is_published', get_update_at, ]
    # list_filter = ['is_published', CourseFilter]
    list_filter = ['is_published']
    search_fields = get_user_search_fields('user_obj') + ['title', 'created_at', ]
    exclude = []
    dynamic_raw_id_fields = []
    # readonly_fields = []
    # actions = []
    raw_id_fields = ['user_obj',]
    inlines = [
        BaseReviewInline,
    ]

    def __init__(self, *args, **kwargs):
        Klass = BaseReviewAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = BaseReview

    def get_queryset(self, request):
        return BaseReview.objects.filter(parent_obj__isnull=True)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # Do something with `instance`
            if instance.id is None:
                instance.model_obj = form.instance.model_obj
                instance.user_obj = request.user
            instance.save()
        formset.save_m2m()


class ReviewInline(BaseReviewInline):
    model_name = Review

    def get_queryset(self, request):
        return Review.objects.filter(parent_obj__isnull=False)


class ReviewAdmin(BaseReviewAdmin):
    fields = ['rate', 'model_obj',]
    list_filter = []
    list_display = ['rate', ]
    search_fields = []
    exclude = []
    dynamic_raw_id_fields = ['model_obj', ]        # list_display = ['rate']

    # search_fields = ['title', 'rate', 'user_obj__username', 'created_at']
    # list_filter = ['is_published', 'rate', 'created_at']
    # readonly_fields = []
    # actions = []
    raw_id_fields = ['user_obj', ]
    inlines = [ReviewInline]

    def __init__(self, *args, **kwargs):
        Klass = ReviewAdmin
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
        model = Review

    def get_queryset(self, request):
        return Review.objects.filter(parent_obj__isnull=True)


class LikeAdmin(BaseModelAdmin):
    list_display = ['user_obj', 'review_obj', 'is_like', get_update_at, ]
    list_filter = []
    fields = []
    exclude = []
    dynamic_raw_id_fields = []
    search_fields = get_user_search_fields('user_obj') + ['id', ]
    raw_id_fields = ['user_obj', ]

    def __init__(self, *args, **kwargs):
        Klass = LikeAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Like


if is_app_installed('aparnik.contrib.segments'):

    from aparnik.contrib.segments.admin import SegmentAdmin
    from .models import BaseReviewSegment


    class BaseReviewSegmentAdmin(SegmentAdmin):
        fields = []
        list_display = []
        search_fields = []
        list_filter = []
        exclude = []
        raw_id_fields = []
        dynamic_raw_id_fields = []

        def __init__(self, *args, **kwargs):
            Klass = BaseReviewSegmentAdmin
            Klass_parent = SegmentAdmin

            super(Klass, self).__init__(*args, **kwargs)
            self.fields = Klass_parent.fields + self.fields
            self.list_display = Klass_parent.list_display + self.list_display
            self.list_filter = Klass_parent.list_filter + self.list_filter
            self.search_fields = Klass_parent.search_fields + self.search_fields
            self.exclude = Klass_parent.exclude + self.exclude
            self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
            self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

        class Meta:
            model = BaseReviewSegment


    admin.site.register(BaseReviewSegment, BaseReviewSegmentAdmin)

admin.site.register(Review, ReviewAdmin)
admin.site.register(Like, LikeAdmin)
