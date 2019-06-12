from unittest import TestCase

from nose.plugins.attrib import attr


@attr(test_type='unit')
class BaseTestCase(TestCase):
    def get_attribute_values(self, instance, attributes):
        return [getattr(instance, attribute) for attribute in attributes]
    
    def assertAttributesEqual(self, queryset, attributes, expected_results, *args, **kwargs):
        results = [self.get_attribute_values(instance, attributes) for instance in queryset]
        return self.assertEquals(results, expected_results, *args, **kwargs)

    def assertInstanceAttributesEqual(self, instance, attributes, expected_results, *args, **kwargs):
        results = self.get_attribute_values(instance, attributes)
        return self.assertEquals(results, expected_results, *args, **kwargs)

    def assertUnorderedListsEqual(self, result_list, expected_result_list, *args, **kwargs):
        return self.assertEquals(set(result_list), set(expected_result_list), *args, **kwargs)

    def assert_expected_file_content(self, output_filename, expected_output_filename):
        output = open(output_filename, 'r').read()
        expected_output = open(expected_output_filename, 'r').read()
        if output != expected_output:
            self.fail('Output file differs from expected output file. '
                      'Use "diff %s %s" for more details'
                      % (output_filename, expected_output_filename))
