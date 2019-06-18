import mammoth
import base64
from pathlib import Path
import shortuuid
import datetime
import os
from autopost.utils.html import HtmlStorage
from django.conf import settings


class QtConvert:

    @staticmethod
    def convert_image(image):
        """
        "data:{0};base64,{1}".format(image.content_type, encoded_src)
        :param image:
        :return:
        """
        with image.open() as image_bytes:
            encoded_src = base64.b64encode(image_bytes.read()).decode("ascii")
        base_path = Path('media/article/') / datetime.datetime.now().strftime('%Y%m%d')
        if not base_path.is_dir():
            os.makedirs(base_path)
        file_name = shortuuid.uuid() + '.jpg'
        image_path = base_path.joinpath(file_name)
        with open(str(image_path), 'wb') as image_file:
            image_file.write(base64.b64decode(encoded_src))
        # 上传图片到七牛空间
        ret, info = HtmlStorage.upload_qiniu(image_path.absolute(), file_name)
        file_path = settings.QINIU_URL + ret['key']
        return {
            "src": str(file_path)
        }

    @staticmethod
    def convert_html_text(doc_path):
        with open(doc_path, 'rb') as docx_file:
            result = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.img_element(QtConvert.convert_image))
        return result.value
