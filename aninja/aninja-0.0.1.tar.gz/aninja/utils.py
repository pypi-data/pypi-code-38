import time
import dateparser
import random
import asyncio

TIME_TEMPLATE = '%a, %d-%b-%Y %H:%M:%S GMT'


def filter_attrs(time_format='number',
                 attrs=('name', 'value', 'domain', 'path', 'expires'),
                 **kwargs) -> dict:
    """filters a dictionary with expected attributes and expected time format
    for the expires attribute.

    Args:
        time_format: 'string' or 'number' or 'original'
        attrs: needed key for pairs
        kwargs: a key-value pairs for a cookie
    """
    result = {}
    for attr in attrs:
        if attr in kwargs:
            result[attr] = kwargs[attr]
            if attr == 'expires':
                result[attr] = format_expires(
                    kwargs[attr], time_format=time_format)
    return result


def format_expires(raw, time_format='number'):
    formatter = {
        'number': expires_to_number,
        'string': expires_to_str,
        'original': lambda x: x
    }
    return formatter[time_format](raw)


def expires_to_number(raw):
    if raw == -1:
        return None
    else:
        return _parse_expires_to_timestamp(raw)


def expires_to_str(raw, template=TIME_TEMPLATE):
    ts = _parse_expires_to_timestamp(raw)
    return time.strftime(template, time.gmtime(ts))


def _parse_expires_to_timestamp(raw):
    if isinstance(raw, str):
        dt = dateparser.parse(raw)
        return dt.timestamp()
    elif isinstance(raw, (int, float)):
        return raw
    else:
        raise TypeError('Need a valid expires time.')


js1 = '''() =>{
    
           Object.defineProperties(navigator,{
             webdriver:{
               get: () => false
             }
           })
        }'''


js2 = '''() => {
        window.navigator.chrome = {
    runtime: {},
    // etc.
  };
    }'''

js3 = '''() =>{
Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
        }'''

js4 = '''() =>{
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5,6],
  });
        }'''


js5 = '''() => {
        alert (
            window.navigator.webdriver
        )
    }'''


def random_delay(min=30, max=50):
    return random.randint(min, max)


def get_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'


def sync_coroutine(coro, loop=None):
    (loop or asyncio.get_event_loop()).run_until_complete(coro)


pretend_js_list = [js1, js2, js3, js4]
