""" Import functions and methods. """
from django.shortcuts import render, get_object_or_404
from django.views.generic import ( View, ListView, DetailView, CreateView,
UpdateView, DeleteView, FormView )
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
""" import from local app. """
from .models import CategoryModelScheme, ArticleModelScheme
from .forms import CategoryFormScheme, ArticleFormScheme


""" Password protected view, Dashboard view for apptwo app. """
# ArticleListDashboard view returns the list of articles.
class ArticleListDashboard(LoginRequiredMixin, ListView):
    model = ArticleModelScheme
    template_name = 'djangoadmin/djangoarticle/article_list_dashboard.html'
    context_object_name = 'article_filter'

    def get_queryset(self):
        return ArticleModelScheme.objects.filter(author=self.request.user)


""" Password protected view, manage category view for apptwo app. """
# CategoryListDashboard returns the list of category
class CategoryListDashboard(LoginRequiredMixin, ListView):
    model = CategoryModelScheme
    template_name = 'djangoadmin/djangoarticle/category_list_dashboard.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return CategoryModelScheme.objects.all()


# Djangoarticle Home view.
class ArticleListView(ListView):
    model = ArticleModelScheme
    template_name = 'djangoadmin/djangoarticle/article_list_view.html'
    context_object_name = 'article_filter'

    def get_queryset(self):
        return ArticleModelScheme.objects.filter_publish()

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['category_filter'] = CategoryModelScheme.objects.filter_publish()
        context['is_promoted'] = ArticleModelScheme.objects.filter_promoted()
        context['is_trending'] = ArticleModelScheme.objects.filter_trending()
        return context


# Djangoarticle Category view.
class CategoryDetailView(ListView):
    model = ArticleModelScheme
    template_name = 'djangoadmin/djangoarticle/category_detail_view.html'
    slug_url_kwarg = 'category_slug'
    context_object_name = 'article_filter'

    def get_queryset(self):
        self.category_detail = get_object_or_404(CategoryModelScheme, slug=self.kwargs['category_slug'])
        return ArticleModelScheme.objects.filter(category=self.category_detail)

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['category_detail'] = self.category_detail
        context['exclude_category'] = CategoryModelScheme.objects.exclude(title=self.category_detail)
        context['article_list'] = ArticleModelScheme.objects.all()
        return context


""" Start a full featured ArticleDetailView for both POST and GET method. """
class ArticleDetailView(DetailView):
    model = ArticleModelScheme
    template_name = 'djangoadmin/djangoarticle/article_detail_view.html'
    context_object_name = 'article_detail'
    slug_url_kwarg = 'article_slug'

    def get_object(self):
        object = super(ArticleDetailView, self).get_object()
        object.total_views += 1
        object.save()
        return object


""" Password protected view, category create view for apptwo app. """
class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = CategoryFormScheme
    template_name = 'djangoadmin/djangoarticle/category_create_view_form.html'
    success_url = reverse_lazy('djangoarticle:category_list_dashboard')
    success_message = "Category created successfully."

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super(CategoryCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CategoryCreateView, self).get_context_data(**kwargs)
        context['category_form'] = context['form']
        return context


""" Password protected view, category update view for apptwo app. """
class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CategoryModelScheme
    form_class = CategoryFormScheme
    template_name = 'djangoadmin/djangoarticle/category_create_view_form.html'
    success_url = reverse_lazy('djangoarticle:category_list_dashboard')
    slug_url_kwarg = 'category_slug'
    success_message = "Category updated successfully."

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super(CategoryUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CategoryUpdateView, self).get_context_data(**kwargs)
        context['category_form'] = context['form']
        return context


""" Password protected view, category delete view for apptwo app. """
class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = CategoryModelScheme
    context_object_name = 'category_detail'
    template_name = 'djangoadmin/djangoarticle/category_delete_view_form.html'
    success_url = reverse_lazy('djangoarticle:category_list_dashboard')
    slug_url_kwarg = 'category_slug'
    success_message = "Category deleted successfully"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(CategoryDeleteView, self).delete(request, *args, **kwargs)


""" Password protected view, article create view for apptwo app. """
class ArticleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = ArticleFormScheme
    template_name = 'djangoadmin/djangoarticle/article_create_view_form.html'
    success_url = reverse_lazy('djangoarticle:article_list_dashboard')
    success_message = "Article created successfully."

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super(ArticleCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ArticleCreateView, self).get_context_data(**kwargs)
        context['article_form'] = context['form']
        return context


""" Password protected view, article update view for apptwo app. """
class ArticleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ArticleModelScheme
    form_class = ArticleFormScheme
    template_name = 'djangoadmin/djangoarticle/article_create_view_form.html'
    success_url = reverse_lazy('djangoarticle:article_list_dashboard')
    slug_url_kwarg = 'article_slug'
    success_message = "Article updated successfully."

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super(ArticleUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ArticleUpdateView, self).get_context_data(**kwargs)
        context['article_form'] = context['form']
        return context


""" Password protected view, article delete view for apptwo app. """
class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = ArticleModelScheme
    context_object_name = 'article_detail'
    template_name = 'djangoadmin/djangoarticle/article_delete_view_form.html'
    success_url = reverse_lazy('djangoarticle:article_list_dashboard')
    slug_url_kwarg = 'article_slug'
    success_message = "Article deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ArticleDeleteView, self).delete(request, *args, **kwargs)