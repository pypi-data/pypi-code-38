from django import test
from django.core.exceptions import ValidationError

from ievv_opensource.utils.validation_error_util import ValidationErrorUtil


class TestValidationErrorUtil(test.TestCase):
    def test_is_dict_based(self):
        self.assertFalse(ValidationErrorUtil(ValidationError('Error')).is_dict_based)
        self.assertFalse(ValidationErrorUtil(ValidationError(['Error1', 'Error2'])).is_dict_based)
        self.assertTrue(ValidationErrorUtil(ValidationError({'myfield': 'MyError'})).is_dict_based)

    def test_as_list(self):
        simpleerror = ValidationError('Error')
        self.assertEqual(len(ValidationErrorUtil(simpleerror).as_list()), 1)
        self.assertEqual(ValidationErrorUtil(simpleerror).as_list()[0].message, 'Error')

        listerror = ValidationError(['Error1', 'Error2'])
        self.assertEqual(len(ValidationErrorUtil(listerror).as_list()), 2)
        self.assertEqual(ValidationErrorUtil(listerror).as_list()[0].message, 'Error1')
        self.assertEqual(ValidationErrorUtil(listerror).as_list()[1].message, 'Error2')

        dicterror = ValidationError({'field1': ['Error1', 'Error2'], 'field2': 'Error3'})
        self.assertEqual(len(ValidationErrorUtil(dicterror).as_list()), 3)
        self.assertEqual(
            {validation_error.message for validation_error in ValidationErrorUtil(dicterror).as_list()},
            {'Error1', 'Error2', 'Error3'})

    def test_as_serializable_list(self):
        simpleerror = ValidationError('Error')
        self.assertEqual(len(ValidationErrorUtil(simpleerror).as_serializable_list()), 1)
        self.assertEqual(ValidationErrorUtil(simpleerror).as_serializable_list()[0], 'Error')

        listerror = ValidationError(['Error1', 'Error2'])
        self.assertEqual(len(ValidationErrorUtil(listerror).as_serializable_list()), 2)
        self.assertEqual(ValidationErrorUtil(listerror).as_serializable_list()[0], 'Error1')
        self.assertEqual(ValidationErrorUtil(listerror).as_serializable_list()[1], 'Error2')

        dicterror = ValidationError({'field1': ['Error1', 'Error2'], 'field2': 'Error3'})
        self.assertEqual(len(ValidationErrorUtil(dicterror).as_serializable_list()), 3)
        self.assertEqual(
            {validation_error for validation_error in ValidationErrorUtil(dicterror).as_serializable_list()},
            {'Error1', 'Error2', 'Error3'})

    def test_as_serializable_dict_simple(self):
        self.assertEqual(
            ValidationErrorUtil(ValidationError('Error')).as_serializable_dict(),
            {
                '__all__': ['Error']
            }
        )

    def test_as_serializable_dict_list(self):
        self.assertEqual(
            ValidationErrorUtil(ValidationError(['Error1', 'Error2'])).as_serializable_dict(),
            {
                '__all__': ['Error1', 'Error2']
            }
        )

    def test_as_serializable_dict_dict(self):
        self.assertEqual(
            ValidationErrorUtil(
                ValidationError({'field1': ['Error1', 'Error2'], 'field2': 'Error3'})
            ).as_serializable_dict(),
            {
                'field1': ['Error1', 'Error2'],
                'field2': ['Error3']
            }
        )

    def test_as_drf_validation_error_simple(self):
        drf_validation_error = ValidationErrorUtil(ValidationError('Error')).as_drf_validation_error()
        self.assertEqual(len(drf_validation_error.detail), 1)
        self.assertEqual(drf_validation_error.detail[0], 'Error')

    def test_as_drf_validation_error_simple_code(self):
        drf_validation_error = ValidationErrorUtil(ValidationError('Error', code='myerror')).as_drf_validation_error()
        self.assertEqual(drf_validation_error.detail[0].code, 'myerror')

    def test_as_drf_validation_error_list(self):
        drf_validation_error = ValidationErrorUtil(ValidationError(['Error1', 'Error2'])).as_drf_validation_error()
        self.assertEqual(len(drf_validation_error.detail), 2)
        self.assertEqual(drf_validation_error.detail[0], 'Error1')
        self.assertEqual(drf_validation_error.detail[1], 'Error2')

    def test_as_drf_validation_error_dict(self):
        drf_validation_error = ValidationErrorUtil(
            ValidationError({'field1': ['Error1', 'Error2'], 'field2': 'Error3'})
        ).as_drf_validation_error()
        self.assertEqual(set(drf_validation_error.detail.keys()), {'field1', 'field2'})
        self.assertEqual(drf_validation_error.detail['field1'][0], 'Error1')
        self.assertEqual(drf_validation_error.detail['field1'][1], 'Error2')
        self.assertEqual(drf_validation_error.detail['field2'][0], 'Error3')

    def test_as_drf_validation_error_dict_code(self):
        drf_validation_error = ValidationErrorUtil(
            ValidationError({
                'field1': [
                    ValidationError('Error1', code='customcode'),
                    'Error2'
                ],
                'field2': ValidationError('Error3', code='customcode2')
            })
        ).as_drf_validation_error()
        self.assertEqual(drf_validation_error.detail['field1'][0].code, 'customcode')
        self.assertEqual(drf_validation_error.detail['field1'][1].code, 'invalid')
        self.assertEqual(drf_validation_error.detail['field2'][0].code, 'customcode2')
