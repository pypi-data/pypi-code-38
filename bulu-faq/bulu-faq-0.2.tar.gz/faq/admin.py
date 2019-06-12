from django.contrib import admin

from .models import Category, FAQ


class FAQInline(admin.TabularInline):
    extra = 0
    model = FAQ
    fields = ['order', 'question', 'answer']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    search_fields = ['name']
    inlines = [FAQInline]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'created_at', 'updated_at']
    list_filter = ['category']
    list_editable = ['order']
    search_fields = ['question', 'answer', 'category__name']
