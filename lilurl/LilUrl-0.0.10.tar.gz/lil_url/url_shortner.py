import random
import string

from flask import Blueprint, redirect, request

from lil_url.helpers.redis_helper import get_redis


def shorten_url(url, url_slug=None, expiry=None, force_new=False):
    """Shortens the real URL to short URL.

    Parameters
    ----------
    `url`: <String>
        Long URL which is to be shorten.

    url_slug: <String>
        If any chosen slug to be served.

    expiry: <Int>
        expiry time in seconds.

    Returns
    -------
    <Dict>:
        Returns respnse dict.
    """

    response = {"success": False, "message": "", "code": "", "slug": "", "short_url": ''}
    from flask import current_app
    from lil_url import DEFAULT_PREFIX

    host, port = None, None
    if current_app.config.get("REDIS_HOST", None):
        host, port = current_app.config.get("REDIS_HOST"), current_app.config.get("REDIS_PORT", None)

    redis = get_redis(host, port)

    if url_slug:
        if redis.exists(url_slug):
            response["message"] = "The slug already exists. Try with a new one."
    else:
        if redis.exists(url):
            url_slug = redis.get(url)
        else:
            url_slug = _generate_url_slug()

    redis.set(url_slug, url)
    redis.set(url, url_slug)

    if expiry:
        redis.expire(url_slug, expiry)

    response["success"] = True
    response["slug"] = url_slug
    response["short_url"] = '{}/{}'.format(current_app.config.get('BASE_URL'), url_slug)

    return response


def server_url(slug):
    """Serves the short URL to new one.

    Parameters
    ----------
    `slug`: <String>
        Slug for which long URL to be served.

    Returns
    -------
        Redirects to the real/long URL.
    """

    host, port = None, None
    from flask import current_app
    if current_app.config.get("REDIS_HOST", None):
        host, port = current_app.config.get("REDIS_HOST", None), current_app.config.get('REDIS_PORT')

    redis = get_redis(host, port)

    if redis.exists(slug):
        return redirect(redis.get(slug))
    else:
        return redirect(redis.get(slug))


def _generate_url_slug(size=10, chars=string.ascii_lowercase + string.digits):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.

    Parameters
    ----------
    size: <Int>
        Size of the slug.

    chars: <string.class>
        Character class to be included in the slug.
    """

    slug = ''.join(random.choice(chars) for _ in range(size))
    from flask import current_app

    host, port = None, None
    if current_app.config.get("REDIS_HOST", None):
        host, port = current_app.config.get("REDIS_HOST", None), current_app.config.get("REDIS_PORT", None)

    redis = get_redis(host, port)

    if redis.exists(slug):
        try:
            return _generate_url_slug()
        except RecursionError:
            return
    else:
        return slug
