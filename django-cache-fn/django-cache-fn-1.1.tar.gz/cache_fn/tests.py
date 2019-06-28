#coding=utf-8
import time
import json
from pprint import pprint
from django.test import TestCase
from common import decorators
from cache_fn.decorators import cache_fn
from django.test.client import RequestFactory
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache

TEST_PREFIX='test.cache'
TEST_SLEEP=0.1
TEST_TIMEOUT=1
TEST_CACHE_TTL=10

@cache_fn(timeout=TEST_TIMEOUT, prefix=TEST_PREFIX, cache_ttl=TEST_CACHE_TTL)
def testRequest(request, user_name):
    d = {'res': 'request', 'time': time.time(), 'user': user_name}
    return JsonResponse(d, safe=False)

@cache_fn(timeout=TEST_TIMEOUT, prefix=TEST_PREFIX, cache_ttl=TEST_CACHE_TTL)
def testJsonResp(k, k2):
    d = {'res': str(k)+str(k2), 'time': time.time()}
    return JsonResponse(d, safe=False)

@cache_fn(timeout=TEST_TIMEOUT, prefix=TEST_PREFIX, cache_ttl=TEST_CACHE_TTL)
def testNormal(k, k2):
    d = {'res': str(k)+str(k2), 'time': time.time()}
    return d

class CacheTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        super(CacheTestCase, self).setUp()

    def tearDown(self):
        super(CacheTestCase, self).tearDown()

    def helper(self, fn, expect, *arg, **kw):
        data = {}
        i=0
        while i<3:
            resp = fn(*arg, **kw)
            if isinstance(resp, HttpResponse):
                self.assertEqual(resp.status_code, 200)
                jd = json.loads(resp.content)
            else:
                jd = resp

            self.assertTrue(expect(jd))
            print(jd)
            data[i] = float(jd['time'])
            i = i+1
            if i<2:
                time.sleep(TEST_SLEEP)
            else:
                time.sleep(TEST_TIMEOUT)

        self.assertEqual(data[0], data[1])
        self.assertFalse(data[0] == data[2])

    def testCacheWithArg(self):
        request = self.factory.get('/test1')
        d = {'fn': 'request', 'time': time.time(), 'user': 'user1'}
        expect1 = lambda d: d['res'] == 'request'
        self.helper(testRequest, expect=expect1, request=request, user_name='user1')

        expect2 = lambda d: d['res'] == 'k1k2'
        self.helper(testNormal, expect=expect2, k='k1', k2='k2')
        expect3 = lambda d: d['res'] == 'k3k4'
        self.helper(testJsonResp, expect=expect3, k='k3', k2='k4')
