# Removing this Comment Section violate The License Terms and 'Terms and Condition'.
"""
#################################################################################
Removing this Comment Section violate The License Terms and 'Terms and Condition'.
This Software 'Djangopost' published under the MIT  License. Permission is hereby
granted, free of  charge,  to any person obtaining  a copy  of this  software and
associated documentation  files (the "Software"), to deal  in the Software without
restriction, including  without  limitation the rights to use, copy, modify,merge,
publish,  distribute,  sublicense,  and/or   sell  copies of the Software, and  to
permit persons to whom the  Software  is  furnished  to  do  so,  subject  to  the
following conditions:

The above  copyright notice and  this permission  notice shall be included  in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF    MERCHANTABILITY,  FITNESS  FOR  A 
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR   COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ###############################################################################
You can contact to Author here.
Author : Vinit bhjram pawar
Email : bhojrampawar@hotmail.com
Website : vinitpawar.com
# ###############################################################################
"""


from . import views
from django.urls import include
from django.conf.urls import re_path


#app name
app_name = 'djangopost'


#urlpatterns go here
urlpatterns = [
    re_path(r'^api/', include('djangopost.rest_api.api_urls')),

    re_path(r'^article/dashboard/$', views.ArticleListDashboard, name='article_list_dashboard'),
    re_path(r'^category/dashboard/$', views.CategoryListDashboard, name='category_list_dashboard'),

    re_path(r'^article/(?P<article_slug>[\w-]+)/delete/$', views.ArticleDeleteView, name='article_delete_view'),
    re_path(r'^article/(?P<article_slug>[\w-]+)/update/$', views.ArticleUpdateView, name='article_update_view'),
    re_path(r'^article/create/$', views.ArticleCreateView, name='article_create_view'),

    re_path(r'^category/(?P<category_slug>[\w-]+)/delete/$', views.CategoryDeleteView, name='category_delete_view'),
    re_path(r'^category/(?P<category_slug>[\w-]+)/update/$', views.CategoryUpdateView, name='category_update_view'),
    re_path(r'^category/create/$', views.CategoryCreateView, name='category_create_view'),

    re_path(r'^article/(?P<article_slug>[\w-]+)/$', views.ArticleDetailView, name='article_detail_view'),
    re_path(r'^category/(?P<category_slug>[\w-]+)/$', views.CategoryDetailView, name='category_detail_view'),
    re_path(r'^$', views.ArticleListView, name='article_list_view'),
]
