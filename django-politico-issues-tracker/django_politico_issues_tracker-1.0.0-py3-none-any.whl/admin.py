from django.contrib import admin
from .models import Candidate, Category, Faq, Issue, Position, Story, Update

admin.site.register(Candidate)
admin.site.register(Category)
admin.site.register(Faq)
admin.site.register(Issue)
admin.site.register(Position)
admin.site.register(Story)
admin.site.register(Update)
