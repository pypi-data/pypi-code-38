# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django_admin_related import utils


class VerifyRelated(ModelAdmin):
    """
        Check if object's has related before delete

        Obs: this is atomic, check all objects before delete
        from best performance use `verify_related_fields`
        because class check all fields is a Point to other model
        and `verify_related_fields` is direct way in field
    """
    verify_related_fields = ()
    delete_selected_confirmation_template = 'admin/delete_selected_confirm.html'

    def has_related_check(self, obj, field_name):
        """
            check if related exists
        """
        return getattr(obj, field_name).exists()

    def has_related(self, obj):
        """
            check if related exists
        """
        obj_fields = False if self.verify_related_fields else True
        fields = self.verify_related_fields or obj._meta.get_fields(include_hidden=False)
        
        for field in fields:
            if obj_fields:
                if not field.is_relation:
                    continue
                
                elif not hasattr(field, 'parent_link'):
                    continue

                field = field.related_name or (field.name + '_set')

            if self.has_related_check(obj, field):
                return True

        return False

    def get_actions(self, request):
        """
            remove original bulk delete (this no verify related before delete)
            and add new bulk delete (with related check)
        """
        actions = super(VerifyRelated, self).get_actions(request)
        
        if 'delete_selected' in actions:
            del actions['delete_selected']

        # Append new delete selected action
        actions['bulk_delete'] = (utils.bulk_delete, 'bulk_delete', utils.bulk_delete.short_description)
        
        return actions

    def delete_model(self, request, obj):
        """
            internal delete 
        """
        if self.has_related(obj):
            messages.error(request, _('This item contains linked models, could not be deleted.'))
            return 

        super(VerifyRelated, self).delete_model(request, obj)
        messages.success(request, _("Successfully deleted."))

    def response_delete(self, request, obj_display, obj_id):
        """
            Overriding Django `response_delete` to remove sucess message
            Determine the HttpResponse for the delete_view stage.
        """
        opts = self.model._meta

        if '_popup' in request.POST:
            popup_response_data = json.dumps({
                'action': 'delete',
                'value': str(obj_id),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                'popup_response_data': popup_response_data,
            })


        if self.has_change_permission(request, None):
            post_url = reverse(
                'admin:%s_%s_changelist' % (opts.app_label, opts.model_name),
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, post_url
            )
        else:
            post_url = reverse('admin:index', current_app=self.admin_site.name)

        return HttpResponseRedirect(post_url)
