# Copyright (c) 2019  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Valerij Maljulin <vmaljuli@redhat.com>


import json
from mock import patch, Mock
import pytest
from module_build_service.utils.greenwave import greenwave
from tests import make_module


class TestGreenwaveQuery():
    @patch("module_build_service.utils.greenwave.requests")
    def test_greenwave_query_decision(self, mock_requests):
        resp_status = 200
        resp_content = {
            "applicable_policies": ["osci_compose_modules"],
            "policies_satisfied": True,
            "satisfied_requirements": [
                {
                    "result_id": 7336633,
                    "testcase": "test-ci.test-module.tier1",
                    "type": "test-result-passed"
                },
                {
                    "result_id": 7336650,
                    "testcase": "test-ci.test-module.tier2",
                    "type": "test-result-passed"
                }
            ],
            "summary": "All required tests passed",
            "unsatisfied_requirements": []
        }
        response = Mock()
        response.json.return_value = resp_content
        response.status_code = resp_status
        mock_requests.post.return_value = response

        fake_build = make_module("pkg:0.1:1:c1", requires_list={"platform": "el8"})

        got_response = greenwave.query_decision(fake_build, prod_version="xxxx-8")

        assert got_response == resp_content
        assert json.loads(mock_requests.post.call_args_list[0][1]["data"]) == {
            "decision_context": "test_dec_context",
            "product_version": "xxxx-8", "subject_type": "some-module",
            "subject_identifier": "pkg-0.1-1.c1"}
        assert mock_requests.post.call_args_list[0][1]["headers"] == {
            "Content-Type": "application/json"}
        assert mock_requests.post.call_args_list[0][1]["url"] == \
            "https://greenwave.example.local/api/v1.0/decision"

    @pytest.mark.parametrize("return_all", (False, True))
    @patch("module_build_service.utils.greenwave.requests")
    def test_greenwave_query_policies(self, mock_requests, return_all):
        resp_status = 200
        resp_content = {
            "policies": [
                {
                    "decision_context": "test_dec_context",
                    "product_versions": ["ver1", "ver3"],
                    "rules": [],
                    "subject_type": "some-module"
                },
                {
                    "decision_context": "test_dec_context",
                    "product_versions": ["ver1", "ver2"],
                    "rules": [],
                    "subject_type": "some-module"
                },
                {
                    "decision_context": "decision_context_2",
                    "product_versions": ["ver4"],
                    "rules": [],
                    "subject_type": "subject_type_2"
                }
            ]
        }
        selected_policies = {"policies": resp_content["policies"][:-1]}

        response = Mock()
        response.json.return_value = resp_content
        response.status_code = resp_status
        mock_requests.get.return_value = response

        got_response = greenwave.query_policies(return_all)

        if return_all:
            assert got_response == resp_content
        else:
            assert got_response == selected_policies
        assert mock_requests.get.call_args_list[0][1]["url"] == \
            "https://greenwave.example.local/api/v1.0/policies"

    @patch("module_build_service.utils.greenwave.requests")
    def test_greenwave_get_product_versions(self, mock_requests):
        resp_status = 200
        resp_content = {
            "policies": [
                {
                    "decision_context": "test_dec_context",
                    "product_versions": ["ver1", "ver3"],
                    "rules": [],
                    "subject_type": "some-module"
                },
                {
                    "decision_context": "test_dec_context",
                    "product_versions": ["ver1", "ver2"],
                    "rules": [],
                    "subject_type": "some-module"
                },
                {
                    "decision_context": "decision_context_2",
                    "product_versions": ["ver4"],
                    "rules": [],
                    "subject_type": "subject_type_2"
                }
            ]
        }
        expected_versions = {"ver1", "ver2", "ver3"}

        response = Mock()
        response.json.return_value = resp_content
        response.status_code = resp_status
        mock_requests.get.return_value = response

        versions_set = greenwave.get_product_versions()

        assert versions_set == expected_versions
        assert mock_requests.get.call_args_list[0][1]["url"] == \
            "https://greenwave.example.local/api/v1.0/policies"

    @pytest.mark.parametrize("policies_satisfied", (True, False))
    @patch("module_build_service.utils.greenwave.requests")
    def test_greenwave_check_gating(self, mock_requests, policies_satisfied):
        resp_status = 200
        policies_content = {
            "policies": [
                {
                    "decision_context": "test_dec_context",
                    "product_versions": ["ver1", "ver3"],
                    "rules": [],
                    "subject_type": "some-module"
                }
            ]
        }

        responses = [Mock() for i in range(3)]
        for r in responses:
            r.status_code = resp_status
        responses[0].json.return_value = policies_content
        responses[1].json.return_value = {"policies_satisfied": False}
        responses[2].json.return_value = {"policies_satisfied": policies_satisfied}
        mock_requests.get.return_value = responses[0]
        mock_requests.post.side_effect = responses[1:]

        fake_build = make_module("pkg:0.1:1:c1", requires_list={"platform": "el8"})
        result = greenwave.check_gating(fake_build)

        assert result == policies_satisfied
