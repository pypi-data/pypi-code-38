
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from pure_pagination import PaginationMixin
from hitcount.views import HitCountDetailView

from articles.models import Article, ArticleType


class ArticleListView(PaginationMixin, ListView):

    template_name = 'articles/list.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.article_type = get_object_or_404(ArticleType, slug=kwargs['type'])
        return super(ArticleListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return self.article_type.articles.all()

    def get_context_data(self, **kwargs):
        cxt = super(ArticleListView, self).get_context_data(**kwargs)
        cxt['article_type'] = self.article_type
        return cxt


class ArticleDetailView(HitCountDetailView):

    template_name = 'articles/info.html'
    count_hit = True

    def get_object(self, queryset=None):
        return get_object_or_404(
            Article,
            type__slug=self.kwargs['type'],
            pk=self.kwargs['id'])
