import os
import sys


def _get_msg():
    os_name = os.name
    py_name = sys.implementation.name
    py_major = sys.implementation.version.major
    py_minor = sys.implementation.version.minor
    py_micro = sys.implementation.version.micro
    hit_msg = '{os_name} {py_name}{py_minor}.{py_major}.{py_micro}... Check'.format_map(
        locals()
    )
    miss_msg = '{os_name} {py_name}{py_minor}.{py_major}.{py_micro}... Huh?'.format_map(
        locals()
    )

    if os_name == 'posix':
        if py_name == 'pypy':
            if py_major == 3:
                if py_minor == 5:
                    return hit_msg
        elif py_name == 'cpython':
            if py_major == 3:
                if py_minor == 5:
                    return hit_msg
                elif py_minor == 6:
                    return hit_msg
                elif py_minor == 7:
                    return hit_msg
    elif os_name == 'nt':
        if py_name == 'cpython':
            if py_major == 3:
                if py_minor == 7:
                    return hit_msg

    return miss_msg  # 'os2', 'ce', 'java', 'riscos'


def test_version_coverage():
    print(_get_msg())
