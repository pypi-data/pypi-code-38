from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('detail/<int:pk>/', views.PostView.as_view(), name='post_info'),
    path('leave_a_comment/<int:post_id>', views.leave_a_comment,
         name='leave_a_comment')

]
