from django.contrib import admin

from .models import Answer, Question


class AnswerInlineAdmin(admin.TabularInline):
    model = Answer
    extra = 0
    ordering = ('order',)


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInlineAdmin]


admin.site.register(Question, QuestionAdmin)
