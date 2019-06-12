from django.contrib import admin

from .models import Category, FAQ


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'created_at', 'updated_at']
    list_filter = ['category']
