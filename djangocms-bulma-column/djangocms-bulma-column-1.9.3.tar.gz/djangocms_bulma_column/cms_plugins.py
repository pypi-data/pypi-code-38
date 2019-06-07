from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import MultiColumnForm
from .models import MultiColumns, Column


class MultiColumnPlugin(CMSPluginBase):
    model = MultiColumns
    module = _("Bulma Multi Columns")
    name = _("Bulma Multi Columns")
    render_template = "cms/plugins/multi_column.html"
    allow_children = True
    child_classes = ["ColumnPlugin"]
    form = MultiColumnForm

    def save_model(self, request, obj, form, change):
        response = super(MultiColumnPlugin, self).save_model(
            request, obj, form, change
        )
        for x in range(int(form.cleaned_data['create'])):
            col = Column(
                parent=obj,
                placeholder=obj.placeholder,
                language=obj.language,
                extra_css=form.cleaned_data.get('extra_css', ""),
                position=CMSPlugin.objects.filter(parent=obj).count(),
                plugin_type=ColumnPlugin.__name__
            )
            col.save()
        return response


class ColumnPlugin(CMSPluginBase):
    model = Column
    module = _("Bulma Multi Columns")
    name = _("Bulma Column")
    render_template = "cms/plugins/column.html"
    parent_classes = ["MultiColumnPlugin"]
    allow_children = True


plugin_pool.register_plugin(MultiColumnPlugin)
plugin_pool.register_plugin(ColumnPlugin)
