import pytest
from csirtg_indicator import Indicator
from pprint import pprint

DISABLE_TESTS = False
try:
    from csirtg_indicator.utils.predict import predict_urls, predict_fqdns, \
        predict_ips
    from csirtg_urlsml_tf import predict as predict_url

except:
    DISABLE_TESTS = True


@pytest.mark.skipif(DISABLE_TESTS, reason='missing csirtg ml libs..')
@pytest.mark.xfail
def test_indicator_predict():
    i = Indicator('https://g00gle.com/1.html')

    r = predict_urls(i)
    assert r[0].probability > .5

    r = predict_fqdns(Indicator('g00gle.com'))
    assert r[0].probability > .5
