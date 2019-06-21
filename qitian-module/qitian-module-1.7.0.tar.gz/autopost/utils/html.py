import os, time, random
from django.conf import settings
from bs4 import BeautifulSoup, Tag
from django.utils import html
from urllib import request, parse
from textrank4zh import TextRank4Sentence, TextRank4Keyword
import shortuuid
import re
import datetime
from qiniu import Auth, put_file, BucketManager
from system.utils.tools import combine_folder
from autopost.models import RemoteImages
from django.db.models import Q


class HtmlStorage:
    """
    Html解析存储工具
    """

    @staticmethod
    def save_content(content, save_img=True, remove_a=True, send_qiniu=True, lazy_photo=''):
        """
        保存html中图片 并提取最一张图片
        :param content:
        :param remove_a:
        :param save_img:
        :param send_qiniu:
        :param lazy_photo:
        :return: html_content, first_img, key_list, summery
        """
        if not isinstance(content, Tag):
            soup = BeautifulSoup(content, 'lxml')
        else:
            soup = content
        all_imgs = soup.find_all('img')
        dir_name = '/article/' + datetime.datetime.now().strftime('%Y%m%d') + '/'
        if not os.path.exists(settings.MEDIA_ROOT + dir_name):
            os.makedirs(settings.MEDIA_ROOT + dir_name)
        first_img = ''
        for img in all_imgs:
            file_path = HtmlStorage.image_parse(img, dir_name, send_qiniu, save_img, lazy_photo=lazy_photo)
            if first_img == '':
                first_img = file_path
        html_content = ''
        for x in soup.contents:
            html_content += str(x)
        if remove_a:
            html_content = re.sub('</?a[^>]*>', '', html_content)
        # 关键词提取
        pure_text = html.strip_tags(html_content)
        tr_keyword = TextRank4Keyword()
        tr_keyword.analyze(pure_text)
        tr_sentence = TextRank4Sentence()
        tr_sentence.analyze(pure_text)
        if first_img.startswith(settings.MEDIA_URL):
            first_img = first_img[len(settings.MEDIA_URL):]
        try:
            ret_summery = tr_sentence.get_key_sentences(1)[0].sentence
        except Exception as ep:
            ret_summery = pure_text[:30]

        key_list = list()
        for item in tr_keyword.get_keywords(10, 2):
            key_list.append(item.word)

        return html_content, first_img, key_list, ret_summery

    @staticmethod
    def image_parse(img_tag, dir_name='', send_qiniu=False, save_img=True, lazy_photo=''):
        if not os.path.exists(settings.MEDIA_ROOT + dir_name):
            os.makedirs(settings.MEDIA_ROOT + dir_name)
        src_key = lazy_photo if lazy_photo else 'src'
        try:
            img_obj = parse.urlparse(img_tag[src_key])
            img_path = img_obj.path

            # 已经是本站文件不保存
            if (not img_obj.hostname or not settings.QINIU_URL.__contains__(img_obj.hostname)) and save_img:
                # 判断是不是微信图片
                if img_obj.netloc.__contains__('mmbiz.qpic.cn'):
                    new_query_str = str(img_obj.query).replace('tp=webp&', '')
                    new_query_obj = (
                        img_obj.scheme, img_obj.netloc, img_obj.path, img_obj.params, new_query_str,
                        img_obj.fragment)
                    query_url = parse.urlunparse(new_query_obj)
                    img_type = img_tag['data-type']
                    del img_tag['data-src']
                else:
                    img_type = img_path.split('.')[-1]
                    query_url = img_tag[src_key]
                if query_url.startswith('//'):
                    scheme = 'http' if img_obj.scheme == '' else img_obj.scheme
                    query_url = scheme + ":" + query_url
                # 检测是否需要保存图片
                if RemoteImages.objects.filter(Q(origin_src=query_url) | Q(remote_src=img_path)).exists():
                    remote_img = RemoteImages.objects.filter(Q(origin_src=query_url) | Q(remote_src=img_path)).get()
                    return remote_img.remote_src

                file_name = shortuuid.uuid() + '.' + img_type
                file_path = dir_name + file_name
                local_path = settings.MEDIA_ROOT + file_path

                if send_qiniu and not str(img_path).__contains__(settings.QINIU_URL):
                    ret, info = HtmlStorage.fetch_qiniu(query_url, file_name)
                    img_tag['src'] = settings.QINIU_URL + ret['key']
                else:
                    request.urlretrieve(query_url, settings.MEDIA_ROOT + file_path)
                    img_tag['src'] = settings.MEDIA_URL + file_path[1:]
                file_path = img_tag['src']
                # 存入图片记录表
                RemoteImages.objects.create(file_name=file_name, origin_src=query_url, local_src=local_path,
                                            remote_src=img_tag['src'])
            else:
                file_path = parse.urlunparse(img_obj)
        except Exception as e:
            print('%s! img utl:%s' % (str(e), img_tag['src']))
            file_path = img_tag[src_key]
        return file_path

    @staticmethod
    def fetch_qiniu(remote_url, file_name, file_type=1, bucket_name=settings.QINIU_BUCKET):
        """
        抓取远程图片上传
        :param remote_url:
        :param file_name:
        :param file_type:
        :param bucket_name:
        :return:
        """
        qiniu = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        upload_folder = combine_folder(settings.QINIU_FOLDER, datetime.datetime.now().strftime('%Y%m%d'))
        upload_name = upload_folder + file_name
        bucket = BucketManager(qiniu)
        ret, info = bucket.fetch(remote_url, bucket_name, upload_name)
        # 转换为指定存储类型
        if file_type == 1:
            bucket.change_type(bucket_name, ret['key'], file_type)
        return ret, info

    @staticmethod
    def upload_qiniu(local_url, file_name, file_type=1, bucket_name=settings.QINIU_BUCKET):
        qiniu = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        upload_folder = combine_folder(settings.QINIU_FOLDER, datetime.datetime.now().strftime('%Y%m%d'))
        upload_name = upload_folder + file_name
        policy = {
            "fileType": file_type
        }
        token = qiniu.upload_token(bucket_name, upload_name, 3600, policy)
        ret, info = put_file(token, upload_name, local_url)
        return ret, info

    @staticmethod
    def change_storage_type(prefix='', bucket_name=settings.QINIU_BUCKET, file_type=1):
        qiniu = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        bucket = BucketManager(qiniu)
        ret, eof, info = bucket.list(bucket_name, prefix=prefix)
        for item in ret['items']:
            bucket.change_type(bucket_name, item['key'], file_type)
