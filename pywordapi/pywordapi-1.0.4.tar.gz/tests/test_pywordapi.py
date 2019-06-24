from pywordapi import wordpress


def test_main():
    api_url = "https://demo.wp-api.org/"
    api = wordpress.Wordpress(api_url)
    results = api.get_posts()
    assert isinstance(results, dict) is True
