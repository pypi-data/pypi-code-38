import http
import inspect

from functools import wraps

from .exceptions import SlipoException


def json_response(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            r = func(*args, **kwargs)

            response = r.json()

            if r.status_code != http.HTTPStatus.OK or not response['success']:
                text = response['errors'][0]['description'] if 'errors' in response else response['error']
                raise SlipoException(text)
            else:
                if 'result' in response:
                    return response['result']
                else:
                    return None
        except SlipoException:
            raise
        except Exception as ex:
            raise SlipoException(ex)

    return wrapper


def file_response(target):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            spec = inspect.getfullargspec(func)
            index = spec.args.index(target)

            try:
                r = func(*args, **kwargs)

                if r.status_code != http.HTTPStatus.OK:
                    response = r.json()

                    text = response['errors'][0]['description'] if 'errors' in response else response['error']
                    raise SlipoException(text)
                else:
                    with open(args[index], 'wb') as f:
                        f.write(r.content)
            except SlipoException:
                raise
            except Exception as ex:
                raise SlipoException(ex)

        return wrapper

    return decorator
