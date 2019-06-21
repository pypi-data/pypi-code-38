from django.views.generic import TemplateView, View
from django.http.response import HttpResponse, JsonResponse
from autopost.utils.crawler import QtCrawler
from autopost.models import AutoTask
from urllib import parse
from system.utils.convert import QtConvert
from pathlib import Path
import datetime
import os
from django.views.decorators.csrf import csrf_exempt


class IndexView(View):
    # template_name = ''

    def dispatch(self, request, *args, **kwargs):
        crawler = QtCrawler()
        return JsonResponse({'code': 200, 'msg': '处理完毕'})


class PreviewList(View):
    def dispatch(self, request, *args, **kwargs):
        ret_data = {'code': 400, 'data': []}
        crawler = QtCrawler()
        url = parse.unquote(request.GET.get('page_url'))
        patterns = parse.unquote(request.GET.get('pattern'))
        if url and patterns:
            articles = crawler.crawl_list(url, patterns, True)
            ret_data['code'] = 200
            ret_data['data'] = articles
        return JsonResponse(ret_data)


class PreviewDetail(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        ret_data = {'code': 400, 'data': []}
        crawler = QtCrawler()
        detail_url = parse.unquote(request.GET.get('detail_url'))
        title_pattern = parse.unquote(request.GET.get('title_pattern'))
        content_pattern = parse.unquote(request.GET.get('content_pattern'))
        exclude_pattern = parse.unquote(request.GET.get('exclude_pattern'))
        title_replace = parse.unquote(request.GET.get('title_replace'))
        content_replace = parse.unquote(request.GET.get('content_replace'))
        lazy_photo = parse.unquote(request.GET.get('lazy_photo'))
        if detail_url and title_pattern and content_pattern:
            title, main_content = crawler.crawl_detail(detail_url, title_pattern, content_pattern, exclude_pattern,
                                                       title_replace=title_replace, content_replace=content_replace,
                                                       lazy_photo=lazy_photo, fetch_img=True, preview=True)
            ret_data['code'] = 200
            ret_data['data'] = {'title': title, 'content': str(main_content)}
        return JsonResponse(ret_data)


class CrawNewsView(View):
    def dispatch(self, request, *args, **kwargs):
        ret_data = {
            'code': 500,
            'data': [],
            'message': ''
        }
        crawler = QtCrawler()
        try:
            result = crawler.crawl_news(task_id=kwargs.get('task_id'))
            if result:
                ret_data['code'] = 200
                ret_data['message'] = '任务执行成功,请在文章列表查看.'
            else:
                ret_data['code'] = 201
                ret_data['message'] = '任务执行失败,请检查系统LOG.'
        except Exception as e:
            ret_data['code'] = 300
            ret_data['message'] = '任务执行失败,未知异常. %s ' % str(e)
        return JsonResponse(ret_data)


class CopyTaskView(View):
    def dispatch(self, request, *args, **kwargs):
        ret_data = {
            'code': 200,
            'data': [],
            'message': ''
        }
        task = AutoTask.objects.get(pk=kwargs.get('task_id'))
        task.id = None
        task.save()
        ret_data['data'] = {'id': task.id}
        return JsonResponse(ret_data)


class ConvertDocxView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        ret_data = {
            'code': 200,
            'data': '',
            'message': ''
        }
        doc_file = request.FILES.get('file')
        base_path = Path('media/files/') / datetime.datetime.now().strftime('%Y%m%d')
        if not base_path.is_dir():
            os.makedirs(base_path)
        doc_path = base_path.joinpath(doc_file.name)
        with open(doc_path, 'wb') as file:
            for chunk in doc_file.chunks():
                file.write(chunk)

        # 解析文稿
        html = QtConvert.convert_html_text(doc_path.absolute())
        ret_data['data'] = html
        return JsonResponse(ret_data)
