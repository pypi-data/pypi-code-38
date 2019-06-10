from django.contrib import admin
""" Import from local app."""
from .models import CategoryModelScheme, ArticleModelScheme
from .modeladmins import CategoryModelSchemeAdmin, ArticleModelSchemeAdmin


# Register your models here.
admin.site.register(CategoryModelScheme, CategoryModelSchemeAdmin)
admin.site.register(ArticleModelScheme, ArticleModelSchemeAdmin)
