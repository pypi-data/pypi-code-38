from django.urls import path
from .views import IndexView, PreviewDetail, PreviewList, CrawNewsView, CopyTaskView, ConvertDocxView

app_name = 'autopost'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('preview_list/', PreviewList.as_view(), name='preview_list'),
    path('preview_detail/', PreviewDetail.as_view(), name='preview_detail'),
    path('craw_news/<int:task_id>/', CrawNewsView.as_view(), name='craw_news'),
    path('copy_task/<int:task_id>/', CopyTaskView.as_view(), name='copy_task'),
    path('convert_docx/', ConvertDocxView.as_view(), name='convert_docx'),
]
