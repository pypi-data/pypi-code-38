from django.db.models import Count
from wagtail.admin.edit_handlers import FieldPanel

from molo.core.models import ArticlePageTags


class TagPanel(FieldPanel):
    def on_instance_bound(self):
        super().on_instance_bound()
        target_model = self.bound_field.field.queryset.model

        data = ArticlePageTags.objects.values('tag').annotate(
            count=Count('tag')
        )
        tag_count = {tag['tag']: tag['count'] for tag in data}

        self.bound_field.field.queryset = target_model.objects.filter(
            id__in=tag_count
        )

        self.bound_field.field.label_from_instance = (
            lambda obj: str(obj) + ' ({})'.format(tag_count[obj.id])
        )
