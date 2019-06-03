""" Integration Test for Type Version Manager Rest API
"""
import json

from django.core.urlresolvers import reverse
from django.test import override_settings
from rest_framework import status

from core_composer_app.components.type import api as type_api
from core_composer_app.rest.type_version_manager import views
from core_main_app.components.version_manager import api as vm_api
from core_main_app.utils.integration_tests.integration_base_test_case import \
    MongoIntegrationBaseTestCase
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from tests.components.type_version_manager.fixtures.fixtures import TypeVersionManagerFixtures

fixture_type = TypeVersionManagerFixtures()


class TestGlobalTypeVersionManagerList(MongoIntegrationBaseTestCase):
    fixture = fixture_type

    def setUp(self):
        super(TestGlobalTypeVersionManagerList, self).setUp()

    def test_get_returns_http_200(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.GlobalTypeVersionManagerList.as_view(), user)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_returns_all_global_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.GlobalTypeVersionManagerList.as_view(), user)

        # Assert
        self.assertEqual(len(response.data), 1)

    def test_get_returned_tvm_are_global(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.GlobalTypeVersionManagerList.as_view(), user)

        # Assert
        self.assertEqual(response.data[0]['user'], None)

    def test_get_filtered_by_correct_title_returns_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.GlobalTypeVersionManagerList.as_view(),
                                              user,
                                              data={'title': self.fixture.type_vm_1.title})

        # Assert
        self.assertEqual(len(response.data), 1)

    def test_get_filtered_by_incorrect_title_returns_no_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.GlobalTypeVersionManagerList.as_view(),
                                              user,
                                              data={'title': 'bad title'})

        # Assert
        self.assertEqual(len(response.data), 0)

    def test_get_filtered_by_expected_is_disabled_returns_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.GlobalTypeVersionManagerList.as_view(),
                                              user,
                                              data={'is_disabled': self.fixture.type_vm_1.is_disabled})

        # Assert
        self.assertEqual(len(response.data), 1)

    def test_get_filtered_by_incorrect_is_disabled_returns_no_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.GlobalTypeVersionManagerList.as_view(),
                                              user,
                                              data={'is_disabled': not self.fixture.type_vm_1.is_disabled})

        # Assert
        self.assertEqual(len(response.data), 0)


class TestUserTypeVersionManagerList(MongoIntegrationBaseTestCase):
    fixture = fixture_type

    def setUp(self):
        super(TestUserTypeVersionManagerList, self).setUp()

    def test_get_returns_http_200(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.UserTypeVersionManagerList.as_view(), user)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_returns_all_user_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.UserTypeVersionManagerList.as_view(), user)

        # Assert
        self.assertEqual(len(response.data), 1)

    def test_get_returned_tvm_are_from_user(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.UserTypeVersionManagerList.as_view(), user)

        # Assert
        self.assertEqual(response.data[0]['user'], '1')

    def test_get_filtered_by_correct_title_returns_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.UserTypeVersionManagerList.as_view(),
                                              user,
                                              data={'title': self.fixture.type_vm_2.title})

        # Assert
        self.assertEqual(len(response.data), 1)

    def test_get_filtered_by_incorrect_title_returns_no_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.UserTypeVersionManagerList.as_view(),
                                              user,
                                              data={'title': 'bad title'})

        # Assert
        self.assertEqual(len(response.data), 0)

    def test_get_filtered_by_expected_is_disabled_returns_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.UserTypeVersionManagerList.as_view(),
                                              user,
                                              data={'is_disabled': self.fixture.type_vm_2.is_disabled})

        # Assert
        self.assertEqual(len(response.data), 1)

    def test_get_filtered_by_incorrect_is_disabled_returns_no_tvm(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(views.UserTypeVersionManagerList.as_view(),
                                              user,
                                              data={'is_disabled': not self.fixture.type_vm_2.is_disabled})

        # Assert
        self.assertEqual(len(response.data), 0)


class TestUserTypeList(MongoIntegrationBaseTestCase):
    fixture = fixture_type

    def setUp(self):
        super(TestUserTypeList, self).setUp()
        type_content = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                       "<xs:simpleType name='temperature'>" \
                       "<xs:restriction base='xs:string'>" \
                       "<xs:enumeration value='Kelvin'/>" \
                       "<xs:enumeration value='Celsius'/>" \
                       "<xs:enumeration value='Fahrenheit'/>" \
                       "</xs:restriction></xs:simpleType>" \
                       "</xs:schema>"
        self.data = {"title": "title",
                     "filename": "filename",
                     "content": type_content}

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_returns_http_201(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_post(views.UserTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_owner_is_user(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_post(views.UserTypeList.as_view(),
                                               user,
                                               data=self.data)

        # get type version manager from posted type
        type_id = response.data['id']
        type_object = type_api.get(type_id)
        type_version_manager = vm_api.get_from_version(type_object)

        # Assert
        self.assertEqual(type_version_manager.user, user.id)

    def test_post_type_name_already_exists_returns_http_400(self):
        # Arrange
        user = create_mock_user('1')
        self.data['title'] = self.fixture.type_vm_1.title

        # Act
        response = RequestMock.do_request_post(views.UserTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_type_with_correct_dependency_returns_http_201(self):
        # Arrange
        user = create_mock_user('1')
        self.data['content'] = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                               "<xs:include schemaLocation='type1_1.xsd'/>" \
                               "<xs:simpleType name='root'/></xs:schema>"

        self.data['dependencies_dict'] = json.dumps({"type1_1.xsd": str(self.fixture.type_1_1.id)})

        # Act
        response = RequestMock.do_request_post(views.UserTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        # FIXME: unable to download self dependency because server not running
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_download_url = reverse("core_main_app_rest_template_download",
                                        kwargs={'pk': self.fixture.type_1_1.id})
        self.assertTrue(expected_download_url in response.data['message'])

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_type_with_incorrect_dependency_schemaLocation_returns_http_400(self):
        # Arrange
        user = create_mock_user('1')
        self.data['content'] = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                               "<xs:include schemaLocation='type1_1.xsd'/>" \
                               "<xs:simpleType name='root'/></xs:schema>"

        self.data['dependencies_dict'] = json.dumps({"test.xsd": str(self.fixture.type_1_1.id)})

        # Act
        response = RequestMock.do_request_post(views.UserTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_type_with_incorrect_dependency_id_returns_http_400(self):
        # Arrange
        user = create_mock_user('1')
        self.data['content'] = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                               "<xs:include schemaLocation='type1_1.xsd'/>" \
                               "<xs:simpleType name='root'/></xs:schema>"

        self.data['dependencies_dict'] = json.dumps({"type1_1.xsd": "bad_id"})

        # Act
        response = RequestMock.do_request_post(views.UserTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestGlobalTypeList(MongoIntegrationBaseTestCase):
    fixture = fixture_type

    def setUp(self):
        super(TestGlobalTypeList, self).setUp()
        type_content = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>" \
                       "<xs:simpleType name='temperature'>" \
                       "<xs:restriction base='xs:string'>" \
                       "<xs:enumeration value='Kelvin'/>" \
                       "<xs:enumeration value='Celsius'/>" \
                       "<xs:enumeration value='Fahrenheit'/>" \
                       "</xs:restriction></xs:simpleType>" \
                       "</xs:schema>"
        self.data = {"title": "title",
                     "filename": "filename",
                     "content": type_content}

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_returns_http_201_if_user_is_staff(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_post(views.GlobalTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_returns_http_403_if_user_is_superuser(self):
        # Arrange
        user = create_mock_user('1', is_superuser=True)

        # Act
        response = RequestMock.do_request_post(views.GlobalTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_returns_http_403_if_user_does_not_have_permission(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_post(views.GlobalTypeList.as_view(),
                                               user,
                                               data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_post_owner_is_global(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_post(views.GlobalTypeList.as_view(),
                                               user,
                                               data=self.data)

        # get type version manager from posted type
        type_id = response.data['id']
        type_object = type_api.get(type_id)
        type_version_manager = vm_api.get_from_version(type_object)

        # Assert
        self.assertEqual(type_version_manager.user, None)
