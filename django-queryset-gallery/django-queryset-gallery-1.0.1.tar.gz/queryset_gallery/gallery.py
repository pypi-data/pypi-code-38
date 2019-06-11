from django.core.exceptions import FieldError
from django.shortcuts import Http404

from queryset_gallery.paginator import Paginator, QuerySetPaginator


class Gallery(object):
    """Base interface for galleries

    Args:
        `paginator` (Paginator): paginator that will be use
        `filters` (list): includes Filter objects (!not classes) that can be use

    Methods:
        `get_page`: apply filters and get necessary page
    """
    paginator = Paginator
    filters = []

    def _apply_filters(self, objects, params_filter):
        for f in self.filters:
            objects = f.apply_from_dict_params(objects=objects, params=params_filter)
        return objects

    def _not_found(self):
        pass

    def get_page(
            self, objects, page_number, per_page,
            filter_params: dict = None, sort_params: list = None
    ):
        filter_params = filter_params or dict()
        objects = self._apply_filters(objects, filter_params)
        paginator = self.paginator(objects, per_page)

        objects, pagination_data = paginator.get_page(page_number)
        pagination_data.get('errors') and self._not_found()
        return objects, pagination_data


class QuerySetGallery(Gallery):
    paginator = QuerySetPaginator
    model = None

    def _get_queryset(self):
        return self.model.objects.all()

    @staticmethod
    def _order_by(objects, lookups: list):
        try:
            return objects.order_by(*lookups)
        except FieldError:
            return objects

    def _not_found(self):
        raise Http404

    def get_page(
            self, page_number, per_page,
            filter_params: dict = None, sort_params: list = None,
            queryset=None
    ):
        objects = self._get_queryset() if not queryset else queryset
        objects = self._order_by(objects, sort_params or list())

        return super().get_page(
            page_number=page_number, per_page=per_page,
            filter_params=filter_params,
            objects=objects
        )
