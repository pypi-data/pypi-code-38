import re

from ambition_prn.action_items import DEATH_REPORT_TMG_ACTION
from django.db.models import Q
from edc_dashboard.view_mixins import EdcViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin

from ...model_wrappers import TmgActionItemModelWrapper as BaseTmgActionItemModelWrapper


class TmgActionItemModelWrapper(BaseTmgActionItemModelWrapper):
    next_url_name = "tmg_death_listboard_url"


class DeathListboardView(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):

    listboard_template = "tmg_death_listboard_template"
    listboard_url = "tmg_death_listboard_url"
    listboard_back_url = "ambition_dashboard:tmg_home_url"
    listboard_panel_style = "warning"
    listboard_model = "edc_action_item.actionitem"
    listboard_model_manager_name = "objects"
    listboard_panel_title = "TMG: Death Reports"
    listboard_view_permission_codename = "edc_dashboard.view_tmg_listboard"
    model_wrapper_cls = TmgActionItemModelWrapper
    navbar_name = "ambition_dashboard"
    navbar_selected_item = "tmg_home"
    ordering = "-created"
    paginate_by = 25
    search_form_url = "tmg_death_listboard_url"
    search_fields = [
        "subject_identifier",
        "action_identifier",
        "parent_action_item__action_identifier",
        "related_action_item__action_identifier",
        "user_created",
        "user_modified",
    ]
    action_type_names = [DEATH_REPORT_TMG_ACTION]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get("subject_identifier"):
            context.update({"q": self.kwargs.get("subject_identifier")})
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(action_type__name__in=self.action_type_names)
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match("^[A-Z]+$", search_term):
            q = Q(first_name__exact=search_term)
        return q
