#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `API_callers` package."""
from unittest import TestCase
from API_callers.user import APIUser


class MockAPIUser(APIUser):
    @property
    def _token(self):
        return {'token': 'JWT token'}


class TestAPIUser(TestCase):
    def test_receiving_json(self):
        user = MockAPIUser('http://www.example.com', {'login': 'user', 'password': 'pass'})
        token = user.get_token()
        self.assertIsNotNone(token)
        self.assertIn(type(token), (dict, str))


