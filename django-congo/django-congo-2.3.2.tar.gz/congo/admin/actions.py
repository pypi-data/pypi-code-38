# -*- coding: utf-8 -*-
from congo.maintenance import get_site_model
from django import shortcuts
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from urlparse import urlparse, parse_qsl, urlunparse

def change_site_membership(modeladmin, request, queryset):
    title = _("Change site membership")
    action = "change_site_membership"

    model = get_site_model()
    sites = model.objects.all()
    object_id_set = ','.join([str(obj.id) for obj in queryset])

    extra_context = {
        "title": title,
        "action": action,
        "sites": sites,
        "object_id_set": object_id_set,
    }

    # @OG change to 'admin/actions/%s.html' % action
    return shortcuts.render(request, 'admin/action_form.html', extra_context)
change_site_membership.short_description = _("Change site membership")

def change_site_membership_action(modeladmin, request):
    try:
        model = modeladmin.queryset(request).model
        object_id_set = request.POST.get('object_id_set')
        objects = model.objects.filter(id__in = object_id_set.split(','))
        site_id_list = request.POST.getlist('sites')
        sites = get_site_model().objects.filter(id__in = site_id_list)
        clear = 'clear' in request.POST

        rows_updated = 0

        for o in objects:
            if hasattr(o, 'sites'):
                if clear:
                    o.sites.clear()
                for s in sites:
                    o.sites.add(s)
            else:
                try:
                    o.site = sites[0]
                except IndexError:
                    o.site = None
            rows_updated += 1

        messages.success(request, _("Site membership was changed: %s") % rows_updated)
    except AttributeError:
        pass

    return HttpResponseRedirect(request.POST.get('next', '..'))

def change_date_range(modeladmin, request, queryset):
    rows_updated = queryset.update(start_date = '2000-01-01', end_date = '2099-01-01')
    modeladmin.message_user(request, _(u"Zakres dat zmieniony: %s") % rows_updated)
change_date_range.short_description = _(u"Zmień zakres dat na 100 lat")

def make_visible(modeladmin, request, queryset):
    rows_updated = queryset.update(is_visible = True)
    modeladmin.message_user(request, _(u"Zmieniono na widoczne: %s") % rows_updated)
make_visible.short_description = _(u"Zmień wybrane na widoczne")

def make_invisible(modeladmin, request, queryset):
    rows_updated = queryset.update(is_visible = False)
    modeladmin.message_user(request, _(u"Zmieniono na niewidoczne: %s") % rows_updated)
make_invisible.short_description = _(u"Zmień wybrane na niewidoczne")

def make_active(modeladmin, request, queryset):
    rows_updated = queryset.update(is_active = True)
    modeladmin.message_user(request, _(u"Zmioniono na aktywne: %s") % rows_updated)
make_active.short_description = _(u"Zmień wybrane na aktywne")

def make_inactive(modeladmin, request, queryset):
    rows_updated = queryset.update(is_active = False)
    modeladmin.message_user(request, _(u"Zmieniono na nieaktywne: %s") % rows_updated)
make_inactive.short_description = _(u"Zmień wybrane na nieakywne")
