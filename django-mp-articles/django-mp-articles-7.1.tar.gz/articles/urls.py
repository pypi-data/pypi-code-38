
from django.urls import path

from articles import views


app_name = 'articles'


urlpatterns = [

    path('<str:type>/', views.ArticleListView.as_view(), name='list'),

    path('<str:type>/<str:slug>_<int:id>/',
         views.ArticleDetailView.as_view(), name='info')

]
