from queryset_gallery.paginator import Paginator, QuerySetPaginator


class Gallery(object):
    """Base interface for galleries

    Args:
        `paginator` (Paginator): paginator that will be use
        `filters` (list): includes Filter object that can be use

    Methods:
        `get_page`: apply filters and get necessary page
    """
    paginator = Paginator
    filters = []

    def _apply_filters(self, objects, params_filter):
        for f in self.filters:
            objects = f.apply_dict_params(objects, params_filter)
        return objects

    def get_page(self, objects, filter_params, page_number, per_page):
        objects = self._apply_filters(objects, filter_params)
        paginator = self.paginator(objects, per_page)
        objects, pagination_data = paginator.get_page(number=page_number)
        return objects, pagination_data


class QuerySetGallery(Gallery):
    paginator = QuerySetPaginator
