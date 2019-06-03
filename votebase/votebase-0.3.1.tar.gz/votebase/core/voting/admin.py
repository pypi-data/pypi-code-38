from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from import_export.admin import ImportExportModelAdmin

from votebase.core.voting.models import Voter, Answer


class QuizResultSentFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('quiz result sent')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_quiz_result_sent'

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
        from votebase.core.surveys.models import Survey
        quizzes = Survey.objects.quizzes()

        if self.value() == 'yes':
            return queryset.filter(is_quiz_result_sent=True, round__survey__in=quizzes)

        if self.value() == 'no':
            return queryset.filter(is_quiz_result_sent=False, round__survey__in=quizzes)


class VoterAdmin(ImportExportModelAdmin):
    actions = ['send_quiz_result', 'resave_quiz_result']
    list_display = ('user', 'survey', 'quiz_result', 'is_quiz_result_sent', 'is_api_voter', 'is_irrelevant', 'created')
    list_filter = (QuizResultSentFilter, 'is_api_voter', 'is_irrelevant', 'continent_code', 'country_code')
    search_fields = ['user__profile__first_name', 'user__profile__last_name', 'user__username', 'user__email', 'hash_key']
    list_editable = ['is_irrelevant', ]
    raw_id_fields = ['user', ]
    readonly_fields = ['survey', 'round', 'user']

    def send_quiz_result(self, request, queryset):
        for voter in queryset:
            voter.send_quiz_result()

    def resave_quiz_result(self, request, queryset):
        for voter in queryset:
            voter.quiz_result = voter.get_quiz_result()
            voter.save()


admin.site.register(Voter, VoterAdmin)


class AnswerAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Answer, AnswerAdmin)