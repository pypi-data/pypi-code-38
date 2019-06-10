from django.contrib import admin


""" Start category admin model here. """
# ModelManagers start here.
class CategoryModelSchemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title',)}
    list_display   = ['title', 'slug', 'pk', 'created_at', 'author', 'verification', 'status']
    list_filter    = ['created_at', 'updated_at']
    search_fields  = ['title',]
    actions = ['make_verified', 'make_published']
    list_per_page = 10
    fieldsets = (
        ('Basic informations', {
            'fields': [('serial', 'title', 'slug')],
        }),
        ('Description', {
            'classes': ['collapse', 'extrapretty'],
            'fields': ['description',],
        }),
        ('Category owner', {
            'fields': ['verification', ('author', 'status'),],
        }),
    )

    def make_verified(self, request, queryset):
        row_updated = queryset.update(verification=True)
        if row_updated == 1:
            message_bit = '1 category was'
        else:
            message_bit = f'{row_updated} categories were'
        self.message_user(request, f'{message_bit} verified successfully.')

    make_verified.short_description = 'make categories verified'
    make_verified.allowed_permissions = ('change',)

    def make_published(self, request, queryset):
        row_updated = queryset.update(status='publish')
        if row_updated == 1:
            message_bit = '1 category was'
        else:
            message_bit = f'{row_updated} categories were'
        self.message_user(request, f'{message_bit} published successfully.')

    make_published.short_description = 'make categories published'
    make_published.allowed_permissions = ('change',)
# ModelManagers end here.
""" End category model here. """


""" Start overview model here. """
# ModelManagers start here.
class ArticleModelSchemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title',)}
    list_display   = ['title', 'category', 'serial', 'author', 'verification', 'status']
    list_filter    = ['status']
    search_fields  = ['title',]
    actions = ['make_verified', 'make_published']
    list_per_page = 10
    fieldsets = (
        ('Basic informations', {
            'fields': ['serial', ('title', 'slug'), 'category'],
        }),
        ('Media files', {
            'classes': ['collapse', 'extrapretty'],
            'fields': ['cover_image'],
        }),
        ('Description', {
            'classes': ['collapse', 'extrapretty'],
            'fields': ['description'],
        }),
        ('Shortlines', {
            'classes': ['collapse', 'extrapretty'],
            'fields': ['shortlines'],
        }),
        ('Content', {
            'classes': ['collapse', 'extrapretty'],
            'fields': ['content'],
        }),
        ('Article owner', {
            'fields': [('verification', 'is_promote', 'is_trend'), 'total_views', ('author', 'status')],
        }),
    )

    def make_verified(self, request, queryset):
        row_updated = queryset.update(verification=True)
        if row_updated == 1:
            message_bit = '1 article was'
        else:
            message_bit = f'{row_updated} articles were'
        self.message_user(request, f'{message_bit} verified successfully.')

    make_verified.short_description = 'make articles verified'
    make_verified.allowed_permissions = ('change',)

    def make_published(self, request, queryset):
        row_updated = queryset.update(status='publish')
        if row_updated == 1:
            message_bit = '1 article was'
        else:
            message_bit = f'{row_updated} articles were'
        self.message_user(request, f'{message_bit} published successfully.')

    make_published.short_description = 'make articles published'
    make_published.allowed_permissions = ('change',)
# ModelManager end here
""" End overview model here. """
