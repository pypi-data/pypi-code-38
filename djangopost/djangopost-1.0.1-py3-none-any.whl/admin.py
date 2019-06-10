from django.contrib import admin
""" Import from local app. """
from .models import CategoryModel
from .models import ArticleModel
from .modeladmins import CategoryModelAdmin
from .modeladmins import ArticleModelAdmin


# Register your models here.
admin.site.register(CategoryModel, CategoryModelAdmin)
admin.site.register(ArticleModel, ArticleModelAdmin)
