from django.contrib import admin

from votebase.core.questions.models import Question, Option


class OptionInline(admin.TabularInline):
    model = Option
    exclude = ('created', 'modified',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'weight', 'survey', 'is_required',
                    'is_quiz')
    list_display_links = ('title',)
    list_filter = ('is_required', 'is_quiz')
    inlines = (OptionInline, )


admin.site.register(Question, QuestionAdmin)


class OptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question', 'is_correct')
    list_display_links = ('title', )


admin.site.register(Option, OptionAdmin)
