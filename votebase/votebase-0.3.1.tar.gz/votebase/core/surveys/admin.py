from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from import_export.admin import ImportExportModelAdmin

from votebase.core.surveys.models import Survey, Round
from votebase.core.questions.models import Question
from votebase.core.utils.admin import duplicate_object


duplicate_object.short_description = _(u'Make a Copy of Object')


class QuizFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('quiz')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_quiz'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'yes':
            return queryset.quizzes()

        if self.value() == 'no':
            return queryset.not_quizzes()


class QuestionInlines(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Survey)
class SurveyAdmin(ImportExportModelAdmin):
    list_display = ('title', 'user', 'is_visible', )
    list_display_links = ('title',)
    list_filter = ('is_visible', QuizFilter)
    # inlines = (QuestionInlines, )
    actions = [duplicate_object]
    raw_id_fields = ['user']


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('title', 'survey', 'permission_level', 'is_active',
                    'is_date_in_range', 'is_secured')
    list_display_links = ('title',)
    list_filter = ('is_active',)

    def is_date_in_range(self, instance):
        return instance.is_date_in_range()
    is_date_in_range.boolean = True

    def is_secured(self, obj):
        return obj.is_secured()
    is_secured.boolean = True
