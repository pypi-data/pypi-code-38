""" Import functions and methods. """
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
""" Import from local app. """
from .models import CategoryModel
from .models import ArticleModel
from .forms import CategoryForm
from .forms import ArticleForm


""" password protected view, Dashboard view for appone app. """
# ArticleListDashboard returns the list of articles associated with registred admin user.
@login_required()
def ArticleListDashboard(request):
    template_name = 'djangoadmin/djangopost/article_list_dashboard.html'
    article_filter = ArticleModel.objects.filter(author=request.user)
    context = {'article_filter': article_filter}
    return render(request, template_name, context)


""" password protected view, Dashboard view for managing categories. """
# CategoryListDashboard returns the list of categories.
@login_required()
def CategoryListDashboard(request):
    template_name = 'djangoadmin/djangopost/category_list_dashboard.html'
    category_list = CategoryModel.objects.all()
    context = {'category_list': category_list}
    return render(request, template_name, context)


# Create your home views here.
def ArticleListView(request):
    template_name = 'djangoadmin/djangopost/article_list_view.html'
    category_filter = CategoryModel.objects.filter_publish()
    article_filter = ArticleModel.objects.filter_publish()
    is_promoted = ArticleModel.objects.is_promoted()
    is_trending = ArticleModel.objects.is_trending()
    context = { 'category_filter': category_filter, 'article_filter': article_filter,
                'is_promoted': is_promoted, 'is_trending': is_trending }
    return render(request, template_name, context)


# Create your category view here
def CategoryDetailView(request, category_slug):
    template_name = 'djangoadmin/djangopost/category_detail_view.html'
    category_detail = CategoryModel.objects.get(slug=category_slug)
    article_list = ArticleModel.objects.all()
    article_filter = article_list.filter(category=category_detail)
    # Exclude the articles by current category.
    exclude_current_category = CategoryModel.objects.exclude(title=category_detail)
    context = { 'category_detail': category_detail, 'article_filter': article_filter,
                'article_list': article_list, 'exclude_category': exclude_current_category }
    return render(request, template_name, context)


# Create your article view here
def ArticleDetailView(request, article_slug):
    template_name = 'djangoadmin/djangopost/article_detail_view.html'
    article_detail = ArticleModel.objects.get(slug=article_slug)
    context = { 'article_detail': article_detail }
    return render(request, template_name, context)


""" password protected view, create new category. """
# CategoryCreateView is here, Login required.
@login_required()
def CategoryCreateView(request):
    template_name = 'djangoadmin/djangopost/category_create_view_form.html'
    if request.method == 'POST':
        categoryform = CategoryForm(request.POST or None)
        if categoryform.is_valid():
            instance = categoryform.save(commit=False)
            instance.author = request.user
            instance.save()
            messages.success(request, 'Category created successfully.', extra_tags='success')
            return redirect('djangopost:category_list_dashboard')
        else:
            messages.error(request, 'Something happened wrong!', extra_tags='warning')
            return redirect('djangopost:category_create_view')
    else:
        categoryform = CategoryForm()
        context = { 'category_form': categoryform }
        return render(request, template_name, context)


""" password protected view, update any existting category. """
# CategoryUpdateView is here, Login required.
@login_required()
def CategoryUpdateView(request, category_slug):
    template_name = 'djangoadmin/djangopost/category_create_view_form.html'
    category_detail = CategoryModel.objects.get(slug=category_slug)
    if request.method == 'POST':
        categoryform  = CategoryForm(request.POST or None, instance=category_detail)
        if categoryform.is_valid():
            categoryform.save()
            messages.success(request, 'Category updated successfully.', extra_tags='success')
            return redirect('djangopost:category_list_dashboard')
        else:
            messages.error(request, 'Something happened wrong!', extra_tags='warning')
            return redirect('djangopost:category_list_dashboard')
    else:
        categoryform = CategoryForm(instance=category_detail)
        context = { 'category_form': categoryform }
        return render(request, template_name, context)


""" password protected view, category category. """
# CategoryDeleteView is here, Login required.
@login_required()
def CategoryDeleteView(request, category_slug):
    template_name = 'djangoadmin/djangopost/category_delete_view_form.html'
    category_detail = CategoryModel.objects.get(slug=category_slug)
    if request.method == 'POST':
        category_detail.delete()
        messages.success(request, 'Category deleted successfully.', extra_tags='success')
        return redirect('djangopost:category_list_dashboard')
    else:
        context = {'category_detail': category_detail }
        return render(request, template_name, context)


""" password protected view, create article view. """
# ArticleCreateView is here, Login required.
@login_required()
def ArticleCreateView(request):
    template_name = 'djangoadmin/djangopost/article_create_view_form.html'
    if request.method == 'POST':
        articleform = ArticleForm(request.POST or None, request.FILES or None)
        if articleform.is_valid():
            instance = articleform.save(commit=False)
            instance.author = request.user
            instance.save()
            messages.success(request, 'Article created successfully.', extra_tags='success')
            return redirect('djangopost:article_list_dashboard')
        else:
            messages.error(request, 'Something went wrong.', extra_tags='warning')
            return redirect('djangopost:article_create_view')
    else:
        articleform = ArticleForm()
        context = {'article_form': articleform}
        return render(request, template_name, context)


""" password protected view, update any existting article. """
# ArticleUpdateView is here, Login required.
@login_required()
def ArticleUpdateView(request, article_slug):
    template_name = 'djangoadmin/djangopost/article_create_view_form.html'
    article_detail = ArticleModel.objects.get(slug=article_slug)
    if request.method == 'POST':
        articleform  = ArticleForm(request.POST or None, request.FILES or None, instance=article_detail)
        if articleform.is_valid():
            instance = articleform.save(commit=False)
            instance.author = request.user
            instance.save()
            messages.success(request, 'Article updated successfully.', extra_tags='success')
            return redirect('djangopost:article_list_dashboard')
        else:
            messages.error(request, 'Something happened wrong!', extra_tags='warning')
            return redirect('djangopost:article_list_dashboard')
    else:
        articleform = ArticleForm(instance=article_detail)
        context = { 'article_form': articleform }
        return render(request, template_name, context)


""" password protected view, article delete view. """
# ArticleDeleteView is here, Login required.
@login_required()
def ArticleDeleteView(request, article_slug):
    template_name = 'djangoadmin/djangopost/article_delete_view_form.html'
    article_detail = ArticleModel.objects.get(slug=article_slug)
    if request.method == 'POST':
        article_detail.delete()
        messages.warning(request, 'article deleted successfully.', extra_tags='warning')
        return redirect('djangopost:article_list_dashboard')
    else:
        context = {'article_detail': article_detail }
        return render(request, template_name, context)
