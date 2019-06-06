import logging
import unittest

from sequoia import criteria

logging.basicConfig(level=logging.DEBUG)


class TestCriteria(unittest.TestCase):
    def test_add_given_inclusion_with_duplicated_field_then_field_should_be_added_only_once(self):
        my_criteria = criteria.Criteria().add(inclusion=criteria.Inclusion.resource("assets").fields("ref", "ref"))

        assert len(my_criteria.inclusion_entries) == 1
        assert len(my_criteria._get_inclusion_entries()[0]._get_fields()) == 1
        assert my_criteria._get_inclusion_entries()[0].resource_name == "assets"

    def test_get_criteria_params_given_more_than_one_inclusion_then_inclusion_param_should_be_created_properly(self):
        my_criteria = criteria.Criteria()\
            .add(inclusion=criteria.Inclusion.resource("assets"))\
            .add(inclusion=criteria.Inclusion.resource("contents"))

        params = my_criteria.get_criteria_params()

        assert len(params) == 1
        assert params == {"include": "assets,contents"}

    def test_get_criteria_params_given_one_inclusion_with_fields_then_inclusion_params_should_be_created(self):
        my_criteria = criteria.Criteria()\
            .add(inclusion=criteria.Inclusion.resource("assets").fields("ref", "name"))

        params = my_criteria.get_criteria_params()

        assert len(params) == 2
        assert params["include"] == "assets"
        assert params["assets.fields"] == "name,ref"

    def test_get_criteria_params_given_simple_criterion_then_param_should_be_created_properly(self):
        my_criteria = criteria.Criteria()\
            .add(criterion=criteria.StringExpressionFactory.field("contentRef").equal_to("theContentRef"))

        params = my_criteria.get_criteria_params()

        assert len(params) == 1
        assert params["withContentRef"] == "theContentRef"
