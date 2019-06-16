from django.contrib import admin
from .models import Post
from .models import Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 3


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'was_published_recently')
    list_filter = ['published_date']
    search_fields = ['text']

    fieldsets = [('Main params', {'fields': ['published_date', 'text']}),
                 ('Secondary params', {'fields': ['title', 'created_date'],
                                       'classes': ['collapse']}),
                 ]

    inlines = [CommentInline]


admin.site.register(Post, PostAdmin)
admin.site.register(Comment)

