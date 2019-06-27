from pywordapi import wordpress


def test_get_posts():
    api_url = "https://demo.wp-api.org/"
    api = wordpress.Wordpress(api_url)
    results = api.get_posts()
    assert isinstance(results, dict) is True


def test_get_categories():
    api_url = "https://demo.wp-api.org/"
    api = wordpress.Wordpress(api_url)
    results = api.get_categories()
    assert isinstance(results, dict) is True


def test_get_posts_from_non_existent_site():
    api_url = "https://demo.iamnotasite.xyz/"
    api = wordpress.Wordpress(api_url)
    results = api.get_posts()
    # print(results['error'])
    assert isinstance(results, dict) is True


def test_get_categories_from_non_existent_site():
    api_url = "https://demo.iamnotasite.xyz/"
    api = wordpress.Wordpress(api_url)
    results = api.get_categories()
    # print(results['error'])
    assert isinstance(results, dict) is True


def test_get_categories_from_non_wordpress_site():
    api_url = "https://httpbin.org/"
    api = wordpress.Wordpress(api_url)
    results = api.get_categories()
    # print(results)
    assert isinstance(results, dict) is True

# def test_get_posts_with_proxy():
    # api_url = "https://demo.wp-api.org/"
    # api_url = ""
    # # proxy_url = ""
    # api = wordpress.Wordpress(api_url, proxy_url)
    # results = api.get_posts()
    # assert isinstance(results, dict) is True
