import os
from unittest import mock, TestCase
from bebanjo.things import image_dict_prepare
from bebanjo.error import InvalidResourceError
from .utils import assert_send_body_calls_match, FileReader, title_from_file

IMAGE_5001 = 'IMAGE_5001.xml'

IMAGE_PATH_LOCAL = 'tests/image/1yeVJox3rjo2jBKrrihIMj7uoS9.JPEG'
IMAGE_PATH_REMOTE = 'https://mydomain.com/image/1yeVJox3rjo2jBKrrihIMj7uoS9.jpg'


class TestImage(TestCase):

    def test_image_dict_prepare(self):
        _, name = os.path.split(IMAGE_PATH_LOCAL)
        image_dict = {'IsPosterArt': True}
        with open(IMAGE_PATH_LOCAL, 'rb') as fh:
            image_dict_prepare(image_dict, name, None, fh)
        assert image_dict['IsPosterArt']
        assert image_dict['encoding'] == 'jpeg'
        assert image_dict['attachment'][:30] == 'data:image/jpeg;base64,/9j/4AA'
        assert image_dict['file_name'] == name

    @mock.patch('bebanjo.things.send_body')
    def test_title_create_image_local_file(self, m_send_body):
        title = title_from_file()
        m_send_body.return_value = FileReader(IMAGE_5001)
        meta = {'alt_name': 'thumb'}
        image = title.images.create_image(IMAGE_PATH_LOCAL, meta=meta)
        assert_send_body_calls_match(
            m_send_body,
            re_method='^POST$',
            re_url=r'.*/api/titles/1001/images$',
            re_body=[
                '^<image>.*</image>$',
                '<alt-name>thumb</alt-name>',
                '<encoding>jpeg</encoding>',
                '<attachment>data:image/jpeg;base64,.*</attachment>',
                '<file-name>1yeVJox3rjo2jBKrrihIMj7uoS9.JPEG</file-name>',
            ]
        )
        assert image.id == 5001

    @mock.patch('bebanjo.things.send_body')
    def test_title_create_image_local_file_override_meta(self, m_send_body):
        title = title_from_file()
        m_send_body.return_value = FileReader(IMAGE_5001)
        meta = {'encoding': 'png', 'file_name': 'poster.jpeg'}
        title.images.create_image(IMAGE_PATH_LOCAL, meta=meta)
        assert_send_body_calls_match(
            m_send_body,
            re_method='^POST$',
            re_url=r'.*/api/titles/1001/images$',
            re_body=[
                '<encoding>png</encoding>',
                '<file-name>poster.jpeg</file-name>',
            ]
        )
    
    @mock.patch('bebanjo.things.send_body')
    def test_create_image_on_non_image_raises(self, m_send_body):
        title = title_from_file()
        m_send_body.return_value = FileReader(IMAGE_5001)
        with self.assertRaises(InvalidResourceError):
            title.create_image(IMAGE_PATH_LOCAL)

    @mock.patch('bebanjo.things.send_body')
    def test_title_create_image_remote_file(self, m_send_body):
        title = title_from_file()
        m_send_body.return_value = FileReader(IMAGE_5001)
        image = title.images.create_image(IMAGE_PATH_REMOTE)
        assert_send_body_calls_match(
            m_send_body,
            re_method='^POST$',
            re_url=r'.*/api/titles/1001/images$',
        )
        assert image.id == 5001
