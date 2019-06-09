import arrow

from ambition_ae.action_items import AE_TMG_ACTION
from ambition_permissions import TMG
from django.core.exceptions import ObjectDoesNotExist
from edc_dashboard.view_mixins import EdcViewMixin
from edc_constants.constants import CLOSED, NEW, OPEN
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin

from ...model_wrappers import TmgActionItemModelWrapper


class TmgAeListboardView(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):

    ae_tmg_model = "ambition_ae.aetmg"

    listboard_template = "tmg_ae_listboard_template"
    listboard_url = "tmg_ae_listboard_url"
    listboard_back_url = "ambition_dashboard:tmg_home_url"
    listboard_panel_style = "warning"
    listboard_model = "edc_action_item.actionitem"
    listboard_panel_title = "TMG: AE Reports"
    listboard_view_permission_codename = "edc_dashboard.view_tmg_listboard"

    model_wrapper_cls = TmgActionItemModelWrapper
    navbar_name = "ambition_dashboard"
    navbar_selected_item = "tmg_home"
    ordering = "-report_datetime"
    paginate_by = 50
    search_form_url = "tmg_ae_listboard_url"
    action_type_names = [AE_TMG_ACTION]

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "parent_action_item__action_identifier",
        "related_action_item__action_identifier",
        "user_created",
        "user_modified",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["AE_TMG_ACTION"] = AE_TMG_ACTION
        context["utc_date"] = arrow.now().date()
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(action_type__name__in=self.action_type_names)
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return options

    def update_wrapped_instance(self, model_wrapper):
        model_wrapper.has_reference_obj_permissions = True
        model_wrapper.has_parent_reference_obj_permissions = True
        model_wrapper.has_related_reference_obj_permissions = True
        try:
            self.request.user.groups.get(name=TMG)
        except ObjectDoesNotExist:
            pass
        else:
            if (
                model_wrapper.reference_obj
                and model_wrapper.reference_obj._meta.label_lower == self.ae_tmg_model
            ):
                model_wrapper.has_reference_obj_permissions = (
                    model_wrapper.reference_obj.user_created
                    == self.request.user.username
                )
            if (
                model_wrapper.parent_reference_obj
                and model_wrapper.parent_reference_obj._meta.label_lower
                == self.ae_tmg_model
            ):  # noqa
                model_wrapper.has_parent_reference_obj_permissions = (
                    model_wrapper.parent_reference_obj.user_created
                    == self.request.user.username
                )  # noqa
            if (
                model_wrapper.related_reference_obj
                and model_wrapper.related_reference_obj._meta.label_lower
                == self.ae_tmg_model
            ):  # noqa
                model_wrapper.has_related_reference_obj_permissions = (
                    model_wrapper.related_reference_obj.user_created
                    == self.request.user.username
                )  # noqa
        return model_wrapper


class StatusTmgAeListboardView(TmgAeListboardView):

    status = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.status
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update({"status": self.status})
        return options


class NewTmgActionItemModelWrapper(TmgActionItemModelWrapper):
    next_url_name = "new_tmg_ae_listboard_url"


class OpenTmgActionItemModelWrapper(TmgActionItemModelWrapper):
    next_url_name = "open_tmg_ae_listboard_url"


class ClosedTmgActionItemModelWrapper(TmgActionItemModelWrapper):
    next_url_name = "closed_tmg_ae_listboard_url"


class NewTmgAeListboardView(StatusTmgAeListboardView):

    listboard_url = "new_tmg_ae_listboard_url"
    search_form_url = "new_tmg_ae_listboard_url"
    status = NEW
    listboard_panel_title = "TMG: New AE Reports"
    model_wrapper_cls = NewTmgActionItemModelWrapper


class OpenTmgAeListboardView(StatusTmgAeListboardView):

    listboard_url = "open_tmg_ae_listboard_url"
    search_form_url = "open_tmg_ae_listboard_url"
    status = OPEN
    listboard_panel_title = "TMG: Open AE Reports"
    model_wrapper_cls = OpenTmgActionItemModelWrapper


class ClosedTmgAeListboardView(StatusTmgAeListboardView):

    listboard_url = "closed_tmg_ae_listboard_url"
    search_form_url = "closed_tmg_ae_listboard_url"
    status = CLOSED
    listboard_panel_title = "TMG: Closed AE Reports"
    model_wrapper_cls = ClosedTmgActionItemModelWrapper
