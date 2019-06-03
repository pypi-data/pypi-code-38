from django.contrib import admin

from votebase.core.accounts.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'email', '_package', 'package_valid_to', 'api_key', 'created')
    list_display_links = ('id', 'get_full_name',)
    list_editable = ('_package', 'package_valid_to')
#    list_filter = ('is_confirmed', 'method_of_contact')
    ordering = ['-created',]
    search_fields = ['first_name', 'last_name', 'user__username', 'user__email']
    raw_id_fields = ['user']

    def email(self, obj):
        return obj.user.email

#    is_free.short_description = _(u'Is key free?')
#    is_free.boolean = True

admin.site.register(Profile, ProfileAdmin)
