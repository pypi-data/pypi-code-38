from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.http import urlquote

from bursary.models import Bursary, BursaryReferee


class BursaryRefereeInline(admin.TabularInline):
    model = BursaryReferee


class BursaryAdmin(admin.ModelAdmin):
    list_display = (
        'user',  'request_food', 'request_accommodation', 'request_travel',
        'need', 'travel_bursary', 'travel_from',
        'accommodation_status', 'accommodation_accept_before',
        'food_status', 'food_accept_before',
        'travel_status', 'travel_accept_before',
        'reimbursed_amount'
    )
    list_filter = ('accommodation_status', 'food_status', 'travel_status',
                   'request_food', 'request_accommodation', 'request_travel',
                   'accommodation_accept_before', 'food_accept_before',
                   'travel_accept_before')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    inlines = (BursaryRefereeInline,)


admin.site.register(Bursary, BursaryAdmin)


class BursaryRefereeAdmin(admin.ModelAdmin):
    readonly_fields = (
        'full_name', 'email', 'presence', 'contributors_link',
        'bursary_request', 'bursary_need', 'bursary_travel',
        'bursary_travel_from', 'bursary_reason_contribution',
        'bursary_reason_plans', 'talk_proposals', 'bursary_reason_diversity',
    )

    def get_queryset(self, request):
        """Only list objects where the current user has to review"""
        qs = super(BursaryRefereeAdmin, self).get_queryset(request)

        if not request.user.has_perm('bursary.add_bursaryreferee'):
            qs = qs.filter(referee=request.user)

        return qs

    def has_change_permission(self, request, obj=None):
        """Only allow changing objects where the current user is reviewer"""
        hcp = super(BursaryRefereeAdmin, self).has_change_permission(request,
                                                                     obj)

        if (hcp and obj
                and not request.user.has_perm('bursary.add_bursaryreferee')):
            return obj.referee == request.user

        return hcp

    def is_admin(self, request):
        return request.user.has_perm('bursary.add_bursaryreferee')

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('Applicant informations', {
                'fields': ('full_name', 'email'),
            }),
            ('Bursary application', {
                'fields': (
                    'bursary_request', 'bursary_need',
                    'bursary_travel', 'bursary_travel_from',
                ),
            }),
            ('Contribution information', {
                'fields': (
                    'contributors_link', 'bursary_reason_contribution',
                    'presence', 'bursary_reason_plans', 'talk_proposals',
                    'contrib_score',
                ),
            }),
            ('Diversity and Inclusion', {
                'fields': (
                    'bursary_reason_diversity', 'outreach_score',
                )
            }),
            ('Notes', {'fields': ('notes', 'final')}),
        )

        # Display more fields for admin users; allows creation of referees by
        # hand
        if self.is_admin(request):
            fieldsets = (
                ('Bursary Referee admin', {
                    'fields': ('bursary', 'referee'),
                }),
            ) + fieldsets

        return fieldsets

    def get_list_display(self, request):
        if self.is_admin(request):
            return (
                'full_name', 'email', 'referee', 'final', 'bursary_request',
                'contrib_score', 'outreach_score', 'notes',
            )
        return (
            'full_name', 'email', 'final', 'bursary_request', 'contrib_score',
            'outreach_score', 'notes',
        )

    def get_list_filter(self, request):
        base_filters = ('final', 'contrib_score', 'outreach_score')
        if self.is_admin(request):
            return base_filters + ('referee',)
        return base_filters

    # Actions
    actions = ['make_referee_final']

    def get_actions(self, request):
        actions = super(BursaryRefereeAdmin, self).get_actions(request)
        if not self.is_admin(request):
            if 'delete_selected' in actions:
                del actions['delete_selected']

        return actions

    def make_referee_final(self, request, queryset):
        rows_updated = queryset.update(final=True)
        self.message_user(request, '%s evaluation%s finalized' % (
            rows_updated, 's' if rows_updated != 1 else '')
        )
    make_referee_final.short_description = "Mark selected evaluations as final"

    # Specific displays for evaluations
    def full_name(self, instance):
        return instance.bursary.user.get_full_name()
    full_name.admin_order_field = 'bursary__user__last_name'

    def email(self, instance):
        return instance.bursary.user.email
    email.admin_order_field = 'bursary__user__email'

    def contributors_link(self, instance):
        url = 'https://contributors.debian.org/contributors/mia/query?q=%s'
        email = instance.bursary.user.email
        return format_html(
            '<a href="{0}" target="_blank">{0}</a>',
            url % urlquote(email),
        )

    def presence(self, instance):
        arrival = instance.bursary.user.attendee.arrival
        departure = instance.bursary.user.attendee.departure

        return "%s to %s" % (arrival, departure)

    def bursary_request(self, instance):
        request = []
        if instance.bursary.request_food:
            request.append('food')
        if instance.bursary.request_accommodation:
            request.append('accommodation')
        if instance.bursary.request_travel:
            request.append('travel')
        return ','.join(request)

    def bursary_need(self, instance):
        return instance.bursary.get_need_display()
    bursary_need.short_description = 'Level of need (self-assessed)'

    def bursary_travel(self, instance):
        return instance.bursary.travel_bursary
    bursary_travel.short_description = 'Requested travel bursary amount (USD)'

    def bursary_travel_from(self, instance):
        return instance.bursary.travel_from
    bursary_travel_from.short_description = 'Traveling from'

    def bursary_reason_contribution(self, instance):
        return instance.bursary.reason_contribution
    bursary_reason_contribution.short_description = 'Contributions to Debian'

    def talk_proposals(self, instance):

        return format_html("<ul>{0}</ul>", format_html_join(
            '',
            '<li>{0} ({1}, <a href="{2}" target="_blank">details</a>)</li>',
            ((talk.title, talk.get_status_display(), talk.get_absolute_url())
             for talk in instance.bursary.user.talks.all())
        ))
    talk_proposals.short_description = 'Events proposed for the conference'

    def bursary_reason_plans(self, instance):
        return instance.bursary.reason_plans
    bursary_reason_plans.short_description = 'Plans for DebCamp or DebConf'

    def bursary_reason_diversity(self, instance):
        return instance.bursary.reason_diversity
    bursary_reason_diversity.short_description = (
        'Diversity and Inclusion criteria')


admin.site.register(BursaryReferee, BursaryRefereeAdmin)
